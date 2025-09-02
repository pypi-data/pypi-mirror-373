"""
core.py - All-in-one Utility Functions for Safe Data Handling, Validation & Helpers
Author: Shaikh Asad & Team
"""

import json
import re
import os
import time
import requests
from typing import Any, Callable, Optional, Type, List


# 🔹 1. Safe Casting & Parsing
def safe_cast(value: Any, cast_type: Type = int, fallback: Optional[Any] = None,
              on_error: Optional[Callable[[Exception, Any], None]] = None) -> Any:
    try:
        return cast_type(value)
    except Exception as e:
        if on_error:
            on_error(e, value)
        return fallback


def is_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "y", "1", "true", "t")
    return bool(value)


def parse_json(string: str, fallback: Any = None) -> Any:
    try:
        return json.loads(string)
    except Exception:
        return fallback


# 🔹 2. Safe Input Handling
def safe_input(prompt: str, cast_type: Type = str, fallback: Any = None) -> Any:
    try:
        return cast_type(input(prompt))
    except Exception:
        return fallback


def ask_yes_no(prompt: str) -> bool:
    return to_bool(input(f"{prompt} (y/n): "))


def choose_from_list(prompt: str, options: List[Any]) -> Any:
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    try:
        choice = int(input("Choose number: "))
        if 1 <= choice <= len(options):
            return options[choice - 1]
    except Exception:
        pass
    return None


# 🔹 3. Validation Utilities
def validate_number_range(value: Any, min_val: float, max_val: float) -> bool:
    try:
        num = float(value)
        return min_val <= num <= max_val
    except Exception:
        return False


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def validate_phone(number: str, country_code: str = "+91") -> bool:
    return number.startswith(country_code) and number[len(country_code):].isdigit()


def validate_password(password: str, min_length: int = 8, require_special: bool = True) -> bool:
    if len(password) < min_length:
        return False
    if require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


# 🔹 4. Error Handling & Logging
def safe_exec(func: Callable, fallback: Any = None, on_error: Optional[Callable] = None) -> Any:
    try:
        return func()
    except Exception as e:
        if on_error:
            on_error(e)
        return fallback


def log_error(error: Exception, message: str = "", file: str = "errors.log"):
    with open(file, "a") as f:
        f.write(f"{time.ctime()} - {message} - {str(error)}\n")


def retry(func: Callable, attempts: int = 3, delay: int = 1) -> Any:
    for i in range(attempts):
        try:
            return func()
        except Exception as e:
            if i < attempts - 1:
                time.sleep(delay)
            else:
                raise e


# 🔹 5. Data Helpers
def flatten_list(nested_list: List[Any]) -> List[Any]:
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def unique_list(lst: List[Any]) -> List[Any]:
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def safe_dict_get(d: dict, key: Any, fallback: Any = None) -> Any:
    return d.get(key, fallback)


# 🔹 6. String Helpers
def safe_strip(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def slugify(string: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", string.lower()).strip("-")


def truncate(string: str, length: int, suffix: str = "...") -> str:
    return string if len(string) <= length else string[:length] + suffix


def normalize_whitespace(string: str) -> str:
    return " ".join(string.split())


# 🔹 7. File & OS Utilities
def safe_read(file: str, fallback: str = "") -> str:
    try:
        with open(file, "r") as f:
            return f.read()
    except Exception:
        return fallback


def safe_write(file: str, data: str, append: bool = False) -> bool:
    try:
        mode = "a" if append else "w"
        with open(file, mode) as f:
            f.write(data)
        return True
    except Exception:
        return False


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def safe_delete(path: str) -> bool:
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        pass
    return False


# 🔹 8. Network Utilities
def is_internet_available(url: str = "http://www.google.com", timeout: int = 3) -> bool:
    try:
        requests.get(url, timeout=timeout)
        return True
    except Exception:
        return False


def safe_get(url: str, fallback: Any = None, timeout: int = 5) -> Any:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return fallback
