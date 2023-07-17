from __future__ import annotations

import typing as t

import pytest


@pytest.fixture
def session_created_response() -> dict[str, t.Any]:
    return {
        "sessionId": "6cf5098bc390d2add8868e6ff1abad68",
        "status": 0,
        "value": {
            "acceptInsecureCerts": False,
            "acceptSslCerts": False,
            "applicationCacheEnabled": False,
            "browserConnectionEnabled": False,
            "browserName": "chrome",
            "chrome": {
                "chromedriverVersion": "79.0.3945.36",
                "userDataDir": "/var/folders/q3/8_wx2_5n5158xk1sq1szlbw0wd1blm/T/.com.google.Chrome.JsN6lz",
            },
            "cssSelectorsEnabled": True,
            "databaseEnabled": False,
            "goog:chromeOptions": {"debuggerAddress": "localhost:51781"},
            "handlesAlerts": True,
            "hasTouchScreen": False,
            "javascriptEnabled": True,
            "locationContextEnabled": True,
            "mobileEmulationEnabled": False,
            "nativeEvents": True,
            "networkConnectionEnabled": False,
            "pageLoadStrategy": "normal",
            "platform": "Mac OS X",
            "proxy": {},
            "rotatable": False,
            "setWindowRect": True,
            "strictFileInteractability": False,
            "takesHeapSnapshot": True,
            "takesScreenshot": True,
            "timeouts": {"implicit": 0, "pageLoad": 300000, "script": 30000},
            "unexpectedAlertBehaviour": "ignore",
            "version": "79.0.3945.88",
            "webStorageEnabled": True,
        },
    }
