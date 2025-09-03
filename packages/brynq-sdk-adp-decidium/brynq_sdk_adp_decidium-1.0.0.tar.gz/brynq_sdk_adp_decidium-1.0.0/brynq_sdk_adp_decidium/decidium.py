from brynq_sdk_brynq import BrynQ
import pandas as pd
import requests
import tempfile
import os
from datetime import datetime, date
from typing import Union, List, Dict, Optional, Any, Literal
# Initialize entity classes
from .workers import Workers
from .payroll import Payroll
from .pay_distributions import PayDistributions
from .document import Document
from .dependents import Dependents

class Decidium(BrynQ):
    """
    This class is meant to be a simple wrapper around the ADP API. In order to start using it, authorize your application in BrynQ.
    You will need to provide a token for the authorization, which can be set up in BrynQ and referred to with a label.
    You can find the ADP API docs here: https://developers.adp.com/
    """
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        self.timeout = 3600
        self.debug = debug

        # Get credentials from BrynQ
        credentials = self.interfaces.credentials.get(system="adp", system_type=system_type)
        # ADP uses OAuth 2.0 with client credentials flow
        self.client_id = credentials['data']['client_id']
        self.client_secret = credentials['data']['client_secret']
        self.certificate_text = credentials['data']['certificate']
        self.base_url = "https://api.eu.adp.com"
        # Initialize session
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None

        # Get initial access token
        self._get_access_token()

        self.workers = Workers(self)
        self.payroll = Payroll(self)
        self.pay_distributions = PayDistributions(self)
        self.document = Document(self)
        self.dependents = Dependents(self)

    # ============================================================================
    # GENERIC HELPER FUNCTIONS (Can be used by all schemas)
    # ============================================================================


    def _get_access_token(self):
        """
        Obtains an access token using OAuth 2.0 client credentials flow
        """
        token_url = "https://accounts.eu.adp.com/auth/oauth/v2/token"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        # Create temporary certificate file from text

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_cert:
            temp_cert.write(self.certificate_text)
            temp_cert_path = temp_cert.name

        try:
            response = requests.post(
                cert=temp_cert_path,
                url=token_url,
                verify=False,
                headers=headers,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']

            # Calculate token expiry time
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in

            # Update session headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
        finally:
            # Clean up temporary certificate file
            if os.path.exists(temp_cert_path):
                os.unlink(temp_cert_path)

    def _get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None,
            filter_param: Optional[str] = None, select_param: Optional[str] = None,
            skip: Optional[int] = None, top: Optional[int] = None, count: Optional[bool] = None) -> Any:
        """
        Makes a GET request to the ADP API endpoint with automatic OData parameter handling

        Args:
            endpoint (str): API endpoint to call (without base URL)
            params (Dict, optional): Additional query parameters
            headers (Dict, optional): Additional headers to send with the request
            filter_param (str, optional): OData $filter parameter
            select_param (str, optional): OData $select parameter
            skip (int, optional): OData $skip parameter for pagination
            top (int, optional): OData $top parameter for limiting results
            count (bool, optional): OData $count parameter for total count

        Returns:
            Any: Raw response data from the API
        """
        self._ensure_valid_token()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Prepare query parameters
        if params is None:
            request_params = {}
        elif isinstance(params, dict):
            request_params = params.copy()
        else:
            request_params = {}

        # Add OData parameters
        if filter_param:
            request_params["$filter"] = filter_param

        if select_param:
            request_params["$select"] = select_param

        if skip is not None:
            request_params["$skip"] = str(skip)

        if top is not None:
            request_params["$top"] = str(top)

        if count is not None:
            request_params["$count"] = "true" if count else "false"

        # Merge additional headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # Create temporary certificate file from text

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_cert:
            temp_cert.write(self.certificate_text)
            temp_cert_path = temp_cert.name

        try:
            response = self.session.get(url=url, cert=temp_cert_path, params=request_params, headers=request_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        finally:
            # Clean up temporary certificate file
            if os.path.exists(temp_cert_path):
                os.unlink(temp_cert_path)

    def _get_with_pagination(self, endpoint: str, response_key: str) -> List[Dict]:
        """
        Makes paginated GET requests to the ADP API endpoint, automatically collecting all data
        by fetching in batches of 50 records until no more data remains.

        Args:
            endpoint (str): API endpoint to call (without base URL)
            response_key (str): Key in response data to extract (default: "workers")

        Returns:
            List[Dict]: Combined list of all data from all pages
        """
        all_data = []
        skip = 0
        batch_size = 50

        while True:
            # Make request for current batch
            response_data = self._get(
                endpoint=endpoint,
                skip=skip,
                top=batch_size
            )

            # Extract the data from response using the specified key
            if isinstance(response_data, dict) and response_key in response_data:
                batch_data = response_data[response_key]
            elif isinstance(response_data, list):
                batch_data = response_data
            else:
                # If response is not in expected format, treat it as a single item
                batch_data = [response_data] if response_data else []

            # Add batch data to all_data
            all_data.extend(batch_data)

            # Check if we got fewer records than requested (indicating end of data)
            break
            if len(batch_data) < batch_size:
                break

            # Move to next batch
            skip += batch_size

            if self.debug:
                print(f"Fetched batch of {len(batch_data)} records. Total collected: {len(all_data)}")

        if self.debug:
            print(f"Pagination complete. Total records collected: {len(all_data)}")

        return all_data

    def _post(self, url: str, request_body: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """
        Makes a POST request to the ADP API endpoint with certificate.

        Args:
            url (str): API endpoint to call (without base URL)
            request_body (Dict, optional): JSON body to send with the request
            headers (Dict, optional): Additional headers to send with the request

        Returns:
            Any: Raw response data from the API
        """
        self._ensure_valid_token()
        # Merge additional headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        # Create temporary certificate file from text

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as temp_cert:
            temp_cert.write(self.certificate_text)
            temp_cert_path = temp_cert.name

        try:
            response = self.session.post(
                url=url,
                cert=temp_cert_path,
                json=request_body,
                headers=request_headers,
                timeout=self.timeout
            )
            return response
        finally:
            # Clean up temporary certificate file
            if os.path.exists(temp_cert_path):
                os.unlink(temp_cert_path)

    def _ensure_valid_token(self):
        """
        Ensures the access token is valid and refreshes it if needed
        """
        if self.access_token is None or self.token_expires_at is None:
            self._get_access_token()
        elif datetime.now().timestamp() >= self.token_expires_at:
            self._get_access_token()
