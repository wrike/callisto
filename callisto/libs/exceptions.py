from __future__ import annotations


class BaseError(Exception):
    ...


class K8sClientTimeout(BaseError):
    pass


class K8sPodNotFound(BaseError):
    pass


class K8SForbidden(BaseError):
    pass


class K8SEmptyPodIp(BaseError):
    pass


class WebDriverException(BaseError):
    pass


class ValidationError(BaseError):
    pass


class SessionNotFound(BaseError):
    pass
