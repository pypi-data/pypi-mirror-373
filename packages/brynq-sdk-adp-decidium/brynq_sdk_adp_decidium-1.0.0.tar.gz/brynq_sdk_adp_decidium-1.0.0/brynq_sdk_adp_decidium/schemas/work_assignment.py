from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------
# Worker Work Assignment Modify Request Schemas
# ---------------------------

class CodeValue(BaseModel):
    """Code value structure used throughout ADP API"""
    code_value: str = Field(..., description="Code value", example="CIT", alias="codeValue")
    short_name: Optional[str] = Field(None, description="Short name", example="Citizen", alias="shortName")
    long_name: Optional[str] = Field(None, description="Long name", example="Citizen Employee", alias="longName")
    subdivision_type: Optional[str] = Field(None, description="Subdivision type", example="INSEE", alias="subdivisionType")

    class Config:
        allow_population_by_field_name = True

class WorkerID(BaseModel):
    """Worker ID structure"""
    id_value: str = Field(..., description="Worker ID value", example="12345", alias="idValue")

    class Config:
        allow_population_by_field_name = True

class EventContext(BaseModel):
    """Event context structure"""
    associate_oid: str = Field(..., description="Associate OID", example="123456789", alias="associateOID")
    work_assignment_id: Optional[str] = Field(None, description="Work assignment ID", example="WA001", alias="workAssignmentID")
    worker_id: Optional[WorkerID] = Field(None, description="Worker ID", alias="workerID")

    class Config:
        allow_population_by_field_name = True

class WorkLocation(BaseModel):
    """Work location structure"""
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "02003", "shortName": "ORION CONSEIL LEVALLOIS", "longName": "ORION CONSEIL LEVALLOIS"}, alias="nameCode")
    item_id: Optional[str] = Field(None, description="Item ID", example="default", alias="itemID")

    class Config:
        allow_population_by_field_name = True

class OrganizationalUnit(BaseModel):
    """Organizational unit structure"""
    item_id: str = Field(..., description="Item ID", example="departmentId", alias="itemID")
    name_code: CodeValue = Field(..., description="Name code", example={"codeValue": "111111"}, alias="nameCode")

    class Config:
        allow_population_by_field_name = True

class WorkerGroup(BaseModel):
    """Worker group structure"""
    group_code: CodeValue = Field(..., description="Group code", alias="groupCode")

    class Config:
        allow_population_by_field_name = True

class AssignmentCostCenter(BaseModel):
    """Assignment cost center structure"""
    cost_center_id: str = Field(..., description="Cost center ID", example="CC001", alias="costCenterID")
    cost_center_name: Optional[str] = Field(None, description="Cost center name", example="Cost Center 1", alias="costCenterName")
    cost_center_percentage: float = Field(..., description="Cost center percentage", example=100.0, alias="costCenterPercentage")

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
    short_name: Optional[str] = Field(None, description="Short name", alias="shortName")
    long_name: Optional[str] = Field(None, description="Long name", example="Pay Hourly Class", alias="longName")

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

class CustomAmountField(BaseModel):
    """Custom amount field structure for monetary values"""
    item_id: str = Field(..., description="Item ID", example="internshipCompensation", alias="itemID")
    amount_value: Optional[Union[int, float]] = Field(None, description="Amount value", example=500.00, alias="amountValue")
    currency_code: Optional[str] = Field(None, description="Currency code", example="EUR", alias="currencyCode")

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

class WorkAssignmentModify(BaseModel):
    """Work assignment modification structure"""
    # Common fields (appear in multiple examples) - MANDATORY
    custom_field_group: CustomFieldGroup = Field(..., description="Custom field group", alias="customFieldGroup")
    effective_date_time: str = Field(..., description="Effective date time (MANDATORY)", example="2024-01-01T00:00:00Z", alias="effectiveDateTime")

    # Optional fields (appear in some examples)
    job_code: Optional[CodeValue] = Field(None, description="Job code", alias="jobCode")
    work_arrangement_code: Optional[CodeValue] = Field(None, description="Work arrangement code", alias="workArrangementCode")
    assigned_work_locations: Optional[List[WorkLocation]] = Field(None, description="Assigned work locations", alias="assignedWorkLocations")
    worker_type_code: Optional[CodeValue] = Field(None, description="Worker type code", alias="workerTypeCode")
    legal_entity_id: Optional[str] = Field(None, description="Legal entity ID", example="LE001", alias="legalEntityID")
    worker_groups: Optional[List[WorkerGroup]] = Field(None, description="Worker groups", alias="workerGroups")
    assignment_cost_centers: Optional[List[AssignmentCostCenter]] = Field(None, description="Assignment cost centers", alias="assignmentCostCenters")
    base_remuneration: Optional[BaseRemuneration] = Field(None, description="Base remuneration", alias="baseRemuneration")

    # New fields for company and cost center information
    legal_entity_code: Optional[CodeValue] = Field(None, description="Legal entity code", example={"codeValue": "LE001", "longName": "Company Name"}, alias="legalEntityCode")

    # Professional category convenience fields (will be added to custom_field_group.codeFields)
    professional_category_code: Optional[str] = Field(None, description="Professional category code (will be added to customFieldGroup)", example="30")
    professional_category_name: Optional[str] = Field(None, description="Professional category name (will be added to customFieldGroup)", example="Employé")

    class Config:
        allow_population_by_field_name = True

class WorkAssignmentTransform(BaseModel):
    """Transform structure for work assignment modify request"""
    effective_date_time: Optional[str] = Field(None, description="Effective date time", example="2024-01-01T00:00:00Z", alias="effectiveDateTime")
    work_assignment: WorkAssignmentModify = Field(..., description="Work assignment", alias="workAssignment")

    class Config:
        allow_population_by_field_name = True

class WorkAssignmentData(BaseModel):
    """Data structure for work assignment modify request"""
    event_context: EventContext = Field(..., description="Event context", alias="eventContext")
    transform: WorkAssignmentTransform = Field(..., description="Transform", alias="transform")

    class Config:
        allow_population_by_field_name = True

class WorkAssignmentEvent(BaseModel):
    """Single work assignment modify event structure"""
    data: WorkAssignmentData = Field(..., description="Data", alias="data")

    class Config:
        allow_population_by_field_name = True

class WorkerWorkAssignmentModifyRequest(BaseModel):
    """Main model for ADP Worker Work Assignment Modify POST request"""
    events: List[WorkAssignmentEvent] = Field(..., description="Events", alias="events")

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True


class TerminationReasonCode(BaseModel):
    """Termination reason code structure"""
    code_value: str = Field(..., description="Termination reason code", example="MU", alias="codeValue")
    short_name: Optional[str] = Field(None, description="Termination reason short name", example="MU", alias="shortName")

    class Config:
        allow_population_by_field_name = True


class WorkAssignmentTerminate(BaseModel):
    """Work assignment termination structure"""
    termination_date: str = Field(..., description="Termination date (YYYY-MM-DD format)", example="2020-10-30", alias="terminationDate")
    termination_reason_code: TerminationReasonCode = Field(..., description="Termination reason code", alias="terminationReasonCode")

    class Config:
        allow_population_by_field_name = True


class WorkerWorkAssignmentTerminate(BaseModel):
    """Worker work assignment termination structure"""
    work_assignment: WorkAssignmentTerminate = Field(..., description="Work assignment termination", alias="workAssignment")

    class Config:
        allow_population_by_field_name = True


class TransformTerminate(BaseModel):
    """Transform structure for work assignment termination"""
    worker: WorkerWorkAssignmentTerminate = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class EventContextTerminate(BaseModel):
    """Event context structure for work assignment termination"""
    worker: Dict[str, Any] = Field(..., description="Worker", alias="worker")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class EventDataTerminate(BaseModel):
    """Event data structure for work assignment termination"""
    event_context: EventContextTerminate = Field(..., description="Event context", alias="eventContext")
    transform: TransformTerminate = Field(..., description="Transform", alias="transform")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class DocumentEventTerminate(BaseModel):
    """Document event structure for work assignment termination"""
    data: EventDataTerminate = Field(..., description="Event data", alias="data")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields


class WorkAssignmentTerminateRequest(BaseModel):
    """Work assignment termination request structure"""
    events: List[DocumentEventTerminate] = Field(..., description="Events", alias="events")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow extra fields
