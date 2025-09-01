class RegisterUserAlreadyExistsException(Exception):
    pass


class RegisterUserPasswordToShortException(Exception):
    pass


class LoginUserNotFoundException(Exception):
    pass


class LoginWrongPasswordException(Exception):
    pass


class ActivateUserNotFoundException(Exception):
    pass


class ActivateUserWrongCodeException(Exception):
    pass


class ResetPasswordNotFoundException(Exception):
    pass


class ResetPasswordWrongCodeException(Exception):
    pass


class SetUserPasswordNotFoundException(Exception):
    pass


__all__ = (
    "RegisterUserPasswordToShortException",
    "ActivateUserNotFoundException",
    "ActivateUserWrongCodeException",
    "LoginUserNotFoundException",
    "LoginWrongPasswordException",
    "RegisterUserAlreadyExistsException",
    "ResetPasswordNotFoundException",
    "ResetPasswordWrongCodeException",
    "SetUserPasswordNotFoundException",
)
