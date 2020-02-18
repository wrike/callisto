from __future__ import annotations

import typing as t


class WebDriverProtocol:
    """WebDriver protocol conventions
    https://w3c.github.io/webdriver/
    P.S: Unfortunately, the chromedriver < 75 doesn't use w3c standard protocol by default
    """

    @staticmethod
    def get_session_deleted_response() -> t.Dict[str, t.Any]:
        """https://w3c.github.io/webdriver/#delete-session"""

        return {'value': None}

    @staticmethod
    def get_session_id(session_response: t.Dict[str, t.Any]) -> str:
        """value/sessionId for w3c
           sessionId for old chrome
        """

        if 'sessionId' in session_response:
            return session_response['sessionId']
        else:
            return session_response['value']['sessionId']

    @staticmethod
    def get_browser_name(session_response: t.Dict[str, t.Any]) -> str:
        """value/capabilities/browserName for w3c
           value/browserName for old chrome
        """

        if 'browserName' in session_response['value']:
            return session_response['value']['browserName']
        else:
            return session_response['value']['capabilities']['browserName']

    @staticmethod
    def get_test_name(session_request: t.Dict[str, t.Any]) -> str:
        """Selenoid feature
           https://aerokube.com/selenoid/latest/#_custom_test_name_name
        """
        return session_request.get('desiredCapabilities', {}).get('name', '')

    @staticmethod
    def get_browser_version(session_response: t.Dict[str, t.Any]) -> str:
        """value/capabilities/browserVersion for w3c
           value/version for old chrome
        """

        if 'version' in session_response['value']:
            return session_response['value']['version']
        else:
            return session_response['value']['capabilities']['browserVersion']

    @staticmethod
    def is_session_created(session_response: t.Dict[str, t.Any]) -> bool:
        """w3c return http-code, don't need this check and hasn't 'status' in body
           old chrome has http-code 200 for all responses and has 'status' in body
        """

        return session_response.get('status', 0) == 0

    @staticmethod
    def patch_session_response(session_response: t.Dict[str, t.Any], pod_name: str, pod_ip: str) -> t.Dict[str, t.Any]:
        """We add pod_name and pod_ip to sessionId for routing traffic on nginx.
           In nginx we use regex for extracting pod_name and pod_ip.
           value/sessionId for w3c
           sessionId for old chrome
        """
        if 'sessionId' in session_response:
            session_response['sessionId'] = f"{pod_name}-{pod_ip}-{session_response['sessionId']}"
        else:
            session_response['value']['sessionId'] = f"{pod_name}-{pod_ip}-{session_response['value']['sessionId']}"

        return session_response
