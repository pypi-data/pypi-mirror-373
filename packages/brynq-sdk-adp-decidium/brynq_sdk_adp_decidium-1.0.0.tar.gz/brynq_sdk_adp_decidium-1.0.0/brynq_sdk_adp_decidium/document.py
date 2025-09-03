from typing import Dict, Optional, Union, Literal, List, Any, get_args
import pandas as pd
from pydantic import BaseModel

from brynq_sdk_functions import Functions
from .schemas.document import IdentityDocumentAddRequest, ImmigrationDocumentAddRequest, DOCUMENT_TYPES
import json
from typing import Any, Callable, Dict, Tuple, List


class Document:
    """
    Handles worker document operations in ADP (identity and immigration documents)
    """


    def __init__(self, decidium):
        self.decidium = decidium

    def __normalize_identity_document_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes flat identity document data to nested ADP structure

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing identity document data with keys:
                - document_id: Document ID (required)
                - type_code: Document type code (e.g., "passport", "SSN", "IDCard", "visa1", "visa2") (required)
                - issue_date: Issue date (YYYY-MM-DD format) (optional)
                - expiration_date: Expiration date (YYYY-MM-DD format) (optional)
                - issuing_party: Issuing party information (optional)
                - document_number: Document number (optional)

        Returns:
            Dict[str, Any]: Nested structure ready for ADP identity document API request
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Validate document type
        type_code = flat_data.get("type_code")
        if type_code not in DOCUMENT_TYPES["identity"]:
            valid_types = list(DOCUMENT_TYPES["identity"].keys())
            raise ValueError(f"Invalid document type '{type_code}'. Valid types are: {valid_types}")

        # Build the base nested structure
        nested_data = {
            "documentID": flat_data.get("document_id"),
            "typeCode": {
                "codeValue": type_code,
                "shortName": DOCUMENT_TYPES["identity"][type_code]["short_name"]
            }
        }

        # Add optional fields if provided
        if "issue_date" in flat_data:
            nested_data["issueDate"] = flat_data["issue_date"]

        if "expiration_date" in flat_data:
            nested_data["expirationDate"] = flat_data["expiration_date"]

        if "issuing_party" in flat_data:
            nested_data["issuingParty"] = flat_data["issuing_party"]

        if "document_number" in flat_data:
            nested_data["documentNumber"] = flat_data["document_number"]

        return nested_data

    def __normalize_immigration_document_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes flat immigration document data to nested ADP structure

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing immigration document data with keys:
                - document_id: Document ID (required)
                - type_code: Document type code (e.g., "resPermit", "workPermit") (required)
                - issue_date: Issue date (YYYY-MM-DD format) (optional)
                - expiration_date: Expiration date (YYYY-MM-DD format) (optional)
                - issuing_party: Issuing party information (optional)
                - document_number: Document number (optional)

        Returns:
            Dict[str, Any]: Nested structure ready for ADP immigration document API request
        """
        if not flat_data:
            raise ValueError("Input data is empty")

        # Validate document type
        type_code = flat_data.get("type_code")
        if type_code not in DOCUMENT_TYPES["immigration"]:
            valid_types = list(DOCUMENT_TYPES["immigration"].keys())
            raise ValueError(f"Invalid immigration document type '{type_code}'. Valid types are: {valid_types}")

        # Build the base nested structure
        nested_data = {
            "documentID": flat_data.get("document_id"),
            "typeCode": {
                "codeValue": type_code,
                "shortName": DOCUMENT_TYPES["immigration"][type_code]["short_name"]
            }
        }

        # Add optional fields if provided
        if "issue_date" in flat_data:
            nested_data["issueDate"] = flat_data["issue_date"]

        if "expiration_date" in flat_data:
            nested_data["expirationDate"] = flat_data["expiration_date"]

        if "issuing_party" in flat_data:
            nested_data["issuingParty"] = flat_data["issuing_party"]

        if "document_number" in flat_data:
            nested_data["documentNumber"] = flat_data["document_number"]

        return nested_data

    def create_identity_document(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Adds an identity document for a worker

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Document data with fields:
                - document_id: Document ID (required)
                - type_code: Document type code (e.g., "passport", "SSN", "IDCard", "visa1", "visa2") (required)
                - issue_date: Issue date (YYYY-MM-DD format) (optional)
                - expiration_date: Expiration date (YYYY-MM-DD format) (optional)
                - issuing_party: Issuing party information (optional)
                - document_number: Document number (optional)
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the add operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.identity-document.add"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            # Normalize flat data to nested structure
            normalized_document = self.__normalize_identity_document_data(data)

            # Build the request data structure
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
                                        "identityDocument": normalized_document
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            # Validate request data with pydantic schema
            try:
                valid_data = IdentityDocumentAddRequest(**request_data)
                request_body = valid_data.model_dump(by_alias=True, exclude_none=True)
            except Exception as e:
                raise ValueError(f"Request validation error: {str(e)}")

            response = self.decidium.post(url=url, request_body=request_body, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to add identity document: {str(e)}")

    def create_immigration_document(
        self,
        associate_oid: str,
        data: Dict[str, Any],
        role_code: Literal["employee", "manager", "practitioner", "administrator", "supervisor"]
    ) -> Dict[str, Any]:
        """
        Adds an immigration document for a worker

        Args:
            associate_oid (str): Worker's Associate OID
            data (Dict[str, Any]): Document data with fields:
                - document_id: Document ID (required)
                - type_code: Document type code (e.g., "resPermit", "workPermit") (required)
                - issue_date: Issue date (YYYY-MM-DD format) (optional)
                - expiration_date: Expiration date (YYYY-MM-DD format) (optional)
                - issuing_party: Issuing party information (optional)
                - document_number: Document number (optional)
            role_code (str): Role code for the transaction

        Returns:
            Dict[str, Any]: Response from the add operation
        """
        url = f"{self.decidium.base_url}/events/hr/v1/worker.immigration-document.add"

        headers = self.decidium.session.headers.copy()
        headers.update({"roleCode": role_code})

        try:
            # Normalize flat data to nested structure
            normalized_document = self.__normalize_immigration_document_data(data)

            # Build the request data structure
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
                                        "immigrationDocument": normalized_document
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            # Validate request data with pydantic schema
            try:
                valid_data = ImmigrationDocumentAddRequest(**request_data)
                request_body = valid_data.model_dump(by_alias=True, exclude_none=True)
            except Exception as validation_error:
                raise ValueError(f"Request validation error: {str(validation_error)}")

            response = self.decidium.post(url=url, request_body=request_body, headers=headers)
            response.raise_for_status()

            return response

        except Exception as e:
            raise ValueError(f"Failed to add immigration document: {str(e)}")
