from typing import Optional, Dict, List, Any
import httpx
from ivoryos_client.exceptions import (
    IvoryosError,
    AuthenticationError,
    ConnectionError,
    WorkflowError,
    TaskError,
)

class IvoryosClient:
    """Client for interacting with IvoryOS API"""

    def __init__(self, url: str, username: str, password: str):
        """
        Initialize IvoryOS client

        Args:
            url: IvoryOS server URL
            username: Username for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip('/')
        self.login_data = {"username": username, "password": password}
        self.client = httpx.Client(follow_redirects=True)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def _check_authentication(self) -> None:
        """Check and handle authentication"""
        try:
            resp = self.client.get(f"{self.url}/", follow_redirects=False)
            if resp.status_code == httpx.codes.OK:
                return

            login_resp = self.client.post(f"{self.url}/auth/login", data=self.login_data)
            if login_resp.status_code != 200:
                raise AuthenticationError(f"Login failed with status {login_resp.status_code}")
        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection error during authentication: {e}") from e

    def get_platform_info(self) -> str:
        """
        Get platform information and available functions

        Returns:
            Platform information string
        """
        try:
            self._check_authentication()
            snapshot = self.client.get(f"{self.url}/instruments").json()
            return (
                # f"IvoryOS is a unified task and workflow orchestrator.\n"
                "workflow execution has 3 blocks, prep, main (iterate) and cleanup.\n"
                "one can execute the workflow using one of the 3 options:\n"
                "1. simple repeat for static workflow with `run_workflow_repeat`\n"
                "2. repeat with kwargs `run_workflow_kwargs`\n"
                "3. campaign `run_workflow_campaign`\n"
                f"Available functions: {snapshot}"
            )
        except Exception as e:
            raise IvoryosError(f"Failed to get platform info: {e}") from e

    def get_execution_status(self):
        """
        Get workflow execution status

        Returns:
            Dictionary containing execution status
        """
        try:
            self._check_authentication()
            resp = self.client.get(f"{self.url}/executions/status")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to get execution status: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error getting workflow status: {e}") from e

    def execute_task(self, component: str, method: str, kwargs: Optional[Dict[str, Any]] = None):
        """
        Execute a robot task

        Args:
            component: Component name (e.g., 'sdl')
            method: Method name (e.g., 'dose_solid')
            kwargs: Method keyword arguments

        Returns:
            Task execution result
        """
        try:
            self._check_authentication()
            if kwargs is None:
                kwargs = {}

            snapshot = self.client.get(f"{self.url}/instruments").json()
            component = component if component.startswith("deck.") else f"deck.{component}"

            if component not in snapshot:
                raise TaskError(f"Component {component} does not exist. Available: {list(snapshot.keys())}")

            kwargs["hidden_name"] = method
            kwargs["hidden_wait"] = False

            resp = self.client.post(f"{self.url}/instruments/{component}", json=kwargs)
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise TaskError(f"Failed to execute task: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, TaskError)):
                raise
            raise TaskError(f"Error executing task: {e}") from e

    def list_workflow_scripts(self, search_key: str = '', deck_name: str = ''):
        """
        List workflow scripts

        Args:
            search_key: Search keyword
            deck_name: Deck name filter

        Returns:
            Dictionary of workflow scripts
        """
        try:
            self._check_authentication()
            params = {}
            if deck_name:
                params['deck'] = deck_name
            if search_key:
                params['keyword'] = search_key
            resp = self.client.get(
                f"{self.url}/library/{deck_name}",
                params=params
            )
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to list workflow scripts: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error listing workflow scripts: {e}") from e

    def load_workflow_script(self, workflow_name: str):
        """
        Load a workflow script

        Args:
            workflow_name: Name of the workflow

        Returns:
            Workflow script data
        """
        try:
            self._check_authentication()
            resp = self.client.get(f"{self.url}/library/{workflow_name}")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to load workflow script: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error loading workflow script: {e}") from e

    def submit_workflow_script(self, workflow_name: str, main_script: str = "",
                               cleanup_script: str = "", prep_script: str = ""):
        """
        Submit a workflow script

        Args:
            workflow_name: Name of the workflow
            main_script: Main script content
            cleanup_script: Cleanup script content
            prep_script: Preparation script content

        Returns:
            Success message
        """
        try:
            self._check_authentication()
            resp = self.client.post(
                url=f"{self.url}/draft/submit_python",
                json={
                    "workflow_name": workflow_name,
                    "script": main_script,
                    "cleanup": cleanup_script,
                    "prep": prep_script
                }
            )
            if resp.status_code == httpx.codes.OK:
                return "Workflow script submitted successfully"
            else:
                raise WorkflowError(f"Failed to submit workflow script: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error submitting workflow script: {e}") from e

    def pause_and_resume(self):
        """
        Toggle pause and resume for workflow execution

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            resp = self.client.post(f"{self.url}/executions/pause-resume")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to toggle pause/resume: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error toggling workflow pause/resume: {e}") from e

    def abort_pending_workflow(self):
        """
        Abort pending workflow execution

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            resp = self.client.post(f"{self.url}/executions/abort/next-iteration")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to abort pending workflow: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error aborting pending workflow: {e}") from e

    def stop_current_workflow(self):
        """
        Stop workflow execution after current step

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            resp = self.client.post(f"{self.url}/executions/abort/next-task")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to stop current workflow: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error stopping current workflow: {e}") from e

    def run_workflow_repeat(self, repeat_time: Optional[int] = None):
        """
        Run the loaded workflow with repeat times

        Args:
            repeat_time: Number of times to repeat the workflow

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            resp = self.client.post(
                f"{self.url}/executions/config",
                json={"repeat": str(repeat_time) if repeat_time is not None else None}
            )
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to start workflow execution: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error starting workflow execution: {e}") from e

    def run_workflow_kwargs(self, kwargs_list: Optional[List[Dict[str, Any]]] = None):
        """
        Run the loaded workflow with a list of keyword arguments

        Args:
            kwargs_list: List of keyword argument dictionaries

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            resp = self.client.post(
                f"{self.url}/executions/config",
                json={"kwargs": kwargs_list}
            )
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to start workflow execution: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error starting workflow execution: {e}") from e

    def run_workflow_campaign(self, parameters: List[Dict[str, Any]],
                              objectives: List[Dict[str, Any]],
                              repeat: int = 25,
                              parameter_constraints: Optional[List[str]] = None):
        """
        Run the loaded workflow with ax-platform

        Args:
            parameters: List of parameter definitions
            objectives: List of objective definitions
            repeat: Number of iterations
            parameter_constraints: List of parameter constraints

        Returns:
            Response from the server
        """
        try:
            self._check_authentication()
            if parameter_constraints is None:
                parameter_constraints = []

            resp = self.client.post(
                f"{self.url}/executions/config",
                json={
                    "parameters": parameters,
                    "objectives": objectives,
                    "parameter_constraints": parameter_constraints,
                    "repeat": repeat,
                }
            )
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to start workflow campaign: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error starting workflow campaign: {e}") from e

    def list_workflow_data(self, workflow_name: str = ""):
        """
        List workflow data

        Args:
            workflow_name: Filter by workflow name

        Returns:
            Dictionary of workflow data
        """
        try:
            self._check_authentication()
            resp = self.client.get(
                f"{self.url}/executions/records",
                params={"keyword": workflow_name}
            )
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to list workflow data: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error listing workflow data: {e}") from e

    def load_workflow_data(self, workflow_id: int):
        """
        Load workflow data

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow data
        """
        try:
            self._check_authentication()
            resp = self.client.get(f"{self.url}/executions/records/{workflow_id}")
            if resp.status_code == httpx.codes.OK:
                return resp.json()
            else:
                raise WorkflowError(f"Failed to load workflow data: {resp.status_code}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, ConnectionError, WorkflowError)):
                raise
            raise WorkflowError(f"Error loading workflow data: {e}") from e


if __name__ == "__main__":
    client = IvoryosClient(
        url="http://localhost:8000/ivoryos",
        username="admin",
        password="admin"
    )

    print(client.list_workflow_data())