from typing import Optional

import requests

from .exceptions import TaskReporterException


class TaskReporter:
    """A class to manage task reporting to Core API.
    Requires:
    * running instance of Core API,
    * Core API access token with sufficient privileges.
    """

    def __init__(
            self,
            api_url: str,
            api_token: str,
            api_timeout: Optional[int] = 10,
    ):
        # Remove possible trailing / from API url.
        self.api_url = api_url.rstrip("/")
        self.api_headers = {
            "ContentType": "application/json",
            "Authorization": f"Token {api_token}"
        }
        self.api_timeout = api_timeout

    def check(self):
        """Checks the connection to Core API.
        This includes both connection & auth errors.
        :return: Boolean - true for alive, false for dead.
        """
        health_url = f"{self.api_url}/health"
        response = requests.get(health_url, headers=self.api_headers, timeout=self.api_timeout)
        if response.status_code == 200:
            return True
        return False

    def _perform_patch(self, content: dict, task_id: int, tasks_endpoint: str = "tasks"):
        url = f"{self.api_url}/{tasks_endpoint}/{task_id}/"
        try:
            return requests.patch(
                url,
                headers=self.api_headers,
                json=content,
                timeout=self.api_timeout
            )
        except Exception as e:
            raise TaskReporterException(f"Error patching document: {e}")

    def _perform_status_update(self, content: dict, task_id: int, tasks_endpoint: str = "tasks", action_endpoint: str = "update_status"):
        url = f"{self.api_url}/{tasks_endpoint}/{task_id}/{action_endpoint}/"
        try:
            return requests.post(
                url,
                headers=self.api_headers,
                json=content,
                timeout=self.api_timeout
            )
        except Exception as e:
            raise TaskReporterException(f"Error patching document: {e}")

    def report_results(self, content: dict, task_id: int):
        """Reports task results to Core API.
        :param: content dict: Keys & values to update in Task model.
        :param: task_id int: Task ID of the object to update.
        :return: Response object.
        """
        response = self._perform_patch(content, task_id)
        if response.status_code not in (200, 204):
            raise TaskReporterException(f"Error code from Core API: {response.status_code}")
        return response

    def update_status(self, key: str, task_id: int, **status_options):
        """Updates the status of sub-tasks to Core API.
        :param: key: Since task statuses are Many-to-Many a normal patch won't work, hence we filter the status we want through the key.
        :param: status_options: Keys & values to update in the status model.
        :return: Response object.
        """
        content = {"key": key, **status_options}
        response = self._perform_status_update(content, task_id)
        if response.status_code not in (200, 204):
            raise TaskReporterException(f"Error code from Core API: {response.status_code}")
        return response
