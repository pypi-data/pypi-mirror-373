import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.simplefilter("ignore", NotOpenSSLWarning)

import platform
import requests

class cmdmateClient:
    def __init__(self, server_url="https://cmdmate-online.onrender.com/"):
        self.server_url = server_url.rstrip("/")

    @staticmethod
    def detect_os() -> str:
        system = platform.system().lower()
        if system == "darwin":
            return "mac"
        elif system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    def get_command(self, query: str, os_name: str = None) -> str:
        if not os_name:
            os_name = self.detect_os()

        payload = {"text": query, "os": os_name}
        
        try:
            response = requests.post(f"{self.server_url}/getCmd", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("command", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}") from e
        
    def get_explanation(self, query: str) -> str:
        payload = {"text": query}

        try:
            response = requests.post(f"{self.server_url}/getExplaination", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("explanation", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}") from e
        

    def get_commitMsg(self, diff_input: str) -> str:
        payload = {"text": diff_input}

        try:
            response = requests.post(f"{self.server_url}/getCommitMsg", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("commit_message", "")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}") from e