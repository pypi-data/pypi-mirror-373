from typing import Dict, Optional, List, Any, Literal, Tuple
import pandas as pd
import requests
from pydantic import BaseModel

from .schemas.pay_distributions import PayDistributionChangeRequest, PayDistributionGet
from brynq_sdk_functions import Functions
import json


class PayDistributions:
    """
    Handles pay distribution operations in ADP
    """

    def __init__(self, decidium):
        self.decidium = decidium
        self.base_uri = "events/payroll/v1/worker.pay-distribution.change"
        self.read_base_uri = "payroll/v2/workers"

    def __normalize_pay_distribution_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat pay distribution data dictionary to nested ADP pay distribution change request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing pay distribution data with keys:
                - associate_oid: Worker's Associate OID (required)
                - distribution_instructions: List of distribution instructions (required)
                    Each instruction should contain:
                    - precedence_code: Precedence code (e.g., "primary", "secondary", "expenses")
                    - precedence_short_name: Short name for precedence
                    - precedence_long_name: Long name for precedence
                    - payment_method_code: Payment method code (e.g., "V" for wire transfer)
                    - payment_method_short_name: Short name for payment method
                    - payment_method_long_name: Long name for payment method
                    - item_id: Item ID (required)
                    - iban: IBAN number (required)
                    - account_name: Account name (required)
                    - swift_code: SWIFT code (required)

        Returns:
            Dict[str, Any]: Nested structure ready for ADP pay distribution change API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Check required fields
        required_fields = ['associate_oid', 'distribution_instructions']
        missing_fields = [field for field in required_fields if field not in flat_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build event context
            event_context = {
                "worker": {
                    "associateOID": flat_data["associate_oid"]
                }
            }

            # Build distribution instructions
            distribution_instructions = []

            for instruction in flat_data["distribution_instructions"]:
                # Build precedence code
                precedence_code = {
                    "codeValue": instruction["precedence_code"]
                }
                if instruction.get("precedence_short_name"):
                    precedence_code["shortName"] = instruction["precedence_short_name"]
                if instruction.get("precedence_long_name"):
                    precedence_code["longName"] = instruction["precedence_long_name"]

                # Build payment method code
                payment_method_code = {
                    "codeValue": instruction["payment_method_code"]
                }
                if instruction.get("payment_method_short_name"):
                    payment_method_code["shortName"] = instruction["payment_method_short_name"]
                if instruction.get("payment_method_long_name"):
                    payment_method_code["longName"] = instruction["payment_method_long_name"]

                # Build deposit account
                deposit_account = {
                    "IBAN": instruction["iban"],
                    "financialAccount": {
                        "accountName": instruction["account_name"]
                    },
                    "financialParty": {
                        "SWIFTCode": instruction["swift_code"]
                    }
                }

                # Build distribution instruction
                distribution_instruction = {
                    "precedenceCode": precedence_code,
                    "paymentMethodCode": payment_method_code,
                    "itemID": instruction["item_id"],
                    "depositAccount": deposit_account
                }

                distribution_instructions.append(distribution_instruction)

            # Build pay distribution
            pay_distribution = {
                "recordType": flat_data.get("record_type", "1"),
                "distributionInstructions": distribution_instructions
            }

            # Build transform
            transform = {
                "payDistribution": pay_distribution
            }

            # Build data
            data = {
                "eventContext": event_context,
                "transform": transform
            }

            # Build the complete request structure
            nested_data = {
                "events": [
                    {
                        "data": data
                    }
                ]
            }

            return nested_data

        except Exception as e:
            raise ValueError(f"Pay distribution data normalization failed: {str(e)}")

    def update(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Changes a worker's pay distribution in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing pay distribution data with keys:
                - associate_oid: Worker's Associate OID (required)
                - distribution_instructions: List of distribution instructions (required)
                    Each instruction should contain:
                    - precedence_code: Precedence code (e.g., "primary", "secondary", "expenses")
                    - precedence_short_name: Short name for precedence (optional)
                    - precedence_long_name: Long name for precedence (optional)
                    - payment_method_code: Payment method code (e.g., "V" for wire transfer)
                    - payment_method_short_name: Short name for payment method (optional)
                    - payment_method_long_name: Long name for payment method (optional)
                    - item_id: Item ID (required)
                    - iban: IBAN number (required)
                    - account_name: Account name (required)
                    - swift_code: SWIFT code (required)

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the pay distribution change operation fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/{self.base_uri}"

        # Prepare request headers
        headers = self.decidium.session.headers.copy()
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat data to nested structure
            request_data = self.__normalize_pay_distribution_data(data)

            # Validate request data with pydantic schema
            try:
                valid_data = PayDistributionChangeRequest(**request_data)
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
            raise Exception(f"An error occurred in pay distribution change operation: {e}")

    def __normalize_pay_distribution_get_data(self, response_data: Dict[str, Any], associate_oid: str) -> pd.DataFrame:
        """
        Normalizes ADP pay distribution GET response to flattened DataFrame.
        Creates one row per distributionInstruction.

        Args:
            response_data: Raw response from ADP API
            associate_oid: The associate OID for context

        Returns:
            pd.DataFrame: Flattened DataFrame with one row per instruction
        """
        pay_distributions = response_data.get("payDistributions", []) if isinstance(response_data, dict) else []

        rows: List[Dict[str, Any]] = []

        for pay_distribution in pay_distributions:
            pay_distribution_item_id = pay_distribution.get("itemID")
            instructions = pay_distribution.get("distributionInstructions", []) or []

            for instr in instructions:
                row: Dict[str, Any] = {
                    "associateOID": associate_oid,
                    "payDistributions.itemID": pay_distribution_item_id,
                    "payDistributions.recordType": pay_distribution.get("recordType"),
                    "distributionInstructions.itemID": instr.get("itemID"),
                    # Payment method
                    "distributionInstructions.paymentMethodCode.codeValue": (instr.get("paymentMethodCode") or {}).get("codeValue"),
                    "distributionInstructions.paymentMethodCode.shortName": (instr.get("paymentMethodCode") or {}).get("shortName"),
                    "distributionInstructions.paymentMethodCode.longName": (instr.get("paymentMethodCode") or {}).get("longName"),
                    # Deposit account
                    "distributionInstructions.depositAccount.IBAN": (instr.get("depositAccount") or {}).get("IBAN"),
                    "distributionInstructions.depositAccount.financialAccount.accountName": ((instr.get("depositAccount") or {}).get("financialAccount") or {}).get("accountName"),
                    "distributionInstructions.depositAccount.financialParty.SWIFTCode": ((instr.get("depositAccount") or {}).get("financialParty") or {}).get("SWIFTCode"),
                    "distributionInstructions.depositAccount.financialParty.nameCode.shortName": (((instr.get("depositAccount") or {}).get("financialParty") or {}).get("nameCode") or {}).get("shortName"),
                    # Precedence
                    "distributionInstructions.precedenceCode.codeValue": (instr.get("precedenceCode") or {}).get("codeValue"),
                    "distributionInstructions.precedenceCode.shortName": (instr.get("precedenceCode") or {}).get("shortName"),
                    "distributionInstructions.precedenceCode.longName": (instr.get("precedenceCode") or {}).get("longName"),
                }
                rows.append(row)

        return pd.DataFrame(rows)

    def get_by_employee_id(self, associate_oid: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieves all pay distributions for a given employee (associate OID) and returns
        a flattened DataFrame validated against PayDistributionGet schema.

        Notes:
        - Although ADP documents two URIs, only `payroll/v2/workers/{aoid}/pay-distributions/1`
          returns a success response for this tenant configuration.
        - No OData parameters are supported.

        Args:
            associate_oid: The associate OID of the worker

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df)
        """
        if not associate_oid:
            raise ValueError("associate_oid is required")

        # Build endpoint according to the note provided
        endpoint = f"/payroll/v2/workers/{associate_oid}/pay-distributions/1"

        # Call ADP API
        response_data = self.decidium._get(endpoint=endpoint)

        # Normalize to flattened rows: one row per distributionInstruction
        try:
            df = self.__normalize_pay_distribution_get_data(response_data, associate_oid)

            # Validate using BrynQ validation helper and Pandera schema
            valid_df, invalid_df = Functions.validate_data(df, PayDistributionGet)
            return valid_df, invalid_df

        except Exception as e:
            raise ValueError(f"Failed to normalize/validate pay distributions: {str(e)}")
