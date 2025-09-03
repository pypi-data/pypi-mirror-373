from typing import Optional, List
from pydantic import BaseModel, Field
import pandas as pd
import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class CodeValue(BaseModel):
    """Code value structure used throughout ADP API"""
    code_value: str = Field(..., alias="codeValue", description="Code value - REQUIRED", example="BANK")
    short_name: Optional[str] = Field(None, alias="shortName", description="Short display name", example="Bank Transfer")
    long_name: Optional[str] = Field(None, alias="longName", description="Long display name", example="Bank Transfer Payment")

    class Config:
        allow_population_by_field_name = True



# ---------------------------
# GET Schema - Flattened Pay Distribution Data
# ---------------------------
class PayDistributionGet(BrynQPanderaDataFrameModel):
    """Flattened schema for ADP Pay Distributions data (one row per distributionInstruction)."""

    # Context
    associate_oid: Series[pd.StringDtype] = pa.Field(coerce=True, description="Associate OID", alias="associateOID")

    # Pay Distribution container
    pay_distribution_item_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Pay Distribution item ID", alias="payDistributions.itemID")

    # Record Type (BANKING.RECORD_TYPE)
    record_type: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Record Type", alias="payDistributions.recordType")

    # Distribution Instruction level
    instruction_item_id: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Instruction item ID", alias="distributionInstructions.itemID")

    # Payment Method
    payment_method_code_value: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payment method code", alias="distributionInstructions.paymentMethodCode.codeValue")
    payment_method_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payment method short name", alias="distributionInstructions.paymentMethodCode.shortName")
    payment_method_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Payment method long name", alias="distributionInstructions.paymentMethodCode.longName")

    # Deposit Account
    deposit_iban: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Deposit IBAN", alias="distributionInstructions.depositAccount.IBAN")
    deposit_account_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Deposit account name", alias="distributionInstructions.depositAccount.financialAccount.accountName")
    deposit_swift_code: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Deposit SWIFT code", alias="distributionInstructions.depositAccount.financialParty.SWIFTCode")
    deposit_bank_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Deposit bank short name", alias="distributionInstructions.depositAccount.financialParty.nameCode.shortName")

    # Precedence
    precedence_code_value: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Precedence code", alias="distributionInstructions.precedenceCode.codeValue")
    precedence_short_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Precedence short name", alias="distributionInstructions.precedenceCode.shortName")
    precedence_long_name: Series[pd.StringDtype] = pa.Field(coerce=True, nullable=True, description="Precedence long name", alias="distributionInstructions.precedenceCode.longName")

    class _Annotation:
        primary_key = "associate_oid"

class FinancialAccount(BaseModel):
    """Financial account information"""
    account_name: str = Field(..., alias="accountName", description="Account name - REQUIRED", example="Main Bank Account")

    class Config:
        allow_population_by_field_name = True


class FinancialParty(BaseModel):
    """Financial party information"""
    swift_code: str = Field(..., alias="SWIFTCode", description="SWIFT code - REQUIRED", example="BNPAFRPP")

    class Config:
        allow_population_by_field_name = True


class DepositAccount(BaseModel):
    """Deposit account information"""
    iban: str = Field(..., alias="IBAN", description="IBAN - REQUIRED", example="FR7630006000011234567890189")
    financial_account: FinancialAccount = Field(..., alias="financialAccount", description="Financial account - REQUIRED")
    financial_party: FinancialParty = Field(..., alias="financialParty", description="Financial party - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class DistributionInstruction(BaseModel):
    """Distribution instruction structure"""
    precedence_code: CodeValue = Field(..., alias="precedenceCode", description="Precedence code - REQUIRED")
    payment_method_code: CodeValue = Field(..., alias="paymentMethodCode", description="Payment method code - REQUIRED")
    item_id: str = Field(..., alias="itemID", description="Item ID - REQUIRED", example="dist001")
    deposit_account: DepositAccount = Field(..., alias="depositAccount", description="Deposit account - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class PayDistribution(BaseModel):
    """Pay distribution structure"""
    record_type: Optional[str] = Field("1", alias="recordType", description="Record Type (Default 1)")
    distribution_instructions: List[DistributionInstruction] = Field(..., alias="distributionInstructions", description="Distribution instructions - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class Worker(BaseModel):
    """Worker information"""
    associate_oid: str = Field(..., alias="associateOID", description="Associate OID - REQUIRED", example="123456789")

    class Config:
        allow_population_by_field_name = True


class EventContext(BaseModel):
    """Event context structure"""
    worker: Worker = Field(..., description="Worker information - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class PayDistributionTransform(BaseModel):
    """Pay distribution transform structure"""
    pay_distribution: PayDistribution = Field(..., alias="payDistribution", description="Pay distribution - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class PayDistributionData(BaseModel):
    """Pay distribution data structure"""
    event_context: EventContext = Field(..., alias="eventContext", description="Event context - REQUIRED")
    transform: PayDistributionTransform = Field(..., description="Transform - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class PayDistributionEvent(BaseModel):
    """Pay distribution event structure"""
    data: PayDistributionData = Field(..., description="Data - REQUIRED")

    class Config:
        allow_population_by_field_name = True


class PayDistributionChangeRequest(BaseModel):
    """Pay Distribution Change Request - for changing worker pay distributions

    Endpoint: POST /events/payroll/v1/worker.pay-distribution.change
    """
    events: List[PayDistributionEvent] = Field(..., description="Events array - REQUIRED")

    class Config:
        allow_population_by_field_name = True
