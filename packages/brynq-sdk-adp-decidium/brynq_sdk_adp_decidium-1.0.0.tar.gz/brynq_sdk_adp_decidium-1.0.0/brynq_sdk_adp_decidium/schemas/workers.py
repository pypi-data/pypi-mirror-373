import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------
# Get Schema - Flattened Worker Data
# ---------------------------
class WorkerGet(BrynQPanderaDataFrameModel):
    """Flattened schema for ADP Worker data"""

    # Core Worker Information
    associate_oid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Associate OID", alias="associateOID")
    worker_id: Series[pd.StringDtype] = pa.Field(coerce=True, description="Worker ID Value", alias="workerID.idValue")

    # Worker Dates
    first_hire_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="First Hire Date", alias="workerDates.firstHireDate")
    original_hire_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Original Hire Date", alias="workerDates.originalHireDate")
    termination_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Termination Date", alias="workerDates.terminationDate")

    # Worker Status
    worker_status_effective_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Worker Status Effective Date", alias="workerStatus.effectiveDate")
    worker_status_code: Series[pd.StringDtype] = pa.Field(
        coerce=True,
        nullable=True,
        description="Worker Status Code",
        alias="workerStatus.statusCode.codeValue"
    )


    # Business Communication
    business_email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Business Email", alias="businessCommunication.emails.emailUri")
    business_landline: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Business Landline", alias="businessCommunication.landlines.formattedNumber")
    business_mobile: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Business Mobile", alias="businessCommunication.mobiles.formattedNumber")
    business_pager: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Business Pager", alias="businessCommunication.pagers.formattedNumber")

    # Work Assignment - Main Fields
    work_assignment_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Assignment ID", alias="workAssignments.itemID")
    payroll_file_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payroll File Number", alias="workAssignments.payrollFileNumber")
    seniority_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Seniority Date", alias="workAssignments.seniorityDate")
    legal_entity_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Entity ID", alias="workAssignments.legalEntityID")
    expected_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Expected Start Date", alias="workAssignments.expectedStartDate")
    hire_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Hire Date", alias="workAssignments.hireDate")
    actual_start_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Actual Start Date", alias="workAssignments.actualStartDate")
    expected_termination_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Expected Termination Date", alias="workAssignments.expectedTerminationDate")
    work_assignment_termination_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Assignment Termination Date", alias="workAssignments.terminationDate")

    # Job Information
    job_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Job Code", alias="workAssignments.jobCode.codeValue")
    job_code_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Job Code Long Name", alias="workAssignments.jobCode.longName")
    job_function_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Job Function Code", alias="workAssignments.jobFunctionCode.codeValue")
    job_function_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Job Function Long Name", alias="workAssignments.jobFunctionCode.longName")
    job_title: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Job Title", alias="workAssignments.jobTitle")

    # Contract Information
    contract_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Contract Code (Worker Type)", alias="workAssignments.workerTypeCode.codeValue")

    # Work Assignment Custom Fields
    payroll_admin_group: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payroll Administration Group", alias="workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup")
    contract_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Contract Type", alias="workAssignments.customFieldGroup.codeFields.contractType")
    contract_reason: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Contract Reason (Recours Reason)", alias="workAssignments.customFieldGroup.codeFields.recoursReason")
    activity: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Activity", alias="workAssignments.customFieldGroup.codeFields.activity")
    remuneration_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Remuneration Type", alias="workAssignments.customFieldGroup.codeFields.remunerationType")
    work_schedule: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Schedule", alias="workAssignments.customFieldGroup.codeFields.workSchedule")
    tlm: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="TLM", alias="workAssignments.customFieldGroup.codeFields.TLM")
    qualification_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Qualification Code (Collaboration Type)", alias="workAssignments.customFieldGroup.codeFields.collaborationType")

    # Work Assignment Number Fields
    coefficient: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Coefficient", alias="workAssignments.customFieldGroup.numberFields.coefficient")
    full_time_hours: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Full Time Hours", alias="workAssignments.customFieldGroup.numberFields.fullTimeHours")
    weekly_hours: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Weekly Hours", alias="workAssignments.customFieldGroup.numberFields.weeklyHours")
    monthly_hours: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Monthly Hours", alias="workAssignments.customFieldGroup.numberFields.monthlyHours")

    # Remuneration
    remuneration_basis_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Remuneration Basis Code", alias="workAssignments.remunerationBasisCode.codeValue")
    pay_period_rate_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Pay Period Rate Amount", alias="workAssignments.baseRemuneration.payPeriodRateAmount.amountValue")
    pay_period_currency: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Pay Period Currency", alias="workAssignments.baseRemuneration.payPeriodRateAmount.currencyCode")
    monthly_rate_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Monthly Rate Amount", alias="workAssignments.baseRemuneration.monthlyRateAmount.amountValue")
    monthly_currency: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Monthly Currency", alias="workAssignments.baseRemuneration.monthlyRateAmount.currencyCode")
    annual_rate_amount: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Annual Rate Amount", alias="workAssignments.baseRemuneration.annualRateAmount.amountValue")
    annual_currency: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Annual Currency", alias="workAssignments.baseRemuneration.annualRateAmount.currencyCode")

    # Work Location
    work_location_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location ID", alias="workAssignments.assignedWorkLocations.itemID")
    work_location_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location Name", alias="workAssignments.assignedWorkLocations.nameCode.longName")
    work_location_country: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location Country", alias="workAssignments.assignedWorkLocations.address.countryCode")
    work_location_city: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location City", alias="workAssignments.assignedWorkLocations.address.cityName")
    work_location_postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location Postal Code", alias="workAssignments.assignedWorkLocations.address.postalCode")
    work_location_line_one: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location Line One", alias="workAssignments.assignedWorkLocations.address.lineOne")
    work_location_line_two: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Work Location Line Two", alias="workAssignments.assignedWorkLocations.address.lineTwo")
    establishment_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Establishment Code (SIRET)", alias="workAssignments.assignedWorkLocations.address.nameCode.codeValue")

    # Company Information
    company_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Company Name", alias="workAssignments.legalEntityCode.longName")
    company_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Company Code", alias="workAssignments.legalEntityCode.codeValue")

    # Department/Organization
    department_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Department ID", alias="workAssignments.assignedOrganizationalUnits.departmentId.nameCode.codeValue")
    department_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Department Name", alias="workAssignments.assignedOrganizationalUnits.departmentId.nameCode.longName")

    # Cost Centers
    cost_center_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Cost Center ID", alias="workAssignments.assignmentCostCenters.costCenterID")
    cost_center_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Cost Center Name", alias="workAssignments.assignmentCostCenters.costCenterName")
    cost_center_percentage: Series[pd.Float64Dtype] = pa.Field(coerce=True, nullable=True, description="Cost Center Percentage", alias="workAssignments.assignmentCostCenters.costCenterPercentage")

    # Work Assignment Custom Fields
    payroll_admin_group: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payroll Administration Group", alias="workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup")
    professional_category_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Professional Category", alias="workAssignments.customFieldGroup.codeFields.professionalCategory.codeValue")
    professional_category_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Professional Category Name", alias="workAssignments.customFieldGroup.codeFields.professionalCategory.longName")
    collaboration_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Collaboration Type", alias="workAssignments.customFieldGroup.codeFields.collaborationType.codeValue")
    collaboration_type_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Collaboration Type Name", alias="workAssignments.customFieldGroup.codeFields.collaborationType.longName")

    # Person Information
    person_birth_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth Date", alias="person.birthDate")
    person_gender: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Gender", alias="person.genderCode.codeValue")
    person_deceased_indicator: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True, description="Deceased Indicator", alias="person.deceasedIndicator")

    # Birth Place
    birth_place_country: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth Place Country", alias="person.birthPlace.countryCode")
    birth_place_city: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth Place City", alias="person.birthPlace.cityName")
    birth_place_postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Birth Place Postal Code", alias="person.birthPlace.postalCode")

    # Marital Status
    marital_status_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital Status Code", alias="person.maritalStatusCode.codeValue")
    marital_status_effective_date: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Marital Status Effective Date", alias="person.maritalStatusCode.effectiveDate")

    # Legal Name
    legal_name_formatted: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Name Formatted", alias="person.legalName.formattedName")
    legal_name_given: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Name Given", alias="person.legalName.givenName")
    legal_name_family_1: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Name Family 1", alias="person.legalName.familyName1")
    legal_name_family_2: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Name Family 2", alias="person.legalName.familyName2")
    legal_name_middle: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Name Middle", alias="person.legalName.middleName")

    # Identity Documents
    identity_document_ssn: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="SSN", alias="person.identityDocuments.SSN.documentID")

    # Personal Communication
    personal_email: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal Email", alias="person.communication.emails.emailUri")
    personal_landline: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal Landline", alias="person.communication.landlines.formattedNumber")
    personal_mobile: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Personal Mobile", alias="person.communication.mobiles.formattedNumber")

    # Legal Address
    legal_address_country: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address Country", alias="person.legalAddress.countryCode")
    legal_address_city: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address City", alias="person.legalAddress.cityName")
    legal_address_postal_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address Postal Code", alias="person.legalAddress.postalCode")
    legal_address_line_one: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address Line One", alias="person.legalAddress.lineOne")
    legal_address_building_number: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address Building Number", alias="person.legalAddress.buildingNumber")
    legal_address_street_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Legal Address Street Name", alias="person.legalAddress.streetName")

    # Citizenship
    citizenship_country_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Citizenship Country Code", alias="person.citizenshipCountryCodes.codeValue")
    citizenship_country_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Citizenship Country Name", alias="person.citizenshipCountryCodes.longName")


    # Alternate IDs
    alternate_id_value: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Alternate ID Value", alias="alternateIDs.idValue")
    alternate_id_scheme: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Alternate ID Scheme", alias="alternateIDs.schemeCode.codeValue")


    class _Annotation:
        primary_key = "associate_oid"

# ---------------------------
# Worker Hire Request Schemas
# ---------------------------

class CodeValue(BaseModel):
    """Code value structure used throughout ADP API"""
    code_value: str = Field(..., description="Code value", example="CIT", alias="codeValue")
    short_name: Optional[str] = Field(None, description="Short name", example="Citizen", alias="shortName")
    long_name: Optional[str] = Field(None, description="Long name", example="Citizen Employee", alias="longName")
    subdivision_type: Optional[str] = Field(None, description="Subdivision type", example="INSEE", alias="subdivisionType")

    class Config:
        allow_population_by_field_name = True

class PreferredSalutation(BaseModel):
    """Preferred salutation structure"""
    salutation_code: Optional[CodeValue] = Field(None, description="Salutation code", example={"codeValue": "M"}, alias="salutationCode")

    class Config:
        allow_population_by_field_name = True

class PersonalName(BaseModel):
    """Person name structure"""
    given_name: str = Field(..., description="Given name", example="CITREQUIREDDATA", alias="givenName")
    family_name_1: str = Field(..., description="Family name 1", example="COMPLETEDHIRE", alias="familyName1")
    family_name_2: Optional[str] = Field(None, description="Family name 2", example="SMITH", alias="familyName2")
    middle_name: Optional[str] = Field(None, description="Middle name", example="JOHN", alias="middleName")
    formatted_name: Optional[str] = Field(None, description="Formatted name", example="COMPLETEDHIRE, CITREQUIREDDATA", alias="formattedName")
    preferred_salutations: Optional[List[PreferredSalutation]] = Field(None, description="Preferred salutations", example=[{"salutationCode": {"codeValue": "M"}}], alias="preferredSalutations")

    class Config:
        allow_population_by_field_name = True

class BirthPlace(BaseModel):
    """Birth place structure"""
    city_name: Optional[str] = Field(None, description="City name", example="PARIS", alias="cityName")
    postal_code: Optional[str] = Field(None, description="Postal code", example="75001", alias="postalCode")
    country_code: Optional[str] = Field(None, description="Country code", example="FR", alias="countryCode")
    country_subdivision_level_1: Optional[CodeValue] = Field(None, description="Country subdivision level 1", example={"codeValue": "100"}, alias="countrySubdivisionLevel1")

    class Config:
        allow_population_by_field_name = True

class Address(BaseModel):
    """Address structure"""
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "66382041300198", "shortName": "SIRET"}, alias="nameCode")
    line_one: str = Field(..., description="Address line one", example="COMPLEMENT ADRESSE", alias="lineOne")
    line_two: str = Field(..., description="Address line two", example="209 B RUE ANATOLE FRANCE", alias="lineTwo")
    line_five: Optional[str] = Field(None, description="Address line five", example="PORT JEAN", alias="lineFive")
    city_name: str = Field(..., description="City name", example="LEVALLOIS PERRET", alias="cityName")
    postal_code: str = Field(..., description="Postal code", example="92688", alias="postalCode")
    country_code: str = Field(..., description="Country code", example="FR", alias="countryCode")
    country_subdivision_level_1: Optional[CodeValue] = Field(None, description="Country subdivision level 1", example={"codeValue": "IDF"}, alias="countrySubdivisionLevel1")
    country_subdivision_level_2: CodeValue = Field(..., description="Country subdivision level 2", example={"codeValue": "LOCALITE", "shortName": "LOCALITE", "longName": "LOCALITE", "subdivisionType": "INSEE"}, alias="countrySubdivisionLevel2")
    unit: str = Field(..., description="Unit", example="453B", alias="unit")
    building_number: Optional[str] = Field(None, description="Building number", example="209", alias="buildingNumber")
    building_number_extension: Optional[str] = Field(None, description="Building number extension", example="B", alias="buildingNumberExtension")
    street_name: Optional[str] = Field(None, description="Street name", example="RUE ANATOLE FRANCE", alias="streetName")

    class Config:
        allow_population_by_field_name = True

class WorkLocation(BaseModel):
    """Work location structure"""
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "02003", "shortName": "ORION CONSEIL LEVALLOIS", "longName": "ORION CONSEIL LEVALLOIS"}, alias="nameCode")
    address: Address = Field(..., description="Address", alias="address")
    item_id: str = Field(..., description="Item ID", example="default", alias="itemID")

    class Config:
        allow_population_by_field_name = True

class OrganizationalUnit(BaseModel):
    """Organizational unit structure"""
    item_id: str = Field(..., description="Item ID", example="departmentId", alias="itemID")
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "111111"}, alias="nameCode")

    class Config:
        allow_population_by_field_name = True

class AmountValue(BaseModel):
    """Amount value structure for monetary amounts"""
    amount_value: Optional[Union[int, float]] = Field(None, description="Amount value", example=3500.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

    class Config:
        allow_population_by_field_name = True

class MonthlyRateAmount(BaseModel):
    """Monthly rate amount structure"""
    amount_value: Optional[Union[int, float]] = Field(None, description="Monthly salary amount", example=3500.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

    class Config:
        allow_population_by_field_name = True

class PayPeriodRateAmount(BaseModel):
    """Pay period rate amount structure"""
    amount_value: Optional[Union[int, float]] = Field(None, description="Pay period rate amount", example=1500.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

    class Config:
        allow_population_by_field_name = True

class AnnualRateAmount(BaseModel):
    """Annual rate amount structure"""
    amount_value: Optional[Union[int, float]] = Field(None, description="Annual rate amount", example=42000.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

    class Config:
        allow_population_by_field_name = True

class BaseRemuneration(BaseModel):
    """Base remuneration structure"""
    recording_basis_code: Optional[CodeValue] = Field(None, description="Recording basis code for theoretical annual salary type (controlled by CSAT reference table)", alias="recordingBasisCode")
    monthly_rate_amount: Optional[MonthlyRateAmount] = Field(None, description="Monthly salary amount", alias="monthlyRateAmount")
    pay_period_rate_amount: Optional[PayPeriodRateAmount] = Field(None, description="Pay period rate amount", alias="payPeriodRateAmount")
    annual_rate_amount: Optional[AnnualRateAmount] = Field(None, description="Annual rate amount", alias="annualRateAmount")

    class Config:
        allow_population_by_field_name = True

class CustomAmountField(BaseModel):
    """Custom amount field structure for monetary values"""
    item_id: str = Field(..., description="Item ID", example="internshipCompensation", alias="itemID")
    amount_value: Optional[Union[int, float]] = Field(None, description="Amount value", example=500.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

    class Config:
        allow_population_by_field_name = True

class CustomFieldItem(BaseModel):
    """Custom field item structure

    Salary-related field IDs:
    - 'workSchedule': Pay hourly class code (controlled by HPR reference table)
    - 'remunerationType': Payroll category (controlled by TYPRE reference table)
    - 'modeRemSATH': Remuneration mode (filter table CSAT, required for recordingBasisCode updates)
    - 'oldSATH': Theoretical annual salary code (old management) - ATOO only (controlled by CSATH reference table)
    """
    item_id: str = Field(..., description="Item ID", example="workSchedule", alias="itemID")
    code_value: Optional[str] = Field(None, description="Code value", example="HPR001", alias="codeValue")
    long_name: Optional[str] = Field(None, description="Long name", example="Pay Hourly Class", alias="longName")

    # Additional custom fields
    short_name: Optional[str] = Field(None, description="Short name", example="SAL", alias="shortName")

    class Config:
        allow_population_by_field_name = True

class CustomStringField(BaseModel):
    """Custom string field structure"""
    item_id: str = Field(..., description="Item ID", example="customField1", alias="itemID")
    string_value: str = Field(..., description="String value", example="Custom string value", alias="stringValue")

    class Config:
        allow_population_by_field_name = True

class CustomDateField(BaseModel):
    """Custom date field structure"""
    item_id: str = Field(..., description="Item ID", example="customDateField", alias="itemID")
    date_value: str = Field(..., description="Date value", example="2024-01-01", alias="dateValue")

    class Config:
        allow_population_by_field_name = True

class CustomNumberField(BaseModel):
    """Custom number field structure"""
    item_id: str = Field(..., description="Item ID", example="customNumberField", alias="itemID")
    number_value: Union[int, float] = Field(..., description="Number value", example=42.5, alias="numberValue")

    class Config:
        allow_population_by_field_name = True

class CustomIndicatorField(BaseModel):
    """Custom indicator field structure"""
    item_id: str = Field(..., description="Item ID", example="customIndicatorField", alias="itemID")
    indicator_value: bool = Field(..., description="Indicator value", example=True, alias="indicatorValue")

    class Config:
        allow_population_by_field_name = True

class CustomFieldGroup(BaseModel):
    """Custom field group structure

    Salary-related code fields:
    - 'workSchedule': Pay hourly class code (Code classe horaire de rémunération) - controlled by HPR reference table
    - 'remunerationType': Payroll category (Classe de Rémunération) - controlled by TYPRE reference table
    - 'modeRemSATH': Remuneration mode (Mode de rémunération) - filter table CSAT, required to update recordingBasisCode
    - 'oldSATH': Theoretical annual salary code (old management) - ATOO only, controlled by CSATH reference table

    Salary-related amount fields:
    - 'internshipCompensation': Internship compensation (Indemnité de stage) - ZEM client only, for interns with remunerationType = 'S'
    """
    code_fields: Optional[List[CustomFieldItem]] = Field(None, description="Code fields including salary codes", example=[{"itemID": "workSchedule", "codeValue": "HPR001"}, {"itemID": "remunerationType", "codeValue": "S"}, {"itemID": "modeRemSATH", "codeValue": "MONTHLY"}], alias="codeFields")
    string_fields: Optional[List[CustomStringField]] = Field(None, description="String fields", alias="stringFields")
    date_fields: Optional[List[CustomDateField]] = Field(None, description="Date fields", alias="dateFields")
    number_fields: Optional[List[CustomNumberField]] = Field(None, description="Number fields", alias="numberFields")
    amount_fields: Optional[List[CustomAmountField]] = Field(None, description="Amount fields for monetary values", example=[{"itemID": "internshipCompensation", "amountValue": 500.00}], alias="amountFields")
    indicator_fields: Optional[List[CustomIndicatorField]] = Field(None, description="Indicator fields", alias="indicatorFields")

    class Config:
        allow_population_by_field_name = True

class WorkAssignment(BaseModel):
    """Work assignment structure for hire request"""
    hire_date: str = Field(..., description="Hire date", example="2019-08-01", alias="hireDate")  # ISO date string
    seniority_date: Optional[str] = Field(None, description="Seniority date", example="2019-08-01", alias="seniorityDate")  # ISO date string
    expected_start_date: Optional[str] = Field(None, description="Expected Start Date", example="2019-08-01", alias="expectedStartDate")  # ISO date string
    expected_termination_date: Optional[str] = Field(None, description="Expected termination date", example="2024-12-31", alias="expectedTerminationDate")
    work_arrangement_code: CodeValue = Field(..., description="Work arrangement code", example={"codeValue": "900"}, alias="workArrangementCode")
    job_code: Optional[CodeValue] = Field(None, description="Job code", example={"codeValue": "DEV001"}, alias="jobCode")
    job_title: Optional[str] = Field(None, description="Job title", example="Software Developer", alias="jobTitle")
    job_function_code: Optional[CodeValue] = Field(None, description="Job function code", example={"codeValue": "IT"}, alias="jobFunctionCode")
    worker_type_code: Optional[CodeValue] = Field(None, description="Worker type code", example={"codeValue": "EMP"}, alias="workerTypeCode")
    assignment_status: Optional[Dict[str, CodeValue]] = Field(None, description="Assignment status", example={"reasonCode": {"codeValue": "1"}}, alias="assignmentStatus")
    payroll_processing_status_code: Optional[CodeValue] = Field(None, description="Payroll processing status code", example={"codeValue": "I"}, alias="payrollProcessingStatusCode")
    occupational_classifications: Optional[List[Dict[str, CodeValue]]] = Field(None, description="Occupational classifications", alias="occupationalClassifications")
    worker_groups: Optional[List[Dict[str, CodeValue]]] = Field(None, description="Worker groups", alias="workerGroups")
    assigned_work_locations: List[WorkLocation] = Field(..., description="Assigned work locations", alias="assignedWorkLocations")
    assigned_organizational_units: Optional[List[OrganizationalUnit]] = Field(None, description="Assigned organizational units", alias="assignedOrganizationalUnits")
    custom_field_group: CustomFieldGroup = Field(..., description="Custom field group", alias="customFieldGroup")
    base_remuneration: Optional[BaseRemuneration] = Field(None, description="Base remuneration with salary information", alias="baseRemuneration")
    remuneration_basis_code: Optional[CodeValue] = Field(None, description="Remuneration basis code (matches get method path)", alias="remunerationBasisCode")

    legal_entity_code: Optional[CodeValue] = Field(None, description="Legal entity code", example={"codeValue": "LE001", "longName": "Company Name"}, alias="legalEntityCode")
    assignment_cost_centers: Optional[List[Dict[str, Any]]] = Field(None, description="Assignment cost centers", example=[{"costCenterID": "CC001", "costCenterName": "Cost Center 1", "costCenterPercentage": 100.0}], alias="assignmentCostCenters")

    collaboration_type: Optional[str] = Field(None, description="Collaboration type", example="SAL", alias="collaborationType")
    contract_type: Optional[str] = Field(None, description="Contract type", example="00", alias="contractType")
    activity: Optional[str] = Field(None, description="Activity", example="01", alias="activity")
    remuneration_type: Optional[str] = Field(None, description="Remuneration type", example="B", alias="remunerationType")
    work_schedule: Optional[str] = Field(None, description="Work schedule", example="101", alias="workSchedule")
    tlm: Optional[str] = Field(None, description="TLM", example="Z", alias="TLM")

    class Config:
        allow_population_by_field_name = True

class Communication(BaseModel):
    """Communication structure"""
    emails: Optional[List[Dict[str, str]]] = Field(None, description="Emails", alias="emails")
    landlines: Optional[List[Dict[str, str]]] = Field(None, description="Landlines", alias="landlines")
    mobiles: Optional[List[Dict[str, str]]] = Field(None, description="Mobiles", alias="mobiles")
    faxes: Optional[List[Dict[str, str]]] = Field(None, description="Faxes", alias="faxes")

    class Config:
        allow_population_by_field_name = True

class MaritalStatusCode(BaseModel):
    """Marital status with effective date"""
    code_value: Optional[str] = Field(None, description="Marital status code", example="M", alias="codeValue")
    effective_date: Optional[str] = Field(None, description="Effective date", example="2019-08-01", alias="effectiveDate")

    class Config:
        allow_population_by_field_name = True

class Person(BaseModel):
    """Person structure for hire request"""
    legal_name: PersonalName = Field(..., description="Legal name", alias="legalName")
    gender_code: CodeValue = Field(..., description="Gender code", example={"codeValue": "M"}, alias="genderCode")
    birth_date: Optional[str] = Field(None, description="Birth date", example="1990-01-01", alias="birthDate")  # ISO date string
    birth_place: Optional[BirthPlace] = Field(None, description="Birth place", alias="birthPlace")
    marital_status_code: Optional[MaritalStatusCode] = Field(None, description="Marital status code", example={"codeValue": "M", "effectiveDate": "2006-08-01"}, alias="maritalStatusCode")
    citizenship_country_codes: Optional[List[CodeValue]] = Field(None, description="Citizenship country codes", alias="citizenshipCountryCodes")
    identity_documents: Optional[List[Dict[str, str]]] = Field(None, description="Identity documents", alias="identityDocuments")
    # SSN convenience field (will be added to identity_documents)
    identity_document_ssn: Optional[str] = Field(None, description="Social Security Number", example="1234567890123")
    legal_address: Optional[Address] = Field(None, description="Legal address", alias="legalAddress")
    communication: Optional[Communication] = Field(None, description="Communication", alias="communication")
    other_personal_addresses: Optional[List[Dict]] = Field(None, description="Other personal addresses", alias="otherPersonalAddresses")
    social_insurance_programs: Optional[List[Dict]] = Field(None, description="Social insurance programs", alias="socialInsurancePrograms")
    immigration_documents: Optional[List[Dict]] = Field(None, description="Immigration documents", alias="immigrationDocuments")

    class Config:
        allow_population_by_field_name = True

class Worker(BaseModel):
    """Worker structure for hire request"""
    worker_id: Optional[Dict[str, str]] = Field(None, description="Worker ID", example={"idValue": "12345"}, alias="workerID")  # {"idValue": "12345"}
    worker_dates: Optional[Dict[str, str]] = Field(None, description="Worker dates", example={"originalHireDate": "2019-08-01"}, alias="workerDates")
    person: Person = Field(..., description="Person", alias="person")
    work_assignment: WorkAssignment = Field(..., description="Work assignment", alias="workAssignment")
    business_communication: Optional[Communication] = Field(None, description="Business communication", alias="businessCommunication")

    class Config:
        allow_population_by_field_name = True

class Transform(BaseModel):
    """Transform structure for hire request"""
    event_status_code: CodeValue = Field(..., description="Event status code", example={"codeValue": "Completed"}, alias="eventStatusCode")
    worker: Worker = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True

class HireData(BaseModel):
    """Data structure for hire request"""
    transform: Transform = Field(..., description="Transform", alias="transform")

    class Config:
        allow_population_by_field_name = True

class HireEvent(BaseModel):
    """Single hire event structure"""
    data: HireData = Field(..., description="Data", alias="data")

    class Config:
        allow_population_by_field_name = True

class WorkerHireRequest(BaseModel):
    """Main model for ADP Worker Hire POST request"""
    events: List[HireEvent] = Field(..., description="Events", example=[{"data": {"transform": {"eventStatusCode": {"codeValue": "Completed"}}}}], alias="events")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True


# ==================================================================================================
# PYDANTIC MODELS FOR WORKER TERMINATE REQUEST (SIMPLIFIED STRUCTURE)
# ==================================================================================================

class WorkerTerminateEventData(BaseModel):
    """Simplified termination event data"""

    # Event Context
    associate_oid: str = Field(..., description="Associate OID", example="tschulz-mp3", alias="eventContext.worker.associateOID")

    # Transform - Worker Dates
    termination_date: str = Field(..., description="Termination date", example="2022-03-31", alias="transform.worker.workerDates.terminationDate")

    # Transform - Termination Reason
    termination_reason_code: str = Field(..., description="Termination reason code", example="DM", alias="transform.worker.terminationReasonCode.codeValue")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


# ==================================================================================================
# PYDANTIC MODELS FOR WORKER REHIRE REQUEST
# ==================================================================================================

class RehireCustomFieldItem(BaseModel):
    """Custom field item with itemID structure for rehire

    Salary-related field IDs:
    - 'workSchedule': Pay hourly class code (controlled by HPR reference table)
    - 'remunerationType': Payroll category (controlled by TYPRE reference table)
    - 'modeRemSATH': Remuneration mode (filter table CSAT, required for recordingBasisCode updates)
    - 'oldSATH': Theoretical annual salary code (old management) - ATOO only (controlled by CSATH reference table)
    """
    item_id: str = Field(..., description="Item ID", example="workSchedule", alias="itemID")
    code_value: Optional[str] = Field(None, description="Code value", example="HPR001", alias="codeValue")
    long_name: Optional[str] = Field(None, description="Long name", example="Pay Hourly Class", alias="longName")

    class Config:
        allow_population_by_field_name = True

class RehireCustomFieldGroup(BaseModel):
    """Custom field group structure for rehire

    Salary-related code fields:
    - 'workSchedule': Pay hourly class code (Code classe horaire de rémunération) - controlled by HPR reference table
    - 'remunerationType': Payroll category (Classe de Rémunération) - controlled by TYPRE reference table
    - 'modeRemSATH': Remuneration mode (Mode de rémunération) - filter table CSAT, required to update recordingBasisCode
    - 'oldSATH': Theoretical annual salary code (old management) - ATOO only, controlled by CSATH reference table

    Salary-related amount fields:
    - 'internshipCompensation': Internship compensation (Indemnité de stage) - ZEM client only, for interns with remunerationType = 'S'
    """
    code_fields: Optional[List[CustomFieldItem]] = Field(None, description="Code fields including salary codes", example=[{"itemID": "workSchedule", "codeValue": "HPR001"}, {"itemID": "remunerationType", "codeValue": "S"}, {"itemID": "modeRemSATH", "codeValue": "MONTHLY"}], alias="codeFields")
    string_fields: Optional[List[CustomStringField]] = Field(None, description="String fields", alias="stringFields")
    date_fields: Optional[List[CustomDateField]] = Field(None, description="Date fields", alias="dateFields")
    number_fields: Optional[List[CustomNumberField]] = Field(None, description="Number fields", alias="numberFields")
    amount_fields: Optional[List[CustomAmountField]] = Field(None, description="Amount fields for monetary values", example=[{"itemID": "internshipCompensation", "amountValue": 500.00}], alias="amountFields")
    indicator_fields: Optional[List[CustomIndicatorField]] = Field(None, description="Indicator fields", alias="indicatorFields")

    class Config:
        allow_population_by_field_name = True

class RehireOrganizationalUnit(BaseModel):
    """Organizational unit with itemID for rehire"""
    item_id: str = Field(..., description="Item ID", example="departmentId", alias="itemID")
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "111111"}, alias="nameCode")

    class Config:
        allow_population_by_field_name = True

class RehireWorkerGroup(BaseModel):
    """Worker group structure for rehire"""
    group_code: CodeValue = Field(..., description="Group code", example={"codeValue": "00"}, alias="groupCode")

    class Config:
        allow_population_by_field_name = True

class RehireOccupationalClassification(BaseModel):
    """Occupational classification structure for rehire"""
    classification_code: CodeValue = Field(..., description="Classification code", example={"codeValue": "CA1"}, alias="classificationCode")

    class Config:
        allow_population_by_field_name = True

class BusinessCommunication(BaseModel):
    """Business communication structure"""
    emails: Optional[List[Dict[str, str]]] = Field(None, description="Emails", example=[{"emailUri": "testmail.lsprh@adp.com"}], alias="emails")
    landlines: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description="Landlines", example=[{"formattedNumber": "50 32"}], alias="landlines")
    mobiles: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description="Mobiles", example=[{"formattedNumber": "06 88 77 99 55"}], alias="mobiles")
    faxes: Optional[List[Dict[str, Union[str, int]]]] = Field(None, description="Faxes", example=[{"formattedNumber": "02 51 13 96 63"}], alias="faxes")

    class Config:
        allow_population_by_field_name = True

class WorkerDates(BaseModel):
    """Worker dates structure for rehire"""
    original_hire_date: Optional[str] = Field(None, description="Original hire date", example="2022-03-31", alias="originalHireDate")
    first_hire_date: Optional[str] = Field(None, description="First hire date", example="2020-01-01", alias="firstHireDate")
    termination_date: Optional[str] = Field(None, description="Termination date", example="2022-03-30", alias="terminationDate")

    class Config:
        allow_population_by_field_name = True

class SocialInsuranceProgram(BaseModel):
    """Social insurance program structure"""
    program_service_center: Optional[Dict[str, CodeValue]] = Field(None, description="Program service center", example={"nameCode": {"codeValue": "53"}}, alias="programServiceCenter")

    class Config:
        allow_population_by_field_name = True

class OtherPersonalAddress(BaseModel):
    """Other personal address structure"""
    country_subdivision_level_1: Optional[CodeValue] = Field(None, description="Country subdivision level 1", example={"codeValue": "THOUARE SUR LOIRE"}, alias="countrySubdivisionLevel1")
    country_subdivision_level_2: Optional[CodeValue] = Field(None, description="Country subdivision level 2", example={"codeValue": "44204", "longName": "THOUARE SUR LOIRE"}, alias="countrySubdivisionLevel2")
    postal_code: Optional[str] = Field(None, description="Postal code", example="44470", alias="postalCode")
    line_five: Optional[str] = Field(None, description="Line five", example="PORT JEAN", alias="lineFive")
    building_number: Optional[str] = Field(None, description="Building number", example="1", alias="buildingNumber")
    building_number_extension: Optional[str] = Field(None, description="Building number extension", example="B", alias="buildingNumberExtension")
    street_name: Optional[str] = Field(None, description="Street name", example="RUE AUGUSTIN FRESNEL", alias="streetName")

    class Config:
        allow_population_by_field_name = True

class RehireAddress(BaseModel):
    """Enhanced address structure for rehire"""
    line_one: Optional[str] = Field(None, description="Address line one", example="123 MAIN STREET", alias="lineOne")
    line_two: Optional[str] = Field(None, description="Address line two", example="APT 456", alias="lineTwo")
    line_five: Optional[str] = Field(None, description="Line five", example="PORT JEAN", alias="lineFive")
    city_name: Optional[str] = Field(None, description="City name", example="THOUARE SUR LOIRE", alias="cityName")
    postal_code: Optional[str] = Field(None, description="Postal code", example="44470", alias="postalCode")
    country_code: Optional[str] = Field(None, description="Country code", example="FR", alias="countryCode")
    country_subdivision_level_1: Optional[CodeValue] = Field(None, description="Country subdivision level 1", example={"codeValue": "THOUARE SUR LOIRE"}, alias="countrySubdivisionLevel1")
    country_subdivision_level_2: Optional[CodeValue] = Field(None, description="Country subdivision level 2", example={"codeValue": "44204", "longName": "THOUARE SUR LOIRE"}, alias="countrySubdivisionLevel2")
    building_number: Optional[str] = Field(None, description="Building number", example="1", alias="buildingNumber")
    building_number_extension: Optional[str] = Field(None, description="Building number extension", example="XX", alias="buildingNumberExtension")
    building_name: Optional[str] = Field(None, description="Building name", example="XX", alias="buildingName")
    street_name: Optional[str] = Field(None, description="Street name", example="RUE AUGUSTIN FRESNEL", alias="streetName")

    class Config:
        allow_population_by_field_name = True

class RehirePerson(BaseModel):
    """Enhanced person structure for rehire"""
    legal_name: Optional[PersonalName] = Field(None, description="Legal name", alias="legalName")
    gender_code: Optional[CodeValue] = Field(None, description="Gender code", example={"codeValue": "M"}, alias="genderCode")
    marital_status_code: Optional[MaritalStatusCode] = Field(None, description="Marital status code", alias="maritalStatusCode")
    birth_date: Optional[str] = Field(None, description="Birth date", example="1979-09-19", alias="birthDate")
    birth_place: Optional[BirthPlace] = Field(None, description="Birth place", alias="birthPlace")
    citizenship_country_codes: Optional[List[CodeValue]] = Field(None, description="Citizenship country codes", alias="citizenshipCountryCodes")
    identity_documents: Optional[List[Dict[str, str]]] = Field(None, description="Identity documents", example=[{"documentID": "1790975200032"}], alias="identityDocuments")
    legal_address: Optional[RehireAddress] = Field(None, description="Legal address", alias="legalAddress")
    other_personal_addresses: Optional[List[OtherPersonalAddress]] = Field(None, description="Other personal addresses", alias="otherPersonalAddresses")
    social_insurance_programs: Optional[List[SocialInsuranceProgram]] = Field(None, description="Social insurance programs", alias="socialInsurancePrograms")
    communication: Optional[BusinessCommunication] = Field(None, description="Communication", alias="communication")

    class Config:
        allow_population_by_field_name = True

class AssignmentStatus(BaseModel):
    """Assignment status structure"""
    reason_code: CodeValue = Field(..., description="Reason code", example={"codeValue": "1"}, alias="reasonCode")

    class Config:
        allow_population_by_field_name = True

class RehireWorkAssignment(BaseModel):
    """Enhanced work assignment structure for rehire"""
    hire_date: str = Field(..., description="Hire date", example="2022-03-31", alias="hireDate")
    seniority_date: Optional[str] = Field(None, description="Seniority date", example="2022-03-31", alias="seniorityDate")  # ISO date string
    expected_start_date: Optional[str] = Field(None, description="Expected Start Date", example="2022-03-31", alias="expectedStartDate")  # ISO date string
    expected_termination_date: Optional[str] = Field(None, description="Expected termination date", example="2024-12-31", alias="expectedTerminationDate")
    assignment_status: Optional[AssignmentStatus] = Field(None, description="Assignment status", alias="assignmentStatus")
    work_arrangement_code: Optional[CodeValue] = Field(None, description="Work arrangement code", example={"codeValue": "900"}, alias="workArrangementCode")
    job_code: Optional[CodeValue] = Field(None, description="Job code", example={"codeValue": "EMPL1"}, alias="jobCode")
    job_title: Optional[str] = Field(None, description="Job title", example="AAA CODE AAA", alias="jobTitle")
    job_function_code: Optional[CodeValue] = Field(None, description="Job function code", example={"codeValue": "10"}, alias="jobFunctionCode")
    worker_type_code: Optional[CodeValue] = Field(None, description="Worker type code", example={"codeValue": "00"}, alias="workerTypeCode")
    occupational_classifications: Optional[List[RehireOccupationalClassification]] = Field(None, description="Occupational classifications", alias="occupationalClassifications")
    worker_groups: Optional[List[RehireWorkerGroup]] = Field(None, description="Worker groups", alias="workerGroups")
    assigned_work_locations: Optional[List[WorkLocation]] = Field(None, description="Assigned work locations", alias="assignedWorkLocations")
    assigned_organizational_units: Optional[List[RehireOrganizationalUnit]] = Field(None, description="Assigned organizational units", alias="assignedOrganizationalUnits")
    custom_field_group: Optional[CustomFieldGroup] = Field(None, description="Custom field group", alias="customFieldGroup")
    base_remuneration: Optional[BaseRemuneration] = Field(None, description="Base remuneration with salary information", alias="baseRemuneration")

    legal_entity_code: Optional[CodeValue] = Field(None, description="Legal entity code", example={"codeValue": "LE001", "longName": "Company Name"}, alias="legalEntityCode")
    assignment_cost_centers: Optional[List[Dict[str, Any]]] = Field(None, description="Assignment cost centers", example=[{"costCenterID": "CC001", "costCenterName": "Cost Center 1", "costCenterPercentage": 100.0}], alias="assignmentCostCenters")

    collaboration_type: Optional[str] = Field(None, description="Collaboration type", example="SAL", alias="collaborationType")
    contract_type: Optional[str] = Field(None, description="Contract type", example="00", alias="contractType")
    activity: Optional[str] = Field(None, description="Activity", example="01", alias="activity")
    remuneration_type: Optional[str] = Field(None, description="Remuneration type", example="B", alias="remunerationType")
    work_schedule: Optional[str] = Field(None, description="Work schedule", example="101", alias="workSchedule")
    tlm: Optional[str] = Field(None, description="TLM", example="Z", alias="TLM")

    class Config:
        allow_population_by_field_name = True

class RehireWorker(BaseModel):
    """Worker structure for rehire request"""
    associate_oid: str = Field(..., description="Associate OID", example="rgrehirefami-7120mp2", alias="associateOID")
    person: Optional[RehirePerson] = Field(None, description="Person", alias="person")
    worker_dates: Optional[WorkerDates] = Field(None, description="Worker dates", alias="workerDates")
    business_communication: Optional[BusinessCommunication] = Field(None, description="Business communication", alias="businessCommunication")
    work_assignment: Optional[RehireWorkAssignment] = Field(None, description="Work assignment", alias="workAssignment")

    class Config:
        allow_population_by_field_name = True

class RehireTransform(BaseModel):
    """Transform structure for rehire request"""
    effective_date_time: Optional[str] = Field(None, description="Effective date time", example="2022-03-31", alias="effectiveDateTime")
    event_status_code: CodeValue = Field(..., description="Event status code", example={"codeValue": "Completed"}, alias="eventStatusCode")
    worker: RehireWorker = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True

class RehireData(BaseModel):
    """Data structure for rehire request"""
    transform: RehireTransform = Field(..., description="Transform", alias="transform")

    class Config:
        allow_population_by_field_name = True

class RehireEvent(BaseModel):
    """Single rehire event structure"""
    data: RehireData = Field(..., description="Data", alias="data")

    class Config:
        allow_population_by_field_name = True

class WorkerRehireRequest(BaseModel):
    """Main model for ADP Worker Rehire POST request"""
    events: List[RehireEvent] = Field(..., description="Events", example=[{"data": {"transform": {"eventStatusCode": {"codeValue": "Completed"}}}}], alias="events")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True

class WorkerUpdateRequest(BaseModel):
    """
    Schema for worker field updates - all fields are optional
    """
    # Personal Information
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD format")
    birth_place_city_name: Optional[str] = Field(None, description="Birth place city name")
    birth_place_country_code: Optional[str] = Field(None, description="Birth place country code")
    birth_place_postal_code: Optional[str] = Field(None, description="Birth place postal code")
    gender: Optional[str] = Field(None, description="Gender code (M/F)")
    citizenship_code: Optional[str] = Field(None, description="Citizenship country code")
    citizenship_short_name: Optional[str] = Field(None, description="Citizenship short name")
    citizenship_long_name: Optional[str] = Field(None, description="Citizenship long name")
    legal_name_given: Optional[str] = Field(None, description="Legal name given name")
    legal_name_family_1: Optional[str] = Field(None, description="Legal name family name 1")
    legal_name_family_2: Optional[str] = Field(None, description="Legal name family name 2")
    legal_name_middle: Optional[str] = Field(None, description="Legal name middle name")
    legal_name_salutation: Optional[str] = Field(None, description="Legal name salutation code")
    marital_status_effective_date: Optional[str] = Field(None, description="Marital status effective date")
    marital_status_code: Optional[str] = Field(None, description="Marital status code")

    # Business Communication
    business_email: Optional[str] = Field(None, description="Business email address")
    business_fax: Optional[str] = Field(None, description="Business fax number")
    business_landline: Optional[str] = Field(None, description="Business landline number")
    business_mobile: Optional[str] = Field(None, description="Business mobile number")
    business_pager: Optional[str] = Field(None, description="Business pager number")

    # Personal Communication
    personal_email: Optional[str] = Field(None, description="Personal email address")
    personal_fax: Optional[str] = Field(None, description="Personal fax number")
    personal_landline: Optional[str] = Field(None, description="Personal landline number")
    personal_mobile: Optional[str] = Field(None, description="Personal mobile number")

    # Legal Address
    legal_address_country_code: Optional[str] = Field(None, description="Legal address country code")
    legal_address_postal_code: Optional[str] = Field(None, description="Legal address postal code")
    legal_address_line_five: Optional[str] = Field(None, description="Legal address line five")
    legal_address_building_number: Optional[str] = Field(None, description="Legal address building number")
    legal_address_building_extension: Optional[str] = Field(None, description="Legal address building extension")
    legal_address_street_name: Optional[str] = Field(None, description="Legal address street name")
    legal_address_subdivision_1: Optional[str] = Field(None, description="Legal address subdivision level 1")
    legal_address_subdivision_2_code: Optional[str] = Field(None, description="Legal address subdivision level 2 code")
    legal_address_subdivision_2_name: Optional[str] = Field(None, description="Legal address subdivision level 2 name")

    # Personal Address
    personal_address_country_code: Optional[str] = Field(None, description="Personal address country code")
    personal_address_city_name: Optional[str] = Field(None, description="Personal address city name")
    personal_address_postal_code: Optional[str] = Field(None, description="Personal address postal code")
    personal_address_line_five: Optional[str] = Field(None, description="Personal address line five")
    personal_address_building_number: Optional[str] = Field(None, description="Personal address building number")
    personal_address_building_extension: Optional[str] = Field(None, description="Personal address building extension")
    personal_address_street_name: Optional[str] = Field(None, description="Personal address street name")
    personal_address_subdivision_2_code: Optional[str] = Field(None, description="Personal address subdivision level 2 code")
    personal_address_subdivision_2_name: Optional[str] = Field(None, description="Personal address subdivision level 2 name")


    class Config:
        extra = "ignore"
