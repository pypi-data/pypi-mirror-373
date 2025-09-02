import base64
import httpx
import os

from typing import Any
from pathlib import Path
from resources import EXCEPTIONS, SCHEMA_TYPES, Feedback
from pydantic import BaseModel, Field

class ClientConfig(BaseModel):
    # Required Config
    api_key: str
    base_url: str

    # Auto Initialized
    base_headers: dict[str, str] | None = Field(default_factory=dict)
    
    # Optional config
    timeout: float = 10.0

    def model_post_init(self, __context) -> None:
        if not self.base_headers:
            self.base_headers = {}

        self.base_headers.update({
            "accept": "application/json",
            "Authorization": f"{self.api_key}"
        })
    
class PyZoneClient:
    def __init__(self, config: ClientConfig):
        self._client = self._get_client(config)

    @staticmethod
    def _get_client(config: ClientConfig):
        return httpx.Client(
            base_url=config.base_url,
            headers=config.base_headers,
            timeout=config.timeout
        )
    
    @staticmethod
    def _raise_for_status(response: httpx.Response):
        statuscode = response.status_code
        data = response.text 

        if statuscode in EXCEPTIONS.keys():
            raise EXCEPTIONS[statuscode](data)
        else:
            return False

    @staticmethod
    def _check_types(type, typename, typeset):
        if typename not in typeset:
            raise ValueError(f"{type}: '{typename}' not in supported: {", ".join(typeset)}")
        else:
            return


    def _request(self, method: str, endpoint: str = "/", 
                 headers: dict[str, str] | None = None,
                 params: dict[str, str] | None = None,
                 json: dict[str, Any] | None = None) -> Any:
        
        response = self._client.request(
            method=method,
            url=endpoint,
            headers=headers,
            params=params,
            json=json
        )

        

        if not self._raise_for_status(response):
            if response.text:
                try:
                    return response.json()
                except ValueError as e: 
                    print(f"[-] Error decoding JSON from {method.upper()} {endpoint}: {e}")
                    raise ValueError("Error decoding JSON")
            else:
                raise ValueError("Request response was empty")

    def get(self, *, endpoint: str = "/", headers: dict[str, str] | None = None, 
                params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", endpoint, headers=headers, params=params)

    def post(self, *, endpoint: str = "/", headers: dict[str, str] | None = None, 
                json: dict[str, Any] | None = None) -> Any:
        return self._request("POST", endpoint, headers=headers, json=json)

    def delete(self, *, endpoint: str = "/", headers: dict[str, str] | None = None, 
               params: dict[str, Any] | None = None) -> Any:
        return self._request("DELETE", endpoint, headers=headers, params=params)
    
    def put(self, *, endpoint: str = "/", headers: dict[str, str] | None = None, 
                params: dict[str,Any] | None = None, json: dict[str, Any] | None = None) -> Any:
        return self._request("PUT", endpoint, params=params, headers=headers, json=json)

    def patch(self, *, endpoint: str = "/", headers: dict[str, str] | None = None, 
                json: dict[str, Any] | None = None) -> Any:
        return self._request("PATCH", endpoint, headers=headers, json=json)

    # Context Memory Functions
    def context_item_create(self, *, content: str, tenant_id: int | None = None, 
                              tenant_label: str | None = None, tenant_union_id: int | None = None) -> Any:
        '''
        Create a new user Context Memory Item (+ optional tenant union OR tenant id/label). 
        Prefer tenant_union_id for union-scoped context (multiple integration slots); tenant_id+tenant_label for upstream tenant scoping.
        
        :type content: str
        :param content: The content of the post
        :type tenant_id: str | None
        :param tenant_id: The ID of the tenant
        :type tenant_label: str | None
        :param tenant_label: The label of the tenant
        :type tenant_union_id: str | None
        :param tenant_union_id: The union ID of the tenant
        '''
        assert content.strip(), ("Content must not be empty")

        if tenant_union_id:
            assert not tenant_id and not tenant_label, ("Provide either tenant_union_id OR (tenant_id + tenant_label), not both")
        else:
            assert tenant_id and tenant_label, ("If tenant_union_id is not provided, both tenant_id and tenant_label are required")

        json = {
            "content": content,
            "tenant_id": tenant_id,
            "tenant_label": tenant_label,
            "tenant_union_id": tenant_union_id
        }

        data = self.post(endpoint="/app/api/v1/context-memory/create", json=json)
        return data

    def context_item_delete(self, *, item_id: int) -> Any:
        '''
        Delete an existing user Context Memory Item

        :type item_id: str
        :param item_id: The ID of the item to delete
        '''

        if not item_id:
            ValueError("item_id must not be empty")


        data = self.delete(endpoint=f"/app/api/v1/context-memory/delete/{item_id}")
        return data

    def context_item_update(self, *, item_id: int, content: str, tenant_id: str = "", 
                              tenant_label: str | None = None, tenant_union_id: str | None = None) -> Any:
        '''
        Update an existing user Context Memory Item (+ optional tenant union OR tenant id/label). 
        Prefer tenant_union_id for union-scoped context (multiple integration slots); tenant_id+tenant_label for upstream tenant scoping.

        :type item_id: str
        :param item_id: The ID of the item to update
        :type content: str
        :type tenant_id: str | None
        :param tenant_id: The ID of the tenant
        :type tenant_label: str | None
        :param tenant_label: The label of the tenant
        :type tenant_union_id: str | None
        :param tenant_union_id: The union ID of the tenant
        '''

        if not item_id:
            ValueError("item_id must not be empty")
        if not content.strip():
            ValueError("content must not be empty")
        
        if tenant_union_id:
            if tenant_id or tenant_label:
                ValueError("Provide either tenant_union_id OR (tenant_id + tenant_label), not both")
        else:
            if (not tenant_id and tenant_label) or (not tenant_label and tenant_id): 
                ValueError("If tenant_union_id is not provided, both tenant_id and tenant_label are required")

        json = {
            "content": content,
            "tenant_id": tenant_id,
            "tenant_label": tenant_label,
            "tenant_union_id": tenant_union_id
        }

        data = self.put(endpoint=f"/app/api/v1/context-memory/update/{item_id}", json=json)
        return data
    
    # Email Functions
    def create_email_investigation(self, email_file_path: str | Path) -> Any:
        '''
        Creates a new email investigation, returning the ID.

        :type email_file_path: str | Path
        :param email_file_path: The path to the target email file
        '''
        try:
            if not os.path.isfile(email_file_path):
                raise FileNotFoundError(f"File not found: {email_file_path}")
        
            with open(email_file_path, "rb") as f:
                binary_content = f.read()

            try:
                encoded = base64.b64encode(binary_content).decode("utf-8")
            except Exception as exc:
                raise exc

            json = {"email": encoded}

            data = self.post(endpoint="/app/api/v1/email/investigation/create", json=json)
            return data

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except PermissionError as e:
            print(f"Permission error: {e}")
        except (ValueError, ConnectionError) as e:
            print(f"Processing error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def investigation_bulk_feedback(self, *, investigation_ids: list[int], status: str, outcome: str, priority: str, outcome_note: str | None = None) -> Any:
        '''
        Bulk update investigation feedback

        :type investigation_ids: list[int]
        :param investigation_ids: The list of IDs for investigations you want to provide feedback for
        :type status: str
        :param status: Current investigation(s) status('): "in_review" or "reviewed"
        :type outcome: str
        :param outcome: The final outcome: "COMPLETED_BREACHED_CONFIRMED", "COMPLETED_BREACHED_SUSPICIOUS", "COMPLETED_FALSE_ALERT",
                     "INCOMPLETE", "IGNORED"
        :type priority: str
        :param priority: The priority of the investigation(s): "informational", "notable", "urgent"
        :type outcome_note: str | None
        :param outcome_note: Notes on the feedback to refer to dropzone agent
        '''
        self._check_types("status", status, Feedback.STATUS_TYPES)
        self._check_types("outcome", outcome, Feedback.OUTCOME_TYPES)
        self._check_types("priority", priority, Feedback.PRIORITY_TYPES)

        json = {
            "investigation_ids": investigation_ids,
            "Feedback": {
                "status": status,
                "outcome": outcome,
                "priority": priority,
                "outcome_note": outcome_note if outcome_note else ""
            }
        }
        
        data = self.patch(endpoint="/app/api/v1/investigation-bulk-feedback", json=json)
        return data
    
    def get_investigation(self, investigation_id: int) -> Any:
        '''
        Returns an alert investigation

        :type investigation_id: int
        :param investigation_id: The id of the target investigated alert
        '''

        if investigation_id < 0:
            raise ValueError("Invgestigation ID cannot be negative.")

        data = self.get(endpoint=f"/app/api/v1/investigation/{investigation_id}")
        return data

    def create_investigation(self, *, schema_key: str, raw_alert_content: dict[Any, Any], force_reinvestigation: bool = False) -> Any:
        '''
        Creates a new alert investigation, returning investigation_id
        Returns existing id if alert already exists (unless force_reinvestigation=True)

        :type  schema_key: str
        :param schema_key: The schema format the endpoint will expect the data to be in
        :type raw_alert_content: dict[Any, Any]
        :param raw_alert_content: The information according to the schema provided
        :type force_reinvestigation: bool
        :param force_reinvestigation: If a duplicate investigation already exist, on False will return existing ID
        on True will open a duplicate
        '''
        self._check_types("Schema Key", schema_key, SCHEMA_TYPES)

        json = {
            "schema_key": schema_key,
            "raw_alert_content": raw_alert_content,
            "force_reinvestigation": force_reinvestigation
        }

        data = self.post(endpoint="/app/api/v1/investigation/create", json=json)
        return data

    def create_custom_investigation(self, *, json: dict[Any, Any], force_reinvestigation: bool = False) -> Any:
        '''
        Request body = arbitrary alert JSON to be parsed & investigated
        Response = investigation_id if successful, error_msg otherwise
        Returns existing id if alert already exists (unless ?force_reinvestigation=True)

        :type json: dict[Any, Any]
        :param json: The body of the custom investigation query
        :type force_reinvestigation: bool
        :param force_reinvestigation: If a duplicate investigation already exist, on False will return existing ID
        on True will open a duplicate
        '''

        if json == {}:
            raise ValueError("Request body must not be empty")
        
        data = self.post(endpoint="/app/api/v1/investigation/create/custom", json=json)
        return data

    def ping(self) -> Any:
        self.get(endpoint="/app/api/v1/ping")

    def system_event_list(self, *, event_from: str | None = None, event_name: str | None= None, event_until: str | None = None,
                          integration_slug: str | None= None, investigation_id: int | None = None, limit: int | None = None,
                          offset: int | None = None, search: str | None = None, user_id: int | None = None) -> Any:
        '''
        List system events for each trigger run batch

        :param event_from: Lower bound for event date/time (ISO 8601 string).
        :type event_from: str, optional
        :param event_name: Filter by event name.
        :type event_name: str, optional
        :param event_until: Upper bound for event date/time (ISO 8601 string).
        :type event_until: str, optional
        :param integration_slug: Filter by integration slug.
        :type integration_slug: str, optional
        :param investigation_id: Filter by investigation ID.
        :type investigation_id: int, optional
        :param limit: Maximum number of results per page.
        :type limit: int, optional
        :param offset: Number of results to skip (for pagination).
        :type offset: int, optional
        :param search: Free-text search in trigger arguments.
        :type search: str, optional
        :param user_id: Filter by user ID.
        :type user_id: int, optional
        '''

        params = {
            "event_from": event_from,
            "event_name": event_name,
            "event_until": event_until,
            "integration_slug": integration_slug,
            "investigation_id": investigation_id,
            "limit": limit,
            "offset": offset,
            "search": search,
            "user_id": user_id
        }
        self.get(endpoint="/app/api/v1/system-events/list", params=params)

    def close(self):
        self._client.close()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    