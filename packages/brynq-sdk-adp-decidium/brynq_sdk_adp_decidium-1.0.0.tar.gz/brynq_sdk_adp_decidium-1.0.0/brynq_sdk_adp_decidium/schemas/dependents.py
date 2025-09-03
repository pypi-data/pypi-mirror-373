import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field
from typing import Optional, List

# ---------------------------
# GET Schema - Flattened Dependent Data
# ---------------------------
class DependentGet(BrynQPanderaDataFrameModel):
    """Flattened schema for ADP Dependents data (one row per dependent)."""

    # Context
    associate_oid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Associate OID", alias="associateOID")
    dependent_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Dependent Item ID", alias="itemID")

    # Effective Date
    effective_date: Optional[Series[pd.StringDtype]] = pa.Field(coerce=True, nullable=True, description="Effective Date", alias="effectiveDate")

    # Relationship Information
    relationship_type_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Relationship Type Code", alias="relationshipTypeCode.codeValue")
    relationship_type_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Relationship Type Short Name", alias="relationshipTypeCode.shortName")
    relationship_type_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Relationship Type Long Name", alias="relationshipTypeCode.longName")

    # Person Information
    given_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Given Name", alias="person.legalName.givenName")
    family_name_1: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Family Name 1", alias="person.legalName.familyName1")
    family_name_2: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Family Name 2", alias="person.legalName.familyName2")
    birth_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth Date", alias="person.birthDate")
    gender_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender Code", alias="person.genderCode.codeValue")
    gender_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender Short Name", alias="person.genderCode.shortName")
    gender_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender Long Name", alias="person.genderCode.longName")
    birth_order: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Birth Order", alias="person.birthOrder")

    # Person Status Indicators
    disabled_indicator: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Disabled Indicator", alias="person.disabledIndicator")
    tax_dependent_indicator: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Tax Dependent Indicator", alias="person.taxDependentIndicator")

    # Marital Status
    marital_status_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital Status Code", alias="person.maritalStatusCode.codeValue")
    marital_status_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital Status Short Name", alias="person.maritalStatusCode.shortName")
    marital_status_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital Status Long Name", alias="person.maritalStatusCode.longName")

    # Communication
    fax_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Fax Number", alias="person.communication.faxes.formattedNumber")
    fax_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Fax Type", alias="person.communication.faxes.itemID")
    landline_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Landline Number", alias="person.communication.landlines.formattedNumber")
    landline_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Landline Type", alias="person.communication.landlines.itemID")

    # Legal Address
    address_country_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Country Code", alias="person.legalAddress.countryCode")
    address_city_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address City Name", alias="person.legalAddress.cityName")
    address_postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Postal Code", alias="person.legalAddress.postalCode")
    address_line_five: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Line Five", alias="person.legalAddress.lineFive")
    address_building_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Building Number", alias="person.legalAddress.buildingNumber")
    address_building_extension: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Building Extension", alias="person.legalAddress.buildingNumberExtension")
    address_street_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Street Name", alias="person.legalAddress.streetName")
    address_subdivision_2_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Subdivision Level 2 Code", alias="person.legalAddress.countrySubdivisionLevel2.codeValue")
    address_subdivision_2_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Address Subdivision Level 2 Name", alias="person.legalAddress.countrySubdivisionLevel2.longName")

    # Social Insurance Programs
    health_insurance_covered: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Health Insurance Covered", alias="person.socialInsurancePrograms.healthInsurance.coveredIndicator")

    # Preferred Salutations
    salutation_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Salutation Code", alias="person.legalName.preferredSalutations.salutationCode.codeValue")
    salutation_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Salutation Short Name", alias="person.legalName.preferredSalutations.salutationCode.shortName")
    salutation_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Salutation Long Name", alias="person.legalName.preferredSalutations.salutationCode.longName")
    salutation_sequence: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Salutation Sequence Number", alias="person.legalName.preferredSalutations.sequenceNumber")

    class _Annotation:
        primary_key = "associate_oid"


# ---------------------------
# CREATE Schema - Dependent Add Request
# ---------------------------

class CodeValue(BaseModel):
    """Code value structure used throughout ADP API"""
    code_value: str = Field(..., alias="codeValue", description="Code value - REQUIRED", example="E")
    short_name: Optional[str] = Field(None, alias="shortName", description="Short display name", example="Child")
    long_name: Optional[str] = Field(None, alias="longName", description="Long display name", example="Child Dependent")

    class Config:
        allow_population_by_field_name = True


class PreferredSalutation(BaseModel):
    """Preferred salutation structure"""
    sequence_number: int = Field(..., alias="sequenceNumber", description="Sequence number - REQUIRED", example=0)
    salutation_code: CodeValue = Field(..., alias="salutationCode", description="Salutation code - REQUIRED", example={"codeValue": "M"})

    class Config:
        allow_population_by_field_name = True


class CountrySubdivisionLevel2(BaseModel):
    """Country subdivision level 2 structure"""
    long_name: str = Field(..., alias="longName", description="Long name - REQUIRED", example="LOCALITE")
    code_value: str = Field(..., alias="codeValue", description="Code value - REQUIRED", example="78121")

    class Config:
        allow_population_by_field_name = True


class LegalAddress(BaseModel):
    """Legal address structure"""
    line_five: Optional[str] = Field(None, alias="lineFive", description="Address line five", example="LIEU DIT")
    building_number: Optional[str] = Field(None, alias="buildingNumber", description="Building number", example="5")
    building_number_extension: Optional[str] = Field(None, alias="buildingNumberExtension", description="Building number extension", example="B")
    street_name: Optional[str] = Field(None, alias="streetName", description="Street name", example="RUE DICIBAS")
    country_subdivision_level_2: Optional[CountrySubdivisionLevel2] = Field(None, alias="countrySubdivisionLevel2", description="Country subdivision level 2")
    city_name: str = Field(..., alias="cityName", description="City name - REQUIRED", example="LE VESINET")
    postal_code: str = Field(..., alias="postalCode", description="Postal code - REQUIRED", example="78110")
    country_code: str = Field(..., alias="countryCode", description="Country code - REQUIRED", example="FR")

    class Config:
        allow_population_by_field_name = True


class CommunicationItem(BaseModel):
    """Communication item structure"""
    item_id: str = Field(..., alias="itemID", description="Item ID - REQUIRED", example="Personal")
    formatted_number: str = Field(..., alias="formattedNumber", description="Formatted number - REQUIRED", example="0801020304")

    class Config:
        allow_population_by_field_name = True


class Communication(BaseModel):
    """Communication structure"""
    faxes: Optional[List[CommunicationItem]] = Field(None, description="Fax numbers", example=[{"itemID": "Personal", "formattedNumber": "0801020304"}])
    landlines: Optional[List[CommunicationItem]] = Field(None, description="Landline numbers", example=[{"itemID": "Personal", "formattedNumber": "0601020304"}])

    class Config:
        allow_population_by_field_name = True


class SocialInsuranceProgram(BaseModel):
    """Social insurance program structure"""
    item_id: str = Field(..., alias="itemID", description="Item ID - REQUIRED", example="healthInsurance")
    covered_indicator: bool = Field(..., alias="coveredIndicator", description="Covered indicator - REQUIRED", example=True)

    class Config:
        allow_population_by_field_name = True


class LegalName(BaseModel):
    """Legal name structure"""
    preferred_salutations: Optional[List[PreferredSalutation]] = Field(None, alias="preferredSalutations", description="Preferred salutations")
    given_name: str = Field(..., alias="givenName", description="Given name - REQUIRED", example="KTY")
    family_name_1: str = Field(..., alias="familyName1", description="Family name 1 - REQUIRED", example="ENFANT")
    family_name_2: Optional[str] = Field(None, alias="familyName2", description="Family name 2", example="NOMNAISSANCE")

    class Config:
        allow_population_by_field_name = True


class Person(BaseModel):
    """Person structure"""
    legal_name: LegalName = Field(..., alias="legalName", description="Legal name - REQUIRED")
    marital_status_code: Optional[CodeValue] = Field(None, alias="maritalStatusCode", description="Marital status code", example={"codeValue": "A"})
    birth_date: str = Field(..., alias="birthDate", description="Birth date - REQUIRED (YYYY-MM-DD)", example="2005-02-14")
    deceased_indicator: Optional[bool] = Field(None, alias="deceasedIndicator", description="Deceased indicator", example=False)
    gender_code: CodeValue = Field(..., alias="genderCode", description="Gender code - REQUIRED", example={"codeValue": "M"})
    tax_dependent_indicator: Optional[bool] = Field(None, alias="taxDependentIndicator", description="Tax dependent indicator", example=True)
    disabled_indicator: Optional[bool] = Field(None, alias="disabledIndicator", description="Disabled indicator", example=True)
    social_insurance_programs: Optional[List[SocialInsuranceProgram]] = Field(None, alias="socialInsurancePrograms", description="Social insurance programs")
    birth_order: Optional[int] = Field(None, alias="birthOrder", description="Birth order", example=1)
    legal_address: Optional[LegalAddress] = Field(None, alias="legalAddress", description="Legal address")
    communication: Optional[Communication] = Field(None, description="Communication")

    class Config:
        allow_population_by_field_name = True


class Dependent(BaseModel):
    """Dependent structure"""
    effective_date: Optional[str] = Field(None, alias="effectiveDate", description="Effective date (YYYY-MM-DD)", example="2024-01-15")
    relationship_type_code: CodeValue = Field(..., alias="relationshipTypeCode", description="Relationship type code - REQUIRED", example={"codeValue": "E"})
    person: Person = Field(..., description="Person information - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class Worker(BaseModel):
    """Worker information"""
    associate_oid: str = Field(..., alias="associateOID", description="Associate OID - REQUIRED", example="AO0P33A53197K43")

    class Config:
        allow_population_by_field_name = True


class EventContext(BaseModel):
    """Event context structure"""
    worker: Worker = Field(..., description="Worker information - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentTransform(BaseModel):
    """Dependent transform structure"""
    dependent: Dependent = Field(..., description="Dependent information - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentData(BaseModel):
    """Dependent data structure"""
    event_context: EventContext = Field(..., alias="eventContext", description="Event context - REQUIRED")
    transform: DependentTransform = Field(..., description="Transform - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentEvent(BaseModel):
    """Dependent event structure"""
    data: DependentData = Field(..., description="Data - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentAddRequest(BaseModel):
    """Dependent Add Request - for adding dependents to workers

    Endpoint: POST /events/hr/v1/dependent.add
    """
    events: List[DependentEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True


# ---------------------------
# UPDATE Schema - Dependent Change Request
# ---------------------------

class DependentContext(BaseModel):
    """Dependent context structure for updates"""
    item_id: str = Field(..., alias="itemID", description="Dependent item ID - REQUIRED", example="2")

    class Config:
        allow_population_by_field_name = True


class UpdateEventContext(BaseModel):
    """Event context structure for dependent updates"""
    worker: Worker = Field(..., description="Worker information - REQUIRED")
    dependent: DependentContext = Field(..., description="Dependent context - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class UpdateLegalName(BaseModel):
    """Legal name structure for updates (all fields optional)"""
    given_name: Optional[str] = Field(None, alias="givenName", description="Given name", example="ENFANT DEUX")
    family_name_1: Optional[str] = Field(None, alias="familyName1", description="Family name 1", example="UPDATED")
    family_name_2: Optional[str] = Field(None, alias="familyName2", description="Family name 2", example="SURNAME")
    preferred_salutations: Optional[List[PreferredSalutation]] = Field(None, alias="preferredSalutations", description="Preferred salutations")

    class Config:
        allow_population_by_field_name = True


class UpdatePerson(BaseModel):
    """Person structure for updates (all fields optional)"""
    legal_name: Optional[UpdateLegalName] = Field(None, alias="legalName", description="Legal name")
    marital_status_code: Optional[CodeValue] = Field(None, alias="maritalStatusCode", description="Marital status code")
    birth_date: Optional[str] = Field(None, alias="birthDate", description="Birth date (YYYY-MM-DD)")
    deceased_indicator: Optional[bool] = Field(None, alias="deceasedIndicator", description="Deceased indicator")
    gender_code: Optional[CodeValue] = Field(None, alias="genderCode", description="Gender code")
    tax_dependent_indicator: Optional[bool] = Field(None, alias="taxDependentIndicator", description="Tax dependent indicator")
    disabled_indicator: Optional[bool] = Field(None, alias="disabledIndicator", description="Disabled indicator")
    social_insurance_programs: Optional[List[SocialInsuranceProgram]] = Field(None, alias="socialInsurancePrograms", description="Social insurance programs")
    birth_order: Optional[int] = Field(None, alias="birthOrder", description="Birth order")
    legal_address: Optional[LegalAddress] = Field(None, alias="legalAddress", description="Legal address")
    communication: Optional[Communication] = Field(None, description="Communication")

    class Config:
        allow_population_by_field_name = True


class UpdateDependent(BaseModel):
    """Dependent structure for updates (all fields optional)"""
    effective_date: Optional[str] = Field(None, alias="effectiveDate", description="Effective date (YYYY-MM-DD)", example="2024-01-15")
    relationship_type_code: Optional[CodeValue] = Field(None, alias="relationshipTypeCode", description="Relationship type code")
    person: Optional[UpdatePerson] = Field(None, description="Person information")

    class Config:
        allow_population_by_field_name = True


class UpdateDependentTransform(BaseModel):
    """Dependent transform structure for updates"""
    dependent: UpdateDependent = Field(..., description="Dependent information - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class UpdateDependentData(BaseModel):
    """Dependent data structure for updates"""
    event_context: UpdateEventContext = Field(..., alias="eventContext", description="Event context - REQUIRED")
    transform: UpdateDependentTransform = Field(..., description="Transform - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class UpdateDependentEvent(BaseModel):
    """Dependent event structure for updates"""
    data: UpdateDependentData = Field(..., description="Data - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentChangeRequest(BaseModel):
    """Dependent Change Request - for updating dependents

    Endpoint: POST /events/hr/v1/dependent.change
    """
    events: List[UpdateDependentEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True


# ---------------------------
# DELETE Schema - Dependent Remove Request
# ---------------------------

class RemoveEventContext(BaseModel):
    """Event context structure for dependent removal"""
    worker: Worker = Field(..., description="Worker information - REQUIRED")
    dependent: DependentContext = Field(..., description="Dependent context - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class RemoveDependentData(BaseModel):
    """Dependent data structure for removal"""
    event_context: RemoveEventContext = Field(..., alias="eventContext", description="Event context - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class RemoveDependentEvent(BaseModel):
    """Dependent event structure for removal"""
    data: RemoveDependentData = Field(..., description="Data - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DependentRemoveRequest(BaseModel):
    """Dependent Remove Request - for removing dependents

    Endpoint: POST /events/hr/v1/dependent.remove
    """
    events: List[RemoveDependentEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True
