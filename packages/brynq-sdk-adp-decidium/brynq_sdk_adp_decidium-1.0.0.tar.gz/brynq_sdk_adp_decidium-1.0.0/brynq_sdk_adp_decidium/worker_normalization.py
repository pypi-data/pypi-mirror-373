from typing import Dict, Optional, Union, Literal, List, Any, get_args
import pandas as pd
from pydantic import BaseModel
from brynq_sdk_functions import Functions
import json
from typing import Any, Callable, Dict, Tuple, List

class WorkerNormalization:
    """
    Handles worker data normalization and update operations
    """

    def __init__(self, decidium):
        self.decidium = decidium

    # ============================================================================
    # WORKER-SPECIFIC HELPER FUNCTIONS
    # ============================================================================

    @staticmethod
    def _first(lst, key=None, default=pd.NA):
        """
        Extract first element from list, optionally by key

        Args:
            lst: List to extract from
            key: Optional key to extract from first element
            default: Default value if extraction fails

        Returns:
            First element or key value from first element
        """
        if isinstance(lst, list) and lst:
            return lst[0] if key is None else lst[0].get(key, default)
        return default

    @staticmethod
    def _extract_ssn(lst):
        """Extract SSN from identity documents (worker-specific)"""
        if isinstance(lst, list):
            for d in lst:
                if (d.get("typeCode") or {}).get("codeValue") == "SSN":
                    return d.get("documentID", pd.NA)
        return pd.NA

    @staticmethod
    def _extract_custom_field(custom_fields_list, field_name, value_key="codeValue"):
        """Extract value from custom field array by itemID"""
        if not isinstance(custom_fields_list, list):
            return pd.NA
        for field in custom_fields_list:
            if isinstance(field, dict) and field.get("itemID") == field_name:
                return field.get(value_key, pd.NA)
        return pd.NA

    @staticmethod
    def _extract_org_unit(org_units_list, unit_type, value_key):
        """Extract organizational unit value by itemID"""
        if not isinstance(org_units_list, list):
            return pd.NA
        for unit in org_units_list:
            if isinstance(unit, dict) and unit.get("itemID") == unit_type:
                return unit.get("nameCode", {}).get(value_key, pd.NA)
        return pd.NA

    @staticmethod
    def _normalize_workers_data(raw_data: list) -> pd.DataFrame:
        """
        Main function to normalize ADP workers data to WorkerGet schema
        Uses generic helper functions from ADP base class

        Args:
            raw_data: Raw workers data from API response
        """
        from .decidium import Decidium

        # Create empty DataFrame with all required columns as template
        empty_df = pd.DataFrame(columns=[
            "associateOID",
            "workerID.idValue",
            "workerDates.firstHireDate",
            "workerDates.originalHireDate",
            "workerDates.terminationDate",
            "workerStatus.effectiveDate",
            "workerStatus.statusCode.codeValue",
            "businessCommunication.emails.emailUri",
            "businessCommunication.emails.itemID",
            "businessCommunication.landlines.formattedNumber",
            "businessCommunication.mobiles.formattedNumber",
            "businessCommunication.pagers.formattedNumber",
            "workAssignments.itemID",
            "workAssignments.payrollFileNumber",
            "workAssignments.seniorityDate",
            "workAssignments.legalEntityID",
            "workAssignments.expectedStartDate",
            "workAssignments.hireDate",
            "workAssignments.actualStartDate",
            "workAssignments.expectedTerminationDate",
            "workAssignments.terminationDate",
            "workAssignments.jobCode.codeValue",
            "workAssignments.jobCode.longName",
            "workAssignments.jobFunctionCode.codeValue",
            "workAssignments.jobFunctionCode.longName",
            "workAssignments.jobTitle",
            "workAssignments.workerTypeCode.codeValue",
            "workAssignments.customFieldGroup.codeFields.collaborationType",
            "workAssignments.customFieldGroup.codeFields.contractType",
            "workAssignments.customFieldGroup.codeFields.recoursReason",
            "workAssignments.customFieldGroup.codeFields.activity",
            "workAssignments.customFieldGroup.codeFields.remunerationType",
            "workAssignments.customFieldGroup.codeFields.workSchedule",
            "workAssignments.customFieldGroup.codeFields.TLM",
            "workAssignments.remunerationBasisCode.codeValue",
            "workAssignments.customFieldGroup.numberFields.coefficient",
            "workAssignments.customFieldGroup.numberFields.fullTimeHours",
            "workAssignments.customFieldGroup.numberFields.weeklyHours",
            "workAssignments.customFieldGroup.numberFields.monthlyHours",
            "workAssignments.baseRemuneration.payPeriodRateAmount.amountValue",
            "workAssignments.baseRemuneration.payPeriodRateAmount.currencyCode",
            "workAssignments.baseRemuneration.monthlyRateAmount.amountValue",
            "workAssignments.baseRemuneration.monthlyRateAmount.currencyCode",
            "workAssignments.baseRemuneration.annualRateAmount.amountValue",
            "workAssignments.baseRemuneration.annualRateAmount.currencyCode",
            "workAssignments.assignedWorkLocations.itemID",
            "workAssignments.assignedWorkLocations.nameCode.longName",
            "workAssignments.assignedWorkLocations.address.countryCode",
            "workAssignments.assignedWorkLocations.address.cityName",
            "workAssignments.assignedWorkLocations.address.postalCode",
            "workAssignments.assignedWorkLocations.address.lineOne",
            "workAssignments.assignedWorkLocations.address.lineTwo",
            "workAssignments.assignedWorkLocations.address.nameCode.codeValue",
            "workAssignments.legalEntityCode.longName",
            "workAssignments.legalEntityCode.codeValue",
            "workAssignments.assignedOrganizationalUnits.departmentId.nameCode.codeValue",
            "workAssignments.assignedOrganizationalUnits.departmentId.nameCode.longName",
            "workAssignments.assignmentCostCenters.costCenterID",
            "workAssignments.assignmentCostCenters.costCenterName",
            "workAssignments.assignmentCostCenters.costCenterPercentage",
            "workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup",
            "workAssignments.customFieldGroup.codeFields.professionalCategory.codeValue",
            "workAssignments.customFieldGroup.codeFields.professionalCategory.longName",
            "workAssignments.customFieldGroup.codeFields.collaborationType.codeValue",
            "workAssignments.customFieldGroup.codeFields.collaborationType.longName",
            "person.birthDate",
            "person.genderCode.codeValue",
            "person.deceasedIndicator",
            "person.birthPlace.countryCode",
            "person.birthPlace.cityName",
            "person.birthPlace.postalCode",
            "person.maritalStatusCode.codeValue",
            "person.maritalStatusCode.effectiveDate",
            "person.legalName.formattedName",
            "person.legalName.givenName",
            "person.legalName.familyName1",
            "person.legalName.familyName2",
            "person.legalName.middleName",
            "person.identityDocuments.SSN.documentID",
            "person.communication.emails.emailUri",
            "person.communication.landlines.formattedNumber",
            "person.communication.mobiles.formattedNumber",
            "person.legalAddress.countryCode",
            "person.legalAddress.cityName",
            "person.legalAddress.postalCode",
            "person.legalAddress.lineOne",
            "person.legalAddress.buildingNumber",
            "person.legalAddress.streetName",
            "person.citizenshipCountryCodes.codeValue",
            "person.citizenshipCountryCodes.longName",
            "alternateIDs.idValue",
            "alternateIDs.schemeCode.codeValue"
        ])

        if not raw_data:
            return empty_df

        # Convert to DataFrame using json_normalize
        df = pd.json_normalize(raw_data, sep=".")

        if df.empty:
            return empty_df

        # Keep the original normalized data to preserve arrays
        # We'll use the template columns to ensure all required columns exist
        result_df = empty_df.copy()

        # Copy over simple columns that exist in both
        for col in result_df.columns:
            if col in df.columns:
                result_df[col] = df[col]

        # ---------- ARRAY EXTRACTIONS ----------
        # Extract arrays from original normalized data (df) and put results in result_df

        # Personal communication arrays
        if "person.communication.emails" in df.columns:
            result_df["person.communication.emails.emailUri"] = df["person.communication.emails"].apply(
                lambda x: WorkerNormalization._first(x, "emailUri") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.communication.emails.emailUri"] = pd.NA

        if "person.communication.landlines" in df.columns:
            result_df["person.communication.landlines.formattedNumber"] = df["person.communication.landlines"].apply(
                lambda x: WorkerNormalization._first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.communication.landlines.formattedNumber"] = pd.NA

        if "person.communication.mobiles" in df.columns:
            result_df["person.communication.mobiles.formattedNumber"] = df["person.communication.mobiles"].apply(
                lambda x: WorkerNormalization._first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.communication.mobiles.formattedNumber"] = pd.NA

        # Business communication arrays
        if "businessCommunication.emails" in df.columns:
            result_df["businessCommunication.emails.emailUri"] = df["businessCommunication.emails"].apply(
                lambda x: WorkerNormalization._first(x, "emailUri") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["businessCommunication.emails.emailUri"] = pd.NA

        if "businessCommunication.landlines" in df.columns:
            result_df["businessCommunication.landlines.formattedNumber"] = df["businessCommunication.landlines"].apply(
                lambda x: WorkerNormalization._first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["businessCommunication.landlines.formattedNumber"] = pd.NA

        if "businessCommunication.mobiles" in df.columns:
            result_df["businessCommunication.mobiles.formattedNumber"] = df["businessCommunication.mobiles"].apply(
                lambda x: WorkerNormalization._first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["businessCommunication.mobiles.formattedNumber"] = pd.NA

        if "businessCommunication.pagers" in df.columns:
            result_df["businessCommunication.pagers.formattedNumber"] = df["businessCommunication.pagers"].apply(
                lambda x: WorkerNormalization._first(x, "formattedNumber") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["businessCommunication.pagers.formattedNumber"] = pd.NA

        # Identity documents (SSN)
        if "person.identityDocuments" in df.columns:
            result_df["person.identityDocuments.SSN.documentID"] = df["person.identityDocuments"].apply(
                lambda x: WorkerNormalization._extract_ssn(x) if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.identityDocuments.SSN.documentID"] = pd.NA

        # Citizenship country codes
        if "person.citizenshipCountryCodes" in df.columns:
            result_df["person.citizenshipCountryCodes.codeValue"] = df["person.citizenshipCountryCodes"].apply(
                lambda x: WorkerNormalization._first(x, "codeValue") if isinstance(x, list) else pd.NA
            )
            result_df["person.citizenshipCountryCodes.longName"] = df["person.citizenshipCountryCodes"].apply(
                lambda x: WorkerNormalization._first(x, "longName") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["person.citizenshipCountryCodes.codeValue"] = pd.NA
            result_df["person.citizenshipCountryCodes.longName"] = pd.NA

        # Alternate IDs
        if "alternateIDs" in df.columns:
            result_df["alternateIDs.idValue"] = df["alternateIDs"].apply(
                lambda x: WorkerNormalization._first(x, "idValue") if isinstance(x, list) else pd.NA
            )
            result_df["alternateIDs.schemeCode.codeValue"] = df["alternateIDs"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("schemeCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )
        else:
            result_df["alternateIDs.idValue"] = pd.NA
            result_df["alternateIDs.schemeCode.codeValue"] = pd.NA

                # ---------- WORK ASSIGNMENTS ARRAYS ----------

        if "workAssignments" in df.columns:
            # Get first work assignment for each worker
            result_df["workAssignments.itemID"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "itemID") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.payrollFileNumber"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "payrollFileNumber") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.seniorityDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "seniorityDate") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.legalEntityID"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "legalEntityID") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.hireDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "hireDate") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.actualStartDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "actualStartDate") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.jobTitle"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "jobTitle") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.expectedStartDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "expectedStartDate") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.expectedTerminationDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "expectedTerminationDate") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.terminationDate"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, "terminationDate") if isinstance(x, list) else pd.NA
            )

            # Job codes
            result_df["workAssignments.jobCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("jobCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.jobCode.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("jobCode", {}).get("longName", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.jobFunctionCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("jobFunctionCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.jobFunctionCode.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("jobFunctionCode", {}).get("longName", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Worker type code (Contract code)
            result_df["workAssignments.workerTypeCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("workerTypeCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Remuneration basis code
            result_df["workAssignments.remunerationBasisCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("remunerationBasisCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Work assignment custom fields
            result_df["workAssignments.customFieldGroup.codeFields.collaborationType"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "collaborationType") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.contractType"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "contractType") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.recoursReason"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "recoursReason") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.activity"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "activity") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.remunerationType"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "remunerationType") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.workSchedule"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "workSchedule") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.TLM"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "TLM") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "payrollAdministrationGroup") if isinstance(x, list) else pd.NA
            )



            # Work assignment number fields
            result_df["workAssignments.customFieldGroup.numberFields.coefficient"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("numberFields", []), "coefficient", "numberValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.numberFields.fullTimeHours"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("numberFields", []), "fullTimeHours", "numberValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.numberFields.weeklyHours"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("numberFields", []), "weeklyHours", "numberValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.numberFields.monthlyHours"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("numberFields", []), "monthlyHours", "numberValue") if isinstance(x, list) else pd.NA
            )

            # Work assignment base remuneration
            result_df["workAssignments.baseRemuneration.payPeriodRateAmount.amountValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("payPeriodRateAmount", {}).get("amountValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.baseRemuneration.payPeriodRateAmount.currencyCode"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("payPeriodRateAmount", {}).get("currencyCode", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.baseRemuneration.monthlyRateAmount.amountValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("monthlyRateAmount", {}).get("amountValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.baseRemuneration.monthlyRateAmount.currencyCode"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("monthlyRateAmount", {}).get("currencyCode", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.baseRemuneration.annualRateAmount.amountValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("annualRateAmount", {}).get("amountValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.baseRemuneration.annualRateAmount.currencyCode"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("baseRemuneration", {}).get("annualRateAmount", {}).get("currencyCode", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Work assignment organization units
            result_df["workAssignments.assignedOrganizationalUnits.departmentId.nameCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_org_unit(WorkerNormalization._first(x, None, {}).get("assignedOrganizationalUnits", []), "departmentId", "codeValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedOrganizationalUnits.departmentId.nameCode.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_org_unit(WorkerNormalization._first(x, None, {}).get("assignedOrganizationalUnits", []), "departmentId", "longName") if isinstance(x, list) else pd.NA
            )

            # Work assignment work locations
            result_df["workAssignments.assignedWorkLocations.itemID"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), "itemID") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.nameCode.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("nameCode", {}).get("longName", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.address.countryCode"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("countryCode", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.address.cityName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("cityName", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.address.postalCode"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("postalCode", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.address.lineOne"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("lineOne", pd.NA) if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.assignedWorkLocations.address.lineTwo"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("lineTwo", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Establishment code (SIRET) from work location address
            result_df["workAssignments.assignedWorkLocations.address.nameCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignedWorkLocations", []), None, {}).get("address", {}).get("nameCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Company name from legal entity code
            result_df["workAssignments.legalEntityCode.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("legalEntityCode", {}).get("longName", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Company code from legal entity code
            result_df["workAssignments.legalEntityCode.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(x, None, {}).get("legalEntityCode", {}).get("codeValue", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Cost center information
            result_df["workAssignments.assignmentCostCenters.costCenterID"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignmentCostCenters", []), None, {}).get("costCenterID", pd.NA) if isinstance(x, list) else pd.NA
            )
            result_df["workAssignments.assignmentCostCenters.costCenterName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignmentCostCenters", []), None, {}).get("costCenterName", pd.NA) if isinstance(x, list) else pd.NA
            )
            result_df["workAssignments.assignmentCostCenters.costCenterPercentage"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._first(WorkerNormalization._first(x, None, {}).get("assignmentCostCenters", []), None, {}).get("costCenterPercentage", pd.NA) if isinstance(x, list) else pd.NA
            )

            # Custom fields
            result_df["workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "payrollAdministrationGroup") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.professionalCategory.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "professionalCategory", "codeValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.professionalCategory.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "professionalCategory", "longName") if isinstance(x, list) else pd.NA
            )
            result_df["workAssignments.customFieldGroup.codeFields.collaborationType.codeValue"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "collaborationType", "codeValue") if isinstance(x, list) else pd.NA
            )

            result_df["workAssignments.customFieldGroup.codeFields.collaborationType.longName"] = df["workAssignments"].apply(
                lambda x: WorkerNormalization._extract_custom_field(WorkerNormalization._first(x, None, {}).get("customFieldGroup", {}).get("codeFields", []), "collaborationType", "longName") if isinstance(x, list) else pd.NA
            )
        else:
            # If workAssignments column doesn't exist, set all work assignment fields to NaN
            result_df["workAssignments.itemID"] = pd.NA
            result_df["workAssignments.payrollFileNumber"] = pd.NA
            result_df["workAssignments.seniorityDate"] = pd.NA
            result_df["workAssignments.legalEntityID"] = pd.NA
            result_df["workAssignments.hireDate"] = pd.NA
            result_df["workAssignments.actualStartDate"] = pd.NA
            result_df["workAssignments.jobTitle"] = pd.NA
            result_df["workAssignments.expectedStartDate"] = pd.NA
            result_df["workAssignments.expectedTerminationDate"] = pd.NA
            result_df["workAssignments.terminationDate"] = pd.NA
            result_df["workAssignments.jobCode.codeValue"] = pd.NA
            result_df["workAssignments.jobCode.longName"] = pd.NA
            result_df["workAssignments.jobFunctionCode.codeValue"] = pd.NA
            result_df["workAssignments.jobFunctionCode.longName"] = pd.NA
            result_df["workAssignments.workerTypeCode.codeValue"] = pd.NA
            result_df["workAssignments.remunerationBasisCode.codeValue"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.collaborationType"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.contractType"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.recoursReason"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.activity"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.remunerationType"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.workSchedule"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.TLM"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup"] = pd.NA
            result_df["workAssignments.customFieldGroup.numberFields.coefficient"] = pd.NA
            result_df["workAssignments.customFieldGroup.numberFields.fullTimeHours"] = pd.NA
            result_df["workAssignments.customFieldGroup.numberFields.weeklyHours"] = pd.NA
            result_df["workAssignments.customFieldGroup.numberFields.monthlyHours"] = pd.NA
            result_df["workAssignments.baseRemuneration.payPeriodRateAmount.amountValue"] = pd.NA
            result_df["workAssignments.baseRemuneration.payPeriodRateAmount.currencyCode"] = pd.NA
            result_df["workAssignments.baseRemuneration.monthlyRateAmount.amountValue"] = pd.NA
            result_df["workAssignments.baseRemuneration.monthlyRateAmount.currencyCode"] = pd.NA
            result_df["workAssignments.baseRemuneration.annualRateAmount.amountValue"] = pd.NA
            result_df["workAssignments.baseRemuneration.annualRateAmount.currencyCode"] = pd.NA
            result_df["workAssignments.assignedOrganizationalUnits.departmentId.nameCode.codeValue"] = pd.NA
            result_df["workAssignments.assignedOrganizationalUnits.departmentId.nameCode.longName"] = pd.NA
            result_df["workAssignments.assignmentCostCenters.costCenterID"] = pd.NA
            result_df["workAssignments.assignmentCostCenters.costCenterName"] = pd.NA
            result_df["workAssignments.assignmentCostCenters.costCenterPercentage"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.payrollAdministrationGroup"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.professionalCategory.codeValue"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.professionalCategory.longName"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.collaborationType.codeValue"] = pd.NA
            result_df["workAssignments.customFieldGroup.codeFields.collaborationType.longName"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.itemID"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.nameCode.longName"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.countryCode"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.cityName"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.postalCode"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.lineOne"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.lineTwo"] = pd.NA
            result_df["workAssignments.assignedWorkLocations.address.nameCode.codeValue"] = pd.NA
            result_df["workAssignments.legalEntityCode.longName"] = pd.NA
            result_df["workAssignments.legalEntityCode.codeValue"] = pd.NA

        # Add business communication email itemID field
        if "businessCommunication.emails" in df.columns:
            result_df["businessCommunication.emails.itemID"] = df["businessCommunication.emails"].apply(
                lambda x: WorkerNormalization._first(x, "itemID") if isinstance(x, list) else pd.NA
            )
        else:
            result_df["businessCommunication.emails.itemID"] = pd.NA

        # ---------- CLEAN UP ORIGINAL ARRAYS ----------
        # No need to drop columns since result_df already has the correct structure
        # The original df with arrays is not returned

        return result_df

        # ----------------------------------------------------------------------
    # 1) field-to-path map with optional transform
    #    ─────────────
    #    • path  : where to write in the nested dict
    #    • transform : value → cleaned/typed value (or None for passthrough)
    # ----------------------------------------------------------------------
    Path = Tuple[Any, ...]
    Transform = Callable[[Any], Any]

    FIELD_RULES: dict[str, Tuple[Path, Transform | None]] = {
        # person ------------------------------------------------------------------
        "given_name": (("person", "legalName", "givenName"), None),
        "family_name_1": (("person", "legalName", "familyName1"), None),
        "family_name_2": (("person", "legalName", "familyName2"), str),
        "middle_name": (("person", "legalName", "middleName"), str),
        "gender_code": (("person", "genderCode", "codeValue"), str.upper),

        "birth_date": (("person", "birthDate"), str),

        # Birth place
        "birth_place_city_name": (("person", "birthPlace", "cityName"), str),
        "birth_place_country_code": (("person", "birthPlace", "countryCode"), str),
        "birth_place_postal_code": (("person", "birthPlace", "postalCode"), str),
        "birth_place_country_subdivision_level_1_code": (("person", "birthPlace", "countrySubdivisionLevel1", "codeValue"), str),

        # Marital status
        "marital_status_code": (("person", "maritalStatusCode", "codeValue"), str),
        "marital_status_effective_date": (("person", "maritalStatusCode", "effectiveDate"), str),

        "citizenship_country_codes": (
            ("person", "citizenshipCountryCodes"),
            lambda v: [{"codeValue": c.strip()} for c in str(v).split(",") if c.strip()],
        ),
        "identity_documents": (
            ("person", "identityDocuments"),
            lambda v: [{"documentID": d.strip()} for d in str(v).split(",") if d.strip()],
        ),

        # Legal address
        "legal_address_name_code": (("person", "legalAddress", "nameCode", "codeValue"), str),
        "legal_address_country_subdivision_level_1": (("person", "legalAddress", "countrySubdivisionLevel1", "codeValue"), str),
        "legal_address_country_code": (("person", "legalAddress", "countryCode"), str),
        "legal_address_postal_code": (("person", "legalAddress", "postalCode"), str),
        "legal_address_line_one": (("person", "legalAddress", "lineOne"), str),
        "legal_address_line_two": (("person", "legalAddress", "lineTwo"), str),
        "legal_address_city_name": (("person", "legalAddress", "cityName"), str),
        "legal_address_unit": (("person", "legalAddress", "unit"), str),
        "legal_address_line_five": (("person", "legalAddress", "lineFive"), str),
        "legal_address_building_number": (("person", "legalAddress", "buildingNumber"), str),
        "legal_address_building_number_extension": (("person", "legalAddress", "buildingNumberExtension"), str),
        "legal_address_building_name": (("person", "legalAddress", "buildingName"), str),
        "legal_address_street_name": (("person", "legalAddress", "streetName"), str),
        "legal_address_country_subdivision_level_2_code": (("person", "legalAddress", "countrySubdivisionLevel2", "codeValue"), str),
        "legal_address_country_subdivision_level_2_long_name": (("person", "legalAddress", "countrySubdivisionLevel2", "longName"), str),
        "legal_address_country_subdivision_level_2": (("person", "legalAddress", "countrySubdivisionLevel2", "codeValue"), str),

        # Person communication
        "person_communication_emails": (
            ("person", "communication", "emails"),
            lambda v: [{"emailUri": str(v)}] if v else None,
        ),
        "person_communication_landlines": (
            ("person", "communication", "landlines"),
            lambda v: [{"formattedNumber": str(v)}] if v else None,
        ),
        "person_communication_mobiles": (
            ("person", "communication", "mobiles"),
            lambda v: [{"formattedNumber": str(v)}] if v else None,
        ),

        # Other person fields
        "other_personal_addresses": (
            ("person", "otherPersonalAddresses"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "social_insurance_program_service_center_code": (
            ("person", "socialInsurancePrograms"),
            lambda v: [{"programServiceCenter": {"nameCode": {"codeValue": str(v)}}}] if v else None,
        ),
        "immigration_documents": (
            ("person", "immigrationDocuments"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),

        # Worker level
        "original_hire_date": (("workerDates", "originalHireDate"), str),

        # Associate OID (for rehire)
        "associate_oid": (("associateOID",), str),

        # Business communication
        "business_communication_emails": (
            ("businessCommunication", "emails"),
            lambda v: [{"emailUri": str(v)}] if v else None,
        ),
        "business_communication_landlines": (
            ("businessCommunication", "landlines"),
            lambda v: [{"formattedNumber": str(v)}] if v else None,
        ),
        "business_communication_mobiles": (
            ("businessCommunication", "mobiles"),
            lambda v: [{"formattedNumber": str(v)}] if v else None,
        ),
        "business_communication_faxes": (
            ("businessCommunication", "faxes"),
            lambda v: [{"formattedNumber": str(v)}] if v else None,
        ),

        # workAssignment -----------------------------------------------------------
        "hire_date": (("workAssignment", "hireDate"), str),
        "seniority_date": (("workAssignment", "seniorityDate"), str),
        "expected_start_date": (("workAssignment", "expectedStartDate"), str),
        "work_arrangement_code": (("workAssignment", "workArrangementCode", "codeValue"), str),
        "job_code": (("workAssignment", "jobCode", "codeValue"), str),
        "job_function_code": (("workAssignment", "jobFunctionCode", "codeValue"), str),
        "job_title": (("workAssignment", "jobTitle"), str),
        "worker_type_code": (("workAssignment", "workerTypeCode", "codeValue"), str),
        "assignment_status_reason_code": (("workAssignment", "assignmentStatus", "reasonCode", "codeValue"), str),
        "payroll_processing_status_code": (("workAssignment", "payrollProcessingStatusCode", "codeValue"), str),
        "base_remuneration_recording_basis_code": (("workAssignment", "baseRemuneration", "recordingBasisCode", "codeValue"), str),
        "recording_basis_code": (("workAssignment", "baseRemuneration", "recordingBasisCode", "codeValue"), str),

        # Base remuneration amount fields
        "monthly_rate_amount": (("workAssignment", "baseRemuneration", "monthlyRateAmount", "amountValue"), float),
        "monthly_rate_currency": (("workAssignment", "baseRemuneration", "monthlyRateAmount", "currencyCode"), str),
        "annual_rate_amount": (("workAssignment", "baseRemuneration", "annualRateAmount", "amountValue"), float),
        "annual_rate_currency": (("workAssignment", "baseRemuneration", "annualRateAmount", "currencyCode"), str),
        "pay_period_rate_amount": (("workAssignment", "baseRemuneration", "payPeriodRateAmount", "amountValue"), float),
        "pay_period_currency": (("workAssignment", "baseRemuneration", "payPeriodRateAmount", "currencyCode"), str),

        # Top-level remuneration basis code (matches get method path)
        "remuneration_basis_code": (("workAssignment", "remunerationBasisCode", "codeValue"), str),

        "expected_termination_date": (("workAssignment", "expectedTerminationDate"), str),

        "occupational_classifications": (
            ("workAssignment", "occupationalClassifications"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "worker_groups": (
            ("workAssignment", "workerGroups"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "assignment_cost_centers": (
            ("workAssignment", "assignmentCostCenters"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),

        # Department - organizational units
        "department_id": (("workAssignment", "assignedOrganizationalUnits", 0, "nameCode", "codeValue"), str),

        # Work location
        "location_code": (("workAssignment", "assignedWorkLocations", 0, "nameCode", "codeValue"), str),
        "location_short_name": (("workAssignment", "assignedWorkLocations", 0, "nameCode", "shortName"), str),
        "location_long_name": (("workAssignment", "assignedWorkLocations", 0, "nameCode", "longName"), str),

        # Work location address
        "address_name_code": (("workAssignment", "assignedWorkLocations", 0, "address", "nameCode", "codeValue"), str),
        "address_short_name": (("workAssignment", "assignedWorkLocations", 0, "address", "nameCode", "shortName"), str),
        "address_unit": (("workAssignment", "assignedWorkLocations", 0, "address", "unit"), str),
        "address_line_one": (("workAssignment", "assignedWorkLocations", 0, "address", "lineOne"), str),
        "address_line_two": (("workAssignment", "assignedWorkLocations", 0, "address", "lineTwo"), str),
        "address_city_name": (("workAssignment", "assignedWorkLocations", 0, "address", "cityName"), str),
        "address_country_code": (("workAssignment", "assignedWorkLocations", 0, "address", "countryCode"), str),
        "address_postal_code": (("workAssignment", "assignedWorkLocations", 0, "address", "postalCode"), str),
        "address_country_subdivision_level_2_code": (("workAssignment", "assignedWorkLocations", 0, "address", "countrySubdivisionLevel2", "codeValue"), str),
        "address_country_subdivision_level_2_short_name": (("workAssignment", "assignedWorkLocations", 0, "address", "countrySubdivisionLevel2", "shortName"), str),
        "address_country_subdivision_level_2_long_name": (("workAssignment", "assignedWorkLocations", 0, "address", "countrySubdivisionLevel2", "longName"), str),
        "address_country_subdivision_level_2_subdivision_type": (("workAssignment", "assignedWorkLocations", 0, "address", "countrySubdivisionLevel2", "subdivisionType"), str),

        # Custom fields are handled specially in _handle_custom_fields method
        # collaboration_type, activity, tlm, contract_type, remuneration_type, work_schedule, etc.

        # Additional custom fields for hire/rehire requests
        "collaboration_type": (("workAssignment", "collaborationType"), str),
        "contract_type": (("workAssignment", "contractType"), str),
        "activity": (("workAssignment", "activity"), str),
        "remuneration_type": (("workAssignment", "remunerationType"), str),
        "work_schedule": (("workAssignment", "workSchedule"), str),
        "tlm": (("workAssignment", "TLM"), str),

        # Custom field groups (JSON format)
        "work_assignment_custom_code_fields": (
            ("workAssignment", "customFieldGroup", "codeFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "work_assignment_custom_string_fields": (
            ("workAssignment", "customFieldGroup", "stringFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "work_assignment_custom_number_fields": (
            ("workAssignment", "customFieldGroup", "numberFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "work_assignment_custom_date_fields": (
            ("workAssignment", "customFieldGroup", "dateFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),

        # Person custom fields
        "person_custom_string_fields": (
            ("person", "customFieldGroup", "stringFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "person_custom_date_fields": (
            ("person", "customFieldGroup", "dateFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
        "person_custom_number_fields": (
            ("person", "customFieldGroup", "numberFields"),
            lambda v: json.loads(v) if isinstance(v, str) else v,
        ),
    }

    # ----------------------------------------------------------------------
    # 2) helpers
    # ----------------------------------------------------------------------
    def _ensure_list_size(self, lst: List, index: int) -> None:
        while len(lst) <= index:
            lst.append({})

    def _insert(self, target: Dict[str, Any], path: Path, value: Any) -> None:
        """Create dict/list containers along `path` and write `value` at the leaf."""
        *parents, leaf = path
        cursor = target

        for i, part in enumerate(parents):
            if isinstance(part, int):  # list index step
                self._ensure_list_size(cursor, part)
                cursor = cursor[part]
            else:  # dict key step
                nxt = parents[i + 1] if i + 1 < len(parents) else leaf
                cursor = cursor.setdefault(part, [] if isinstance(nxt, int) else {})

        if isinstance(leaf, int):
            self._ensure_list_size(cursor, leaf)
            cursor[leaf] = value
        else:
            cursor[leaf] = value

    # ----------------------------------------------------------------------
    # 3) the only public function you need
    # ----------------------------------------------------------------------
    def _flat_dict_to_nested_dict(self, flat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a flat worker dict into the nested draft expected by WorkerHireRequest.

        * Uses FIELD_RULES for mapping & cleaning.
        * Ignores keys not listed in FIELD_RULES.
        """
        nested: Dict[str, Any] = {}

        # Handle regular fields
        for key, raw_value in flat.items():
            rule = self.FIELD_RULES.get(key)
            if not rule or raw_value is None:
                continue

            path, transform = rule
            value = transform(raw_value) if transform else raw_value
            self._insert(nested, path, value)

        # Add salutation once gender is known
        gender = flat.get("gender_code", "M").upper()
        salutation_code = {"codeValue": "M" if gender == "M" else "F"}
        self._insert(nested, ("person", "legalName", "preferredSalutations"), [{"salutationCode": salutation_code}])

        # Handle custom fields specially
        self._handle_custom_fields(nested, flat)

        # Handle SSN specially (add to existing identity_documents or create new)
        if "identity_document_ssn" in flat and flat["identity_document_ssn"]:
            existing_docs = nested.get("person", {}).get("identityDocuments", [])
            ssn_doc = {"documentID": str(flat["identity_document_ssn"])}
            if existing_docs:
                existing_docs.append(ssn_doc)
            else:
                self._insert(nested, ("person", "identityDocuments"), [ssn_doc])

        # Add required itemID for organizational units
        if "department_id" in flat and flat["department_id"]:
            self._insert(nested, ("workAssignment", "assignedOrganizationalUnits", 0, "itemID"), "departmentId")

        # Add required itemID for work locations
        if "location_code" in flat and flat["location_code"]:
            self._insert(nested, ("workAssignment", "assignedWorkLocations", 0, "itemID"), "default")

        # Clean up empty structures that shouldn't be there
        self._clean_empty_structures(nested)

        return nested

    def _handle_custom_fields(self, nested: Dict[str, Any], flat: Dict[str, Any]) -> None:
        """Handle custom fields that need special itemID + codeValue format."""
        custom_fields = []

        # Basic custom fields
        if "collaboration_type" in flat and flat["collaboration_type"]:
            custom_fields.append({"itemID": "collaborationType", "codeValue": str(flat["collaboration_type"])})

        if "activity" in flat and flat["activity"]:
            custom_fields.append({"itemID": "activity", "codeValue": str(flat["activity"])})

        if "tlm" in flat and flat["tlm"]:
            custom_fields.append({"itemID": "TLM", "codeValue": str(flat["tlm"])})

        if "contract_type" in flat and flat["contract_type"]:
            custom_fields.append({"itemID": "contractType", "codeValue": str(flat["contract_type"])})

        if "remuneration_type" in flat and flat["remuneration_type"]:
            custom_fields.append({"itemID": "remunerationType", "codeValue": str(flat["remuneration_type"])})

        if "work_schedule" in flat and flat["work_schedule"]:
            custom_fields.append({"itemID": "workSchedule", "codeValue": str(flat["work_schedule"])})

        # New salary-related custom fields
        if "mode_rem_sath" in flat and flat["mode_rem_sath"]:
            custom_fields.append({"itemID": "modeRemSATH", "codeValue": str(flat["mode_rem_sath"])})

        if "old_sath" in flat and flat["old_sath"]:
            custom_fields.append({"itemID": "oldSATH", "codeValue": str(flat["old_sath"])})

        if "temporary_employment_agency" in flat and flat["temporary_employment_agency"]:
            custom_fields.append({"itemID": "temporaryEmploymentAgency", "codeValue": str(flat["temporary_employment_agency"])})

        if "recours_reason" in flat and flat["recours_reason"]:
            custom_fields.append({"itemID": "recoursReason", "codeValue": str(flat["recours_reason"])})

        if "subcontractor_status" in flat and flat["subcontractor_status"]:
            custom_fields.append({"itemID": "subcontractorStatus", "codeValue": str(flat["subcontractor_status"])})

        # Add additional custom fields from JSON
        if "work_assignment_custom_code_fields" in flat and flat["work_assignment_custom_code_fields"]:
            try:
                additional_fields = json.loads(flat["work_assignment_custom_code_fields"])
                if isinstance(additional_fields, list):
                    custom_fields.extend(additional_fields)
            except (json.JSONDecodeError, TypeError):
                pass

        if custom_fields:
            self._insert(nested, ("workAssignment", "customFieldGroup", "codeFields"), custom_fields)

        # Handle string fields from JSON
        if "work_assignment_custom_string_fields" in flat and flat["work_assignment_custom_string_fields"]:
            try:
                string_fields = json.loads(flat["work_assignment_custom_string_fields"])
                if isinstance(string_fields, list):
                    self._insert(nested, ("workAssignment", "customFieldGroup", "stringFields"), string_fields)
            except (json.JSONDecodeError, TypeError):
                pass

        # Handle date fields from JSON
        if "work_assignment_custom_date_fields" in flat and flat["work_assignment_custom_date_fields"]:
            try:
                date_fields = json.loads(flat["work_assignment_custom_date_fields"])
                if isinstance(date_fields, list):
                    self._insert(nested, ("workAssignment", "customFieldGroup", "dateFields"), date_fields)
            except (json.JSONDecodeError, TypeError):
                pass

        # Handle number fields from JSON
        if "work_assignment_custom_number_fields" in flat and flat["work_assignment_custom_number_fields"]:
            try:
                number_fields = json.loads(flat["work_assignment_custom_number_fields"])
                if isinstance(number_fields, list):
                    self._insert(nested, ("workAssignment", "customFieldGroup", "numberFields"), number_fields)
            except (json.JSONDecodeError, TypeError):
                pass

        # Handle amount fields (for internship compensation etc.)
        amount_fields = []

        if "internship_compensation" in flat and flat["internship_compensation"]:
            amount_field = {"itemID": "internshipCompensation", "amountValue": float(flat["internship_compensation"])}
            if "internship_currency" in flat and flat["internship_currency"]:
                amount_field["currencyCode"] = str(flat["internship_currency"])
            amount_fields.append(amount_field)

        if amount_fields:
            self._insert(nested, ("workAssignment", "customFieldGroup", "amountFields"), amount_fields)

    def _clean_empty_structures(self, nested: Dict[str, Any]) -> None:
        """Remove empty objects that can cause ADP API issues."""
        # Don't add empty structures - just remove them if they exist but are empty
        # Note: payrollProcessingStatusCode removed - it should show if it has value
        paths_to_check = [
            ("person", "birthPlace", "countrySubdivisionLevel1"),
            ("person", "maritalStatusCode"),
            ("person", "legalAddress", "nameCode"),
            ("person", "legalAddress", "countrySubdivisionLevel1"),
            ("person", "legalAddress", "countrySubdivisionLevel2"),
            ("person", "communication"),
            ("workAssignment", "customFieldGroup"),
            ("businessCommunication",),
        ]

        for path in paths_to_check:
            self._remove_if_empty(nested, path)

    def _remove_if_empty(self, nested: Dict[str, Any], path: tuple) -> None:
        """Remove a path if it exists and is empty."""
        try:
            *parents, leaf = path
            cursor = nested

            for part in parents:
                if isinstance(part, int):
                    cursor = cursor[part]
                else:
                    cursor = cursor[part]

            if leaf in cursor:
                value = cursor[leaf]
                if isinstance(value, dict) and not value:
                    del cursor[leaf]
                elif isinstance(value, list) and not value:
                    del cursor[leaf]
        except (KeyError, IndexError, TypeError):
            pass

    def _normalize_terminate_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat termination data dictionary to nested ADP terminate request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing termination data with keys:
                - associate_oid: Worker's Associate OID (required)
                - termination_date: Termination date (YYYY-MM-DD format) (required)
                - termination_reason_code: Termination reason code (required)

        Returns:
            Dict[str, Any]: Nested structure ready for ADP terminate API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        # Check required fields
        required_fields = ['associate_oid', 'termination_date', 'termination_reason_code']
        missing_fields = [field for field in required_fields if field not in flat_data or not flat_data[field]]

        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build nested structure
            nested_data = {
            "events": [
                {
                    "data": {
                        "eventContext": {
                            "worker": {
                                    "associateOID": str(flat_data['associate_oid'])
                            }
                        },
                        "transform": {
                            "worker": {
                                "workerDates": {
                                        "terminationDate": str(flat_data['termination_date'])
                                },
                                "terminationReasonCode": {
                                        "codeValue": str(flat_data['termination_reason_code'])
                                }
                            }
                        }
                    }
                }
            ]
        }

            return nested_data

        except Exception as e:
            raise ValueError(f"Termination data normalization failed: {str(e)}")

    def _normalize_rehire_data(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat rehire data dictionary to nested ADP rehire request structure.

        Args:
            flat_data (Dict[str, Any]): Flat dictionary containing rehire data with required fields:
                - associate_oid: Worker's Associate OID (required)
                - rehire_date: Rehire date (YYYY-MM-DD format) (required)
                - effective_date_time: Effective date time (YYYY-MM-DD format) (required)
                - reason_code: Reason code for rehire (optional, defaults to "IMPORT")

        Returns:
            Dict[str, Any]: Nested structure ready for ADP rehire API request

        Raises:
            ValueError: If required fields are missing or normalization fails
        """
        # Check required fields
        required_fields = ['associate_oid', 'rehire_date', 'effective_date_time']
        missing_fields = [field for field in required_fields if field not in flat_data or not flat_data[field]]

        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        try:
            # Build rehire request structure according to ADP API specification
            rehire_request = {
                "events": [
                    {
                        "data": {
                            "transform": {
                                "effectiveDateTime": str(flat_data['effective_date_time']),
                                "eventStatusCode": {
                                    "codeValue": str(flat_data.get('event_status_code', 'Completed'))
                                },
                                "worker": {
                                    "associateOID": str(flat_data['associate_oid']),
                                    "workerDates": {
                                        "rehireDate": str(flat_data['rehire_date'])
                                    },
                                    "workerStatus": {
                                        "reasonCode": {
                                            "codeValue": str(flat_data.get('reason_code', 'IMPORT'))
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            }

            return rehire_request

        except Exception as e:
            raise ValueError(f"Rehire data normalization failed: {str(e)}")
