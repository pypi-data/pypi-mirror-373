"""
API client for ivybloom CLI
"""

import httpx
import sys
import json
from typing import Dict, Any, Optional, List
from rich.console import Console

from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.colors import get_console, print_error, print_info

console = get_console()

class IvyBloomAPIClient:
    """HTTP client for ivybloom API"""
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        self.config = config
        self.auth_manager = auth_manager
        # Use frontend URL for all API calls - frontend handles Clerk auth and proxying
        self.base_url = config.get_frontend_url()
        self.timeout = config.get('timeout', 30)
        
        # Initialize HTTP client with cookie support and redirect following
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_default_headers(),
            follow_redirects=True,
            cookies={}  # Enable cookie jar for session management
        )
    
    def _ensure_authenticated(self) -> None:
        """Ensure user is authenticated before making requests"""
        # Accept any valid auth method: JWT/OAuth/API key
        if not self.auth_manager.is_authenticated():
            raise Exception(
                "Authentication required. Please run 'ivybloom auth login' (browser/device/link) or provide an API key."
            )
    
    def _get_default_headers(self, *, prefer_jwt: bool = False) -> Dict[str, str]:
        """Get default headers for requests"""
        # Build default headers including auth; prefer API key for stability, then JWT/OAuth
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ivybloom-cli/0.5.17",
            "Accept": "application/json"
        }
        # Add Authorization header via AuthManager (JWT/OAuth/API key)
        headers.update(self.auth_manager.get_auth_headers(prefer_jwt=prefer_jwt))
        
        # Include client identifier for analytics and linking
        try:
            client_id = self.config.get_or_create_client_id()
            # Prefer lowercase header for compatibility with Node/edge middleware
            headers["x-ivybloom-client"] = client_id
        except Exception:
            pass
        
        return headers
    
    def _refresh_headers(self, *, prefer_jwt: bool = False):
        """Refresh authentication headers (for retry logic)"""
        # Get fresh headers including updated Clerk session
        fresh_headers = self._get_default_headers(prefer_jwt=prefer_jwt)
        self.client.headers.update(fresh_headers)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with error handling"""
        try:
            # Ensure endpoint joins correctly with base_url
            path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
            
            # Ensure headers are fresh for this request
            self._refresh_headers()
            
            if self.config.get('debug'):
                # Send debug logs to stderr to avoid contaminating stdout (which may be parsed as JSON)
                print(f"{method} {endpoint} -> (sending request)", file=sys.stderr)
            
            response = self.client.request(method, path, **kwargs)
            
            if self.config.get('debug'):
                # Route debug logs to stderr
                print(f"{method} {endpoint} -> {response.status_code}", file=sys.stderr)
            
            return response
        except httpx.TimeoutException:
            raise Exception("Request timed out. Check your network and try again.")
        except httpx.ConnectError:
            raise Exception("Could not connect to API server. Verify IVY_ORCHESTRATOR_URL and your network.")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request with automatic token refresh"""
        self._ensure_authenticated()
        response = self._make_request("GET", endpoint, params=params)
        
        # Handle 401 with potential token refresh retry
        if response.status_code == 401:
            try:
                error_data = response.json()
                detail = error_data.get("code")
            except Exception:
                detail = None
                
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("❌ CLI not linked to your account. Run 'ivybloom auth link' to link this CLI installation.")
            
            # Try refreshing API key/JWT headers and retrying once
            # Send human-readable notice to stderr so stdout remains machine-parseable
            print("Access token may be expired, attempting refresh...", file=sys.stderr)
            self._refresh_headers()
            
            # Retry the request with refreshed headers
            retry_response = self._make_request("GET", endpoint, params=params)
            if retry_response.status_code == 401:
                # Secondary fallback: retry once forcing JWT if available
                self._refresh_headers(prefer_jwt=True)
                retry_jwt_response = self._make_request("GET", endpoint, params=params)
                if retry_jwt_response.status_code == 401:
                    raise Exception("❌ Authentication failed. Please run 'ivybloom auth login' or check your API key.")
                response = retry_jwt_response
            else:
                # Use the retry response for further processing
                response = retry_response
            
        elif response.status_code == 403:
            raise Exception("❌ Access denied. You don't have permission for this resource.")
        elif response.status_code == 404:
            raise Exception("❌ Resource not found.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_data.get('message', f'HTTP {response.status_code}'))
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"❌ API error: {error_msg}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"data": response.text}
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request with automatic token refresh"""
        self._ensure_authenticated()
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        
        response = self._make_request("POST", endpoint, **kwargs)
        
        # Handle 401 with potential token refresh retry
        if response.status_code == 401:
            try:
                detail = response.json().get("code")
            except Exception:
                detail = None
                
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("Authentication required. Run 'ivybloom auth link' to link this CLI and retry.")
            
            # Prefer forcing JWT/OAuth token first (some backends require verifiable user token)
            print("Access token may be expired, attempting refresh...", file=sys.stderr)
            self._refresh_headers(prefer_jwt=True)
            retry_jwt_first = self._make_request("POST", endpoint, **kwargs)
            if retry_jwt_first.status_code == 401:
                # Fallback: refresh default headers (API key) and retry
                self._refresh_headers(prefer_jwt=False)
                retry_default = self._make_request("POST", endpoint, **kwargs)
                if retry_default.status_code == 401:
                    raise Exception("Authentication failed. Please check your API key or login status.")
                response = retry_default
            else:
                response = retry_jwt_first
            
        elif response.status_code == 403:
            raise Exception("Access denied. You don't have permission for this resource.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API error: {error_msg}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"data": response.text}
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        self._ensure_authenticated()
        response = self._make_request("DELETE", endpoint)
        
        if response.status_code == 401:
            try:
                detail = response.json().get("code")
            except Exception:
                detail = None
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("Authentication required. Run 'ivybloom auth link' to link this CLI and retry.")
            # Retry once forcing JWT/OAuth token if available
            self._refresh_headers(prefer_jwt=True)
            retry_jwt_response = self._make_request("DELETE", endpoint)
            if retry_jwt_response.status_code == 401:
                raise Exception("Authentication failed. Please check your API key or login status.")
            response = retry_jwt_response
        elif response.status_code == 403:
            raise Exception("Access denied. You don't have permission for this resource.")
        elif response.status_code == 404:
            raise Exception("Resource not found.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API error: {error_msg}")
        
        if response.status_code == 204:
            return {"success": True}
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"success": True}
    
    # CLI-specific API methods
    def list_tools(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """List available tools
        
        Args:
            verbose: If True, request extended/verbose fields from the API
        
        Returns:
            List of tool summaries (render-safe fields by default)
        """
        params = {"verbose": True} if verbose else None
        data = self.get("/api/cli/tools", params=params)
        return data
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool using the verbose tools list.
        
        First attempts to use the per-tool schema endpoint if available.
        Falls back to loading the verbose tools list and extracting the schema.
        """
        # 1) Try direct endpoint if present
        try:
            return self.get(f"/api/cli/tools/{tool_name}/schema")
        except Exception:
            # Fallback to verbose tools listing
            pass

        tools_verbose = self.list_tools(verbose=True)
        if not isinstance(tools_verbose, list):
            raise Exception("Unexpected response while loading tools list for schema")
        
        def normalize(value: Any) -> str:
            return str(value).strip().lower() if value is not None else ""
        target = tool_name.strip().lower()
        
        for tool in tools_verbose:
            if not isinstance(tool, dict):
                continue
            candidates = [
                normalize(tool.get("name")),
                normalize(tool.get("id")),
                normalize(tool.get("tool")),
                normalize(tool.get("slug")),
            ]
            if target in candidates:
                schema_obj = tool.get("schema") or tool.get("parameters")
                if isinstance(schema_obj, dict):
                    return schema_obj
                if isinstance(schema_obj, str):
                    try:
                        return json.loads(schema_obj)
                    except Exception:
                        pass
                # Minimal fallback when schema not present but metadata exists
                return {
                    "description": tool.get("description", ""),
                    "parameters": {},
                }
        
        raise Exception(f"Schema for tool '{tool_name}' not found in tools list")
    
    def create_job(self, job_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job"""
        # Ensure the request matches the API specification
        payload = {
            "tool_name": job_request.get("tool_name"),  # CLI uses tool_name
            "parameters": job_request.get("parameters", {}),
            "project_id": job_request.get("project_id"),
            "job_title": job_request.get("job_title"),
            "wait_for_completion": job_request.get("wait_for_completion", False)
        }
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return self.post("/api/cli/jobs", json_data=payload)
    
    def get_job_status(self, job_id: str, include_logs: bool = False, logs_tail: int | None = None) -> Dict[str, Any]:
        """Get job status"""
        params: Dict[str, Any] | None = None
        if include_logs:
            params = {"include_logs": True}
            if isinstance(logs_tail, int) and logs_tail > 0:
                params["logs_tail"] = logs_tail
        response = self.get(f"/api/cli/jobs/{job_id}", params=params)
        
        # Map database field names to CLI-expected field names for backward compatibility
        if response and 'id' in response:
            response['job_id'] = response['id']  # Map id -> job_id for CLI compatibility
        if response and 'job_type' in response:
            response['tool_name'] = response['job_type']  # Map job_type -> tool_name for CLI
        if response and 'progress_percent' in response:
            response['progress_percentage'] = response['progress_percent']  # Map progress_percent -> progress_percentage
            
        return response
    
    def get_job_results(self, job_id: str, format: str = "json") -> Dict[str, Any]:
        """Get job results"""
        params = {"format": format}
        response = self.get(f"/api/cli/jobs/{job_id}/results", params=params)
        
        # Map database field names for consistency
        if response and 'id' in response:
            response['job_id'] = response['id']
        if response and 'job_type' in response:
            response['tool_name'] = response['job_type']
            
        return response
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a job"""
        return self.delete(f"/api/cli/jobs/{job_id}")
    
    def get_job_download_urls(self, job_id: str, artifact_type: str = None) -> Dict[str, Any]:
        """Get presigned download URLs for job artifacts"""
        params = {'job_id': job_id}
        if artifact_type:
            params['artifact_type'] = artifact_type
        
        return self.get("/api/cli/download", params=params)
    
    def list_jobs(self, **filters) -> List[Dict[str, Any]]:
        """List jobs with optional filters"""
        # Map CLI parameter names to API parameter names
        params = {}
        if 'project_id' in filters and filters['project_id']:
            params['project_id'] = filters['project_id']
        if 'status' in filters and filters['status']:
            params['status'] = filters['status']
        if 'tool_name' in filters and filters['tool_name']:
            params['job_type'] = filters['tool_name']  # Map tool_name to job_type
        if 'created_after' in filters and filters['created_after']:
            params['created_after'] = filters['created_after']
        if 'created_before' in filters and filters['created_before']:
            params['created_before'] = filters['created_before']
        if 'limit' in filters and filters['limit']:
            params['limit'] = filters['limit']
        if 'offset' in filters and filters['offset']:
            params['offset'] = filters['offset']
        
        return self.get("/api/cli/jobs", params=params)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List user's projects with response normalization.
        
        Returns a list of project dicts. Accepts multiple response shapes:
        - [ {..}, {..} ]
        - { "projects": [..] }
        - { "data": [..] }
        Also maps legacy "project_id" -> "id" for compatibility.
        """
        data = self.get("/api/cli/projects")
        items: List[Dict[str, Any]]
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            if isinstance(data.get("projects"), list):
                raw_items = data["projects"]
            elif isinstance(data.get("data"), list):
                raw_items = data["data"]
            else:
                raise Exception("Unexpected response while listing projects (expected a list of projects).")
        else:
            raise Exception("Unexpected response while listing projects (expected a list of projects).")

        items = []
        for item in raw_items:
            if not isinstance(item, dict):
                # Skip malformed entries rather than failing the entire call
                continue
            normalized = dict(item)
            if "id" not in normalized and "project_id" in normalized:
                normalized["id"] = normalized["project_id"]
            items.append(normalized)
        return items
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        return self.get(f"/api/cli/projects/{project_id}")
    
    def list_project_jobs(self, project_id: str) -> List[Dict[str, Any]]:
        """List jobs for a specific project"""
        return self.get(f"/api/cli/projects/{project_id}/jobs")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self.get("/api/cli/account")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.get("/api/cli/usage")
    
    def check_cli_linking_status(self, client_id: str) -> Dict[str, Any]:
        """Check if CLI client is linked to a user account
        
        Returns:
            Dict with 'linked' boolean and optionally 'ready' boolean.
            - linked: True if the client is linked to a user account
            - ready: True if the temporary API key is ready for retrieval (newer deployments)
                    If absent, fallback to legacy behavior (older deployments)
        """
        return self.get(f"/api/cli/link-status/{client_id}")
    
    def verify_cli_linking(self, client_id: str) -> Dict[str, Any]:
        """Verify and complete CLI linking process
        
        Should only be called when linked=True AND ready=True (if ready flag is present)
        to avoid 410 "expired/already retrieved" responses.
        
        Returns:
            Dict with 'success' boolean and 'api_key' string on success.
            May return 410 if temp key is missing/expired/already retrieved.
        """
        return self.post(f"/api/cli/verify-link/{client_id}")
    
    # Missing API endpoints for other CLI commands
    def list_workflows(self, **filters) -> List[Dict[str, Any]]:
        """List workflows with optional filters"""
        params = {}
        if 'project_id' in filters and filters['project_id']:
            params['project_id'] = filters['project_id']
        if 'status' in filters and filters['status']:
            params['status'] = filters['status']
        if 'limit' in filters and filters['limit']:
            params['limit'] = filters['limit']
        if 'offset' in filters and filters['offset']:
            params['offset'] = filters['offset']
        if 'sort_by' in filters and filters['sort_by']:
            params['sort_by'] = filters['sort_by']
        if 'sort_order' in filters and filters['sort_order']:
            params['sort_order'] = filters['sort_order']
        
        return self.get("/api/cli/workflows", params=params)
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details"""
        return self.get(f"/api/cli/workflows/{workflow_id}")
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        return self.post("/api/cli/workflows", json_data=workflow_data)
    
    def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow"""
        payload = {"parameters": parameters or {}}
        return self.post(f"/api/cli/workflows/{workflow_id}/execute", json_data=payload)
    
    def list_data_files(self, **filters) -> List[Dict[str, Any]]:
        """List data files with optional filters"""
        params = {}
        if 'project_id' in filters and filters['project_id']:
            params['project_id'] = filters['project_id']
        if 'file_type' in filters and filters['file_type']:
            params['file_type'] = filters['file_type']
        if 'tags' in filters and filters['tags']:
            params['tags'] = filters['tags']
        if 'limit' in filters and filters['limit']:
            params['limit'] = filters['limit']
        if 'offset' in filters and filters['offset']:
            params['offset'] = filters['offset']
        if 'sort_by' in filters and filters['sort_by']:
            params['sort_by'] = filters['sort_by']
        if 'sort_order' in filters and filters['sort_order']:
            params['sort_order'] = filters['sort_order']
        
        return self.get("/api/cli/data", params=params)
    
    def upload_data_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a data file"""
        return self.post("/api/cli/data/upload", json_data=file_data)
    
    def get_data_file(self, file_id: str) -> Dict[str, Any]:
        """Get data file details"""
        return self.get(f"/api/cli/data/{file_id}")
    
    def delete_data_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a data file"""
        return self.delete(f"/api/cli/data/{file_id}")
    
    def get_config_settings(self) -> Dict[str, Any]:
        """Get CLI configuration settings from backend"""
        return self.get("/api/cli/config")
    
    def update_config_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update CLI configuration settings"""
        return self.post("/api/cli/config", json_data=settings)
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()