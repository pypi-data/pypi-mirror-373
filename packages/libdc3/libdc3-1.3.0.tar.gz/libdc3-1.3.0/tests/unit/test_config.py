import pytest

from libdc3.config import Config


def test_config_setters_and_getters():
    c = Config()
    c.set_keytab_usr("dummy")
    c.set_keytab_pwd("dummy")
    c.set_auth_cert_path("dummy")
    c.set_auth_key_path("dummy")
    assert c.KEYTAB_USR == "dummy"
    assert c.KEYTAB_PWD == "dummy"
    assert c.AUTH_CERT == "dummy"
    assert c.AUTH_CERT_KEY == "dummy"


def test_validate_x509cert_raises():
    c = Config()
    with pytest.raises(ValueError):
        c.validate_x509cert()
