# Copyright: (c) 2023 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

from ._win32_types cimport *


cdef class WideCharString:
    cdef LPWSTR raw
    cdef Py_ssize_t length


cdef str wide_char_to_str(
    const LPWSTR value,
    int size = *,
    int none_is_empty = *,
)
