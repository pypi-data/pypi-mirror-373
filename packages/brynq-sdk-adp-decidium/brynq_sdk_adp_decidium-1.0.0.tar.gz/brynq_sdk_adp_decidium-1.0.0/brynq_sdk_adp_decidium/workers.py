from typing import Dict, Optional, Union, Literal, List, Any, get_args, Tuple
import pandas as pd
from pydantic import BaseModel
import requests
from .schemas.workers import WorkerGet, WorkerHireRequest,  WorkerRehireRequest, WorkerTerminateEventData, WorkerUpdateRequest
from brynq_sdk_functions import Functions
import json
from typing import Any, Callable, Dict, Tuple, List
from .worker_normalization import WorkerNormalization
from .worker_update_functions import WorkerUpdateFunctions
from .work_assignment import WorkAssignment

class Workers:
    """
    Handles worker information retrieval operations in ADP
    """

    def __init__(self, decidium):
        self.decidium = decidium
        self.base_uri = "hr/v2/workers"
        self.normalizations = WorkerNormalization(decidium)
        self.update_functions = WorkerUpdateFunctions(decidium)
        self.work_assignment = WorkAssignment(decidium)

    def get(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieves workers from ADP with OData parameters and normalizes to WorkerGet schema.
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
                - valid_df: Validated and normalized workers data conforming to WorkerGet schema
                - invalid_df: Invalid data that failed validation (empty DataFrame if all data is valid)

        Raises:
            ValueError: If the workers data fails validation
        """
        # Build endpoint URL
        endpoint = "/hr/v2/workers"

        # Get raw data from ADP API using the enhanced get method
        workers = self.decidium._get_with_pagination(endpoint=endpoint, response_key="workers")

        try:
            # Apply normalization using our standardized function
            df_normalized = self.normalizations._normalize_workers_data(workers)

            # Validate using Functions.validate_data
            valid_df, invalid_df = Functions.validate_data(df_normalized, WorkerGet)
            return valid_df, invalid_df

        except Exception as e:
            raise ValueError(f"Workers data normalization/validation failed: {str(e)}")

    def get_by_id(self,aoid: str,) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieves a single worker by Associate OID from ADP with normalized data.

        Args:
            aoid (str): Associate OID (required)
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
                - valid_df: Validated and normalized worker data conforming to WorkerGet schema
                - invalid_df: Invalid data that failed validation (empty DataFrame if all data is valid)

        Raises:
            ValueError: If the worker data fails validation or aoid is missing
        """
        if not aoid:
            raise ValueError("aoid is required")

        # Build endpoint URL
        endpoint = f"{self.base_uri}/{aoid}"

        response_data = self.decidium._get(
            endpoint=endpoint
        )
        # Extract workers from response
        workers = response_data.get("workers", [])

        try:
            # Apply normalization using our standardized function
            df_normalized = self.normalizations._normalize_workers_data(workers)

            # Validate using Functions.validate_data
            valid_df, invalid_df = Functions.validate_data(df_normalized, WorkerGet)
            return valid_df, invalid_df

        except Exception as e:
            raise ValueError(f"Worker data normalization/validation failed for aoid {aoid}: {str(e)}")

    def create(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Hires a single worker in ADP from worker data dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing worker data with required fields:
            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the hire operation fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/events/hr/v1/worker.hire"

        # Prepare request headers
        headers = self.decidium.session.headers.copy()
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat worker data to nested structure using separate method
            worker_nested = self.normalizations._flat_dict_to_nested_dict(data)
            # Prepare request body
            request_data = {
                "events": [
                    {
                        "data": {
                            "transform": {
                                "eventStatusCode": {
                                    "codeValue": "Completed"
                                },
                                "worker": worker_nested
                            }
                        }
                    }
                ]
            }

            # Validate request data with pydantic schema
            try:
                valid_data = WorkerHireRequest(**request_data)
                # Use validated data for the request (with proper aliases)
                request_data = valid_data.model_dump(by_alias=True, exclude_none=True)

            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            # Make POST request using session
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            return response

        except Exception as e:
            raise Exception(f"An error occurred in hire operation: {e}")

    def terminate(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Terminates a worker in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing termination data with keys:
                - associate_oid: Worker's Associate OID (required)
                - termination_date: Termination date (YYYY-MM-DD format) (required)
                - termination_reason_code: Termination reason code (e.g., "DM") (required)

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the termination operation fails or validation fails
        """

        url = f"{self.decidium.base_url}/events/hr/v1/worker.terminate"

        # Prepare request headers
        headers={}
        headers.update({
            "roleCode": role_code
        })

        try:
            # First validate the flat data with schema (uses field names directly)
            WorkerTerminateEventData(**data)

            # After validation, build the nested structure
            request_data = self.normalizations._normalize_terminate_data(data)

            # Make POST request using session
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in terminate operation: {e}")

    def rehire(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Rehires a worker in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing rehire data with required fields:
            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the rehire operation fails or required fields are missing

        """

        url = f"{self.decidium.base_url}/events/hr/v1/worker.rehire"

        # Prepare request headers
        headers = self.decidium.session.headers.copy()
        headers.update({
            "roleCode": role_code
        })

        try:
            # First normalize flat data to nested structure
            request_data = self.normalizations._normalize_rehire_data(data)

            # Then validate the nested structure with WorkerRehireRequest
            WorkerRehireRequest(**request_data)

            # Make POST request using session
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in rehire operation: {e}")

    def update(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates multiple worker fields based on dictionary

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Dictionary with field names as keys and values to update
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Results for each update operation
        """
        # Validate the input dictionary using WorkerUpdateRequest schema
        try:
            # Validate dict directly with Pydantic BaseModel
            validated_model = WorkerUpdateRequest(**data)
            # Convert back to dict using model_dump without aliases
            validated_dict = validated_model.model_dump(exclude_none=True, by_alias=False)

        except Exception as e:
            return {
                'status': 'validation_error',
                'error': f"Input validation failed: {str(e)}"
            }

        # Map field names to update functions
        update_functions = {
            'birth_date': self.update_functions._update_birth_date,
            'gender': self.update_functions._update_gender,
            'business_email': self.update_functions._update_business_email,
            'business_fax': self.update_functions._update_business_fax,
            'business_landline': self.update_functions._update_business_landline,
            'business_mobile': self.update_functions._update_business_mobile,
            'business_pager': self.update_functions._update_business_pager,
            'personal_email': self.update_functions._update_personal_email,
            'personal_fax': self.update_functions._update_personal_fax,
            'personal_landline': self.update_functions._update_personal_landline,
            'personal_mobile': self.update_functions._update_personal_mobile
        }

        # Group complex fields that need to be handled together
        complex_field_groups = {
            'birth_place': ['birth_place_city_name', 'birth_place_country_code', 'birth_place_postal_code'],
            'citizenship': ['citizenship_code', 'citizenship_short_name', 'citizenship_long_name'],
            'legal_name': ['legal_name_given', 'legal_name_family_1', 'legal_name_family_2', 'legal_name_middle', 'legal_name_salutation'],
            'marital_status': ['marital_status_effective_date', 'marital_status_code'],
            'legal_address': ['legal_address_country_code', 'legal_address_postal_code', 'legal_address_line_five', 'legal_address_building_number', 'legal_address_building_extension', 'legal_address_street_name', 'legal_address_subdivision_1', 'legal_address_subdivision_2_code', 'legal_address_subdivision_2_name'],
            'personal_address': ['personal_address_country_code', 'personal_address_city_name', 'personal_address_postal_code', 'personal_address_line_five', 'personal_address_building_number', 'personal_address_building_extension', 'personal_address_street_name', 'personal_address_subdivision_2_code', 'personal_address_subdivision_2_name']
        }

        complex_update_functions = {
            'birth_place': self.update_functions._update_birth_place,
            'citizenship': self.update_functions._update_citizenship,
            'legal_name': self.update_functions._update_legal_name,
            'marital_status': self.update_functions._update_marital_status,
            'legal_address': self.update_functions._update_legal_address,
            'personal_address': self.update_functions._update_personal_address
        }

        results = {}
        processed_complex_fields = set()

        for field_name, value in validated_dict.items():
            # Check if this field is part of a complex group
            complex_group = None
            for group_name, group_fields in complex_field_groups.items():
                if field_name in group_fields:
                    complex_group = group_name
                    break

            if complex_group and complex_group not in processed_complex_fields:
                # Process all fields in this complex group together
                group_data = {}
                for group_field in complex_field_groups[complex_group]:
                    if group_field in validated_dict:
                        group_data[group_field] = validated_dict[group_field]

                if group_data:  # Only process if we have data for this group
                    try:
                        result = complex_update_functions[complex_group](associate_oid, group_data, role_code)
                        results[complex_group] = result
                        processed_complex_fields.add(complex_group)
                    except Exception as e:
                        results[complex_group] = {
                            'status': 'error',
                            'error': str(e)
                        }
                        processed_complex_fields.add(complex_group)

            elif field_name in update_functions and field_name not in processed_complex_fields:
                # Process simple fields
                try:
                    result = update_functions[field_name](associate_oid, value, role_code)
                    results[field_name] = result
                except Exception as e:
                    results[field_name] = {
                        'status': 'error',
                        'error': str(e)
                    }

        return results
