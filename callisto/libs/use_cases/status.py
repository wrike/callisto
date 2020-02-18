from __future__ import annotations

import typing as t


if t.TYPE_CHECKING:
    from ..domains.state import SessionState
    from ..services.state import StateService


class StatusUseCase:
    """`/status` handler for Selenoid-UI
    """

    def __init__(self, state_service: StateService) -> None:
        self.state_service = state_service

    @staticmethod
    def _get_session_dict(session_state: SessionState) -> t.Dict[str, t.Any]:
        return {
            'id': f'{session_state.patched_session_id}',
            'vnc': session_state.vnc_enabled,
            'screen': session_state.screen_resolution,
            'caps': {
                'browserName': session_state.browser_name,
                'version': session_state.browser_version,
                'screenResolution': session_state.screen_resolution,
                'enableVNC': session_state.vnc_enabled,
                'name': session_state.test_name,
                'timeZone': session_state.timezone
            }
        }

    def get_status(self) -> t.Dict[str, t.Any]:
        return {
            'total': int(self.state_service.get_active_sessions_number()),
            'used': int(self.state_service.get_active_sessions_number()),
            'queued': 0,  # we don't limit maximum active sessions, so, queued is always 0
            'pending': int(self.state_service.get_sessions_creating()),
            'browsers': {
                '': {
                    '': {
                        'browsers': {
                            'count': self.state_service.get_active_sessions_number(),
                            'sessions': [self._get_session_dict(session)
                                         for session in self.state_service.get_active_sessions().values()],
                        }
                    }
                }
            }
        }
