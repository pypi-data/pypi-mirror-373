from typing import Dict, Optional, List, Any, Tuple, Literal
import pandas as pd
import requests
from pydantic import BaseModel

from .schemas.dependents import DependentGet, DependentAddRequest, DependentChangeRequest, DependentRemoveRequest
from brynq_sdk_functions import Functions
import json

class Dependents:
    """
    Handles ADP Dependents API operations
    """

    def __init__(self, decidium):
        self.decidium = decidium
        self.base_uri = "hr/v1/associates"

    def get_by_employee_id(self, associate_oid: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retrieves all dependents for a given employee (associate OID) and returns
        a flattened DataFrame validated against DependentGet schema.

        Args:
            associate_oid: The associate OID of the worker

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (valid_df, invalid_df)
        """
        if not associate_oid:
            raise ValueError("associate_oid is required")

        # Build endpoint
        endpoint = f"/{self.base_uri}/{associate_oid}/dependents"

        try:
            # Make API call
            response = self.decidium._get(endpoint)
            # Parse response
            dependents_data = response.get("dependents", [])

            if not dependents_data:
                # Return empty DataFrames if no dependents
                empty_df = pd.DataFrame(columns=DependentGet.get_schema_columns())
                return empty_df, empty_df

            # Normalize data
            normalized_df = self.__normalize_dependent_get_data(dependents_data)

            # Validate data
            valid_df, invalid_df = Functions.validate_data(normalized_df, DependentGet)

            return valid_df, invalid_df

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve dependents for associate {associate_oid}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing dependents data for associate {associate_oid}: {str(e)}")

    def __normalize_dependent_get_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """
        Normalizes ADP Dependents API response to flattened DataFrame.

        Args:
            raw_data: Raw dependents data from API response

        Returns:
            pd.DataFrame: Flattened DataFrame with dependent information
        """
        if not raw_data:
            return pd.DataFrame()

        # Convert to DataFrame using json_normalize
        df = pd.json_normalize(raw_data, sep=".")

        if df.empty:
            return df

        # Create result DataFrame with all required columns
        result_df = pd.DataFrame(columns=[
            "associateOID",
            "itemID",
            "effectiveDate",
            "relationshipTypeCode.codeValue",
            "relationshipTypeCode.shortName",
            "relationshipTypeCode.longName",
            "person.legalName.givenName",
            "person.legalName.familyName1",
            "person.legalName.familyName2",
            "person.birthDate",
            "person.genderCode.codeValue",
            "person.genderCode.shortName",
            "person.genderCode.longName",
            "person.birthOrder",
            "person.disabledIndicator",
            "person.taxDependentIndicator",
            "person.maritalStatusCode.codeValue",
            "person.maritalStatusCode.shortName",
            "person.maritalStatusCode.longName",
            "person.communication.faxes.formattedNumber",
            "person.communication.faxes.itemID",
            "person.communication.landlines.formattedNumber",
            "person.communication.landlines.itemID",
            "person.legalAddress.countryCode",
            "person.legalAddress.cityName",
            "person.legalAddress.postalCode",
            "person.legalAddress.lineFive",
            "person.legalAddress.buildingNumber",
            "person.legalAddress.buildingNumberExtension",
            "person.legalAddress.streetName",
            "person.legalAddress.countrySubdivisionLevel2.codeValue",
            "person.legalAddress.countrySubdivisionLevel2.longName",
            "person.socialInsurancePrograms.healthInsurance.coveredIndicator",
            "person.legalName.preferredSalutations.salutationCode.codeValue",
            "person.legalName.preferredSalutations.salutationCode.shortName",
            "person.legalName.preferredSalutations.salutationCode.longName",
            "person.legalName.preferredSalutations.sequenceNumber"
        ])

        # Copy over simple columns that exist in both
        for col in result_df.columns:
            if col in df.columns:
                result_df[col] = df[col]

        # Handle array extractions
        # Communication arrays
        if "person.communication.faxes" in df.columns:
            result_df["person.communication.faxes.formattedNumber"] = df["person.communication.faxes"].apply(
                lambda x: self.__first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
            result_df["person.communication.faxes.itemID"] = df["person.communication.faxes"].apply(
                lambda x: self.__first(x, "itemID") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.communication.faxes.formattedNumber"] = pd.NA
            result_df["person.communication.faxes.itemID"] = pd.NA

        if "person.communication.landlines" in df.columns:
            result_df["person.communication.landlines.formattedNumber"] = df["person.communication.landlines"].apply(
                lambda x: self.__first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
            result_df["person.communication.landlines.itemID"] = df["person.communication.landlines"].apply(
                lambda x: self.__first(x, "itemID") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.communication.landlines.formattedNumber"] = pd.NA
            result_df["person.communication.landlines.itemID"] = pd.NA

        # Social insurance programs
        if "person.socialInsurancePrograms" in df.columns:
            result_df["person.socialInsurancePrograms.healthInsurance.coveredIndicator"] = df["person.socialInsurancePrograms"].apply(
                lambda x: self.__extract_social_insurance(x, "healthInsurance", "coveredIndicator") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.socialInsurancePrograms.healthInsurance.coveredIndicator"] = pd.NA

        # Preferred salutations
        if "person.legalName.preferredSalutations" in df.columns:
            result_df["person.legalName.preferredSalutations.salutationCode.codeValue"] = df["person.legalName.preferredSalutations"].apply(
                lambda x: self.__first(x, None, {}).get("salutationCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )
            result_df["person.legalName.preferredSalutations.salutationCode.shortName"] = df["person.legalName.preferredSalutations"].apply(
                lambda x: self.__first(x, None, {}).get("salutationCode", {}).get("shortName", pd.NA) if isinstance(x, list) else pd.NA
            )
            result_df["person.legalName.preferredSalutations.salutationCode.longName"] = df["person.legalName.preferredSalutations"].apply(
                lambda x: self.__first(x, None, {}).get("salutationCode", {}).get("longName", pd.NA) if isinstance(x, list) else pd.NA
            )
            result_df["person.legalName.preferredSalutations.sequenceNumber"] = df["person.legalName.preferredSalutations"].apply(
                lambda x: self.__first(x, "sequenceNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.legalName.preferredSalutations.salutationCode.codeValue"] = pd.NA
            result_df["person.legalName.preferredSalutations.salutationCode.shortName"] = pd.NA
            result_df["person.legalName.preferredSalutations.salutationCode.longName"] = pd.NA
            result_df["person.legalName.preferredSalutations.sequenceNumber"] = pd.NA

        return result_df

    @staticmethod
    def __first(lst, key=None, default=pd.NA):
        """Extract first element from list, optionally by key"""
        if isinstance(lst, list) and lst:
            return lst[0] if key is None else lst[0].get(key, default)
        return default

    @staticmethod
    def __extract_social_insurance(lst, program_id, field_name):
        """Extract value from social insurance programs by itemID"""
        if not isinstance(lst, list):
            return pd.NA
        for program in lst:
            if isinstance(program, dict) and program.get("itemID") == program_id:
                return program.get(field_name, pd.NA)
        return pd.NA

    def create(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Creates a dependent for a worker in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing dependent data with required fields:
                - associate_oid: Worker's Associate OID (required)
                - relationship_type_code: Relationship type code (required, e.g., "E" for child)
                - given_name: Given name (required)
                - family_name_1: Family name 1 (required)
                - birth_date: Birth date in YYYY-MM-DD format (required)
                - gender_code: Gender code (required, e.g., "M" or "F")
                - city_name: City name (required)
                - postal_code: Postal code (required)
                - country_code: Country code (required, e.g., "FR")

                Optional fields:
                - family_name_2: Family name 2
                - marital_status_code: Marital status code (e.g., "A")
                - deceased_indicator: Deceased indicator (boolean)
                - tax_dependent_indicator: Tax dependent indicator (boolean)
                - disabled_indicator: Disabled indicator (boolean)
                - birth_order: Birth order (integer)
                - line_five: Address line five
                - building_number: Building number
                - building_number_extension: Building number extension
                - street_name: Street name
                - subdivision_2_code: Country subdivision level 2 code
                - subdivision_2_name: Country subdivision level 2 name
                - salutation_code: Salutation code (e.g., "M")
                - salutation_sequence: Salutation sequence number (default: 0)
                - health_insurance_covered: Health insurance covered indicator (boolean)
                - fax_numbers: List of fax numbers with format [{"itemID": "Personal", "formattedNumber": "0801020304"}]
                - landline_numbers: List of landline numbers with format [{"itemID": "Personal", "formattedNumber": "0601020304"}]

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the dependent creation fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/events/hr/v1/dependent.add"

        # Prepare request headers
        headers = {}
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat data to nested structure
            request_data = self.__normalize_dependent_create_data(data)

            # Validate request data with pydantic schema
            try:
                valid_data = DependentAddRequest(**request_data)
                # Use validated data for the request (with proper aliases)
                request_data = valid_data.model_dump(by_alias=True, exclude_none=True)

            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            # Make POST request
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in dependent creation: {e}")

    def __normalize_dependent_create_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat dependent data dictionary to nested ADP dependent add request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing dependent data

        Returns:
            Dict[str, Any]: Nested structure ready for ADP dependent add API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Check required fields
        required_fields = [
            'associate_oid', 'relationship_type_code', 'given_name', 'family_name_1',
            'birth_date', 'gender_code', 'city_name', 'postal_code', 'country_code'
        ]
        missing_fields = [field for field in required_fields if field not in flat_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build legal name structure
            legal_name = {
                "givenName": str(flat_data["given_name"]),
                "familyName1": str(flat_data["family_name_1"])
            }

            if flat_data.get("family_name_2"):
                legal_name["familyName2"] = str(flat_data["family_name_2"])

            # Add preferred salutations if provided
            if flat_data.get("salutation_code"):
                legal_name["preferredSalutations"] = [{
                    "sequenceNumber": flat_data.get("salutation_sequence", 0),
                    "salutationCode": {
                        "codeValue": str(flat_data["salutation_code"])
                    }
                }]

            # Build person structure
            person = {
                "legalName": legal_name,
                "birthDate": str(flat_data["birth_date"]),
                "genderCode": {
                    "codeValue": str(flat_data["gender_code"])
                }
            }

            # Add optional person fields
            if flat_data.get("marital_status_code"):
                person["maritalStatusCode"] = {
                    "codeValue": str(flat_data["marital_status_code"])
                }

            if flat_data.get("deceased_indicator") is not None:
                person["deceasedIndicator"] = bool(flat_data["deceased_indicator"])

            if flat_data.get("tax_dependent_indicator") is not None:
                person["taxDependentIndicator"] = bool(flat_data["tax_dependent_indicator"])

            if flat_data.get("disabled_indicator") is not None:
                person["disabledIndicator"] = bool(flat_data["disabled_indicator"])

            if flat_data.get("birth_order") is not None:
                person["birthOrder"] = int(flat_data["birth_order"])

            # Build legal address if required fields are present
            legal_address = {
                "cityName": str(flat_data["city_name"]),
                "postalCode": str(flat_data["postal_code"]),
                "countryCode": str(flat_data["country_code"])
            }

            # Add optional address fields
            if flat_data.get("line_five"):
                legal_address["lineFive"] = str(flat_data["line_five"])

            if flat_data.get("building_number"):
                legal_address["buildingNumber"] = str(flat_data["building_number"])

            if flat_data.get("building_number_extension"):
                legal_address["buildingNumberExtension"] = str(flat_data["building_number_extension"])

            if flat_data.get("street_name"):
                legal_address["streetName"] = str(flat_data["street_name"])

            if flat_data.get("subdivision_2_code") and flat_data.get("subdivision_2_name"):
                legal_address["countrySubdivisionLevel2"] = {
                    "codeValue": str(flat_data["subdivision_2_code"]),
                    "longName": str(flat_data["subdivision_2_name"])
                }

            person["legalAddress"] = legal_address

            # Build communication structure if communication data is provided
            communication = {}

            if flat_data.get("fax_numbers"):
                communication["faxes"] = flat_data["fax_numbers"]

            if flat_data.get("landline_numbers"):
                communication["landlines"] = flat_data["landline_numbers"]

            if communication:
                person["communication"] = communication

            # Build social insurance programs if provided
            if flat_data.get("health_insurance_covered") is not None:
                person["socialInsurancePrograms"] = [{
                    "itemID": "healthInsurance",
                    "coveredIndicator": bool(flat_data["health_insurance_covered"])
                }]

            # Build dependent structure
            dependent = {
                "relationshipTypeCode": {
                    "codeValue": str(flat_data["relationship_type_code"])
                },
                "person": person
            }

            # Add effective date if provided
            if flat_data.get("effective_date"):
                dependent["effectiveDate"] = str(flat_data["effective_date"])

            # Create final request structure
            request_data = {
                "events": [{
                    "data": {
                        "eventContext": {
                            "worker": {
                                "associateOID": str(flat_data["associate_oid"])
                            }
                        },
                        "transform": {
                            "dependent": dependent
                        }
                    }
                }]
            }

            return request_data

        except Exception as e:
            raise ValueError(f"Dependent data normalization failed: {str(e)}")

    def update(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Updates a dependent in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing dependent update data with required fields:
                - associate_oid: Worker's Associate OID (required)
                - dependent_item_id: Dependent's item ID (required)

                Optional fields for update:
                - given_name: Updated given name
                - family_name_1: Updated family name 1
                - family_name_2: Updated family name 2
                - relationship_type_code: Updated relationship type code
                - marital_status_code: Updated marital status code
                - birth_date: Updated birth date (YYYY-MM-DD)
                - deceased_indicator: Updated deceased indicator (boolean)
                - gender_code: Updated gender code
                - tax_dependent_indicator: Updated tax dependent indicator (boolean)
                - disabled_indicator: Updated disabled indicator (boolean)
                - birth_order: Updated birth order (integer)
                - salutation_code: Updated salutation code
                - salutation_sequence: Updated salutation sequence number
                - health_insurance_covered: Updated health insurance covered indicator (boolean)
                - city_name: Updated city name
                - postal_code: Updated postal code
                - country_code: Updated country code
                - line_five: Updated address line five
                - building_number: Updated building number
                - building_number_extension: Updated building number extension
                - street_name: Updated street name
                - subdivision_2_code: Updated country subdivision level 2 code
                - subdivision_2_name: Updated country subdivision level 2 name
                - fax_numbers: Updated fax numbers list
                - landline_numbers: Updated landline numbers list

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the dependent update fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/events/hr/v1/dependent.change"

        # Prepare request headers
        headers = {}
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat data to nested structure
            request_data = self.__normalize_dependent_update_data(data)

            # Validate request data with pydantic schema
            try:
                valid_data = DependentChangeRequest(**request_data)
                # Use validated data for the request (with proper aliases)
                request_data = valid_data.model_dump(by_alias=True, exclude_none=True)

            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            # Make POST request
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in dependent update: {e}")

    def __normalize_dependent_update_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat dependent update data dictionary to nested ADP dependent change request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing dependent update data

        Returns:
            Dict[str, Any]: Nested structure ready for ADP dependent change API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Check required fields
        required_fields = ['associate_oid', 'dependent_item_id']
        missing_fields = [field for field in required_fields if field not in flat_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build dependent update structure (only include fields that are being updated)
            dependent_update = {}

            # Add effective date if provided
            if flat_data.get("effective_date"):
                dependent_update["effectiveDate"] = str(flat_data["effective_date"])

            # Build person structure if any person fields are being updated
            person_update = {}

            # Legal name updates
            legal_name_update = {}
            if flat_data.get("given_name"):
                legal_name_update["givenName"] = str(flat_data["given_name"])
            if flat_data.get("family_name_1"):
                legal_name_update["familyName1"] = str(flat_data["family_name_1"])
            if flat_data.get("family_name_2"):
                legal_name_update["familyName2"] = str(flat_data["family_name_2"])

            # Add preferred salutations if provided
            if flat_data.get("salutation_code"):
                legal_name_update["preferredSalutations"] = [{
                    "sequenceNumber": flat_data.get("salutation_sequence", 0),
                    "salutationCode": {
                        "codeValue": str(flat_data["salutation_code"])
                    }
                }]

            if legal_name_update:
                person_update["legalName"] = legal_name_update

            # Other person fields
            if flat_data.get("marital_status_code"):
                person_update["maritalStatusCode"] = {
                    "codeValue": str(flat_data["marital_status_code"])
                }

            if flat_data.get("birth_date"):
                person_update["birthDate"] = str(flat_data["birth_date"])

            if flat_data.get("deceased_indicator") is not None:
                person_update["deceasedIndicator"] = bool(flat_data["deceased_indicator"])

            if flat_data.get("gender_code"):
                person_update["genderCode"] = {
                    "codeValue": str(flat_data["gender_code"])
                }

            if flat_data.get("tax_dependent_indicator") is not None:
                person_update["taxDependentIndicator"] = bool(flat_data["tax_dependent_indicator"])

            if flat_data.get("disabled_indicator") is not None:
                person_update["disabledIndicator"] = bool(flat_data["disabled_indicator"])

            if flat_data.get("birth_order") is not None:
                person_update["birthOrder"] = int(flat_data["birth_order"])

            # Legal address updates
            legal_address_update = {}
            if flat_data.get("city_name"):
                legal_address_update["cityName"] = str(flat_data["city_name"])
            if flat_data.get("postal_code"):
                legal_address_update["postalCode"] = str(flat_data["postal_code"])
            if flat_data.get("country_code"):
                legal_address_update["countryCode"] = str(flat_data["country_code"])
            if flat_data.get("line_five"):
                legal_address_update["lineFive"] = str(flat_data["line_five"])
            if flat_data.get("building_number"):
                legal_address_update["buildingNumber"] = str(flat_data["building_number"])
            if flat_data.get("building_number_extension"):
                legal_address_update["buildingNumberExtension"] = str(flat_data["building_number_extension"])
            if flat_data.get("street_name"):
                legal_address_update["streetName"] = str(flat_data["street_name"])
            if flat_data.get("subdivision_2_code") and flat_data.get("subdivision_2_name"):
                legal_address_update["countrySubdivisionLevel2"] = {
                    "codeValue": str(flat_data["subdivision_2_code"]),
                    "longName": str(flat_data["subdivision_2_name"])
                }

            if legal_address_update:
                person_update["legalAddress"] = legal_address_update

            # Communication updates
            communication_update = {}
            if flat_data.get("fax_numbers"):
                communication_update["faxes"] = flat_data["fax_numbers"]
            if flat_data.get("landline_numbers"):
                communication_update["landlines"] = flat_data["landline_numbers"]

            if communication_update:
                person_update["communication"] = communication_update

            # Social insurance programs updates
            if flat_data.get("health_insurance_covered") is not None:
                person_update["socialInsurancePrograms"] = [{
                    "itemID": "healthInsurance",
                    "coveredIndicator": bool(flat_data["health_insurance_covered"])
                }]

            if person_update:
                dependent_update["person"] = person_update

            # Relationship type code update
            if flat_data.get("relationship_type_code"):
                dependent_update["relationshipTypeCode"] = {
                    "codeValue": str(flat_data["relationship_type_code"])
                }

            # Create final request structure
            request_data = {
                "events": [{
                    "data": {
                        "eventContext": {
                            "worker": {
                                "associateOID": str(flat_data["associate_oid"])
                            },
                            "dependent": {
                                "itemID": str(flat_data["dependent_item_id"])
                            }
                        },
                        "transform": {
                            "dependent": dependent_update
                        }
                    }
                }]
            }

            return request_data

        except Exception as e:
            raise ValueError(f"Dependent update data normalization failed: {str(e)}")

    def delete(
        self,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> requests.Response:
        """
        Removes/deletes a dependent from a worker in ADP using flat dictionary data.

        Args:
            data (Dict[str, Any]): Flat dictionary containing dependent removal data with required fields:
                - associate_oid: Worker's Associate OID (required)
                - dependent_item_id: Dependent's item ID (required)

            role_code (str): The role the user is playing during the transaction (required)
                Allowed values: "employee", "manager", "practitioner", "administrator", "supervisor"

        Returns:
            requests.Response: Direct response from ADP API

        Raises:
            ValueError: If the dependent removal fails or required fields are missing
        """

        url = f"{self.decidium.base_url}/events/hr/v1/dependent.remove"

        # Prepare request headers
        headers = {}
        headers.update({
            "roleCode": role_code
        })

        try:
            # Normalize flat data to nested structure
            request_data = self.__normalize_dependent_delete_data(data)

            # Validate request data with pydantic schema
            try:
                valid_data = DependentRemoveRequest(**request_data)
                # Use validated data for the request (with proper aliases)
                request_data = valid_data.model_dump(by_alias=True, exclude_none=True)

            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            # Make POST request
            response = self.decidium._post(
                url=url,
                request_body=request_data,
                headers=headers,
            )
            response.raise_for_status()
            return response

        except Exception as e:
            raise Exception(f"An error occurred in dependent removal: {e}")

    def __normalize_dependent_delete_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat dependent delete data dictionary to nested ADP dependent remove request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing dependent deletion data

        Returns:
            Dict[str, Any]: Nested structure ready for ADP dependent remove API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Check required fields
        required_fields = ['associate_oid', 'dependent_item_id']
        missing_fields = [field for field in required_fields if field not in flat_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Create simple request structure for removal (no transform needed)
            request_data = {
                "events": [{
                    "data": {
                        "eventContext": {
                            "worker": {
                                "associateOID": str(flat_data["associate_oid"])
                            },
                            "dependent": {
                                "itemID": str(flat_data["dependent_item_id"])
                            }
                        }
                    }
                }]
            }

            return request_data

        except Exception as e:
            raise ValueError(f"Dependent delete data normalization failed: {str(e)}")
