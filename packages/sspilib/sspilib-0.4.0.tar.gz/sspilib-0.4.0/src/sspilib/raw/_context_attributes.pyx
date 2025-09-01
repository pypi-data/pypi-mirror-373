# Copyright: (c) 2023 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

from __future__ import annotations

import collections
import enum

from ._security_buffer cimport FreeContextBuffer
from ._security_context cimport CtxtHandle
from ._security_package cimport PSecPkgInfoW
from ._text cimport wide_char_to_str
from ._win32_types cimport *

from ._ntstatus import NtStatus
from ._security_package import SecurityPackageCapability


cdef extern from "python_sspi.h":
    unsigned int SECPKG_ATTR_SIZES
    unsigned int SECPKG_ATTR_NAMES
    unsigned int SECPKG_ATTR_LIFESPAN
    unsigned int SECPKG_ATTR_DCE_INFO
    unsigned int SECPKG_ATTR_STREAM_SIZES
    unsigned int SECPKG_ATTR_KEY_INFO
    unsigned int SECPKG_ATTR_AUTHORITY
    unsigned int SECPKG_ATTR_PROTO_INFO
    unsigned int SECPKG_ATTR_PASSWORD_EXPIRY
    unsigned int SECPKG_ATTR_SESSION_KEY
    unsigned int SECPKG_ATTR_PACKAGE_INFO
    unsigned int SECPKG_ATTR_USER_FLAGS
    unsigned int SECPKG_ATTR_NEGOTIATION_INFO
    unsigned int SECPKG_ATTR_NATIVE_NAMES
    unsigned int SECPKG_ATTR_FLAGS
    unsigned int SECPKG_ATTR_USE_VALIDATED
    unsigned int SECPKG_ATTR_CREDENTIAL_NAME
    unsigned int SECPKG_ATTR_TARGET_INFORMATION
    unsigned int SECPKG_ATTR_ACCESS_TOKEN
    unsigned int SECPKG_ATTR_TARGET
    unsigned int SECPKG_ATTR_AUTHENTICATION_ID
    unsigned int SECPKG_ATTR_LOGOFF_TIME
    unsigned int SECPKG_ATTR_NEGO_KEYS
    unsigned int SECPKG_ATTR_PROMPTING_NEEDED
    unsigned int SECPKG_ATTR_UNIQUE_BINDINGS
    unsigned int SECPKG_ATTR_ENDPOINT_BINDINGS
    unsigned int SECPKG_ATTR_CLIENT_SPECIFIED_TARGET
    unsigned int SECPKG_ATTR_LAST_CLIENT_TOKEN_STATUS
    unsigned int SECPKG_ATTR_NEGO_PKG_INFO
    unsigned int SECPKG_ATTR_NEGO_STATUS
    unsigned int SECPKG_ATTR_CONTEXT_DELETED
    unsigned int SECPKG_ATTR_DTLS_MTU
    unsigned int SECPKG_ATTR_DATAGRAM_SIZES
    unsigned int SECPKG_ATTR_SUBJECT_SECURITY_ATTRIBUTES
    unsigned int SECPKG_ATTR_APPLICATION_PROTOCOL
    unsigned int SECPKG_ATTR_NEGOTIATED_TLS_EXTENSIONS
    unsigned int SECPKG_ATTR_IS_LOOPBACK

    cdef struct _SecPkgContext_NamesW:
        LPWSTR sUserName
    ctypedef _SecPkgContext_NamesW SecPkgContext_NamesW
    ctypedef SecPkgContext_NamesW *PSecPkgContext_NamesW

    cdef struct _SecPkgContext_PackageInfoW:
        PSecPkgInfoW PackageInfo
    ctypedef _SecPkgContext_PackageInfoW SecPkgContext_PackageInfoW
    ctypedef SecPkgContext_PackageInfoW *PSecPkgContext_PackageInfoW

    cdef struct _SecPkgContext_Sizes:
        unsigned int cbMaxToken
        unsigned int cbMaxSignature
        unsigned int cbBlockSize
        unsigned int cbSecurityTrailer
    ctypedef _SecPkgContext_Sizes SecPkgContext_Sizes
    ctypedef SecPkgContext_Sizes *PSecPkgContext_Sizes

    cdef struct _SecPkgContext_SessionKey:
        unsigned int SessionKeyLength
        unsigned char *SessionKey
    ctypedef _SecPkgContext_SessionKey SecPkgContext_SessionKey
    ctypedef SecPkgContext_SessionKey *PSecPkgContext_SessionKey

    # https://learn.microsoft.com/en-us/windows/win32/api/sspi/nf-sspi-querycontextattributesw
    SECURITY_STATUS QueryContextAttributesW(
        PCtxtHandle   phContext,
        unsigned int ulAttribute,
        void          *pBuffer
    ) nogil

cdef class SecPkgContext:

    cdef (unsigned int, void *) __c_value__(SecPkgContext self):
        return (0, NULL)

cdef class SecPkgContextNames(SecPkgContext):
    cdef SecPkgContext_NamesW raw

    def __dealloc__(SecPkgContextNames self):
        if self.raw.sUserName:
            FreeContextBuffer(self.raw.sUserName)
            self.raw.sUserName = NULL

    cdef (unsigned int, void *) __c_value__(SecPkgContextNames self):
        return (SECPKG_ATTR_NAMES, &self.raw)

    def __repr__(SecPkgContextNames self):
        return f"SecPkgContextNames(username={self.username!r})"

    @property
    def username(SecPkgContextNames self) -> str:
        if self.raw.sUserName == NULL:
            return ""
        else:
            return wide_char_to_str(self.raw.sUserName)

cdef class SecPkgContextPackageInfo(SecPkgContext):
    cdef SecPkgContext_PackageInfoW raw

    def __dealloc__(SecPkgContextPackageInfo self):
        if self.raw.PackageInfo:
            FreeContextBuffer(self.raw.PackageInfo)
            self.raw.PackageInfo = NULL

    cdef (unsigned int, void *) __c_value__(SecPkgContextPackageInfo self):
        return (SECPKG_ATTR_PACKAGE_INFO, &self.raw)

    def __repr__(SecPkgContextPackageInfo self):
        kwargs = [f"{k}={v}" for k, v in {
            'capabilities': self.capabilities.value,
            'version': self.version,
            'rpcid': self.rpcid,
            'max_token': self.max_token,
            'name': repr(self.name),
            'comment': repr(self.comment),
        }.items()]

        return f"SecPkgContextPackageInfo({', '.join(kwargs)})"

    @property
    def capabilities(SecPkgContextPackageInfo self) -> SecurityPackageCapability:
        return SecurityPackageCapability(self.raw.PackageInfo.fCapabilities)

    @property
    def version(SecPkgContextPackageInfo self) -> int:
        return self.raw.PackageInfo.wVersion

    @property
    def rpcid(SecPkgContextPackageInfo self) -> int:
        return self.raw.PackageInfo.wRPCID

    @property
    def max_token(SecPkgContextPackageInfo self) -> int:
        return self.raw.PackageInfo.cbMaxToken

    @property
    def name(SecPkgContextPackageInfo self) -> str:
        return wide_char_to_str(self.raw.PackageInfo.Name, size=-1, none_is_empty=1)

    @property
    def comment(SecPkgContextPackageInfo self) -> str:
        return wide_char_to_str(self.raw.PackageInfo.Comment, size=-1, none_is_empty=1)

cdef class SecPkgContextSessionKey(SecPkgContext):
    cdef SecPkgContext_SessionKey raw

    def __dealloc__(SecPkgContextSessionKey self):
        if self.raw.SessionKey:
            FreeContextBuffer(self.raw.SessionKey)
            self.raw.SessionKeyLength = 0
            self.raw.SessionKey = NULL

    cdef (unsigned int, void *) __c_value__(SecPkgContextSessionKey self):
        return (SECPKG_ATTR_SESSION_KEY, &self.raw)

    def __repr__(SecPkgContextSessionKey self):
        return f"SecPkgContextSessionKey(session_key={self.session_key!r})"

    @property
    def session_key(SecPkgContextSessionKey self) -> bytes:
        if self.raw.SessionKeyLength and self.raw.SessionKey != NULL:
            return (<char *>self.raw.SessionKey)[:self.raw.SessionKeyLength]
        else:
            return b""

cdef class SecPkgContextSizes(SecPkgContext):
    cdef SecPkgContext_Sizes raw

    cdef (unsigned int, void *) __c_value__(SecPkgContextSizes self):
        return (SECPKG_ATTR_SIZES, &self.raw)

    def __repr__(SecPkgContextSizes self) -> str:
        kwargs = [f"{k}={v}" for k, v in {
            'max_token': self.max_token,
            'max_signature': self.max_signature,
            'block_size': self.block_size,
            'security_trailer': self.security_trailer,
        }.items()]

        return f"SecPkgContextSizes({', '.join(kwargs)})"

    @property
    def max_token(SecPkgContextSizes self) -> int:
        return self.raw.cbMaxToken

    @property
    def max_signature(SecPkgContextSizes self) -> int:
        return self.raw.cbMaxSignature

    @property
    def block_size(SecPkgContextSizes self) -> int:
        return self.raw.cbBlockSize

    @property
    def security_trailer(SecPkgContextSizes self) -> int:
        return self.raw.cbSecurityTrailer

def query_context_attributes(
    CtxtHandle context not None,
    type attribute not None,
) -> SecPkgContext:
    if not issubclass(attribute, SecPkgContext):
        raise TypeError("attribute must be a type of SecPkgContext")

    cdef SecPkgContext value = attribute()
    cdef (unsigned int, void*) raw = value.__c_value__()

    with nogil:
        res = QueryContextAttributesW(
            &context.raw,
            raw[0],
            raw[1],
        )

    if res:
        PyErr_SetFromWindowsErr(res)

    return value
