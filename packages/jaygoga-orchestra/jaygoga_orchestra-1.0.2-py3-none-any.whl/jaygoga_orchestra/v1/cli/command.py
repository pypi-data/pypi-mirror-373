from rich.console import Console
console = Console()
import requests
from requests.exceptions import JSONDecodeError
from rich.console import Console

from jaygoga_orchestra.v1.cli.authentication.token import get_auth_token
from jaygoga_orchestra.v1.cli.plus_api import PlusAPI

console = Console()

class BaseCommand:
    def __init__(self):
        
        set_tracer()

class PlusAPIMixin:
    def __init__(self, telemetry):
        try:
            telemetry.set_tracer()
            self.plus_api_client = PlusAPI(api_key=get_auth_token())
        except Exception:
            self._deploy_signup_error_span = telemetry.deploy_signup_error_span()
            print(
                "Please sign up/login to Govinda+ before using the CLI.",
                style="bold red",
            )
            print("Run 'jaygoga_orchestra.v1 login' to sign up/login.", style="bold green")
            raise SystemExit

    def _validate_response(self, response: requests.Response) -> None:
        """
        Handle and display error messages from API responses.

        Args:
            response (requests.Response): The response from the Plus API
        """
        try:
            json_response = response.json()
        except (JSONDecodeError, ValueError):
            print(
                "Failed to parse response from Enterprise API failed. Details:",
                style="bold red",
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response:\n{response.content}")
            raise SystemExit

        if response.status_code == 422:
            print(
                "Failed to complete operation. Please fix the following errors:",
                style="bold red",
            )
            for field, messages in json_response.items():
                for message in messages:
                    print(
                        f"* [bold red]{field.capitalize()}[/bold red] {message}"
                    )
            raise SystemExit

        if not response.ok:
            print(
                "Request to Enterprise API failed. Details:", style="bold red"
            )
            details = (
                json_response.get("error")
                or json_response.get("message")
                or response.content
            )
            print(f"{details}")
            raise SystemExit