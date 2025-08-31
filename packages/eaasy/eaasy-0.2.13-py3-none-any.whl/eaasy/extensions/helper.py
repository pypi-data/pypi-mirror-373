from re import match
from flask_oidc import OpenIDConnect
import functools
from typing import Callable

def validate_email_address(email: str | None):
    if email is not None and not match(r"[^@]+@[^@]+\.[^@]+", email):
        raise Exception({
            'status_code': 400,
            'message': f"'{email}' is not a valid email address",
            'data': {'email': email}
        })


def validate_phone_number(phone: str | None):
    if phone is not None and not match(r"\d{10,11}", phone):
        raise Exception({
            'status_code': 400,
            'message': f"'{phone}' is not a valid phone number",
            'data': {'phone': phone}
        })
    

def verify_oidc(oidc: OpenIDConnect | None) -> Callable:
    if oidc is None:
        return lambda f: f
    
    assert_is_instance(oidc, OpenIDConnect)

    def decorator(f):
        @oidc.accept_token()
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated
    return decorator

def assert_is_instance(obj, cls): # pragma: no cover
    assert isinstance(obj, cls)
