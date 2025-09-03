import pandas as pd
import pandera as pa
from pandera.typing import Series
from typing import List, Dict, Optional, Union
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field

# ---------------------------
# Pay Data Input ADD/REPLACE Schemas
# ---------------------------

class CodeValue(BaseModel):
    """Code value structure used throughout ADP API

    Standard ADP code structure with value and display names
    """
    code_value: Union[str, float] = Field(..., alias="codeValue", description="Code value - REQUIRED", example="HP")
    short_name: Optional[str] = Field(None, alias="shortName", description="Short display name - optional", example="Hours Presences")
    long_name: Optional[str] = Field(None, alias="longName", description="Long display name - optional", example="Hours Presences")

    class Config:
        allow_population_by_field_name = True

class PayDataInputRate(BaseModel):
    """Rate information for earning inputs"""
    rate_value: Optional[float] = Field(None, alias="rateValue", description="Rate value - can be empty", example=0.7)
    base_multiplier_value: Optional[float] = Field(None, alias="baseMultiplierValue", description="Base multiplier value - can be empty", example=250.0)

    class Config:
        allow_population_by_field_name = True

class PayDataInputPayAllocation(BaseModel):
    """Pay allocation for earning inputs"""
    allocation_id: Optional[str] = Field(None, alias="allocationID", description="Allocation ID - can be empty", example="DEPT001")

    class Config:
        allow_population_by_field_name = True

class PayDataInputEarningInput(BaseModel):
    """Earning input data"""
    earning_code: CodeValue = Field(..., alias="earningCode", description="Earning code - REQUIRED", example={"codeValue": "0271"})
    rate: Optional[PayDataInputRate] = Field(None, description="Rate information - can be empty", example={"rateValue": 0.0, "baseMultiplierValue": 0.0})
    number_of_hours: Optional[float] = Field(None, alias="numberOfHours", description="Number of hours - can be empty", example=20.0)
    earned_pay_period_start_date: Optional[str] = Field(None, alias="earnedPayPeriodStartDate", description="Earned pay period start date - can be empty", example="2024-07-01")

    class Config:
        allow_population_by_field_name = True

class PayDataInputConfigurationTag(BaseModel):
    """Configuration tag for calculation factors"""
    tag_code: Optional[str] = Field(None, alias="tagCode", description="Tag code - can be empty", example="")
    tag_values: Optional[List[str]] = Field(None, alias="tagValues", description="Tag values - can be empty")

    class Config:
        allow_population_by_field_name = True

class PayDataInputValidityPeriod(BaseModel):
    """Validity period for calculation factors"""
    start_date_time: Optional[str] = Field(None, alias="startDateTime", description="Start date time - optional (October 2024)", example="2024-07-01T00:00:00Z")

    class Config:
        allow_population_by_field_name = True

class PayDataInputCalculationFactorInput(BaseModel):
    """Calculation factor input data"""
    calculation_factor_code: CodeValue = Field(..., alias="calculationFactorCode", description="Calculation factor code - REQUIRED", example={"codeValue": "I001"})
    calculation_factor_rate: CodeValue = Field(..., alias="calculationFactorRate", description="Calculation factor rate with base unit code - REQUIRED", example={"baseUnitCode": {"codeValue": 7.5}})
    configuration_tags: Optional[List[PayDataInputConfigurationTag]] = Field(None, alias="configurationTags", description="Configuration tags - can be empty")
    validity_period: Optional[PayDataInputValidityPeriod] = Field(None, alias="validityPeriod", description="Validity period - optional (October 2024)")

    class Config:
        allow_population_by_field_name = True

class PayDataInputSegmentQuantity(BaseModel):
    """Segment quantity for time inputs"""
    quantity_value: Optional[float] = Field(None, alias="quantityValue", description="Quantity value - can be empty for incident in full day", example=10.0)
    unit_code: Optional[CodeValue] = Field(None, alias="unitCode", description="Unit code - optional", example={"codeValue": "HOUR"})

    class Config:
        allow_population_by_field_name = True

class PayDataInputSegmentClassification(BaseModel):
    """Segment classification for time inputs"""
    classification_code: CodeValue = Field(..., alias="classificationCode", description="Classification code - REQUIRED", example={"codeValue": "HP"})

    class Config:
        allow_population_by_field_name = True

class PayDataInputTimeSegment(BaseModel):
    """Time segment data"""
    segment_classifications: Optional[List[PayDataInputSegmentClassification]] = Field(None, alias="segmentClassifications", description="Segment classifications")
    segment_quantity: Optional[PayDataInputSegmentQuantity] = Field(None, alias="segmentQuantity", description="Segment quantity")

    class Config:
        allow_population_by_field_name = True

class PayDataInputTimeEvaluationPeriod(BaseModel):
    """Time evaluation period"""
    start_date: str = Field(..., alias="startDate", description="Start date - REQUIRED", example="2024-07-15")
    end_date: str = Field(..., alias="endDate", description="End date - REQUIRED", example="2024-07-15")

    class Config:
        allow_population_by_field_name = True

class PayDataInputTimeInput(BaseModel):
    """Time input data"""
    time_evaluation_period: PayDataInputTimeEvaluationPeriod = Field(..., alias="timeEvaluationPeriod", description="Time evaluation period - REQUIRED")
    time_segments: Optional[List[PayDataInputTimeSegment]] = Field(None, alias="timeSegments", description="Time segments - optional")

    class Config:
        allow_population_by_field_name = True

class PayDataInputPayInput(BaseModel):
    """Pay input containing earning and calculation factor inputs"""
    earning_inputs: Optional[List[PayDataInputEarningInput]] = Field(None, alias="earningInputs", description="Earning inputs")
    calculation_factor_inputs: Optional[List[PayDataInputCalculationFactorInput]] = Field(None, alias="calculationFactorInputs", description="Calculation factor inputs")
    pay_allocation: Optional[PayDataInputPayAllocation] = Field(None, alias="payAllocation", description="Pay allocation - can be empty")

    class Config:
        allow_population_by_field_name = True

class PayDataInputPayrollProfilePayInput(BaseModel):
    """Payroll profile pay input"""
    pay_inputs: Optional[List[PayDataInputPayInput]] = Field(None, alias="payInputs", description="Pay inputs")
    time_inputs: Optional[List[PayDataInputTimeInput]] = Field(None, alias="timeInputs", description="Time inputs")

    class Config:
        allow_population_by_field_name = True

class PayDataInputPayeePayInput(BaseModel):
    """Payee pay input"""
    associate_oid: str = Field(..., alias="associateOID", description="Associate OID - REQUIRED", example="ckovach-7170mp5")
    pay_period_start_date: str = Field(..., alias="payPeriodStartDate", description="Pay period start date - REQUIRED", example="2024-08-01")
    payroll_profile_pay_inputs: List[PayDataInputPayrollProfilePayInput] = Field(..., alias="payrollProfilePayInputs", description="Payroll profile pay inputs - REQUIRED")

    class Config:
        allow_population_by_field_name = True

class PayDataInputData(BaseModel):
    """Pay data input main data"""
    item_id: Optional[str] = Field(None, alias="itemID", description="Item ID - REQUIRED for replace operations, optional for add (October 2024)", example="99994817")
    payee_pay_inputs: List[PayDataInputPayeePayInput] = Field(..., alias="payeePayInputs", description="Payee pay inputs - REQUIRED")

    class Config:
        allow_population_by_field_name = True

class PayDataInputTransform(BaseModel):
    """Pay data input transform container"""
    pay_data_input: PayDataInputData = Field(..., alias="payDataInput", description="Pay data input - REQUIRED")

    class Config:
        allow_population_by_field_name = True

class PayDataInputEventData(BaseModel):
    """Pay data input event data"""
    transform: PayDataInputTransform = Field(..., description="Transform data - REQUIRED")

    class Config:
        allow_population_by_field_name = True

class PayDataInputEvent(BaseModel):
    """Pay data input event"""
    data: PayDataInputEventData = Field(..., description="Event data - REQUIRED")

    class Config:
        allow_population_by_field_name = True

class PayDataInputAddRequest(BaseModel):
    """Pay Data Input Add Request - for adding pay data inputs

    Endpoint: POST /events/payroll/v1/pay-data-input.add
    Recommendation: Maximum 100 pay data inputs per request
    """
    events: List[PayDataInputEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

class PayDataInputReplaceRequest(BaseModel):
    """Pay Data Input Replace Request - for replacing existing pay data inputs

    Endpoint: POST /events/payroll/v1/pay-data-input.replace
    Note: itemID is REQUIRED for replace operations (October 2024)
    """
    events: List[PayDataInputEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
