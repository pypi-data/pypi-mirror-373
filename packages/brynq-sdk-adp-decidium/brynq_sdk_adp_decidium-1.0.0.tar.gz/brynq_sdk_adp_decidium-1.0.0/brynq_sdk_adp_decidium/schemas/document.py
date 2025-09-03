from typing import Dict, Optional, List, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentTypeCode(BaseModel):
    """Document type code structure"""
    code_value: str = Field(..., description="Document type code", example="passport", alias="codeValue")
    short_name: Optional[str] = Field(None, description="Document type short name", example="Passeport", alias="shortName")

    class Config:
        allow_population_by_field_name = True


class IssuingParty(BaseModel):
    """Issuing party structure"""
    name_code: DocumentTypeCode = Field(..., description="Issuing party name code", alias="nameCode")

    class Config:
        allow_population_by_field_name = True


class IdentityDocument(BaseModel):
    """Identity document structure"""
    document_id: str = Field(..., description="Document ID", example="123456789", alias="documentID")
    type_code: DocumentTypeCode = Field(..., description="Document type code", alias="typeCode")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD format)", example="2020-01-15", alias="issueDate")
    expiration_date: Optional[str] = Field(None, description="Expiration date (YYYY-MM-DD format)", example="2030-01-15", alias="expirationDate")
    issuing_party: Optional[IssuingParty] = Field(None, description="Issuing party", alias="issuingParty")
    document_number: Optional[str] = Field(None, description="Document number", example="FR123456789", alias="documentNumber")

    class Config:
        allow_population_by_field_name = True


class ImmigrationDocument(BaseModel):
    """Immigration document structure"""
    document_id: str = Field(..., description="Document ID", example="RF12345789", alias="documentID")
    type_code: DocumentTypeCode = Field(..., description="Document type code", example="resPermit", alias="typeCode")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD format)", example="2024-01-01", alias="issueDate")
    expiration_date: Optional[str] = Field(None, description="Expiration date (YYYY-MM-DD format)", example="2030-01-01", alias="expirationDate")
    issuing_party: Optional[IssuingParty] = Field(None, description="Issuing party", alias="issuingParty")
    document_number: Optional[str] = Field(None, description="Document number", example="RF12345789", alias="documentNumber")

    class Config:
        allow_population_by_field_name = True


class Person(BaseModel):
    """Person structure for document operations"""
    identity_document: Optional[IdentityDocument] = Field(None, description="Identity document", alias="identityDocument")
    immigration_document: Optional[ImmigrationDocument] = Field(None, description="Immigration document", alias="immigrationDocument")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class Worker(BaseModel):
    """Worker structure for document operations"""
    associate_oid: str = Field(..., description="Associate OID", example="gmartinelli-7150mp3", alias="associateOID")
    person: Optional[Person] = Field(None, description="Person", alias="person")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class EventContext(BaseModel):
    """Event context structure"""
    worker: Dict[str, Any] = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class Transform(BaseModel):
    """Transform structure for document operations"""
    worker: Dict[str, Any] = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class EventData(BaseModel):
    """Event data structure"""
    event_context: EventContext = Field(..., description="Event context", alias="eventContext")
    transform: Transform = Field(..., description="Transform", alias="transform")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class DocumentEvent(BaseModel):
    """Document event structure"""
    data: EventData = Field(..., description="Event data", alias="data")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class IdentityDocumentAddRequest(BaseModel):
    """Identity document add request structure"""
    events: List[DocumentEvent] = Field(..., description="Events", alias="events")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class ImmigrationDocumentAddRequest(BaseModel):
    """Immigration document add request structure"""
    events: List[DocumentEvent] = Field(..., description="Events", alias="events")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


# Document type constants based on schema information
DOCUMENT_TYPES = {
    "identity": {
        "SSN": {"code_value": "SSN", "short_name": "Numéro de sécurité sociale"},
        "IDCard": {"code_value": "IDCard", "short_name": "Carte d'identité"},
        "passport": {"code_value": "passport", "short_name": "Passeport"},
        "visa1": {"code_value": "visa1", "short_name": "Visa 1"},
        "visa2": {"code_value": "visa2", "short_name": "Visa 2"}
    },
    "immigration": {
        "resPermit": {"code_value": "resPermit", "short_name": "Residence Permit"},
        "workPermit": {"code_value": "workPermit", "short_name": "Work Permit"}
    }
}
