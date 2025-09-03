from typing import Dict, Optional, Union, Literal, List, Any, get_args
import pandas as pd
from pydantic import BaseModel
import requests
from .schemas.work_assignment import WorkerWorkAssignmentModifyRequest, WorkAssignmentTerminateRequest
from brynq_sdk_functions import Functions
import json
from typing import Any, Callable, Dict, Tuple, List

class WorkAssignment:
    """
    Handles worker work assignment modification operations in ADP
    """

    def __init__(self, decidium):
        self.decidium = decidium
        self.base_uri = "events/hr/v1/worker.work-assignment.modify"
    def __normalize_work_assignment_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat work assignment data dictionary to nested ADP work assignment modify request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing work assignment modification data

        Returns:
            Dict[str, Any]: Nested structure ready for ADP work assignment modify API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        try:
            # Build event context
            event_context = {
                "associateOID": flat_data.get("associate_oid")
            }

            # Add optional event context fields
            if flat_data.get("work_assignment_id"):
                event_context["workAssignmentID"] = flat_data["work_assignment_id"]

            if flat_data.get("worker_id"):
                event_context["workerID"] = {
                    "idValue": flat_data["worker_id"]
                }

            # Build work assignment structure
            work_assignment = {}

            # Add effective date time if provided (this will be used in both transform and workAssignment level)
            effective_date_time = flat_data.get("effective_date_time")
            if effective_date_time:
                work_assignment["effectiveDateTime"] = effective_date_time

            # Add job code if provided
            if flat_data.get("job_code"):
                work_assignment["jobCode"] = {
                    "codeValue": flat_data["job_code"]
                }

            # Add work arrangement code if provided
            if flat_data.get("work_arrangement_code"):
                work_assignment["workArrangementCode"] = {
                    "codeValue": flat_data["work_arrangement_code"]
                }

            # Add assigned work locations if provided
            if flat_data.get("assigned_work_locations"):
                work_assignment["assignedWorkLocations"] = []
                for location in flat_data["assigned_work_locations"]:
                    work_location = {
                        "nameCode": {
                            "codeValue": location.get("code_value")
                        }
                    }
                    if location.get("item_id"):
                        work_location["itemID"] = location["item_id"]
                    work_assignment["assignedWorkLocations"].append(work_location)

            # Add worker type code if provided
            if flat_data.get("worker_type_code"):
                work_assignment["workerTypeCode"] = {
                    "codeValue": flat_data["worker_type_code"]
                }

            # Add legal entity ID if provided
            if flat_data.get("legal_entity_id"):
                work_assignment["legalEntityID"] = flat_data["legal_entity_id"]

            # Add worker groups if provided
            if flat_data.get("worker_groups"):
                work_assignment["workerGroups"] = []
                for group in flat_data["worker_groups"]:
                    work_assignment["workerGroups"].append({
                        "groupCode": {
                            "codeValue": group.get("code_value")
                        }
                    })

            # Add assignment cost centers if provided
            if flat_data.get("assignment_cost_centers"):
                work_assignment["assignmentCostCenters"] = []
                for cost_center in flat_data["assignment_cost_centers"]:
                    work_assignment["assignmentCostCenters"].append({
                        "costCenterID": cost_center.get("cost_center_id"),
                        "costCenterPercentage": cost_center.get("cost_center_percentage")
                    })

            # Add base remuneration if provided - ENHANCED with all amount fields
            base_remuneration = {}

            # Recording basis code (inside baseRemuneration)
            if flat_data.get("recording_basis_code"):
                base_remuneration["recordingBasisCode"] = {
                    "codeValue": flat_data["recording_basis_code"]
                }

            # Monthly rate amount
            if flat_data.get("monthly_rate_amount"):
                monthly_rate = {"amountValue": flat_data["monthly_rate_amount"]}
                if flat_data.get("monthly_rate_currency"):
                    monthly_rate["currencyCode"] = flat_data["monthly_rate_currency"]
                base_remuneration["monthlyRateAmount"] = monthly_rate

            # Annual rate amount
            if flat_data.get("annual_rate_amount"):
                annual_rate = {"amountValue": flat_data["annual_rate_amount"]}
                if flat_data.get("annual_rate_currency"):
                    annual_rate["currencyCode"] = flat_data["annual_rate_currency"]
                base_remuneration["annualRateAmount"] = annual_rate

            # Pay period rate amount
            if flat_data.get("pay_period_rate_amount"):
                pay_period_rate = {"amountValue": flat_data["pay_period_rate_amount"]}
                if flat_data.get("pay_period_currency"):
                    pay_period_rate["currencyCode"] = flat_data["pay_period_currency"]
                base_remuneration["payPeriodRateAmount"] = pay_period_rate

            # Add baseRemuneration to work assignment if any fields exist
            if base_remuneration:
                work_assignment["baseRemuneration"] = base_remuneration

            # Add remunerationBasisCode at top level (matches get method path)
            if flat_data.get("remuneration_basis_code"):
                work_assignment["remunerationBasisCode"] = {
                    "codeValue": flat_data["remuneration_basis_code"]
                }

            # Build custom field group
            custom_field_group = {}

            # Add code fields if provided
            if flat_data.get("custom_code_fields"):
                custom_field_group["codeFields"] = []
                for field in flat_data["custom_code_fields"]:
                    code_field = {
                        "itemID": field.get("item_id"),
                        "codeValue": field.get("code_value")
                    }
                    if field.get("short_name"):
                        code_field["shortName"] = field["short_name"]
                    if field.get("long_name"):
                        code_field["longName"] = field["long_name"]
                    custom_field_group["codeFields"].append(code_field)

            # Add professional category to code fields if provided
            if flat_data.get("professional_category_code"):
                if "codeFields" not in custom_field_group:
                    custom_field_group["codeFields"] = []

                professional_category_field = {
                    "itemID": "professionalCategory",
                    "codeValue": str(flat_data["professional_category_code"])
                }
                if flat_data.get("professional_category_name"):
                    professional_category_field["longName"] = str(flat_data["professional_category_name"])

                custom_field_group["codeFields"].append(professional_category_field)

            # Add string fields if provided
            if flat_data.get("custom_string_fields"):
                custom_field_group["stringFields"] = []
                for field in flat_data["custom_string_fields"]:
                    custom_field_group["stringFields"].append({
                        "itemID": field.get("item_id"),
                        "stringValue": field.get("string_value")
                    })

            # Add date fields if provided
            if flat_data.get("custom_date_fields"):
                custom_field_group["dateFields"] = []
                for field in flat_data["custom_date_fields"]:
                    custom_field_group["dateFields"].append({
                        "itemID": field.get("item_id"),
                        "dateValue": field.get("date_value")
                    })

            # Add number fields if provided
            if flat_data.get("custom_number_fields"):
                custom_field_group["numberFields"] = []
                for field in flat_data["custom_number_fields"]:
                    custom_field_group["numberFields"].append({
                        "itemID": field.get("item_id"),
                        "numberValue": field.get("number_value")
                    })

            # Add indicator fields if provided
            if flat_data.get("custom_indicator_fields"):
                custom_field_group["indicatorFields"] = []
                for field in flat_data["custom_indicator_fields"]:
                    custom_field_group["indicatorFields"].append({
                        "itemID": field.get("item_id"),
                        "indicatorValue": field.get("indicator_value")
                    })

            # Add amount fields if provided (for internship compensation etc.)
            if flat_data.get("custom_amount_fields"):
                custom_field_group["amountFields"] = []
                for field in flat_data["custom_amount_fields"]:
                    amount_field = {
                        "itemID": field.get("item_id"),
                        "amountValue": field.get("amount_value")
                    }
                    if field.get("currency_code"):
                        amount_field["currencyCode"] = field["currency_code"]
                    custom_field_group["amountFields"].append(amount_field)

            # Handle direct internship compensation fields
            if flat_data.get("internship_compensation"):
                if "amountFields" not in custom_field_group:
                    custom_field_group["amountFields"] = []

                internship_field = {
                    "itemID": "internshipCompensation",
                    "amountValue": flat_data["internship_compensation"]
                }
                if flat_data.get("internship_currency"):
                    internship_field["currencyCode"] = flat_data["internship_currency"]

                custom_field_group["amountFields"].append(internship_field)

            # Add custom field group to work assignment
            if custom_field_group:
                work_assignment["customFieldGroup"] = custom_field_group

            # Build the complete request structure
            nested_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": event_context,
                            "transform": {
                                "effectiveDateTime": effective_date_time,
                                "workAssignment": work_assignment
                            }
                        }
                    }
                ]
            }

            return nested_data

        except Exception as e:
            raise ValueError(f"Work assignment data normalization failed: {str(e)}")

    def update(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Modifies a worker's work assignment in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing work assignment modification data
            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the work assignment modification operation fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/{self.base_uri}"

        # Prepare request headers
        headers = self.decidium.session.headers.copy()
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat work assignment data to nested structure
            request_data = self.__normalize_work_assignment_data(data)

            # Validate request data with pydantic schema
            try:
                valid_data = WorkerWorkAssignmentModifyRequest(**request_data)
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
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in work assignment modification operation: {e}")

    def terminate(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Terminates a worker's work assignment in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing work assignment termination data with keys:
                - associate_oid: Worker's Associate OID (required)
                - termination_date: Termination date (YYYY-MM-DD format) (required)
                - termination_reason_code: Termination reason code (e.g., "MU") (required)
                - termination_reason_short_name: Termination reason short name (optional)

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the work assignment termination operation fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/events/hr/v1/worker.work-assignment.terminate"

        # Prepare request headers
        headers = self.decidium.session.headers.copy()
        headers.update({
            "roleCode": role_code
        })

        try:
            # Build the request data structure
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": data.get("associate_oid")
                                }
                            },
                            "transform": {
                                "worker": {
                                    "workAssignment": {
                                        "terminationDate": data.get("termination_date"),
                                        "terminationReasonCode": {
                                            "codeValue": data.get("termination_reason_code"),
                                            "shortName": data.get("termination_reason_short_name", data.get("termination_reason_code"))
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            # Validate request data with pydantic schema
            try:
                valid_data = WorkAssignmentTerminateRequest(**request_data)
                request_body = valid_data.model_dump(by_alias=True, exclude_none=True)
            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            response = self.decidium._post(url=url, request_body=request_body, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to terminate work assignment: {str(e)}")
