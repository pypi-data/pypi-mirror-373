import sys
import os
# Add the parent directory to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brynq_sdk_adp_decidium.decidium import Decidium

import json
import pandas as pd
import pandera as pa
from brynq_sdk_functions import Functions
from dotenv import load_dotenv
load_dotenv()


decidium = Decidium()
worker_9_data = {
    # 👤 PERSONAL INFORMATION (from example)
    "given_name": "Yakup",
    "family_name_1": "Keskinaa",
    "gender_code": "M",

    # Required person fields that were missing
    "person_birth_date": "1990-01-01",
    "birth_place_city": "PARIS",
    "birth_place_country": "FR",
    "birth_place_postal_code": "75001",
    "legal_address_country": "FR",
    "legal_address_postal_code": "75001",
    "legal_address_subdivision_1": "75",

    # Required legalAddress fields for Pydantic validation (matching Address schema)
    "legal_address_name_code": "ADDRESS001",
    "legal_address_line_one": "123 RUE DE LA PAIX",
    "legal_address_line_two": "APT 456",
    "legal_address_city_name": "PARIS",
    "legal_address_country_code": "FR",
    "legal_address_country_subdivision_level_2": "75101",  # Valid INSEE code for Paris 1er
    "legal_address_unit": "A",

    "citizenship_country_codes": "FR",
    "identity_document_ssn": "1900101234567",  # Valid SSN format: 1(male) 90(year) 01(month) 01(day) 234(place) 56(sequence) 7(key)

    # Required contract fields that were missing
    # "contract_type": "CDI",  # Using work_arrangement_code instead

    # 💼 HIRING DETAILS (from example)
    "hire_date": "2025-08-01",
    "seniority_date": "2025-08-01",  # Seniority date field added
    "expected_start_date": "2025-08-01",  # Expected start date field added
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",

    # Additional new custom fields for hire/rehire requests
    # "contract_type": "00",  # Invalid code - commented out
    "remuneration_type": "B",
    "work_schedule": "101",

        # 🧪 CUSTOM FIELDS FOR TESTING - Using existing valid field IDs
    # Custom Code Fields (JSON format) - Using existing valid IDs
    "work_assignment_custom_code_fields": json.dumps([
        {"itemID": "workSchedule", "codeValue": "1111", "longName": "TEST SCHEDULE 1111"},
        {"itemID": "remunerationType", "codeValue": "2222", "longName": "TEST REMUNERATION 2222"},
        {"itemID": "activity", "codeValue": "3333", "longName": "TEST ACTIVITY 3333"}
    ]),

    # Custom String Fields (JSON format) - Using existing valid IDs
    "work_assignment_custom_string_fields": json.dumps([
        {"itemID": "fullTimeHours", "stringValue": "TEST_STRING_1111"},
        {"itemID": "weeklyHours", "stringValue": "TEST_STRING_2222"}
    ]),

    # Custom Date Fields (JSON format) - Using existing valid IDs
    "work_assignment_custom_date_fields": json.dumps([
        {"itemID": "classificationDate", "dateValue": "2025-11-11"},
        {"itemID": "hireDate", "dateValue": "2025-12-22"}
    ]),

    # Custom Number Fields (JSON format) - Using existing valid IDs
    "work_assignment_custom_number_fields": json.dumps([
        {"itemID": "fullTimeHours", "numberValue": 1111.11},
        {"itemID": "weeklyHours", "numberValue": 2222.22},
        {"itemID": "monthlyHours", "numberValue": 3333.33}
    ]),

    # Job Information - Using valid codes
    # "job_code": "DEV001",  # Invalid code - commented out
    "job_title": "Software Developer",
    # "job_function_code": "IT",  # Invalid code - commented out

    # Remuneration
    # "remuneration_type": "SALARY",  # Invalid string - using "B" code instead (already defined above)
    # "work_schedule": "FULL_TIME",  # Invalid string - using "101" code instead (already defined above)
    "coefficient": 1.0,
    "full_time_hours": 40.0,
    "weekly_hours": 40.0,
    "monthly_hours": 173.33,

    # 💰 NEW SALARY FIELDS - All optional for flexible testing
    # Base Remuneration (matches get method paths) - CSAT codes commented until we find valid ones
    # "recording_basis_code": "ANNUAL",       # baseRemuneration.recordingBasisCode (CSAT reference table)
    # "remuneration_basis_code": "ANNUAL",    # remunerationBasisCode (top level - matches get method)
    # Need to check existing employees to find valid CSAT reference codes

    # All Amount Fields (matching get method structure)
    "monthly_rate_amount": 3500.00,         # baseRemuneration.monthlyRateAmount.amountValue
    "monthly_rate_currency": "EUR",         # baseRemuneration.monthlyRateAmount.currencyCode
    "annual_rate_amount": 42000.00,         # baseRemuneration.annualRateAmount.amountValue
    "annual_rate_currency": "EUR",          # baseRemuneration.annualRateAmount.currencyCode
    "pay_period_rate_amount": 1500.00,      # baseRemuneration.payPeriodRateAmount.amountValue
    "pay_period_currency": "EUR",           # baseRemuneration.payPeriodRateAmount.currencyCode

    # Custom Salary Fields - Need to find valid reference codes
    # "mode_rem_sath": "MONTHLY",             # Remuneration mode (CSAT filter table) - need valid code
    # "old_sath": "LEGACY",                   # Old theoretical annual salary (CSATH reference table - ATOO only)
    # Commented until we identify valid CSAT/CSATH reference codes

    # Internship Compensation (ZEM client only, for remunerationType = "S")
    # "internship_compensation": 500.00,    # Uncomment for intern testing
    # "internship_currency": "EUR",         # Uncomment for intern testing

    # 📍 WORK LOCATION DETAILS (from example)
    "location_short_name": "ORION CONSEIL LEVALLOIS",
    "location_long_name": "ORION CONSEIL LEVALLOIS",
    "address_name_code": "66382041300198",
    "address_short_name": "SIRET",
    "address_line_one": "COMPLEMENT ADRESSE",
    "address_line_two": "209 B RUE ANATOLE FRANCE",
    "address_city_name": "LEVALLOIS PERRET",
    "address_country_code": "FR",
    "address_postal_code": "92688",
    "address_unit": "453B",
    "address_country_subdivision_level_2_code": "LOCALITE",
    "address_country_subdivision_level_2_short_name": "LOCALITE",
    "address_country_subdivision_level_2_long_name": "LOCALITE",
    "address_country_subdivision_level_2_subdivision_type": "INSEE"
}
results_9 = decidium.workers.create(worker_9_data, role_code="practitioner")
workers = decidium.workers.get()
work_assignment_professional_category_data = {
    "associate_oid": 'rrp0423-csenecaut-4pr',  # Use the actual associate_oid from created employee
    "effective_date_time": "2025-08-02T00:00:00Z",  # Day after hire_date - employee should be active
    "professional_category_code": "30",
    "professional_category_name": "Employé",
    "custom_code_fields": [
        {
            "item_id": "collaborationType",
            "code_value": "SAL",
            "long_name": "Salarié"
        },
        {
            "item_id": "workSchedule",
            "code_value": "101",
            "long_name": "Full Time Schedule"
        },
        {
            "item_id": "remunerationType",
            "code_value": "F",
            "long_name": "Fixed Salary"
        },
        # {
        #     "item_id": "modeRemSATH",
        #     "code_value": "MONTHLY",  # Need valid CSAT code
        #     "long_name": "Monthly Mode"
        # },
        # {
        #     "item_id": "oldSATH",
        #     "code_value": "LEGACY",   # Need valid CSATH code
        #     "long_name": "Legacy Salary Type"
        # }
        # Commented until we find valid reference codes
    ],

    # 💰 BASE REMUNERATION - All amount fields (using valid CSAT codes)
    # "recording_basis_code": "MONTHLY",       # baseRemuneration.recordingBasisCode (CSAT) - Try valid code
    # "remuneration_basis_code": "MONTHLY",    # remunerationBasisCode (top level) - Try valid code
    # Commented out until we find valid CSAT codes from existing employees

    # Amount Fields with realistic values
    "monthly_rate_amount": 9999.00,           # baseRemuneration.monthlyRateAmount.amountValue
    "monthly_rate_currency": "EUR",           # baseRemuneration.monthlyRateAmount.currencyCode
    "annual_rate_amount": 9999.00,           # baseRemuneration.annualRateAmount.amountValue
    "annual_rate_currency": "EUR",            # baseRemuneration.annualRateAmount.currencyCode
    "pay_period_rate_amount": 9999.33,        # baseRemuneration.payPeriodRateAmount.amountValue
    "pay_period_currency": "EUR",             # baseRemuneration.payPeriodRateAmount.currencyCode

    # 💰 CUSTOM AMOUNT FIELDS (if needed for special cases)
    # "internship_compensation": 600.00,      # For interns only (ZEM client)
    # "internship_currency": "EUR"            # For interns only (ZEM client)
}
work_assignment_resp = decidium.workers.work_assignment.update(work_assignment_professional_category_data, role_code="administrator")


# 🔍 CHECK VALID CSAT CODES - Get existing employee to see valid remuneration_basis_code values
print("=== Checking existing employee for valid CSAT codes ===")
existing_employee = decidium.workers.get_by_id("ykeskinaaaa-xjr")
if len(existing_employee[0]) > 0:
    sample_employee = existing_employee[0].iloc[0].to_dict()
    print(f"remuneration_basis_code: {sample_employee.get('remuneration_basis_code', 'N/A')}")
    print(f"monthly_rate_amount: {sample_employee.get('monthly_rate_amount', 'N/A')}")
    print(f"annual_rate_amount: {sample_employee.get('annual_rate_amount', 'N/A')}")
    print(f"Sample employee data keys: {list(sample_employee.keys())}")
else:
    print("No employee data found")
print("=" * 50)



# 💰 INTERN TEST DATA - Example with internship compensation (ZEM client only)
intern_test_data = {
    # Copy basic fields from worker_9_data
    "given_name": "Marie",
    "family_name_1": "STAGIAIRE",
    "gender_code": "F",
    "person_birth_date": "2000-01-01",
    "birth_place_city": "LYON",
    "birth_place_country": "FR",
    "birth_place_postal_code": "69001",
    "legal_address_country": "FR",
    "legal_address_postal_code": "69001",
    "legal_address_subdivision_1": "69",
    "legal_address_name_code": "INTERN001",
    "legal_address_line_one": "123 RUE DE L'UNIVERSITE",
    "legal_address_line_two": "RESIDENCE ETUDIANTE",
    "legal_address_city_name": "LYON",
    "legal_address_country_code": "FR",
    "legal_address_country_subdivision_level_2": "69001",
    "legal_address_unit": "B12",
    "citizenship_country_codes": "FR",
    "identity_document_ssn": "2000101234567",

    # Hiring details for intern
    "hire_date": "2025-09-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",

    # INTERN SPECIFIC FIELDS
    "remuneration_type": "S",  # "S" for Stagiaire (intern)
    "work_schedule": "101",

    # 💰 INTERN SALARY FIELDS (ZEM client only)
    "internship_compensation": 600.00,      # Indemnité de stage
    "internship_currency": "EUR",           # Currency
    "recording_basis_code": "INTERN",       # Special basis for interns
    "remuneration_basis_code": "INTERN",    # Top level basis code

    # Location details (same as main example)
    "location_short_name": "ORION CONSEIL LEVALLOIS",
    "location_long_name": "ORION CONSEIL LEVALLOIS",
    "address_name_code": "66382041300198",
    "address_short_name": "SIRET",
    "address_line_one": "COMPLEMENT ADRESSE",
    "address_line_two": "209 B RUE ANATOLE FRANCE",
    "address_city_name": "LEVALLOIS PERRET",
    "address_country_code": "FR",
    "address_postal_code": "92688",
    "address_unit": "453B",
    "address_country_subdivision_level_2_code": "LOCALITE",
    "address_country_subdivision_level_2_short_name": "LOCALITE",
    "address_country_subdivision_level_2_long_name": "LOCALITE",
    "address_country_subdivision_level_2_subdivision_type": "INSEE"
}

# Uncomment to test intern creation (ZEM client only)
# intern_results = decidium.workers.create(intern_test_data, role_code="practitioner")

workers = decidium.workers.get()

worker_by_id = decidium.workers.get_by_id("rrp0423-tali-dg6")

# Test data for worker update name (simplified test)
worker_update_name_data = {
    "legal_name_given": "YAKUBOO",
    "legal_name_family_1": "KESKINKOOOOO",
    "legal_name_salutation": "M"
}

name_update_results = decidium.workers.update(
    associate_oid="ykeskinaaaa-bsc",
    data=worker_update_name_data,
    role_code="administrator"
)

terminate_data = {
    "associate_oid": "ykeskinaaaa-94g",
    "termination_date": "2025-08-30",
    "termination_reason_code": "DM"
}
update_id ='ykeskinaaaa-bsc'
result = decidium.workers.terminate(terminate_data,role_code="employee")


worker_by_id = decidium.workers.get_by_id("rrp0423-tali-dg6")

work_assignment_terminate_data = {
    "associate_oid": "rrp0423-tberthe-7vc",
    "termination_date": "2025-10-30",
    "termination_reason_code": "MU",
    "termination_reason_short_name": "MU"
}


results_wa_terminate = decidium.workers.work_assignment.terminate(work_assignment_terminate_data, role_code="manager")
# Test Work Assignment Update with Professional Category

dependents = decidium.dependents.get_by_employee_id("rrp0423-bbureau-k3g")
dependent_data = {
    "associate_oid": "rrp0423-bbureau-k3g",
    "relationship_type_code": "E",
    "given_name": "aaaaaaaa",
    "family_name_1": "DEPENDENT",
    "birth_date": "2000-01-15",
    "gender_code": "M",
    "city_name": "PARIS",
    "postal_code": "75001",
    "country_code": "FR"
}
create_resp = decidium.dependents.create(dependent_data, role_code="administrator")
dependent_delete_data = {
    "associate_oid": "rrp0423-bbureau-k3g",
    "dependent_item_id": "6"
}
delete_resp = decidium.dependents.delete(dependent_delete_data, role_code="administrator")

dependent_update_data = {
    "associate_oid": "rrp0423-bbureau-k3g",
    "dependent_item_id": "2",
    "given_name": "ENFANT DEUX"
}
update_resp = decidium.dependents.update(dependent_update_data, role_code="administrator")
# Test Dependent Update
# Test Dependent Delete








# Worker 9: Updated with all fields from the working example
dists = decidium.pay_distributions.get_by_employee_id("rrp0423-tali-dg6")

pay_distribution_data = {
    "associate_oid": "rrp0423-agoulette-r9g",
    "distribution_instructions": [
        {
            "precedence_code": "primary",
            "precedence_short_name": "Compte principal",
            "precedence_long_name": "Compte principal",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "1",
            "iban": "FR7610107154545663105548",
            "account_name": "COMPTE PRIMAIRE 1",
            "swift_code": "BBBBFRPPXXX"
        },
        {
            "precedence_code": "secondary",
            "precedence_short_name": "Compte secondaire",
            "precedence_long_name": "Compte secondaire",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "2",
            "iban": "FR763000203234567890168",
            "account_name": "COMPTE SECONDAIRE 2",
            "swift_code": "CCCCFRPP"
        },
        {
            "precedence_code": "expenses",
            "precedence_short_name": "Compte frais",
            "precedence_long_name": "Compte frais",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "3",
            "iban": "FR7614410022234567890163",
            "account_name": "COMPTE FRAIS",
            "swift_code": "CCCCFR2A"
        }
    ]
}

results_pd = decidium.pay_distributions.update(pay_distribution_data, role_code="manager")


rehire_data = {
    # 👤 PERSONAL INFORMATION (from example)
    "associate_oid": "rrp0423-aaklil-7bf",
    "rehire_date": "2025-08-30",
    "effective_date_time": "2025-08-30",
    # 💼 HIRING DETAILS (from example)
    "hire_date": "2025-08-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",

    # 📍 WORK LOCATION DETAILS (from example)
    "location_short_name": "ORION CONSEIL LEVALLOIS",
    "location_long_name": "ORION CONSEIL LEVALLOIS",
    "address_name_code": "66382041300198",
    "address_short_name": "SIRET",
    "address_line_one": "COMPLEMENT ADRESSE",
    "address_line_two": "209 B RUE ANATOLE FRANCE",
    "address_city_name": "LEVALLOIS PERRET",
    "address_country_code": "FR",
    "address_postal_code": "92688",
    "address_unit": "453B",
    "address_country_subdivision_level_2_code": "LOCALITE",
    "address_country_subdivision_level_2_short_name": "LOCALITE",
    "address_country_subdivision_level_2_long_name": "LOCALITE",
    "address_country_subdivision_level_2_subdivision_type": "INSEE",

    # New fields for company and cost center information
    "company_name": "ORION CONSEIL",
    "company_code": "OR001",
    "establishment_code": "66382041300198",
    "cost_center_id": "CC001",
    "cost_center_name": "Sales Department",
    "cost_center_percentage": 100.0,

    # New custom fields
    "payroll_admin_group": "ADMIN_GROUP_1",
    "professional_category": "30",
    "professional_category_name": "Employé",
    "collaboration_type": "SAL",
    "collaboration_type_name": "Salarié",

    # Additional contract fields
    "contract_code": "EMP",
    "contract_reason": "NEW_HIRE",
    "qualification_code": "SAL",

    # Additional new custom fields for rehire requests
    # "contract_type": "00",  # Invalid code - commented out
    "remuneration_type": "B",
    "work_schedule": "101"
}

result = decidium.workers.rehire(rehire_data, role_code="employee") ## JSON parse error ADP side.
# Test Worker 9: Another STA (Stagiaire) without payrollProcessingStatusCode
print("=== Testing Worker 9: Another STA (Stagiaire) without payrollProcessingStatusCode ===")
# Direct usage of worker_9_data - no more dictionary comprehension needed
workers = decidium.workers.get()




update_test_data = {
    "birth_date": "1985-02-11",
    "gender": "M",
    "business_email": "new_business_email@decidium.com",
    "business_mobile": "0633333333",
    "legal_name_given": "PHILIPPE",
    "legal_name_family_1": "MASSINA",
    "legal_name_salutation": "M",
    "marital_status_effective_date": "2013-02-01",
    "marital_status_code": "C",
    "citizenship_code": "ES",
    "citizenship_short_name": "ESPAGNE",
    "citizenship_long_name": "ESPAGNE",
    "birth_place_city_name": "REDON",
    "birth_place_country_code": "FR",
    "birth_place_postal_code": "35600",
    "business_fax": "0202020202",
    "business_landline": "0251010101",
    "business_pager": "0533333333",
    "personal_email": "change@decidium.com",
    "personal_fax": "0444444444",
    "personal_landline": "0533333333",
    "personal_mobile": "0633333333",
    "legal_address_country_code": "FR",
    "legal_address_postal_code": "44300",
    "legal_address_line_five": "LIEU DIT",
    "legal_address_building_number": "21",
    "legal_address_building_extension": "B",
    "legal_address_street_name": "Legal address Change",
    "legal_address_subdivision_1": "NANTES",
    "legal_address_subdivision_2_code": "69266",
    "legal_address_subdivision_2_name": "VILLEURBANNE",
    "personal_address_country_code": "FI",
    "personal_address_city_name": "Helsinski",
    "personal_address_postal_code": "44300",
    "personal_address_line_five": "LIEU DIT",
    "personal_address_building_number": "21",
    "personal_address_building_extension": "B",
    "personal_address_street_name": "Personal address change",
    "personal_address_subdivision_2_code": "69266",
    "personal_address_subdivision_2_name": "VILLEURBANNE",

    # New fields for company and cost center information
    "company_name": "ORION CONSEIL",
    "company_code": "OR001",
    "establishment_code": "66382041300198",
    "cost_center_id": "CC001",
    "cost_center_name": "Sales Department",
    "cost_center_percentage": 100.0,

    # New custom fields
    "payroll_admin_group": "ADMIN_GROUP_1",
    "professional_category": "30",
    "professional_category_name": "Employé",
    "collaboration_type": "SAL",
    "collaboration_type_name": "Salarié",

    # Additional contract fields
    "contract_code": "EMP",
    "contract_reason": "NEW_HIRE",
    "qualification_code": "SAL"
}

# Test associate OID (replace with a real one)
test_associate_oid = "rrp0423-arolland-q4q"  # Replace with actual associate OID

# Test the update_worker_fields function
update_results = decidium.workers.update(
    associate_oid=test_associate_oid,
    updates_dict=update_test_data,
    role_code="administrator"
)





rehire_data = {
    # 👤 PERSONAL INFORMATION (from example)
    "associate_oid": "rrp0423-aaklil-7bf",
    "rehire_date": "2025-08-30",
    "effective_date_time": "2025-08-30",
    # 💼 HIRING DETAILS (from example)
    "hire_date": "2025-08-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",

    # 📍 WORK LOCATION DETAILS (from example)
    "location_short_name": "ORION CONSEIL LEVALLOIS",
    "location_long_name": "ORION CONSEIL LEVALLOIS",
    "address_name_code": "66382041300198",
    "address_short_name": "SIRET",
    "address_line_one": "COMPLEMENT ADRESSE",
    "address_line_two": "209 B RUE ANATOLE FRANCE",
    "address_city_name": "LEVALLOIS PERRET",
    "address_country_code": "FR",
    "address_postal_code": "92688",
    "address_unit": "453B",
    "address_country_subdivision_level_2_code": "LOCALITE",
    "address_country_subdivision_level_2_short_name": "LOCALITE",
    "address_country_subdivision_level_2_long_name": "LOCALITE",
    "address_country_subdivision_level_2_subdivision_type": "INSEE",

    # New fields for company and cost center information
    "company_name": "ORION CONSEIL",
    "company_code": "OR001",
    "establishment_code": "66382041300198",
    "cost_center_id": "CC001",
    "cost_center_name": "Sales Department",
    "cost_center_percentage": 100.0,

    # New custom fields
    "payroll_admin_group": "ADMIN_GROUP_1",
    "professional_category": "30",
    "professional_category_name": "Employé",
    "collaboration_type": "SAL",
    "collaboration_type_name": "Salarié",

    # Additional contract fields
    "contract_code": "EMP",
    "contract_reason": "NEW_HIRE",
    "qualification_code": "SAL"
}

result = decidium.workers.rehire(rehire_data, role_code="employee") ## JSON parse error ADP side.
# Test immigration document add
immigration_document_data = {
    "document_id": "RF12e345",
    "type_code": "resPermit",
    "issue_date": "2025-02-01",
    "expiration_date": "2030-02-01",
    "issuing_party": {
        "nameCode": {
            "codeValue": "Préfecture de Paris"
        }
    },
    "document_number": "RF12e345"
}

immigration_result = decidium.document.create_immigration_document(
    associate_oid="rrp0423-agoulette-r9g",
    document_data=immigration_document_data,
    role_code="practitioner"
)
# Test identity document add
identity_document_data = {
    "document_id": "123456789",
    "type_code": "passport",
    "issue_date": "2020-01-15",
    "expiration_date": "2030-01-15",
    "issuing_party": {
        "nameCode": {
            "codeValue": "Government of France"
        }
    },
    "document_number": "FR123456789"
}


document_result = decidium.document.create_identity_document(
    associate_oid="rrp0423-agoulette-r9g",
    document_data=identity_document_data,
    role_code="practitioner"
)

# Create test dictionary for pay data input


pay_data_input_dict = {
    "associate_oid": "rrp0423-agoulette-r9g",
    "pay_period_start_date": "2024-08-01",
    "pay_inputs": [
        {
            "input_type": "earning",
            "earning_code": "0271",
            "number_of_hours": 20.0,
            "earned_pay_period_start_date": "2024-07-01"
        },
        {
            "input_type": "earning",
            "earning_code": "1622",
            "number_of_hours": 2.0,
            "earned_pay_period_start_date": "2024-07-01"
        },
        {
            "input_type": "calculation_factor",
            "calculation_factor_code": "I001",
            "calculation_factor_rate_value": "7.5",
            "configuration_tag_code": "",
            "validity_period_start_date": "2024-07-01T00:00:00Z"
        },
        {
            "input_type": "time",
            "time_evaluation_start_date": "2024-07-15",
            "time_evaluation_end_date": "2024-07-21",
            "segment_classification_code": "CP"
        }
    ]
}
results_pay = decidium.payroll.add_input_data(pay_data_input_dict, role_code="manager")
# Test Pay Distribution Change
print("=== Testing Pay Distribution Change ===")
# Test Pay Data Input Add
print("=== Testing Pay Data Input Add ===")



work_assignment_data = {
    "associate_oid": "rrp0423-agoulette-r9g",
    "effective_date_time": "2024-01-01T00:00:00Z",
    "custom_code_fields": [
        {
            "item_id": "collaborationType",
            "code_value": "SAL"
        }
    ],

    # New fields for company and cost center information
    "company_name": "ORION CONSEIL",
    "company_code": "OR001",
    "establishment_code": "66382041300198",
    "cost_center_id": "CC001",
    "cost_center_name": "Sales Department",
    "cost_center_percentage": 100.0,

    # New custom fields
    "payroll_admin_group": "ADMIN_GROUP_1",
    "professional_category": "30",
    "professional_category_name": "Employé",
    "collaboration_type": "SAL",
    "collaboration_type_name": "Salarié",

    # Additional contract fields
    "contract_code": "EMP",
    "contract_reason": "NEW_HIRE",
    "qualification_code": "SAL"
}
print("\n" + "="*50 + "\n")



# Test data for problematic fields only
problematic_fields_data = {
    "citizenship_code": "ES",
    "citizenship_short_name": "ESPAGNE",
    "citizenship_long_name": "ESPAGNE",
    "business_landline": "0251010101",
    "personal_email": "change@decidium.com",
    "personal_fax": "0444444444",
    "personal_landline": "0533333333",
    "personal_mobile": "0633333333",
    "legal_address_country_code": "FR",
    "legal_address_postal_code": "44300",
    "legal_address_line_five": "LIEU DIT",
    "legal_address_building_number": "21",
    "legal_address_building_extension": "B",
    "legal_address_street_name": "Legal address Change",
    "legal_address_subdivision_1": "NANTES",
    "legal_address_subdivision_2_code": "69266",
    "legal_address_subdivision_2_name": "VILLEURBANNE",
    "personal_address_country_code": "FI",
    "personal_address_city_name": "Helsinski",
    "personal_address_postal_code": "44300",
    "personal_address_line_five": "LIEU DIT",
    "personal_address_building_number": "21",
    "personal_address_building_extension": "B",
    "personal_address_street_name": "Personal address change",
    "personal_address_subdivision_2_code": "69266",
    "personal_address_subdivision_2_name": "VILLEURBANNE",

    # New fields for company and cost center information
    "company_name": "ORION CONSEIL",
    "company_code": "OR001",
    "establishment_code": "66382041300198",
    "cost_center_id": "CC001",
    "cost_center_name": "Sales Department",
    "cost_center_percentage": 100.0,

    # New custom fields
    "payroll_admin_group": "ADMIN_GROUP_1",
    "professional_category": "30",
    "professional_category_name": "Employé",
    "collaboration_type": "SAL",
    "collaboration_type_name": "Salarié",

    # Additional contract fields
    "contract_code": "EMP",
    "contract_reason": "NEW_HIRE",
    "qualification_code": "SAL"
}
results_wa = decidium.workers.work_assignment.modify(work_assignment_data, role_code="manager")
# Test Work Assignment Termination
print("=== Testing Work Assignment Termination ===")


# Test Document operations
print("=== Testing Document Operations ===")
# Test data





# Test Work Assignment Modification

# Test Pay Distribution Update
pay_distribution_test_data = {
    "associate_oid": "adupont-7150mp3",
    "record_type": "1",
    "distribution_instructions": [
        {
            "precedence_code": "primary",
            "precedence_short_name": "Compte principal",
            "precedence_long_name": "Compte principal",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "1",
            "iban": "FR7610107154545663105548",
            "account_name": "COMPTE PRIMAIRE 1",
            "swift_code": "BBBBFRPPXXX"
        },
        {
            "precedence_code": "secondary",
            "precedence_short_name": "Compte secondaire",
            "precedence_long_name": "Compte secondaire",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "2",
            "iban": "FR763000203234567890168",
            "account_name": "COMPTE SECONDAIRE 2",
            "swift_code": "CCCCFRPP"
        },
        {
            "precedence_code": "expenses",
            "precedence_short_name": "Compte frais",
            "precedence_long_name": "Compte frais",
            "payment_method_code": "V",
            "payment_method_short_name": "Virement",
            "payment_method_long_name": "Virement",
            "item_id": "3",
            "iban": "FR7614410022234567890163",
            "account_name": "COMPTE FRAIS",
            "swift_code": "CCCCFR2A"
        }
    ]
}
