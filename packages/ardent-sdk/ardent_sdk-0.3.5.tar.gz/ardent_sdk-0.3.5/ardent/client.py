import httpx
import time
import hmac
import hashlib
from uuid import uuid4
from typing import Dict, Any, Optional, List
from .exceptions import ArdentAPIError, ArdentAuthError, ArdentValidationError
import json

from .configs_values import config_definition

class ArdentClient:
    def __init__(
        self, 
        public_key: str,
        secret_key: str,
        base_url: str = "https://ardentbackendwebappfinal.azurewebsites.net"
    ):
        if not public_key or not secret_key:
            raise ArdentValidationError("Both public and secret keys are required")
            
        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid4())
        self._client = httpx.Client(timeout=3000.0)

    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time()))
        message = f"{timestamp}{method}{path}{body}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-API-Key": self.public_key,
            "X-Signature": signature,
            "X-Timestamp": timestamp,
            "X-Session-ID": self.session_id,
            "Content-Type": "application/json"
        }

    def create_job(self, message: str) -> Dict[str, Any]:
        path = "/v1/jobs/createJob"
        body = {
            "userMessage": message,
        }
        
        try:
            json_body = json.dumps(body, separators=(',', ':'))
            
            headers = self._sign_request(
                method="POST",
                path=path,
                body=json_body
            )
            
            response = self._client.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=body
            )


            
            response.raise_for_status()
            
            if response.status_code == 201:  # Handle 201 Created specifically
                response_data = response.json()
                if not response_data:
                    raise ArdentAPIError("API returned empty response")
                
                # Ensure required fields are present
                required_fields = ['id', 'files_share_name', 'userID']
                if not all(field in response_data for field in required_fields):
                    # Generate an ID if missing
                    if 'id' not in response_data:
                        response_data['id'] = str(uuid4())
                    # Use empty string for missing share name
                    if 'files_share_name' not in response_data:
                        response_data['files_share_name'] = ''
                    # Use provided userID if missing

                        
                return response_data
                
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )
        except json.JSONDecodeError as e:
            raise ArdentAPIError(f"Invalid JSON response from API: {str(e)}")

    def execute_job(
        self, 
        jobID: str, 
        message: str, 
        files_share_name: str, 
        userID: str,
        safe_mode: bool = False
    ) -> Dict[str, Any]:
        """Execute a job with the given parameters."""
        path = "/v1/jobs/APIChat"  # Updated endpoint path
        body = {
            "jobID": jobID,
            "userMessage": message,
            "files_share_name": files_share_name,
            "userID": userID,
            "safeMode": safe_mode
        }
        
        try:
            json_body = json.dumps(body, separators=(',', ':'))
            headers = self._sign_request(
                method="POST",
                path=path,
                body=json_body
            )
            
            response = self._client.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            elif e.response.status_code == 402:
                raise ArdentAPIError("Out of credits")
            elif e.response.status_code == 403:
                raise ArdentAuthError("Missing required scope: job:execute")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )

    def create_and_execute_job(
        self, 
        message: str,
        safe_mode: bool = False
    ) -> Dict[str, Any]:
        """Create and execute a job in one operation."""
        # First create the job
        path = "/v1/jobs/createJob"
        create_body = {
            "userMessage": message,
        }
        
        try:
            # Create job
            json_body = json.dumps(create_body, separators=(',', ':'))
            headers = self._sign_request(
                method="POST",
                path=path,
                body=json_body
            )
            
            create_response = self._client.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=create_body
            )
            create_response.raise_for_status()
            job = create_response.json()
            
            if not job:
                raise ArdentAPIError("Job creation failed - empty response")
                
            # Then execute the job
            execute_path = "/v1/jobs/APIChat"
            execute_body = {
                "jobID": job["id"],
                "userMessage": message,
                "files_share_name": job["files_share_name"],
                "safeMode": safe_mode
            }
            
            json_body = json.dumps(execute_body, separators=(',', ':'))
            headers = self._sign_request(
                method="POST",
                path=execute_path,
                body=json_body
            )
            
            execute_response = self._client.post(
                f"{self.base_url}{execute_path}",
                headers=headers,
                json=execute_body
            )
            execute_response.raise_for_status()
            execute_result = execute_response.json()
            create_and_execute_responses = {**execute_result, **job}
            return create_and_execute_responses
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            elif e.response.status_code == 402:
                raise ArdentAPIError("Out of credits")
            elif e.response.status_code == 403:
                raise ArdentAuthError("Missing required scope: job:execute")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )
        

        
    def recursive_structure_validation(self, value: Any, structure_def: Any, path: str = "") -> None:
        """
        Recursively validate data against a structure definition.

        Args:
            value: The value to validate
            structure_def: The structure definition to validate against
            path: The path to the value in the structure
        """


        
        if isinstance(structure_def, type):
            if not isinstance(value, structure_def):
                raise ArdentValidationError(
                    f"Invalid type at {path}. Expected {structure_def.__name__}, got {type(value).__name__}"
                )
        elif isinstance(structure_def, dict):
            expected_type = structure_def["type"]
            if not isinstance(value, expected_type):
                raise ArdentValidationError(
                    f"Invalid type at {path}. Expected {expected_type.__name__}, got {type(value).__name__}"
                )
            
            if "structure" in structure_def:
                for i, item in enumerate(value):
                    item_path = f"{path}[{i}]"
                    
                    for req_field in structure_def["structure"]["required"]:
                        if req_field not in item:
                            raise ArdentValidationError(f"Missing required field '{req_field}' at {item_path}")
                    
                    for prop_name, prop_def in structure_def["structure"]["properties"].items():
                        if prop_name in item:
                            self.recursive_structure_validation(
                                item[prop_name],
                                prop_def,
                                f"{item_path}.{prop_name}"
                            )

    def _validate_config_structure(self, config_type: str, config_info: Dict[str, Any], config_data: Dict[str, Any]) -> None:
        """
        Validate configuration structure based on config type.
        """
        # First check required parameters
        required_params = config_info["required_params"]
        for param in required_params:
            if param not in config_data:
                raise ArdentValidationError(f"Missing required parameter: {param}")

        # Validate each field against its structure definition
        for param, structure_def in config_info["structure"].items():
            if param in config_data:
                self.recursive_structure_validation(
                    config_data[param],
                    structure_def,
                    param
                )

    def set_config(
        self,
        config_type: str,
        id: Optional[str] = None,
        **config_params: Any
    ) -> Dict[str, Any]:
        """
        Set configuration for various data sources.
        
        Args:
            config_type: The type of configuration ('mongodb', 'postgreSQL', etc.)
            id: Optional unique identifier for the configuration. If not provided, one will be generated.
            **config_params: Configuration parameters specific to the type
        """
        # Generate UUID if not provided
        if id is None:
            id = str(uuid4())

        # Combined mapping of config types to their endpoints and required parameters
        

        # Validate config type
        if config_type not in config_definition:
            raise ArdentValidationError(f"Invalid configuration type: {config_type}")
        
        config_info = config_definition[config_type]
        path = '/v1/configs/setConfig'

        
        # Validate required parameters
        """
        missing_params = [param for param in config_info["required_params"] 
                         if param not in config_params]
        if missing_params:
            raise ArdentValidationError(
                f"Missing required parameters for {config_type}: {', '.join(missing_params)}"
            )
        
        # Validate parameter types against structure
        for param, expected_type in config_info["structure"].items():
            if param in config_params:
                value = config_params[param]
                if not isinstance(value, expected_type):
                    raise ArdentValidationError(
                        f"Invalid type for parameter '{param}' in {config_type} config. "
                        f"Expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                
        """

        config_info = config_definition[config_type]

        # Use the general validation function for all config types
        self._validate_config_structure(config_type, config_info, config_params)

        # Construct request body
        body = {
            "Config": {
                "type": config_type,
                "id": id,
                **config_params
            }
        }
        
        try:
            json_body = json.dumps(body, separators=(',', ':'))
            headers = self._sign_request(
                method="POST",
                path=path,
                body=json_body
            )
            
            response = self._client.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )

    def delete_config(self, config_id: str) -> Dict[str, Any]:
        """
        Delete a configuration by its ID.
        
        Args:
            config_id: The ID of the configuration to delete
        """
        path = "/v1/configs/deleteConfig"
        body = {
            "id": config_id
        }
        
        try:
            json_body = json.dumps(body, separators=(',', ':'))
            headers = self._sign_request(
                method="DELETE",
                path=path,
                body=json_body
            )
            
            response = self._client.request(
                "DELETE",
                f"{self.base_url}{path}",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            elif e.response.status_code == 403:
                raise ArdentAuthError("Missing required scope: config:write")
            elif e.response.status_code == 404:
                raise ArdentAPIError("Configuration not found")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )

    def delete_job(
        self, 
        job_id: str, 
    ) -> Dict[str, Any]:
        """
        Delete a job by its ID.
        
        Args:
            job_id: The ID of the job to delete
            
        Returns:
            Dict containing confirmation of deletion
        """
        path = "/v1/jobs/deleteJob"
        body = {
            "jobID": job_id,
        }
        
        try:
            json_body = json.dumps(body, separators=(',', ':'))
            headers = self._sign_request(
                method="DELETE",
                path=path,
                body=json_body
            )
            
            response = self._client.request(
                "DELETE",
                f"{self.base_url}{path}",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            
            # DELETE operations typically return 204 No Content
            if response.status_code == 204:
                return {"status": "success", "message": "Job deleted successfully"}
            
            # Handle any other success responses
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"status": "success", "message": "Job deleted successfully"}
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            elif e.response.status_code == 403:
                raise ArdentAuthError("Missing required scope: job:delete or cannot delete jobs for different user")
            elif e.response.status_code == 404:
                raise ArdentAPIError("Job not found")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )

    def close(self):
        """Close the underlying HTTP client and clean up resources."""
        if hasattr(self, '_client'):
            self._client.close()

    def get_job_files(self, jobID: str) -> Dict[str, Any]:
        """
        Get the file system associated with a specific job.
        
        Args:
            jobID: The ID of the job to get files for
            
        Returns:
            Dict containing the file system information
        """
        path = f"/v1/jobs/{jobID}/files"
        
        try:
            headers = self._sign_request(
                method="GET",
                path=path
            )
            
            response = self._client.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ArdentAuthError("Invalid API key or signature")
            elif e.response.status_code == 404:
                raise ArdentAPIError("Job not found")
            raise ArdentAPIError(
                f"API request failed: {str(e)}", 
                status_code=e.response.status_code,
                response=e.response
            )