"""
PyCoke - Swiss Army Knife utility package for Python developers
Author: Shaikh Asad & Team
"""

from .core import (
    safe_cast, is_numeric, to_bool, parse_json,
    safe_input, ask_yes_no, choose_from_list,
    validate_number_range, validate_email, validate_phone, validate_password,
    safe_exec, log_error, retry,
    flatten_list, chunk_list, unique_list, safe_dict_get,
    safe_strip, slugify, truncate, normalize_whitespace,
    safe_read, safe_write, file_exists, safe_delete,
    is_internet_available, safe_get
)

__all__ = [
    "safe_cast", "is_numeric", "to_bool", "parse_json",
    "safe_input", "ask_yes_no", "choose_from_list",
    "validate_number_range", "validate_email", "validate_phone", "validate_password",
    "safe_exec", "log_error", "retry",
    "flatten_list", "chunk_list", "unique_list", "safe_dict_get",
    "safe_strip", "slugify", "truncate", "normalize_whitespace",
    "safe_read", "safe_write", "file_exists", "safe_delete",
    "is_internet_available", "safe_get"
]
