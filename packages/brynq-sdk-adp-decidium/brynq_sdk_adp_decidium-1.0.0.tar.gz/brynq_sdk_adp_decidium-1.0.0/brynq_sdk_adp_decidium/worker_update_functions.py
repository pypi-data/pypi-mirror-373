from typing import Dict, Optional, Union, Literal, List, Any, get_args
import pandas as pd
from pydantic import BaseModel

from .schemas.workers import WorkerGet, WorkerHireRequest,  WorkerRehireRequest, WorkerTerminateEventData
from brynq_sdk_functions import Functions
import json
from typing import Any, Callable, Dict, Tuple, List
from .worker_normalization import WorkerNormalization

class WorkerUpdateFunctions:
    """
    Handles worker field update operations in ADP
    """

    def __init__(self, decidium):
        self.decidium = decidium
        self.base_uri = "hr/v2/workers"
        self.normalizations = WorkerNormalization(decidium)

    def _update_birth_date(
        self,
        associate_oid: str,
        birth_date: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker birth date

        Args:
            associate_oid (str): Worker's Associate OID
            birth_date (str): New birth date (YYYY-MM-DD format)
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.birth-date.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "birthDate": birth_date
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'birth_date',
                'status': 'error',
                'error': str(e)
            }

    def _update_birth_place(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker birth place

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Birth place data with fields:
                - birth_place_city_name: City name
                - birth_place_country_code: Country code
                - birth_place_postal_code: Postal code
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.birth-place.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            # Build nested birth place object from flat dictionary
            field_mapping = {
                "birth_place_city_name": "cityName",
                "birth_place_country_code": "countryCode",
                "birth_place_postal_code": "postalCode"
            }

            birth_place_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            # Add default subdivision if we have any birth place data
            if birth_place_nested:
                birth_place_nested["countrySubdivisionLevel1"] = {
                    "codeValue": "35",
                    "shortName": "",
                    "longName": "",
                    "subdivisionType": ""
                }
                birth_place_nested["formattedBirthPlace"] = ""

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "birthPlace": birth_place_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'birth_place',
                'status': 'error',
                'error': str(e)
            }

    def _update_gender(
        self,
        associate_oid: str,
        gender_code: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker gender

        Args:
            associate_oid (str): Worker's Associate OID
            gender_code (str): Gender code (M/F)
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.gender.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "genderCode": {
                                            "codeValue": gender_code
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'gender',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_email(
        self,
        associate_oid: str,
        email_uri: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker business email

        Args:
            associate_oid (str): Worker's Associate OID
            email_uri (str): New business email address
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.email.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "email": {
                                            "emailUri": email_uri
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_email',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_email_add(
        self,
        associate_oid: str,
        email_uri: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Adds a new business email for the worker.
        Args:
            associate_oid (str): Worker's Associate OID
            email_uri (str): New business email address
            role_code (str): Role code for the transaction
        Returns:
            Dict[str, Any]: Response from the add operation
        """
        url = f"{self.decidium.base_url}/event-notifications/hr/v1/worker.business-communication.email.add"
        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})
        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "email": {
                                            "emailUri": email_uri
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }


            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()
            return {
                'associate_oid': associate_oid,
                'field': 'business_email_add',
                'status': 'success',
                'response': {"message": "Request printed for testing"}
            }
        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_email_add',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_fax(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker business fax

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New business fax number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.fax.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "fax": {
                                            "formattedNumber": formatted_number
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_fax',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_fax_add(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Adds a new business fax for the worker.
        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New business fax number
            role_code (str): Role code for the transaction
        Returns:
            Dict[str, Any]: Response from the add operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.fax.add"
        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})
        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "fax": {
                                            "formattedNumber": formatted_number
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }
            print(f"=== BUSINESS FAX ADD REQUEST ===")
            print(f"URL: {url}")
            print(f"Request Data: {json.dumps(request_data, indent=2)}")
            print("=" * 50)

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()
            return {
                'associate_oid': associate_oid,
                'field': 'business_fax_add',
                'status': 'success',
                'response': {"message": "Request printed for testing"}
            }
        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_fax_add',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_landline(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker business landline

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New business landline number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.landline.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "landline": {
                                            "formattedNumber": formatted_number
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_landline',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_mobile(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker business mobile

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New business mobile number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.mobile.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "mobile": {
                                            "formattedNumber": formatted_number
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_mobile',
                'status': 'error',
                'error': str(e)
            }

    def _update_business_pager(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker business pager (çağrı cihazı)

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New business pager number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.business-communication.pager.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "businessCommunication": {
                                        "pager": {
                                            "formattedNumber": formatted_number
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'business_pager',
                'status': 'error',
                'error': str(e)
            }

    def _update_citizenship(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker citizenship

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Citizenship data with fields:
                - citizenship_code: Country code (e.g., "ES")
                - citizenship_short_name: Short country name (e.g., "ESPAGNE")
                - citizenship_long_name: Long country name (e.g., "ESPAGNE")
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.citizenship.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
                        # Build nested citizenship object from flat dictionary
            field_mapping = {
                "citizenship_code": "codeValue",
                "citizenship_short_name": "shortName",
                "citizenship_long_name": "longName"
            }

            citizenship_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "citizenshipCountryCode": citizenship_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'citizenship',
                'status': 'error',
                'error': str(e)
            }

    def _update_legal_name(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker legal name

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Legal name data with fields:
                - legal_name_given: Given name
                - legal_name_family_1: First family name
                - legal_name_family_2: Second family name
                - legal_name_middle: Middle name(s)
                - legal_name_salutation: Salutation code
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.legal-name.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
                        # Build nested legal name object from flat dictionary
            field_mapping = {
                "legal_name_given": "givenName",
                "legal_name_middle": "middleName",
                "legal_name_family_1": "familyName1",
                "legal_name_family_2": "familyName2"
            }

            legal_name_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            # Handle salutation separately as it has nested structure
            if "legal_name_salutation" in data:
                legal_name_nested["preferredSalutations"] = [
                    {
                        "salutationCode": {
                            "codeValue": data["legal_name_salutation"]
                        }
                    }
                ]

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "legalName": legal_name_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'legal_name',
                'status': 'error',
                'error': str(e)
            }

    def _update_marital_status(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker marital status

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Marital status data with fields:
                - marital_status_effective_date: Effective date (YYYY-MM-DD format)
                - marital_status_code: Marital status code (e.g., "C" for married)
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.marital-status.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
                        # Build nested marital status object from flat dictionary
            field_mapping = {
                "marital_status_effective_date": "effectiveDate",
                "marital_status_code": "codeValue"
            }

            marital_status_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "maritalStatusCode": marital_status_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            print(f"=== MARITAL STATUS UPDATE REQUEST ===")
            print(f"URL: {url}")
            print(f"Request Data: {json.dumps(request_data, indent=2)}")
            print("=" * 50)

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'marital_status',
                'status': 'error',
                'error': str(e)
            }

    def _update_legal_address(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker legal address

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Legal address data with fields:
                - legal_address_country_code: Country code
                - legal_address_postal_code: Postal code
                - legal_address_line_five: Line five
                - legal_address_building_number: Building number
                - legal_address_building_extension: Building number extension
                - legal_address_street_name: Street name
                - legal_address_subdivision_1: Subdivision level 1
                - legal_address_subdivision_2_code: Subdivision level 2 code
                - legal_address_subdivision_2_name: Subdivision level 2 name
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.legal-address.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
                        # Build nested legal address object from flat dictionary
            field_mapping = {
                "legal_address_country_code": "countryCode",
                "legal_address_postal_code": "postalCode",
                "legal_address_line_five": "lineFive",
                "legal_address_building_number": "buildingNumber",
                "legal_address_building_extension": "buildingNumberExtension",
                "legal_address_street_name": "streetName"
            }

            legal_address_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            # Add subdivision if we have subdivision data
            subdivision_mapping = {
                "legal_address_subdivision_2_code": "codeValue",
                "legal_address_subdivision_2_name": "longName"
            }

            subdivision_data = {
                subdivision_mapping[k]: v
                for k, v in data.items()
                if k in subdivision_mapping
            }

            if subdivision_data:
                legal_address_nested["countrySubdivisionLevel2"] = subdivision_data

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "legalAddress": legal_address_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'legal_address',
                'status': 'error',
                'error': str(e)
            }

    def _update_personal_address(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker personal address

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Personal address data with fields:
                - personal_address_country_code: Country code
                - personal_address_city_name: City name
                - personal_address_postal_code: Postal code
                - personal_address_line_five: Line five
                - personal_address_building_number: Building number
                - personal_address_building_extension: Building number extension
                - personal_address_street_name: Street name
                - personal_address_subdivision_2_code: Subdivision level 2 code
                - personal_address_subdivision_2_name: Subdivision level 2 name
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.personal-address.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
                        # Build nested personal address object from flat dictionary
            field_mapping = {
                "personal_address_country_code": "countryCode",
                "personal_address_city_name": "cityName",
                "personal_address_postal_code": "postalCode",
                "personal_address_line_five": "lineFive",
                "personal_address_building_number": "buildingNumber",
                "personal_address_building_extension": "buildingNumberExtension",
                "personal_address_street_name": "streetName"
            }

            personal_address_nested = {
                field_mapping[k]: v
                for k, v in data.items()
                if k in field_mapping
            }

            # Add subdivision if we have subdivision data
            subdivision_mapping = {
                "personal_address_subdivision_2_code": "codeValue",
                "personal_address_subdivision_2_name": "longName"
            }

            subdivision_data = {
                subdivision_mapping[k]: v
                for k, v in data.items()
                if k in subdivision_mapping
            }

            if subdivision_data:
                personal_address_nested["countrySubdivisionLevel2"] = subdivision_data

            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "personalAddress": personal_address_nested
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'personal_address',
                'status': 'error',
                'error': str(e)
            }

    def _update_personal_email(
        self,
        associate_oid: str,
        email_uri: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker personal email

        Args:
            associate_oid (str): Worker's Associate OID
            email_uri (str): New personal email address
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.personal-communication.email.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "communication": {
                                            "email": {
                                                "emailUri": email_uri
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'personal_email',
                'status': 'error',
                'error': str(e)
            }

    def _update_personal_fax(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker personal fax

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New personal fax number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.personal-communication.fax.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "communication": {
                                            "fax": {
                                                "formattedNumber": formatted_number
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'personal_fax',
                'status': 'error',
                'error': str(e)
            }

    def _update_personal_landline(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker personal landline

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New personal landline number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.personal-communication.landline.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "communication": {
                                            "landline": {
                                                "formattedNumber": formatted_number
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'personal_landline',
                'status': 'error',
                'error': str(e)
            }

    def _update_personal_mobile(
        self,
        associate_oid: str,
        formatted_number: str,
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Updates worker personal mobile

        Args:
            associate_oid (str): Worker's Associate OID
            formatted_number (str): New personal mobile number
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the update operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.personal-communication.mobile.change"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            request_data = {
                "events": [
                    {
                        "data": {
                            "eventContext": {
                                "worker": {
                                    "associateOID": associate_oid
                                }
                            },
                            "transform": {
                                "worker": {
                                    "person": {
                                        "communication": {
                                            "mobile": {
                                                "formattedNumber": formatted_number
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            response = self.decidium._post(url=url, request_body=request_data, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            return {
                'associate_oid': associate_oid,
                'field': 'personal_mobile',
                'status': 'error',
                'error': str(e)
            }
