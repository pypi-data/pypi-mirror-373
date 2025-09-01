# Copyright: (c) 2023 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

from ._win32_types cimport *


cdef class CredHandle:
    cdef _CredHandle raw
    cdef int needs_free
