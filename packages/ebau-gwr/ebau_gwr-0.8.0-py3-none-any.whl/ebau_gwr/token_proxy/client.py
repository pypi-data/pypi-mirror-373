import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class HousingStatClient:
    def _request(self, method_name, *args, **kwargs):
        return getattr(requests, method_name)(*args, **kwargs)

    def _handle_response(self, response):
        if 400 <= response.status_code < 600:
            return {
                "success": False,
                "status_code": response.status_code,
                "reason": response.content.decode(),
            }

        return response.json()

    def get_token(self, username, password):
        headers = {"content-type": "application/json"}
        data = {
            "username": username,
            "password": password,
            "wsk_id": settings.GWR_HOUSING_STAT_WSK_ID,
        }
        resp = self._request(
            "post",
            f"{settings.GWR_HOUSING_STAT_BASE_URI}/tokenWS/",
            headers=headers,
            json=data,
        )
        return self._handle_response(resp)
