# gemini_parallel_api.py

import os
import time
import logging
import threading
import concurrent.futures
import traceback
import random
from typing import Union
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
import queue
import uuid

# Import media processing utilities
try:
    # Try relative import (when run as package)
    from .gemini_media_processor import prepare_media_contents
    from .types import PromptData
except ImportError:
    # Try absolute import (when run as script/debugger)
    from gemini_media_processor import prepare_media_contents  # type: ignore
    from types import PromptData  # type: ignore

load_dotenv()


# --- Constants ---
# Markers for internal communication about API call outcomes
EXHAUSTED_MARKER = "RESOURCE_EXHAUSTED"
PERSISTENT_ERROR_MARKER = "PERSISTENT_ERROR"
ALL_KEYS_WAITING_MARKER = "ALL_KEYS_WAITING"

# Key status markers for the manager
KEY_STATUS_AVAILABLE = "AVAILABLE"
KEY_STATUS_COOLDOWN = "COOLDOWN"  # Status: cooling down after use
KEY_STATUS_TEMPORARILY_EXHAUSTED = "TEMPORARILY_EXHAUSTED"  # Status: temporarily exhausted
KEY_STATUS_FULLY_EXHAUSTED = "FULLY_EXHAUSTED"  # Status: fully exhausted
KEY_STATUS_FAILED_INIT = "FAILED_INIT"

# Configure logging for the module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s",
)


class AdvancedApiKeyManager:
    """
    Advanced API key manager: supports worker-specific key assignment with cooldown, 
    staged exhausted states, time-based recovery, and adaptive cooldown adjustment.
    """
    def __init__(self, keylist_names, 
                 paid_keys=None,
                 key_settings=None,
                 adaptive_cooldown_settings=None):
        """
        Initialize the advanced API key manager.

        Args:
            keylist_names (list[str] | str | int): 
                - List of environment variable names containing API keys
                - "all": Find all GEMINI_API_KEY_* environment variables
                - Integer (e.g., 5): Search for GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEY_5
                - Range string (e.g., "1-15"): Search for GEMINI_API_KEY_1 through GEMINI_API_KEY_15
            paid_keys (str | list[str] | None): 
                - "all": All keys are paid
                - List of strings: Environment variable names of paid keys (e.g., ["GEMINI_API_KEY_1", "GEMINI_API_KEY_3"])
                - None: All keys are free (default behavior)
            key_settings (dict | None): Settings for each key category
                Example: {
                    "free": {
                        "key_cooldown_seconds": 30,
                        "exhausted_wait_seconds": 120,
                        "fully_exhausted_wait_seconds": 43200,
                        "max_exhausted_retries": 3
                    },
                    "paid": {
                        "key_cooldown_seconds": 0,
                        "exhausted_wait_seconds": 60,
                        "fully_exhausted_wait_seconds": 3600,
                        "max_exhausted_retries": 5
                    }
                }
                If not provided, default settings will be used.
            adaptive_cooldown_settings (dict | None): Settings for adaptive cooldown adjustment
                Example: {
                    "enabled": True,  # Whether to enable adaptive cooldown
                    "exhaustion_threshold": 0.02,  # Threshold rate (2% default)
                    "initial_multiplier": 1.1,  # Initial cooldown increase (10%)
                    "max_multiplier": 1.5,  # Maximum cooldown increase (50%)
                    "multiplier_increment": 0.1,  # How much to increase multiplier each time
                    "api_call_window": 300,  # Window to track API calls (5 minutes)
                    "cooldown_recovery_rate": 0.9  # Multiplier for cooldown recovery (90% of previous)
                }
        """
        self.paid_keys = paid_keys
        
        # Default adaptive cooldown settings
        default_adaptive_settings = {
            "enabled": True,
            "exhaustion_threshold": 0.02,  # 2% exhaustion rate threshold
            "initial_multiplier": 1.1,  # Start with 10% increase
            "max_multiplier": 1.5,  # Maximum 50% increase
            "multiplier_increment": 0.1,  # Increase by 10% each time
            "api_call_window": 300,  # 5 minute window
            "cooldown_recovery_rate": 0.9  # Reduce multiplier by 10% on recovery
        }
        
        # Parse adaptive cooldown settings or use defaults
        if adaptive_cooldown_settings is None:
            self.adaptive_settings = default_adaptive_settings
        else:
            self.adaptive_settings = {**default_adaptive_settings, **adaptive_cooldown_settings}
        
        # Adaptive cooldown tracking
        self.api_call_history = []  # List of (timestamp, was_exhausted) tuples
        self.current_cooldown_multiplier = 1.0  # Current multiplier for cooldowns
        self.last_adjustment_time = 0  # Last time cooldowns were adjusted
        self.adjustment_count = 0  # Number of times cooldowns have been increased
        
        # Default settings for each category
        default_free_settings = {
            "key_cooldown_seconds": 30,  # 30 seconds cooldown
            "exhausted_wait_seconds": 120,  # 2 minutes temporary exhaustion
            "fully_exhausted_wait_seconds": 43200,  # 12 hours full exhaustion
            "max_exhausted_retries": 3  # 3 retries before full exhaustion
        }
        
        default_paid_settings = {
            "key_cooldown_seconds": 0,  # No cooldown for paid keys by default
            "exhausted_wait_seconds": 120,  # 2 minutes temporary exhaustion
            "fully_exhausted_wait_seconds": 43200,  # 12 hours full exhaustion
            "max_exhausted_retries": 3  # 3 retries before full exhaustion
        }
        
        # Parse key_settings or use defaults
        if key_settings is None:
            self.category_settings = {
                "free": default_free_settings,
                "paid": default_paid_settings
            }
        else:
            self.category_settings = {
                "free": {**default_free_settings, **key_settings.get("free", {})},
                "paid": {**default_paid_settings, **key_settings.get("paid", {})}
            }
        
        # Load keys with their environment variable names
        self.api_keys, self.key_to_env_name = self._load_keys_with_names(keylist_names)
        if not self.api_keys:
            raise ValueError("No valid API keys found from provided environment variables.")

        # Determine which keys are paid
        paid_key_set = self._determine_paid_keys(paid_keys)

        # Track detailed information for each key
        self.key_info = {}
        for key in self.api_keys:
            # Check if this key is paid based on its environment variable name
            env_name = self.key_to_env_name.get(key, "")
            is_paid = key in paid_key_set
            
            self.key_info[key] = {
                'status': KEY_STATUS_AVAILABLE,
                'last_used_time': 0,  # Last usage time
                'status_change_time': 0,  # Status change time
                'exhausted_count': 0,  # Consecutive exhausted count
                'total_exhausted_count': 0,  # Total exhausted count
                'assigned_worker': None,  # Which worker is using this key
                'category': 'paid' if is_paid else 'free',  # Key category
                'env_name': env_name,  # Environment variable name for debugging
            }
        
        self.num_keys = len(self.api_keys)
        
        # Worker-specific key assignments
        self.worker_assignments = {}  # worker_id -> api_key
        self.available_keys = set(self.api_keys)  # Keys not assigned to any worker
        
        self._lock = threading.Lock()
        self._adaptive_lock = threading.Lock()  # Separate lock for adaptive tracking

        # Count free and paid keys
        free_count = sum(1 for info in self.key_info.values() if info['category'] == 'free')
        paid_count = sum(1 for info in self.key_info.values() if info['category'] == 'paid')
        
        logging.info(f"AdvancedApiKeyManager initialized with {self.num_keys} keys (Free: {free_count}, Paid: {paid_count}).")
        
        # Log settings for each category
        for category, settings in self.category_settings.items():
            if (category == "free" and free_count > 0) or (category == "paid" and paid_count > 0):
                logging.info(f"{category.capitalize()} key settings: "
                            f"Cooldown: {settings['key_cooldown_seconds']}s, "
                            f"Exhausted wait: {settings['exhausted_wait_seconds']}s, "
                            f"Fully exhausted wait: {settings['fully_exhausted_wait_seconds']}s, "
                            f"Max retries: {settings['max_exhausted_retries']}")
        
        # Log adaptive cooldown settings if enabled
        if self.adaptive_settings['enabled']:
            logging.info(f"Adaptive cooldown enabled: threshold={self.adaptive_settings['exhaustion_threshold']:.1%}, "
                        f"window={self.adaptive_settings['api_call_window']}s")

    def _determine_paid_keys(self, paid_keys):
        """
        Determine which API keys are paid based on the paid_keys parameter.
        
        Args:
            paid_keys (str | list[str] | None): 
                - "all": All keys are paid
                - List of strings: Environment variable names of paid keys
                - None: No paid keys
                
        Returns:
            set: Set of API keys that are paid
        """
        paid_key_set = set()
        
        if paid_keys is None:
            # All keys are free
            logging.info("All keys are configured as free (with cooldown).")
            return paid_key_set
        
        if paid_keys == "all":
            # All keys are paid
            paid_key_set = set(self.api_keys)
            logging.info("All keys are configured as paid (no cooldown).")
            return paid_key_set
        
        if isinstance(paid_keys, list):
            # Specific keys are paid based on environment variable names
            for env_name in paid_keys:
                # Find the key associated with this environment variable name
                for key, key_env_name in self.key_to_env_name.items():
                    if key_env_name == env_name:
                        paid_key_set.add(key)
                        logging.debug(f"Key from '{env_name}' configured as paid.")
                        break
                else:
                    logging.warning(f"Environment variable '{env_name}' specified in paid_keys not found in loaded keys.")
            
            logging.info(f"Configured {len(paid_key_set)} keys as paid (no cooldown).")
        
        return paid_key_set

    def _load_keys_with_names(self, keylist_names):
        """
        Load API keys from environment variables and track their names.
        
        Returns:
            tuple: (list of API keys, dict mapping key to env variable name)
        """
        keys = []
        key_to_env_name = {}
        
        # Handle special cases
        if keylist_names == "all":
            # Search for all GEMINI_API_KEY* environment variables
            logging.info("Searching for all GEMINI_API_KEY_* environment variables...")
            for env_var, value in os.environ.items():
                if env_var.startswith("GEMINI_API_KEY") and value and len(value) > 10:
                    keys.append(value)
                    key_to_env_name[value] = env_var
                    logging.debug(f"Found API key from environment variable '{env_var}'.")
        elif isinstance(keylist_names, str) and '-' in keylist_names:
            # Handle range notation (e.g., "1-15")
            try:
                parts = keylist_names.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start_num = int(parts[0])
                    end_num = int(parts[1])
                    if start_num <= end_num:
                        logging.info(f"Searching for keys GEMINI_API_KEY_{start_num} through GEMINI_API_KEY_{end_num}...")
                        for i in range(start_num, end_num + 1):
                            key_name = f"GEMINI_API_KEY_{i}"
                            key = os.getenv(key_name)
                            if key and len(key) > 10:
                                keys.append(key)
                                key_to_env_name[key] = key_name
                                logging.debug(f"Loaded key from {key_name}.")
                            else:
                                logging.debug(f"Environment variable '{key_name}' not found or invalid.")
                    else:
                        logging.warning(f"Invalid range '{keylist_names}': start ({start_num}) should be <= end ({end_num})")
                else:
                    logging.warning(f"Invalid range format '{keylist_names}'. Expected format: 'start-end' (e.g., '1-15')")
            except Exception as e:
                logging.error(f"Error parsing range '{keylist_names}': {e}")
        elif isinstance(keylist_names, (int, str)) and str(keylist_names).isdigit():
            # Handle numeric input: search GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEY_n
            num_keys = int(keylist_names)
            logging.info(f"Searching for keys GEMINI_API_KEY_1 through GEMINI_API_KEY_{num_keys}...")
            for i in range(1, num_keys + 1):
                key_name = f"GEMINI_API_KEY_{i}"
                key = os.getenv(key_name)
                if key and len(key) > 10:
                    keys.append(key)
                    key_to_env_name[key] = key_name
                    logging.debug(f"Loaded key from {key_name}.")
                else:
                    logging.debug(f"Environment variable '{key_name}' not found or invalid.")
        elif isinstance(keylist_names, list):
            # Handle list of key names (original behavior)
            for key_name in keylist_names:
                key = os.getenv(key_name)
                if key and len(key) > 10:
                    keys.append(key)
                    key_to_env_name[key] = key_name
                    logging.debug(f"Loaded key from {key_name}.")
                else:
                    logging.warning(f"Environment variable '{key_name}' not found or invalid.")
        
        logging.info(f"Successfully loaded {len(keys)} valid API keys.")
        return keys, key_to_env_name

    def _load_keys(self, keylist_names):
        """
        Load API keys from environment variables.
        
        Examples:
            - keylist_names = ["GEMINI_API_KEY_1", "GEMINI_API_KEY_2"]  # Specific key names
            - keylist_names = "all"  # Find all GEMINI_API_KEY_* environment variables
            - keylist_names = 5  # Load GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEY_5
            - keylist_names = "1-15"  # Load GEMINI_API_KEY_1 through GEMINI_API_KEY_15
        """
        keys = []
        
        # Handle special cases
        if keylist_names == "all":
            # Search for all GEMINI_API_KEY* environment variables
            logging.info("Searching for all GEMINI_API_KEY_* environment variables...")
            for env_var, value in os.environ.items():
                if env_var.startswith("GEMINI_API_KEY") and value and len(value) > 10:
                    keys.append(value)
                    logging.debug(f"Found API key from environment variable '{env_var}'.")
        elif isinstance(keylist_names, str) and '-' in keylist_names:
            # Handle range notation (e.g., "1-15")
            try:
                parts = keylist_names.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start_num = int(parts[0])
                    end_num = int(parts[1])
                    if start_num <= end_num:
                        logging.info(f"Searching for keys GEMINI_API_KEY_{start_num} through GEMINI_API_KEY_{end_num}...")
                        for i in range(start_num, end_num + 1):
                            key_name = f"GEMINI_API_KEY_{i}"
                            key = os.getenv(key_name)
                            if key and len(key) > 10:
                                keys.append(key)
                                logging.debug(f"Loaded key from {key_name}.")
                            else:
                                logging.debug(f"Environment variable '{key_name}' not found or invalid.")
                    else:
                        logging.warning(f"Invalid range '{keylist_names}': start ({start_num}) should be <= end ({end_num})")
                else:
                    logging.warning(f"Invalid range format '{keylist_names}'. Expected format: 'start-end' (e.g., '1-15')")
            except Exception as e:
                logging.error(f"Error parsing range '{keylist_names}': {e}")
        elif isinstance(keylist_names, (int, str)) and str(keylist_names).isdigit():
            # Handle numeric input: search GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEY_n
            num_keys = int(keylist_names)
            logging.info(f"Searching for keys GEMINI_API_KEY_1 through GEMINI_API_KEY_{num_keys}...")
            for i in range(1, num_keys + 1):
                key_name = f"GEMINI_API_KEY_{i}"
                key = os.getenv(key_name)
                if key and len(key) > 10:
                    keys.append(key)
                    logging.debug(f"Loaded key from {key_name}.")
                else:
                    logging.debug(f"Environment variable '{key_name}' not found or invalid.")
        elif isinstance(keylist_names, list):
            # Handle list of key names (original behavior)
            for key_name in keylist_names:
                key = os.getenv(key_name)
                if key and len(key) > 10:
                    keys.append(key)
                    logging.debug(f"Loaded key from {key_name}.")
                else:
                    logging.warning(f"Environment variable '{key_name}' not found or invalid.")
        
        logging.info(f"Successfully loaded {len(keys)} valid API keys.")
        return keys

    def _update_key_status_based_on_time(self):
        """Update key statuses based on time with adaptive cooldown adjustments."""
        current_time = time.time()
        
        for key, info in self.key_info.items():
            category = info['category']
            # Get adjusted settings with multiplier applied
            settings = self.get_adjusted_cooldowns(category)
            
            if info['status'] == KEY_STATUS_COOLDOWN:
                # Check if cooldown time has passed based on adjusted settings
                if current_time - info['status_change_time'] >= settings['key_cooldown_seconds']:
                    info['status'] = KEY_STATUS_AVAILABLE
                    logging.debug(f"{category.capitalize()} key ...{key[-4:]} cooldown finished, now AVAILABLE")
            
            elif info['status'] == KEY_STATUS_TEMPORARILY_EXHAUSTED:
                # Check if temporary exhaustion time has passed based on adjusted settings
                if current_time - info['status_change_time'] >= settings['exhausted_wait_seconds']:
                    info['status'] = KEY_STATUS_AVAILABLE
                    logging.info(f"{category.capitalize()} key ...{key[-4:]} temporary exhaustion recovered, now AVAILABLE")
            
            elif info['status'] == KEY_STATUS_FULLY_EXHAUSTED:
                # Check if full exhaustion time has passed based on category settings (not adjusted)
                base_settings = self.category_settings[category]
                if current_time - info['status_change_time'] >= base_settings['fully_exhausted_wait_seconds']:
                    info['status'] = KEY_STATUS_AVAILABLE
                    info['exhausted_count'] = 0  # Reset count
                    logging.info(f"{category.capitalize()} key ...{key[-4:]} full exhaustion recovered, now AVAILABLE")

    def assign_key_to_worker(self, worker_id: str):
        """
        Assign a key to a specific worker. Each worker gets a dedicated key.
        
        Args:
            worker_id (str): Unique identifier for the worker
            
        Returns:
            str: API key assigned to the worker
            str: ALL_KEYS_WAITING_MARKER if no keys are available
            None: if no usable keys exist
        """
        with self._lock:
            # Update key statuses based on time
            self._update_key_status_based_on_time()
            
            # Check if worker already has a key assigned
            if worker_id in self.worker_assignments:
                assigned_key = self.worker_assignments[worker_id]
                key_info = self.key_info[assigned_key]
                
                # If assigned key is still usable (not FULLY_EXHAUSTED or FAILED_INIT), keep it
                if key_info['status'] not in [KEY_STATUS_FULLY_EXHAUSTED, KEY_STATUS_FAILED_INIT]:
                    logging.debug(f"Worker {worker_id} keeping assigned key ...{assigned_key[-4:]} (status: {key_info['status']})")
                    return assigned_key
                else:
                    # Release the unusable key and find a new one
                    logging.info(f"Worker {worker_id} releasing unusable key ...{assigned_key[-4:]} (status: {key_info['status']})")
                    self._release_key_from_worker(worker_id, assigned_key)
            
            # Find an available key for assignment - randomize selection
            available_key = None
            available_keys_list = list(self.available_keys)
            random.shuffle(available_keys_list)  # Randomize to distribute load
            for key in available_keys_list:
                key_info = self.key_info[key]
                if key_info['status'] not in [KEY_STATUS_FULLY_EXHAUSTED, KEY_STATUS_FAILED_INIT]:
                    available_key = key
                    break
            
            if available_key is None:
                # Check if any assigned keys can be reassigned (if their worker is done) - randomize
                unassigned_keys = [(key, info) for key, info in self.key_info.items()
                                   if info['assigned_worker'] is None and 
                                   info['status'] not in [KEY_STATUS_FULLY_EXHAUSTED, KEY_STATUS_FAILED_INIT]]
                if unassigned_keys:
                    random.shuffle(unassigned_keys)  # Randomize selection
                    available_key = unassigned_keys[0][0]
                    self.available_keys.add(available_key)
            
            if available_key is None:
                # No usable keys available
                status_counts = {}
                for info in self.key_info.values():
                    status = info['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts.get(KEY_STATUS_FAILED_INIT, 0) == self.num_keys:
                    logging.error("FATAL: All API keys failed initialization.")
                    return None
                
                logging.info(f"Worker {worker_id} waiting - no available keys. Status: {status_counts}")
                return ALL_KEYS_WAITING_MARKER
            
            # Assign the key to the worker
            self.worker_assignments[worker_id] = available_key
            self.key_info[available_key]['assigned_worker'] = worker_id
            self.available_keys.discard(available_key)
            
            logging.info(f"Assigned key ...{available_key[-4:]} to worker {worker_id}")
            return available_key
    
    def _release_key_from_worker(self, worker_id: str, api_key: str):
        """Internal method to release a key from a worker."""
        if worker_id in self.worker_assignments and self.worker_assignments[worker_id] == api_key:
            del self.worker_assignments[worker_id]
            self.key_info[api_key]['assigned_worker'] = None
            self.available_keys.add(api_key)
            logging.debug(f"Released key ...{api_key[-4:]} from worker {worker_id}")

    def release_key_from_worker(self, worker_id: str, api_key: str):
        """
        Release a key from a worker (public method).
        
        Args:
            worker_id (str): Worker identifier
            api_key (str): API key to release
        """
        with self._lock:
            self._release_key_from_worker(worker_id, api_key)

    def check_key_status(self, api_key: str) -> str:
        """
        Check the current status of a specific API key.
        
        Args:
            api_key (str): The API key to check
            
        Returns:
            str: Current status of the key
        """
        with self._lock:
            self._update_key_status_based_on_time()
            if api_key in self.key_info:
                return self.key_info[api_key]['status']
            return KEY_STATUS_FAILED_INIT

    def can_use_key_now(self, api_key: str) -> bool:
        """
        Check if a key can be used immediately (not in cooldown or temporarily exhausted).
        
        Args:
            api_key (str): The API key to check
            
        Returns:
            bool: True if key can be used now, False otherwise
        """
        status = self.check_key_status(api_key)
        return status == KEY_STATUS_AVAILABLE

    def mark_key_used(self, api_key: str):
        """
        Mark a key as just used (put it in cooldown based on its category with adaptive adjustments).
        
        Args:
            api_key (str): The API key that was used
        """
        with self._lock:
            if api_key not in self.key_info:
                logging.error(f"Unknown key marked as used: {api_key}")
                return
            
            info = self.key_info[api_key]
            category = info['category']
            # Get adjusted cooldown with multiplier applied
            adjusted_settings = self.get_adjusted_cooldowns(category)
            cooldown_seconds = adjusted_settings['key_cooldown_seconds']
            
            info['last_used_time'] = time.time()
            
            # Only put in cooldown if cooldown_seconds > 0
            if cooldown_seconds > 0:
                info['status'] = KEY_STATUS_COOLDOWN
                info['status_change_time'] = time.time()
                logging.debug(f"{category.capitalize()} key ...{api_key[-4:]} marked as used, now in COOLDOWN for {cooldown_seconds:.1f}s")
            else:
                # No cooldown for this category (e.g., paid keys with 0 cooldown)
                info['status'] = KEY_STATUS_AVAILABLE
                logging.debug(f"{category.capitalize()} key ...{api_key[-4:]} marked as used, no cooldown (immediately available)")

    def mark_key_exhausted(self, api_key):
        """
        Mark key as exhausted.
        Classify as temporary or full exhaustion based on consecutive exhausted count and category settings.
        Also tracks exhaustion for adaptive cooldown adjustment.
        """
        with self._lock:
            if api_key not in self.key_info:
                logging.error(f"Unknown key marked as exhausted: {api_key}")
                return
            
            info = self.key_info[api_key]
            category = info['category']
            settings = self.category_settings[category]
            
            info['exhausted_count'] += 1
            info['total_exhausted_count'] += 1
            current_time = time.time()
            
            masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else "invalid key"
            
            # Track this exhaustion event for adaptive cooldown
            if self.adaptive_settings['enabled']:
                self._track_api_call(current_time, was_exhausted=True)
            
            if info['exhausted_count'] >= settings['max_exhausted_retries']:
                # Change to fully exhausted status (not adjusted)
                info['status'] = KEY_STATUS_FULLY_EXHAUSTED
                info['status_change_time'] = current_time
                wait_hours = settings['fully_exhausted_wait_seconds'] / 3600
                logging.warning(
                    f"{category.capitalize()} key {masked_key} marked as FULLY_EXHAUSTED "
                    f"(count: {info['exhausted_count']}) - waiting {wait_hours:.1f}h"
                )
            else:
                # Change to temporarily exhausted status (use adjusted wait time)
                adjusted_settings = self.get_adjusted_cooldowns(category)
                info['status'] = KEY_STATUS_TEMPORARILY_EXHAUSTED
                info['status_change_time'] = current_time
                wait_minutes = adjusted_settings['exhausted_wait_seconds'] / 60
                logging.warning(
                    f"{category.capitalize()} key {masked_key} marked as TEMPORARILY_EXHAUSTED "
                    f"(count: {info['exhausted_count']}) - waiting {wait_minutes:.1f}m"
                    f"{' (adjusted)' if self.current_cooldown_multiplier != 1.0 else ''}"
                )

    def mark_key_successful(self, api_key):
        """
        Called when key usage is successful.
        Resets exhausted count and tracks successful call for adaptive cooldown.
        """
        with self._lock:
            if api_key not in self.key_info:
                return
            
            info = self.key_info[api_key]
            if info['exhausted_count'] > 0:
                logging.info(f"Key ...{api_key[-4:]} successful, resetting exhausted count from {info['exhausted_count']} to 0")
                info['exhausted_count'] = 0
            
            # Track this successful call for adaptive cooldown
            if self.adaptive_settings['enabled']:
                current_time = time.time()
                self._track_api_call(current_time, was_exhausted=False)

    def mark_key_failed_init(self, api_key):
        """Mark key initialization failure."""
        with self._lock:
            if api_key not in self.key_info:
                return
            
            self.key_info[api_key]['status'] = KEY_STATUS_FAILED_INIT
            masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else "invalid key"
            logging.error(f"Key {masked_key} marked as FAILED_INIT")

    def get_keys_status_summary(self):
        """Return status summary of all keys."""
        with self._lock:
            self._update_key_status_based_on_time()
            
            summary = {}
            for key, info in self.key_info.items():
                masked_key = f"...{key[-4:]}"
                summary[masked_key] = {
                    'status': info['status'],
                    'category': info['category'],
                    'exhausted_count': info['exhausted_count'],
                    'total_exhausted_count': info['total_exhausted_count'],
                    'assigned_worker': info['assigned_worker']
                }
            
            return summary

    def get_any_available_key(self, worker_id: str = None):
        """
        Get any available key for immediate use (for streaming processors).
        This method doesn't assign keys permanently to workers, allowing for more dynamic usage.
        
        Args:
            worker_id (str, optional): Worker identifier for logging purposes
            
        Returns:
            str: API key that can be used immediately
            str: ALL_KEYS_WAITING_MARKER if no keys are available
            None: if no usable keys exist
        """
        with self._lock:
            # Update key statuses based on time
            self._update_key_status_based_on_time()
            
            # Find any key that can be used immediately - randomize selection
            available_key = None
            available_keys = [(key, info) for key, info in self.key_info.items()
                              if info['status'] == KEY_STATUS_AVAILABLE]
            if available_keys:
                available_key = random.choice(available_keys)[0]  # Random selection
            
            if available_key is None:
                # Check status counts for decision making
                status_counts = {}
                for info in self.key_info.values():
                    status = info['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts.get(KEY_STATUS_FAILED_INIT, 0) == self.num_keys:
                    logging.error("FATAL: All API keys failed initialization.")
                    return None
                
                worker_msg = f" for worker {worker_id}" if worker_id else ""
                logging.debug(f"No available keys{worker_msg}. Status: {status_counts}")
                return ALL_KEYS_WAITING_MARKER
            
            # Mark key as temporarily assigned
            self.key_info[available_key]['last_used_time'] = time.time()
            
            masked_key = f"...{available_key[-4:]}" if len(available_key) > 4 else "invalid key"
            worker_msg = f" to worker {worker_id}" if worker_id else ""
            logging.debug(f"Providing available key {masked_key}{worker_msg}")
            return available_key

    def mark_key_returned(self, api_key: str, worker_id: str = None):
        """
        Mark a key as returned after use (for dynamic key usage).
        This doesn't release assignment like release_key_from_worker since the key wasn't permanently assigned.
        
        Args:
            api_key (str): The API key that was used
            worker_id (str, optional): Worker identifier for logging purposes
        """
        # This is essentially the same as mark_key_used, but with different semantics
        self.mark_key_used(api_key)
        
        masked_key = f"...{api_key[-4:]}" if len(api_key) > 4 else "invalid key"
        worker_msg = f" from worker {worker_id}" if worker_id else ""
        logging.debug(f"Key {masked_key} returned{worker_msg}, now in cooldown")
    
    def _track_api_call(self, timestamp: float, was_exhausted: bool):
        """
        Track an API call for adaptive cooldown calculation.
        
        Args:
            timestamp (float): Time of the API call
            was_exhausted (bool): Whether this call resulted in exhaustion
        """
        with self._adaptive_lock:
            # Add to history
            self.api_call_history.append((timestamp, was_exhausted))
            
            # Clean up old entries outside the window
            window_start = timestamp - self.adaptive_settings['api_call_window']
            self.api_call_history = [(t, e) for t, e in self.api_call_history if t >= window_start]
            
            # Check if we should adjust cooldowns
            if len(self.api_call_history) >= 10:  # Need at least 10 calls to calculate rate
                self._check_and_adjust_cooldowns(timestamp)
    
    def _check_and_adjust_cooldowns(self, current_time: float):
        """
        Check exhaustion rate and adjust cooldowns if threshold is exceeded.
        
        Args:
            current_time (float): Current timestamp
        """
        # Calculate exhaustion rate
        total_calls = len(self.api_call_history)
        exhausted_calls = sum(1 for _, was_exhausted in self.api_call_history if was_exhausted)
        exhaustion_rate = exhausted_calls / total_calls if total_calls > 0 else 0
        
        # Check if we need to adjust cooldowns
        threshold = self.adaptive_settings['exhaustion_threshold']
        
        if exhaustion_rate > threshold:
            # Increase cooldowns
            if self.current_cooldown_multiplier < self.adaptive_settings['max_multiplier']:
                old_multiplier = self.current_cooldown_multiplier
                
                # Increase multiplier progressively
                if self.adjustment_count == 0:
                    self.current_cooldown_multiplier = self.adaptive_settings['initial_multiplier']
                else:
                    self.current_cooldown_multiplier = min(
                        self.current_cooldown_multiplier + self.adaptive_settings['multiplier_increment'],
                        self.adaptive_settings['max_multiplier']
                    )
                
                self.adjustment_count += 1
                self.last_adjustment_time = current_time
                
                logging.warning(
                    f"Exhaustion rate {exhaustion_rate:.1%} exceeds threshold {threshold:.1%}. "
                    f"Increasing cooldown multiplier from {old_multiplier:.1f}x to {self.current_cooldown_multiplier:.1f}x "
                    f"(adjustment #{self.adjustment_count})"
                )
                
                # Apply new multiplier to all categories
                self._apply_cooldown_multiplier()
        
        elif exhaustion_rate < threshold / 2 and self.current_cooldown_multiplier > 1.0:
            # Recovery: if exhaustion rate is below half the threshold, gradually reduce multiplier
            if current_time - self.last_adjustment_time > self.adaptive_settings['api_call_window']:
                old_multiplier = self.current_cooldown_multiplier
                self.current_cooldown_multiplier = max(
                    1.0,
                    self.current_cooldown_multiplier * self.adaptive_settings['cooldown_recovery_rate']
                )
                
                if self.current_cooldown_multiplier == 1.0:
                    self.adjustment_count = 0
                    logging.info(
                        f"Exhaustion rate {exhaustion_rate:.1%} is low. "
                        f"Cooldowns restored to normal (multiplier: 1.0x)"
                    )
                else:
                    logging.info(
                        f"Exhaustion rate {exhaustion_rate:.1%} is low. "
                        f"Reducing cooldown multiplier from {old_multiplier:.1f}x to {self.current_cooldown_multiplier:.1f}x"
                    )
                
                self.last_adjustment_time = current_time
                self._apply_cooldown_multiplier()
    
    def _apply_cooldown_multiplier(self):
        """
        Apply the current cooldown multiplier to all category settings.
        This affects key_cooldown_seconds, exhausted_wait_seconds, and api_call_interval.
        """
        # Note: This modifies the runtime values, not the original settings
        # The actual application happens in the processors
        pass
    
    def get_adjusted_cooldowns(self, category: str) -> dict:
        """
        Get the adjusted cooldown settings for a category.
        
        Args:
            category (str): 'free' or 'paid'
            
        Returns:
            dict: Adjusted settings with multiplier applied
        """
        base_settings = self.category_settings[category].copy()
        
        if self.adaptive_settings['enabled'] and self.current_cooldown_multiplier != 1.0:
            # Apply multiplier to time-based settings
            base_settings['key_cooldown_seconds'] *= self.current_cooldown_multiplier
            base_settings['exhausted_wait_seconds'] *= self.current_cooldown_multiplier
            
            # Log when queried (but not too frequently)
            if hasattr(self, '_last_adjusted_log_time'):
                if time.time() - self._last_adjusted_log_time > 60:  # Log at most once per minute
                    logging.debug(f"Using adjusted cooldowns for {category} keys (multiplier: {self.current_cooldown_multiplier:.1f}x)")
                    self._last_adjusted_log_time = time.time()
            else:
                self._last_adjusted_log_time = time.time()
        
        return base_settings
    
    def get_adaptive_status(self) -> dict:
        """
        Get current adaptive cooldown status.
        
        Returns:
            dict: Status information including exhaustion rate and multiplier
        """
        with self._adaptive_lock:
            total_calls = len(self.api_call_history)
            exhausted_calls = sum(1 for _, was_exhausted in self.api_call_history if was_exhausted)
            exhaustion_rate = exhausted_calls / total_calls if total_calls > 0 else 0
            
            return {
                'enabled': self.adaptive_settings['enabled'],
                'current_multiplier': self.current_cooldown_multiplier,
                'exhaustion_rate': exhaustion_rate,
                'threshold': self.adaptive_settings['exhaustion_threshold'],
                'adjustment_count': self.adjustment_count,
                'total_calls_in_window': total_calls,
                'exhausted_calls_in_window': exhausted_calls,
                'window_seconds': self.adaptive_settings['api_call_window']
            }

class GeminiParallelProcessor:
    """
    Manages parallel calls to the Gemini API using a DynamicApiKeyManager.
    It handles API key rotation, resource exhaustion retries, and general API errors.
    """
    def __init__(self, key_manager: AdvancedApiKeyManager, model_name: str,
                 worker_cooldown_seconds: float = 20,  # 20 seconds worker cooldown
                 api_call_interval: float = 5.0, 
                 max_workers: int = 4,  # 4 workers by default
                 api_call_retries: int = 3,  # 3 retries by default
                 return_response: bool = False):
        """
        Initializes the parallel processor with dynamic key allocation and dual cooldown system.

        Args:
            key_manager (AdvancedApiKeyManager): An instance of the API key manager.
            model_name (str): The name of the Gemini model to use (e.g., "gemini-2.0-flash-001").
            worker_cooldown_seconds (float): Time (in seconds) each worker waits between API calls.
                                            Workers grab any available key after cooldown expires.
            api_call_interval (float): Minimum time (in seconds) to wait between consecutive API calls 
                                      made by ANY worker. Prevents IP ban from too many simultaneous requests.
            max_workers (int): The maximum number of parallel threads to use. Recommended to be less or equal to 4.
            api_call_retries (int): Maximum number of retries for API call errors (default: 3).
            return_response (bool): Whether to return the full response object instead of just the text.
        """
        self.key_manager = key_manager
        self.model_name = model_name
        self.worker_cooldown_seconds = worker_cooldown_seconds
        self.api_call_interval = api_call_interval
        self.max_workers = max_workers
        self.api_call_retries = api_call_retries
        self.return_response = return_response

        # Track worker cooldowns individually
        self.worker_last_call_time = {}  # worker_id -> last_call_timestamp
        self.worker_lock = threading.Lock()
        
        # Global API call timing control (prevents IP ban)
        self._last_api_call_time = 0.0
        self._api_call_lock = threading.Lock()
        
        logging.info(
            f"GeminiParallelProcessor initialized for model '{self.model_name}' "
            f"with {self.max_workers} workers, worker cooldown {self.worker_cooldown_seconds}s, "
            f"and global API interval {self.api_call_interval}s."
        )
    
    def get_adjusted_api_interval(self) -> float:
        """Get the adjusted API call interval with adaptive multiplier applied."""
        if self.key_manager.adaptive_settings['enabled']:
            return self.api_call_interval * self.key_manager.current_cooldown_multiplier
        return self.api_call_interval
    
    def get_adjusted_worker_cooldown(self) -> float:
        """Get the adjusted worker cooldown with adaptive multiplier applied."""
        if self.key_manager.adaptive_settings['enabled']:
            return self.worker_cooldown_seconds * self.key_manager.current_cooldown_multiplier
        return self.worker_cooldown_seconds



    def _make_single_api_call(self, client_instance, prompt_data: Union[dict, PromptData]) -> str:
        """
        Executes a single API call to the Gemini model.
        Handles retries for non-quota errors.
        Supports both text-only and text+audio/video prompts with position specification.

        Args:
            client_instance: An initialized genai.Client instance.
            prompt_data (Union[dict, PromptData]): Dictionary or PromptData object containing:
                - 'prompt' (str): The text prompt (can contain <audio> and <video> tokens for positioning)
                - 'audio_path' (str or list[str], optional): Path(s) to audio file(s)
                - 'audio_bytes' (bytes or list[bytes], optional): Audio bytes
                - 'video_url' (str or list[str], optional): URL(s) of video file(s)
                - 'video_path' (str or list[str], optional): Path(s) to video file(s)
                - 'video_bytes' (bytes or list[bytes], optional): Video bytes
                - 'audio_mime_type' (str or list[str], optional): MIME type(s) of audio file(s) (e.g., 'audio/mp3')
                - 'video_mime_type' (str or list[str], optional): MIME type(s) of video file(s) (e.g., 'video/mp4')
                - 'video_metadata' (dict or list[dict], optional): Metadata for video file(s)
                - 'generation_config' (dict, optional): Generation config for the API call
        
        Instructions:
            - Use <audio> and <video> tokens in prompt to specify positioning
            - Multiple tokens are supported and will be matched with files in order
            - Videos and audios bigger than 20MB are recommended to be uploaded with paths
            
        Returns:
            str: The raw text response from the Gemini model on success.
            str: `EXHAUSTED_MARKER` if a ResourceExhausted error occurs.
            str: `PERSISTENT_ERROR_MARKER` if other errors persist after retries.
        """
        # Convert PromptData to dict if needed
        if isinstance(prompt_data, PromptData):
            prompt_dict = prompt_data.to_dict()
        else:
            prompt_dict = prompt_data
        
        # Prepare media contents using external utility
        contents, error_msg = prepare_media_contents(client_instance, prompt_dict)
        if contents is None:
            return PERSISTENT_ERROR_MARKER
        
        generation_config = prompt_dict.get('generation_config', {})
        
        # Perform API call with retries
        retries = 0
        wait_time = 30  # Initial retry delay in seconds
        while retries < self.api_call_retries:  # Maximum retries for API call errors
            response = None
            try:
                # Global API call interval control - prevents IP ban from simultaneous requests
                with self._api_call_lock:
                    current_time = time.time()
                    time_since_last_call = current_time - self._last_api_call_time
                    adjusted_interval = self.get_adjusted_api_interval()
                    
                    if time_since_last_call < adjusted_interval:
                        sleep_time = adjusted_interval - time_since_last_call
                        worker_id = threading.current_thread().name
                        logging.debug(f"Worker {worker_id} waiting {sleep_time:.2f}s for global API interval (adjusted: {adjusted_interval:.1f}s)")
                        time.sleep(sleep_time)
                    
                    # Update last API call time before making the call
                    self._last_api_call_time = time.time()
                
                # Handle generation_config - support dict or types objects
                if isinstance(generation_config, types.GenerateContentConfig):
                    config = generation_config
                elif isinstance(generation_config, dict) and generation_config:
                    # Convert nested configs if they're dicts
                    config_kwargs = generation_config.copy()
                    
                    # Convert thinkingConfig if it's a dict
                    if 'thinkingConfig' in config_kwargs and isinstance(config_kwargs['thinkingConfig'], dict):
                        config_kwargs['thinkingConfig'] = types.ThinkingConfig(**config_kwargs['thinkingConfig'])
                    elif 'thinking_config' in config_kwargs and isinstance(config_kwargs['thinking_config'], dict):
                        config_kwargs['thinkingConfig'] = types.ThinkingConfig(**config_kwargs.pop('thinking_config'))
                    
                    # Convert speechConfig if it's a dict
                    if 'speechConfig' in config_kwargs and isinstance(config_kwargs['speechConfig'], dict):
                        config_kwargs['speechConfig'] = types.SpeechConfig(**config_kwargs['speechConfig'])
                    elif 'speech_config' in config_kwargs and isinstance(config_kwargs['speech_config'], dict):
                        config_kwargs['speechConfig'] = types.SpeechConfig(**config_kwargs.pop('speech_config'))
                    
                    # Convert snake_case to camelCase for other fields
                    if 'max_output_tokens' in config_kwargs:
                        config_kwargs['maxOutputTokens'] = config_kwargs.pop('max_output_tokens')
                    if 'stop_sequences' in config_kwargs:
                        config_kwargs['stopSequences'] = config_kwargs.pop('stop_sequences')
                    if 'response_mime_type' in config_kwargs:
                        config_kwargs['responseMimeType'] = config_kwargs.pop('response_mime_type')
                    if 'response_logprobs' in config_kwargs:
                        config_kwargs['responseLogprobs'] = config_kwargs.pop('response_logprobs')
                    if 'top_p' in config_kwargs:
                        config_kwargs['topP'] = config_kwargs.pop('top_p')
                    if 'top_k' in config_kwargs:
                        config_kwargs['topK'] = config_kwargs.pop('top_k')
                    if 'presence_penalty' in config_kwargs:
                        config_kwargs['presencePenalty'] = config_kwargs.pop('presence_penalty')
                    if 'frequency_penalty' in config_kwargs:
                        config_kwargs['frequencyPenalty'] = config_kwargs.pop('frequency_penalty')
                    if 'candidate_count' in config_kwargs:
                        config_kwargs['candidateCount'] = config_kwargs.pop('candidate_count')
                    if 'response_modalities' in config_kwargs:
                        config_kwargs['responseModalities'] = config_kwargs.pop('response_modalities')
                    if 'media_resolution' in config_kwargs:
                        config_kwargs['mediaResolution'] = config_kwargs.pop('media_resolution')
                    if 'response_schema' in config_kwargs:
                        config_kwargs['responseSchema'] = config_kwargs.pop('response_schema')
                    if 'response_json_schema' in config_kwargs:
                        config_kwargs['responseJsonSchema'] = config_kwargs.pop('response_json_schema')
                    
                    config = types.GenerateContentConfig(**config_kwargs)
                else:
                    config = types.GenerateContentConfig()
                
                response = client_instance.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
                response_text = response.text.strip()
                
                # Log content types for debugging
                media_count = sum(1 for content in contents if hasattr(content, 'file_data') or hasattr(content, 'inline_data'))
                content_type = f"text+{media_count}media" if media_count > 0 else "text-only"
                logging.debug(f"API call successful ({content_type}). Response length: {len(response_text)}.")
                if self.return_response:
                    return response
                else:
                    return response_text

            except genai_errors.APIError as e:
                # Handle different error codes based on official Gemini API documentation
                error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
                
                if error_code == 429:  # RESOURCE_EXHAUSTED
                    logging.warning(f"RESOURCE_EXHAUSTED (429): {e}. Signaling exhaustion.")
                    return EXHAUSTED_MARKER
                    
                elif error_code in [400, 403, 404]:  # Non-retryable errors
                    # 400: INVALID_ARGUMENT, FAILED_PRECONDITION
                    # 403: PERMISSION_DENIED  
                    # 404: NOT_FOUND
                    logging.error(f"Non-retryable error ({error_code}): {e}. Signaling persistent error.")
                    return PERSISTENT_ERROR_MARKER
                    
                elif error_code in [500, 503, 504]:  # Retryable server errors
                    # 500: INTERNAL - Google internal error
                    # 503: UNAVAILABLE - Service temporarily overloaded/down
                    # 504: DEADLINE_EXCEEDED - Service couldn't complete in time
                    logging.warning(
                        f"Retryable server error ({error_code}): {e}. "
                        f"Retry {retries + 1}/{self.api_call_retries}..."
                    )
                else:
                    # Unknown error code - treat as retryable
                    logging.warning(
                        f"Unknown APIError ({error_code}): {e}. "
                        f"Retry {retries + 1}/{self.api_call_retries}..."
                    )
            except Exception as e:
                logging.error(
                    f"Unexpected error during API call: {type(e).__name__} - {e}. "
                    f"Traceback: {traceback.format_exc()}. "
                    f"Retry {retries + 1}/{self.api_call_retries}..."
                )

            retries += 1
            if retries < self.api_call_retries:
                logging.info(f"Waiting {wait_time}s before retrying API call...")
                time.sleep(wait_time)
                wait_time = wait_time * 2**retries # Exponential backoff
            else:
                logging.error(
                    f"Failed API call after {self.api_call_retries} retries."
                )
                return PERSISTENT_ERROR_MARKER

        return PERSISTENT_ERROR_MARKER

    def _worker_task(self, prompt_data: Union[dict, PromptData]) -> tuple:
        """
        Worker function with dynamic key allocation and worker cooldown management.
        
        1. Worker checks its own cooldown before attempting any work
        2. Worker grabs any available key when ready to work  
        3. After API call, worker enters cooldown and key enters cooldown separately
        4. No permanent key assignment - keys are grabbed dynamically per task

        Args:
            prompt_data (Union[dict, PromptData]): A dictionary or PromptData object containing 'prompt' (str) and
                                'metadata' (dict) for the task.

        Returns:
            tuple: (metadata_dict, api_response_text_or_marker, error_message_str)
        """
        # Handle both dict and PromptData
        if isinstance(prompt_data, PromptData):
            prompt = prompt_data.prompt
            metadata = prompt_data.metadata
        else:
            prompt = prompt_data['prompt']
            metadata = prompt_data['metadata']
        task_id = metadata.get('task_id', 'unknown_task')
        worker_id = threading.current_thread().name

        if not prompt:
            logging.warning(f"Skipping task {task_id} due to empty prompt.")
            return metadata, None, "Empty prompt provided."

        # Check worker cooldown first
        with self.worker_lock:
            current_time = time.time()
            last_call_time = self.worker_last_call_time.get(worker_id, 0)
            time_since_last_call = current_time - last_call_time
            adjusted_cooldown = self.get_adjusted_worker_cooldown()
            
            if time_since_last_call < adjusted_cooldown:
                wait_time = adjusted_cooldown - time_since_last_call
                logging.debug(f"Worker {worker_id} in cooldown, waiting {wait_time:.1f}s (adjusted: {adjusted_cooldown:.1f}s)")
                time.sleep(wait_time)

        # Dynamic key allocation - try to get any available key
        max_wait_time = 3600  # Maximum 1 hour waiting for keys
        start_time = time.time()
        attempt_count = 0
        
        while (time.time() - start_time) < max_wait_time:
            # Get any available key for this task
            current_api_key = self.key_manager.get_any_available_key(worker_id)

            if current_api_key == ALL_KEYS_WAITING_MARKER:
                # All keys are busy, wait and retry
                elapsed = time.time() - start_time
                if elapsed > max_wait_time / 2:  # After half the time, log warning
                    logging.warning(f"Worker {worker_id} has been waiting {elapsed:.0f}s for available keys")
                
                # Progressive backoff: wait longer as time goes on
                wait_time = min(30, 10 + (attempt_count // 10) * 5)  # 10s, 15s, 20s, up to 30s
                logging.debug(f"Worker {worker_id} waiting {wait_time}s - all keys busy (attempt {attempt_count + 1})")
                time.sleep(wait_time)
                attempt_count += 1
                continue
            elif current_api_key is None:
                logging.error(f"Worker {worker_id} for task {task_id} - FATAL: No usable keys")
                return metadata, None, "Fatal: No usable API keys available."

            masked_key = f"...{current_api_key[-4:]}" if len(current_api_key) > 4 else "invalid key"
            
            # Initialize client with the key
            try:
                logging.debug(f"Worker {worker_id} using key {masked_key} for task {task_id}")
                client_instance = genai.Client(api_key=current_api_key)

            except Exception as e:
                logging.error(f"Failed to initialize client for {task_id} with key {masked_key}: {e}")
                self.key_manager.mark_key_failed_init(current_api_key)
                continue

            # Perform API call
            result = self._make_single_api_call(client_instance, prompt_data)
            
            # Update worker's last call time regardless of result (API call was made)
            with self.worker_lock:
                self.worker_last_call_time[worker_id] = time.time()
            
            if result == EXHAUSTED_MARKER:
                # Key is exhausted - mark it and try again with another key
                logging.warning(f"Key {masked_key} exhausted for task {task_id}, trying another key")
                self.key_manager.mark_key_exhausted(current_api_key)
                continue
            elif result == PERSISTENT_ERROR_MARKER:
                # Persistent error - treat this task as failed
                logging.error(f"Persistent error for {task_id} with key {masked_key}")
                return metadata, None, "Persistent API call error."
            else:
                # Success! Update key cooldown
                logging.debug(f"Success for {task_id} with key {masked_key}")
                
                # Mark key as successful and put it in cooldown
                self.key_manager.mark_key_successful(current_api_key)
                self.key_manager.mark_key_returned(current_api_key, worker_id)
                
                return metadata, result, None

        # Timeout exceeded
        elapsed_time = time.time() - start_time
        logging.error(f"Task {task_id} failed after {elapsed_time:.0f}s of waiting for available keys")
        return metadata, None, f"Failed: All keys exhausted for {elapsed_time:.0f}s. Keys may need quota reset."

    def process_prompts(self, prompts_with_metadata: list[Union[dict, PromptData]]) -> list[tuple]:
        """
        Processes a list of prompts in parallel using dynamic key allocation.
        Workers grab any available key when ready to work, with individual worker cooldowns.
        Supports text-only and multimedia inputs with flexible positioning.

        Args:
            prompts_with_metadata (list[Union[dict, PromptData]]): A list of dictionaries or PromptData objects, where each
                                                can contain:
                                                - 'prompt' (str): The text prompt to send to Gemini.
                                                  Can contain <audio> and <video> tokens for positioning.
                                                - 'audio_path' (str or list[str], optional): Path(s) to audio file(s).
                                                - 'audio_bytes' (bytes or list[bytes], optional): Audio bytes.
                                                - 'audio_mime_type' (str or list[str], optional): MIME type(s) of audio (default: 'audio/mp3').
                                                - 'video_url' (str or list[str], optional): URL(s) of video file(s).
                                                - 'video_path' (str or list[str], optional): Path(s) to video file(s).
                                                - 'video_bytes' (bytes or list[bytes], optional): Video bytes.
                                                - 'video_mime_type' (str or list[str], optional): MIME type(s) of video (default: 'video/mp4').
                                                - 'video_metadata' (dict or list[dict], optional): Metadata for video file(s).
                                                - 'generation_config' (dict, optional): Generation config for the API call.
                                                - 'metadata' (dict): A dictionary of any
                                                  additional data associated with this prompt
                                                  (e.g., original line index, task info).
                                                  It's recommended to include a 'task_id' for logging.

        Example usage with positioning:
            prompts_with_metadata = [{
                'prompt': 'Analyze this audio: <audio> Then compare with this video: <video> What do you think about <audio>?',
                'audio_path': ['audio1.mp3', 'audio2.mp3'],
                'video_path': ['video1.mp4'],
                'metadata': {'task_id': 'multimedia_analysis_1'}
            }]

        Returns:
            list[tuple]: A list of tuples, where each tuple contains:
                         (metadata_dict, api_response_text_or_none, error_message_str_or_none).
                         The `metadata_dict` is the original metadata passed in.
                         `api_response_text_or_none` is the raw text response from Gemini on success,
                         or None if an error occurred.
                         `error_message_str_or_none` is None on success, or a string describing the error.
        """
        if not prompts_with_metadata:
            logging.info("No prompts to process.")
            return []

        # Determine actual number of workers based on available keys and max_workers setting
        # We need at least one key for any worker to start.
        actual_workers = min(self.max_workers, len(prompts_with_metadata), self.key_manager.num_keys)
        if actual_workers == 0:
            logging.error("No workers can be started: No prompts, no keys, or max_workers is 0.")
            return []

        logging.info(f"Starting parallel processing with {actual_workers} workers for {len(prompts_with_metadata)} prompts.")
        results = []
        errors = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=actual_workers, thread_name_prefix="GeminiAPIWorker"
        ) as executor:
            # Map each prompt_data to the _worker_task
            futures = {}
            for prompt_data in prompts_with_metadata:
                if isinstance(prompt_data, PromptData):
                    metadata = prompt_data.metadata
                else:
                    metadata = prompt_data['metadata']
                futures[executor.submit(self._worker_task, prompt_data)] = metadata

            processed_count = 0
            last_log_time = time.time()
            for future in concurrent.futures.as_completed(futures):
                original_metadata = futures[future]
                task_id = original_metadata.get('task_id', 'unknown_task')
                try:
                    metadata_res, api_response_text, error_msg = future.result()
                    if error_msg is None:
                        results.append((metadata_res, api_response_text, error_msg))
                    else:
                        errors.append((metadata_res, error_msg))
                except Exception as exc:
                    errors.append((original_metadata, exc))
                    logging.error(
                        f"Task for {task_id} generated an unhandled exception: {exc}",
                        exc_info=True,
                    )

                processed_count += 1
                current_time = time.time()
                # Log progress periodically
                if processed_count % 50 == 0 or current_time - last_log_time > 30:
                    logging.info(
                        f"Progress: {processed_count}/{len(prompts_with_metadata)} tasks completed."
                    )
                    last_log_time = current_time

        # Clean up worker cooldown tracking after all tasks are completed
        with self.worker_lock:
            workers_to_remove = [worker_id for worker_id in self.worker_last_call_time.keys() 
                               if worker_id.startswith("GeminiAPIWorker")]
            for worker_id in workers_to_remove:
                del self.worker_last_call_time[worker_id]
                logging.debug(f"Removed cooldown tracking for completed worker {worker_id}")

        logging.info(f"Parallel processing finished. Processed {processed_count} tasks.")
        logging.info(f"Key status summary: {self.key_manager.get_keys_status_summary()}")
        return results

class GeminiStreamingProcessor:
    """
    Streaming version of GeminiParallelProcessor that maintains persistent workers
    and processes single requests on-demand with dynamic key allocation.
    
    Key differences from batch processor:
    - Persistent workers (no thread creation overhead)
    - Dynamic key allocation (workers grab any available key)
    - Immediate processing (no batching required)
    - Maximum efficiency (no worker waits while other keys are available)
    
    Example efficiency improvement:
    - Batch: Worker with exhausted key waits 2 minutes for recovery
    - Stream: Worker immediately grabs another available key
    
    Usage:
        processor = GeminiStreamingProcessor(key_manager, model_name)
        processor.start()  # Start persistent workers
        
        # Process single requests
        result = processor.process_single(prompt_data)
        
        processor.stop()  # Stop workers when done
    """
    def __init__(self, key_manager: AdvancedApiKeyManager, model_name: str,
                 worker_cooldown_seconds: float = 20,  # 20 seconds worker cooldown
                 api_call_interval: float = 5.0, 
                 max_workers: int = 4,  # 4 workers by default
                 api_call_retries: int = 3,  # 3 retries by default
                 return_response: bool = False):
        """
        Initialize the streaming processor with dual cooldown system.
        
        Args:
            key_manager (AdvancedApiKeyManager): An instance of the API key manager.
            model_name (str): The name of the Gemini model to use.
            worker_cooldown_seconds (float): Time (in seconds) each worker waits between API calls.
            api_call_interval (float): Minimum time between API calls (global IP ban protection).
            max_workers (int): Maximum number of persistent worker threads.
            api_call_retries (int): Maximum number of retries for API call errors (default: 3).
            return_response (bool): Whether to return the full response object instead of just the text.
        """
        self.key_manager = key_manager
        self.model_name = model_name
        self.worker_cooldown_seconds = worker_cooldown_seconds
        self.api_call_interval = api_call_interval
        self.max_workers = max_workers
        self.api_call_retries = api_call_retries
        self.return_response = return_response
        
        # Track worker cooldowns individually
        self.worker_last_call_time = {}  # worker_id -> last_call_timestamp
        self.worker_lock = threading.Lock()
        
        # Global API call timing control (shared with batch processor if needed)
        self._last_api_call_time = 0.0
        self._api_call_lock = threading.Lock()
        
        # Streaming-specific components
        self.request_queue = queue.Queue()  # Queue for incoming requests
        self.result_dict = {}  # Dictionary to store results by request_id
        self.result_events = {}  # Events to signal when results are ready
        
        self.executor = None
        self.workers_running = False
        self.worker_futures = []
        
        logging.info(
            f"GeminiStreamingProcessor initialized for model '{self.model_name}' "
            f"with {self.max_workers} workers, worker cooldown {self.worker_cooldown_seconds}s, "
            f"and global API interval {self.api_call_interval}s."
        )
    
    def get_adjusted_api_interval(self) -> float:
        """Get the adjusted API call interval with adaptive multiplier applied."""
        if self.key_manager.adaptive_settings['enabled']:
            return self.api_call_interval * self.key_manager.current_cooldown_multiplier
        return self.api_call_interval
    
    def get_adjusted_worker_cooldown(self) -> float:
        """Get the adjusted worker cooldown with adaptive multiplier applied."""
        if self.key_manager.adaptive_settings['enabled']:
            return self.worker_cooldown_seconds * self.key_manager.current_cooldown_multiplier
        return self.worker_cooldown_seconds

    def start(self):
        """Start the persistent worker pool."""
        if self.workers_running:
            logging.warning("Workers are already running.")
            return
        
        # Determine actual number of workers
        actual_workers = min(self.max_workers, self.key_manager.num_keys)
        if actual_workers == 0:
            raise ValueError("No workers can be started: no keys available.")
        
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=actual_workers, 
            thread_name_prefix="GeminiStreamWorker"
        )
        
        # Start persistent workers
        self.workers_running = True
        for i in range(actual_workers):
            future = self.executor.submit(self._persistent_worker, i)
            self.worker_futures.append(future)
        
        logging.info(f"Started {actual_workers} persistent workers for streaming processing.")

    def stop(self):
        """Stop the persistent worker pool."""
        if not self.workers_running:
            logging.warning("Workers are not running.")
            return
        
        logging.info("Stopping persistent workers...")
        self.workers_running = False
        
        # Send stop signals to all workers
        for _ in self.worker_futures:
            self.request_queue.put(None)  # None is the stop signal
        
        # Wait for all workers to finish
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        
        self.worker_futures.clear()
        
        # Clean up worker key assignments
        worker_assignments_snapshot = dict(self.key_manager.worker_assignments)
        for worker_id, api_key in worker_assignments_snapshot.items():
            if worker_id.startswith("GeminiStreamWorker"):
                logging.debug(f"Releasing key ...{api_key[-4:]} from stopped worker {worker_id}")
                self.key_manager.release_key_from_worker(worker_id, api_key)
        
        # Clean up worker cooldown tracking
        with self.worker_lock:
            workers_to_remove = [worker_id for worker_id in self.worker_last_call_time.keys() 
                               if worker_id.startswith("GeminiStreamWorker")]
            for worker_id in workers_to_remove:
                del self.worker_last_call_time[worker_id]
                logging.debug(f"Removed cooldown tracking for stopped worker {worker_id}")
        
        logging.info("All persistent workers stopped.")

    def process_single(self, prompt_data: Union[dict, PromptData], timeout: float | None = None) -> tuple:
        """
        Process a single prompt and return the result.
        
        Args:
            prompt_data (Union[dict, PromptData]): Dictionary or PromptData object containing prompt and metadata
            timeout (float): Maximum time to wait for result (default: 5 minutes)
            
        Returns:
            tuple: (metadata_dict, api_response_text_or_none, error_message_str_or_none)
            
        Raises:
            RuntimeError: If workers are not running
            TimeoutError: If processing takes longer than timeout
        """
        if not self.workers_running:
            raise RuntimeError("Workers are not running. Call start() first.")
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Create result event
        result_event = threading.Event()
        self.result_events[request_id] = result_event
        
        # Add task ID if not present
        if isinstance(prompt_data, PromptData):
            if 'task_id' not in prompt_data.metadata:
                prompt_data.metadata['task_id'] = f"stream_{request_id[:8]}"
        else:
            if 'metadata' not in prompt_data:
                prompt_data['metadata'] = {}
            if 'task_id' not in prompt_data['metadata']:
                prompt_data['metadata']['task_id'] = f"stream_{request_id[:8]}"
        
        # Submit request to queue
        request = {
            'request_id': request_id,
            'prompt_data': prompt_data
        }
        self.request_queue.put(request)
        
        # Wait for result
        if result_event.wait(timeout=timeout):
            result = self.result_dict.pop(request_id)
            self.result_events.pop(request_id)
            return result
        else:
            # Timeout occurred
            self.result_events.pop(request_id, None)
            self.result_dict.pop(request_id, None)
            raise TimeoutError(f"Processing timed out after {timeout} seconds")

    def _persistent_worker(self, worker_index: int):
        """
        Persistent worker that continuously processes requests from the queue.
        
        Args:
            worker_index (int): Index of this worker for identification
        """
        worker_id = f"{threading.current_thread().name}_{worker_index}"
        logging.debug(f"Persistent worker {worker_id} started.")
        
        while self.workers_running:
            try:
                # Get request from queue (blocking with timeout)
                request = self.request_queue.get(timeout=1.0)
                
                # Check for stop signal
                if request is None:
                    break
                
                request_id = request['request_id']
                prompt_data = request['prompt_data']
                
                # Process the request using existing worker logic
                result = self._process_single_request(prompt_data, worker_id)
                
                # Store result and signal completion
                self.result_dict[request_id] = result
                if request_id in self.result_events:
                    self.result_events[request_id].set()
                
                # Mark task as done
                self.request_queue.task_done()
                
            except queue.Empty:
                # Timeout on queue.get - continue if still running
                continue
            except Exception as e:
                logging.error(f"Persistent worker {worker_id} error: {e}", exc_info=True)
        
        logging.debug(f"Persistent worker {worker_id} stopped.")

    def _process_single_request(self, prompt_data: Union[dict, PromptData], worker_id: str) -> tuple:
        """
        Process a single request using dynamic key allocation for maximum efficiency.
        
        Unlike batch processing where workers are assigned dedicated keys, streaming workers
        grab any available key for each request. This ensures no worker is idle while 
        other keys are available.
        
        Example: With 4 keys and 4 workers, if one key is exhausted, the affected worker
        immediately tries another available key instead of waiting for recovery.
        
        Args:
            prompt_data (Union[dict, PromptData]): The prompt data to process
            worker_id (str): Worker identifier
            
        Returns:
            tuple: (metadata_dict, api_response_text_or_marker, error_message_str)
        """
        # Handle both dict and PromptData
        if isinstance(prompt_data, PromptData):
            prompt = prompt_data.prompt
            metadata = prompt_data.metadata
        else:
            prompt = prompt_data.get('prompt', '')
            metadata = prompt_data.get('metadata', {})
        task_id = metadata.get('task_id', 'unknown_task')

        if not prompt:
            logging.warning(f"Skipping task {task_id} due to empty prompt.")
            return metadata, None, "Empty prompt provided."

        # Check worker cooldown first
        with self.worker_lock:
            current_time = time.time()
            last_call_time = self.worker_last_call_time.get(worker_id, 0)
            time_since_last_call = current_time - last_call_time
            adjusted_cooldown = self.get_adjusted_worker_cooldown()
            
            if time_since_last_call < adjusted_cooldown:
                wait_time = adjusted_cooldown - time_since_last_call
                logging.debug(f"Worker {worker_id} in cooldown, waiting {wait_time:.1f}s (adjusted: {adjusted_cooldown:.1f}s)")
                time.sleep(wait_time)

        # Dynamic key allocation - grab any available key for each request
        max_wait_time = 300  # Maximum 5 minutes waiting for keys
        start_time = time.time()
        attempt_count = 0
        
        while (time.time() - start_time) < max_wait_time:
            # Get any available key for this request (no permanent assignment)
            current_api_key = self.key_manager.get_any_available_key(worker_id)

            if current_api_key == ALL_KEYS_WAITING_MARKER:
                # All keys are busy, wait and retry
                elapsed = time.time() - start_time
                if elapsed > max_wait_time / 2:  # After half the time, log warning
                    logging.warning(f"Worker {worker_id} has been waiting {elapsed:.0f}s for available keys")
                
                # Progressive backoff: wait longer as time goes on
                wait_time = min(30, 10 + (attempt_count // 10) * 5)  # 10s, 15s, 20s, up to 30s
                logging.debug(f"Worker {worker_id} waiting {wait_time}s - all keys busy (attempt {attempt_count + 1})")
                time.sleep(wait_time)
                attempt_count += 1
                continue
            elif current_api_key is None:
                logging.error(f"Worker {worker_id} for task {task_id} - FATAL: No usable keys")
                return metadata, None, "Fatal: No usable API keys available."

            masked_key = f"...{current_api_key[-4:]}" if len(current_api_key) > 4 else "invalid key"
            
            # Initialize client with the key
            try:
                logging.debug(f"Worker {worker_id} using key {masked_key} for task {task_id}")
                client_instance = genai.Client(api_key=current_api_key)

            except Exception as e:
                logging.error(f"Failed to initialize client for {task_id} with key {masked_key}: {e}")
                self.key_manager.mark_key_failed_init(current_api_key)
                continue

            # Perform API call
            result = self._make_single_api_call(client_instance, prompt_data)
            
            # Update worker's last call time regardless of result (API call was made)
            with self.worker_lock:
                self.worker_last_call_time[worker_id] = time.time()
            
            if result == EXHAUSTED_MARKER:
                # Key is exhausted - mark it and try again with another key
                logging.warning(f"Key {masked_key} exhausted for task {task_id}, trying another key")
                self.key_manager.mark_key_exhausted(current_api_key)
                continue
            elif result == PERSISTENT_ERROR_MARKER:
                # Persistent error - treat this task as failed
                logging.error(f"Persistent error for {task_id} with key {masked_key}")
                return metadata, None, "Persistent API call error."
            else:
                # Success! Update key cooldown
                logging.debug(f"Success for {task_id} with key {masked_key}")
                
                # Mark key as successful and put it in cooldown
                self.key_manager.mark_key_successful(current_api_key)
                self.key_manager.mark_key_returned(current_api_key, worker_id)
                return metadata, result, None

        # Timeout exceeded
        elapsed_time = time.time() - start_time
        logging.error(f"Task {task_id} failed after {elapsed_time:.0f}s of waiting for available keys")
        return metadata, None, f"Failed: All keys exhausted for {elapsed_time:.0f}s. Keys may need quota reset."

    def _make_single_api_call(self, client_instance, prompt_data: Union[dict, PromptData]) -> str:
        """
        Executes a single API call - same logic as GeminiParallelProcessor but optimized.
        """
        # Convert PromptData to dict if needed
        if isinstance(prompt_data, PromptData):
            prompt_dict = prompt_data.to_dict()
        else:
            prompt_dict = prompt_data
        
        # Prepare media contents using external utility
        contents, error_msg = prepare_media_contents(client_instance, prompt_dict)
        if contents is None:
            return PERSISTENT_ERROR_MARKER
        
        generation_config = prompt_dict.get('generation_config', {})
        
        # Perform API call with retries
        retries = 0
        wait_time = 30  # Initial retry delay in seconds
        while retries < self.api_call_retries:  # Maximum retries for API call errors
            response = None
            try:
                # Global API call interval control - prevents IP ban from simultaneous requests
                with self._api_call_lock:
                    current_time = time.time()
                    time_since_last_call = current_time - self._last_api_call_time
                    adjusted_interval = self.get_adjusted_api_interval()
                    
                    if time_since_last_call < adjusted_interval:
                        sleep_time = adjusted_interval - time_since_last_call
                        worker_id = threading.current_thread().name
                        logging.debug(f"Worker {worker_id} waiting {sleep_time:.2f}s for global API interval (adjusted: {adjusted_interval:.1f}s)")
                        time.sleep(sleep_time)
                    
                    # Update last API call time before making the call
                    self._last_api_call_time = time.time()
                
                # Handle generation_config - support dict or types objects
                if isinstance(generation_config, types.GenerateContentConfig):
                    config = generation_config
                elif isinstance(generation_config, dict) and generation_config:
                    # Convert nested configs if they're dicts
                    config_kwargs = generation_config.copy()
                    
                    # Convert thinkingConfig if it's a dict
                    if 'thinkingConfig' in config_kwargs and isinstance(config_kwargs['thinkingConfig'], dict):
                        config_kwargs['thinkingConfig'] = types.ThinkingConfig(**config_kwargs['thinkingConfig'])
                    elif 'thinking_config' in config_kwargs and isinstance(config_kwargs['thinking_config'], dict):
                        config_kwargs['thinkingConfig'] = types.ThinkingConfig(**config_kwargs.pop('thinking_config'))
                    
                    # Convert speechConfig if it's a dict
                    if 'speechConfig' in config_kwargs and isinstance(config_kwargs['speechConfig'], dict):
                        config_kwargs['speechConfig'] = types.SpeechConfig(**config_kwargs['speechConfig'])
                    elif 'speech_config' in config_kwargs and isinstance(config_kwargs['speech_config'], dict):
                        config_kwargs['speechConfig'] = types.SpeechConfig(**config_kwargs.pop('speech_config'))
                    
                    # Convert snake_case to camelCase for other fields
                    if 'max_output_tokens' in config_kwargs:
                        config_kwargs['maxOutputTokens'] = config_kwargs.pop('max_output_tokens')
                    if 'stop_sequences' in config_kwargs:
                        config_kwargs['stopSequences'] = config_kwargs.pop('stop_sequences')
                    if 'response_mime_type' in config_kwargs:
                        config_kwargs['responseMimeType'] = config_kwargs.pop('response_mime_type')
                    if 'response_logprobs' in config_kwargs:
                        config_kwargs['responseLogprobs'] = config_kwargs.pop('response_logprobs')
                    if 'top_p' in config_kwargs:
                        config_kwargs['topP'] = config_kwargs.pop('top_p')
                    if 'top_k' in config_kwargs:
                        config_kwargs['topK'] = config_kwargs.pop('top_k')
                    if 'presence_penalty' in config_kwargs:
                        config_kwargs['presencePenalty'] = config_kwargs.pop('presence_penalty')
                    if 'frequency_penalty' in config_kwargs:
                        config_kwargs['frequencyPenalty'] = config_kwargs.pop('frequency_penalty')
                    if 'candidate_count' in config_kwargs:
                        config_kwargs['candidateCount'] = config_kwargs.pop('candidate_count')
                    if 'response_modalities' in config_kwargs:
                        config_kwargs['responseModalities'] = config_kwargs.pop('response_modalities')
                    if 'media_resolution' in config_kwargs:
                        config_kwargs['mediaResolution'] = config_kwargs.pop('media_resolution')
                    if 'response_schema' in config_kwargs:
                        config_kwargs['responseSchema'] = config_kwargs.pop('response_schema')
                    if 'response_json_schema' in config_kwargs:
                        config_kwargs['responseJsonSchema'] = config_kwargs.pop('response_json_schema')
                    
                    config = types.GenerateContentConfig(**config_kwargs)
                else:
                    config = types.GenerateContentConfig()
                
                response = client_instance.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
                response_text = response.text
                
                # Log content types for debugging
                media_count = sum(1 for content in contents if hasattr(content, 'file_data') or hasattr(content, 'inline_data'))
                content_type = f"text+{media_count}media" if media_count > 0 else "text-only"
                logging.debug(f"API call successful ({content_type})")
                if self.return_response:
                    return response
                else:
                    return response_text

            except genai_errors.APIError as e:
                # Handle different error codes based on official Gemini API documentation
                error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
                
                if error_code == 429:  # RESOURCE_EXHAUSTED
                    logging.warning(f"RESOURCE_EXHAUSTED (429): {e}. Signaling exhaustion.")
                    return EXHAUSTED_MARKER
                    
                elif error_code in [400, 403, 404]:  # Non-retryable errors
                    # 400: INVALID_ARGUMENT, FAILED_PRECONDITION
                    # 403: PERMISSION_DENIED  
                    # 404: NOT_FOUND
                    logging.error(f"Non-retryable error ({error_code}): {e}. Signaling persistent error.")
                    return PERSISTENT_ERROR_MARKER
                    
                elif error_code in [500, 503, 504]:  # Retryable server errors
                    # 500: INTERNAL - Google internal error
                    # 503: UNAVAILABLE - Service temporarily overloaded/down
                    # 504: DEADLINE_EXCEEDED - Service couldn't complete in time
                    logging.warning(
                        f"Retryable server error ({error_code}): {e}. "
                        f"Retry {retries + 1}/{self.api_call_retries}..."
                    )
                else:
                    # Unknown error code - treat as retryable
                    logging.warning(
                        f"Unknown APIError ({error_code}): {e}. "
                        f"Retry {retries + 1}/{self.api_call_retries}..."
                    )
            except Exception as e:
                logging.error(
                    f"Unexpected error during API call: {type(e).__name__} - {e}. "
                    f"Traceback: {traceback.format_exc()}. "
                    f"Retry {retries + 1}/{self.api_call_retries}..."
                )

            retries += 1
            if retries < self.api_call_retries:
                logging.info(f"Waiting {wait_time}s before retrying API call...")
                time.sleep(wait_time)
                wait_time = wait_time * 2**retries # Exponential backoff
            else:
                logging.error(
                    f"Failed API call after {self.api_call_retries} retries."
                )
                return PERSISTENT_ERROR_MARKER

        return PERSISTENT_ERROR_MARKER

    def get_queue_size(self) -> int:
        """Get the current size of the request queue."""
        return self.request_queue.qsize()

    def is_running(self) -> bool:
        """Check if the workers are currently running."""
        return self.workers_running

    def get_worker_status(self) -> dict:
        """Get status information about the workers and keys."""
        return {
            'workers_running': self.workers_running,
            'queue_size': self.get_queue_size(),
            'max_workers': self.max_workers,
            'active_workers': len(self.worker_futures),
            'key_status': self.key_manager.get_keys_status_summary()
        }
