import pandas as pd
import json
from typing import Optional, Dict, Any, List, Literal
from urllib.parse import urlencode
import requests
from .schemas.payroll import PayDataInputAddRequest
from brynq_sdk_functions import Functions


class Payroll:
    """
    ADP Payroll class for managing payroll output operations.
    """

    def __init__(self, decidium):
        """
        Initialize the Payroll class.

        Args:
            decidium: The main Decidium instance
        """
        self.decidium = decidium

    def __normalize_add_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat pay data input dictionary to nested ADP pay data input add request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing pay data input with keys:
                - associate_oid: Worker's Associate OID (required)
                - pay_period_start_date: Pay period start date (required)
                - pay_inputs: List of pay inputs (required)
                    Each pay input should contain:
                    - input_type: Type of input ("earning", "calculation_factor", "time")
                    - earning_code: Earning code (for earning inputs)
                    - number_of_hours: Number of hours (for earning inputs)
                    - earned_pay_period_start_date: Earned pay period start date (for earning inputs)
                    - calculation_factor_code: Calculation factor code (for calculation factor inputs)
                    - calculation_factor_rate_value: Calculation factor rate value (for calculation factor inputs)
                    - configuration_tag_code: Configuration tag code (for calculation factor inputs)
                    - validity_period_start_date: Validity period start date (for calculation factor inputs)
                    - time_evaluation_start_date: Time evaluation start date (for time inputs)
                    - time_evaluation_end_date: Time evaluation end date (for time inputs)
                    - segment_classification_code: Segment classification code (for time inputs)
                    - segment_quantity_value: Segment quantity value (for time inputs)

        Returns:
            Dict[str, Any]: Nested structure ready for ADP pay data input add API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Check required fields
        required_fields = ['associate_oid', 'pay_period_start_date', 'pay_inputs']
        missing_fields = [field for field in required_fields if field not in flat_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build payee pay input structure
            payee_pay_input = {
                "associateOID": str(flat_data["associate_oid"]),
                "payPeriodStartDate": str(flat_data["pay_period_start_date"]),
                "payrollProfilePayInputs": [{
                    "payInputs": [],
                    "timeInputs": []
                }]
            }

            # Process each pay input
            for pay_input in flat_data["pay_inputs"]:
                input_type = pay_input.get("input_type")

                if input_type == 'earning':
                    # Create earning input
                    earning_input = {
                        "earningCode": {"codeValue": str(pay_input["earning_code"])}
                    }

                    # Add optional fields
                    if pay_input.get('number_of_hours'):
                        earning_input["numberOfHours"] = float(pay_input['number_of_hours'])

                    if pay_input.get('rate_value') or pay_input.get('base_multiplier_value'):
                        earning_input["rate"] = {}
                        if pay_input.get('rate_value'):
                            earning_input["rate"]["rateValue"] = float(pay_input['rate_value'])
                        if pay_input.get('base_multiplier_value'):
                            earning_input["rate"]["baseMultiplierValue"] = float(pay_input['base_multiplier_value'])

                    if pay_input.get('pay_allocation_id'):
                        earning_input["payAllocation"] = {"allocationID": str(pay_input['pay_allocation_id'])}

                    if pay_input.get('earned_pay_period_start_date'):
                        earning_input["earnedPayPeriodStartDate"] = str(pay_input['earned_pay_period_start_date'])

                    payee_pay_input["payrollProfilePayInputs"][0]["payInputs"].append(earning_input)

                elif input_type == 'calculation_factor':
                    # Create calculation factor input
                    calc_factor_input = {
                        "calculationFactorCode": {"codeValue": str(pay_input["calculation_factor_code"])},
                        "calculationFactorRate": {
                            "baseUnitCode": {"codeValue": str(pay_input["calculation_factor_rate_value"])}
                        }
                    }

                    # Add optional fields
                    if pay_input.get('configuration_tag_code'):
                        calc_factor_input["configurationTags"] = [{"tagCode": str(pay_input['configuration_tag_code'])}]

                    if pay_input.get('validity_period_start_date'):
                        calc_factor_input["validityPeriod"] = {"startDateTime": str(pay_input['validity_period_start_date'])}

                    payee_pay_input["payrollProfilePayInputs"][0]["payInputs"].append(calc_factor_input)

                elif input_type == 'time':
                    # Create time input
                    time_input = {
                        "timeEvaluationPeriod": {
                            "startDate": str(pay_input['time_evaluation_start_date']),
                            "endDate": str(pay_input['time_evaluation_end_date'])
                        }
                    }

                    # Add time segments if classification code exists
                    if pay_input.get('segment_classification_code'):
                        time_segment = {
                            "segmentClassifications": [{
                                "classificationCode": {"codeValue": str(pay_input['segment_classification_code'])}
                            }]
                        }

                        # Add quantity if exists
                        if pay_input.get('segment_quantity_value'):
                            time_segment["segmentQuantity"] = {
                                "quantityValue": float(pay_input['segment_quantity_value']),
                                "unitCode": {"codeValue": "HOUR"}
                            }

                        time_input["timeSegments"] = [time_segment]

                    payee_pay_input["payrollProfilePayInputs"][0]["timeInputs"].append(time_input)

            # Create final request structure
            request_data = {
                "events": [{
                    "data": {
                        "transform": {
                            "payDataInput": {
                                "payeePayInputs": [payee_pay_input]
                            }
                        }
                    }
                }]
            }

            return request_data

        except Exception as e:
            raise ValueError(f"Pay data input normalization failed: {str(e)}")

    def create_input_data(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Add pay data input for a month using flat dictionary.

        Args:
            data (Dict[str, Any]): Flat dictionary containing pay data input information
            role_code (str): The role the user is playing during the transaction
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If validation or API request fails
        """

        # Normalize flat data to nested structure
        try:
            request_data = self.__normalize_add_data(data)
        except Exception as normalization_error:
            raise ValueError(f"Data normalization error: {str(normalization_error)}")

        # Validate input data with pydantic schema
        try:
            valid_data = PayDataInputAddRequest(**request_data)
            request_body = valid_data.model_dump(by_alias=True, exclude_none=True)
        except Exception as validation_error:
            raise ValueError(f"Request validation error: {str(validation_error)}")

        endpoint = f"{self.decidium.base_url}/events/payroll/v1/pay-data-input.add"
        headers={}
        headers["roleCode"] = role_code

        try:
            response = self.decidium._post(
                url=endpoint,
                request_body=request_body,
                headers=headers,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            raise ValueError(f"Failed to add pay data input: {str(e)}")
