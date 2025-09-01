# Copyright: (c) 2023 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import sspilib.raw as sr


def test_enumerate_security_packages() -> None:
    actual = sr.enumerate_security_packages()
    assert isinstance(actual, list)
    for sec_pkg in actual:
        assert isinstance(sec_pkg, sr.SecPkgInfo)
        assert isinstance(sec_pkg.capabilities, sr.SecurityPackageCapability)
        assert isinstance(sec_pkg.name, str)
        assert sec_pkg.name
        assert isinstance(sec_pkg.comment, str)
