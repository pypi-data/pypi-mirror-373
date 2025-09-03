# BrynQ SDK ADP Decidium

Python SDK for ADP (Automatic Data Processing) API - Decidium Integration. This package provides all the essential functions needed to interact with ADP HR systems.

## Installation

```bash
pip install brynq_sdk_adp_decidium
```

## Quick Start

```python
from brynq_sdk_adp_decidium.decidium import Decidium

# Create Decidium instance
decidium = Decidium()

# Get all workers
workers, invalid_workers = decidium.workers.get()

# Get specific worker by ID
worker, invalid_data = decidium.workers.get_by_id("rrp0423-jterras-2jr")
```

## Core Features

### 1. Worker Management (Workers)

#### Listing Workers
```python
# Get all workers
workers, invalid_workers = decidium.workers.get()

# Get specific worker by ID
worker, invalid_data = decidium.workers.get_by_id("associate_oid_here")
```

#### Hiring New Workers
```python
# New worker data
new_worker_data = {
    "given_name": "Yakup",
    "family_name_1": "Keskin",
    "gender_code": "M",
    "hire_date": "2025-08-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",
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

# Hire the worker
result = decidium.workers.hire(new_worker_data, role_code="practitioner")
```

#### Updating Worker Information
```python
# Fields to update
update_data = {
    "birth_date": "1985-02-11",
    "gender": "M",
    "business_email": "new_business_email@adp.com",
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
    "personal_email": "change@adp.com",
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
    "personal_address_subdivision_2_name": "VILLEURBANE"
}

# Update the worker
result = decidium.workers.update(
    associate_oid="rrp0423-arolland-q4q",
    updates_dict=update_data,
    role_code="administrator"
)
```

#### Terminating Workers
```python
# Termination data
terminate_data = {
    "associate_oid": "rrp0423-aaklil-7bf",
    "termination_date": "2025-07-31",
    "termination_reason_code": "DM"
}

# Terminate the worker
result = decidium.workers.terminate(terminate_data, role_code="employee")
```

#### Rehiring Workers
```python
# Rehire data
rehire_data = {
    "associate_oid": "rrp0423-aaklil-7bf",
    "rehire_date": "2025-08-30",
    "effective_date_time": "2025-08-30",
    "hire_date": "2025-08-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",
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

# Rehire the worker
result = decidium.workers.rehire(rehire_data, role_code="employee")
```

### 2. Payroll Management

#### Adding Payroll Data
```python
# Payroll data
pay_data = {
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

# Add payroll data
result = decidium.payroll.add_input_data(pay_data, role_code="manager")
```

### 3. Pay Distributions

#### Updating Pay Distribution
```python
# Pay distribution data
distribution_data = {
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

# Update pay distribution
result = decidium.pay_distributions.update(distribution_data, role_code="manager")
```

### 4. Work Assignment

#### Modifying Work Assignment
```python
# Work assignment data
work_assignment_data = {
    "associate_oid": "rrp0423-agoulette-r9g",
    "effective_date_time": "2024-01-01T00:00:00Z",
    "custom_code_fields": [
        {
            "item_id": "collaborationType",
            "code_value": "SAL"
        }
    ]
}

# Modify work assignment
result = decidium.workers.work_assignment.modify(work_assignment_data, role_code="manager")
```

#### Terminating Work Assignment
```python
# Work assignment termination data
terminate_assignment_data = {
    "associate_oid": "rrp0423-aaklil-7bf",
    "termination_date": "2025-10-30",
    "termination_reason_code": "MU"
}

# Terminate work assignment
result = decidium.workers.work_assignment.terminate(terminate_assignment_data, role_code="manager")
```

### 5. Document Management

#### Adding Identity Documents
```python
# Identity document data
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

# Add identity document
result = decidium.document.create_identity_document(
    associate_oid="rrp0423-agoulette-r9g",
    document_data=identity_document_data,
    role_code="practitioner"
)
```

#### Adding Immigration Documents
```python
# Immigration document data
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

# Add immigration document
result = decidium.document.create_immigration_document(
    associate_oid="rrp0423-agoulette-r9g",
    document_data=immigration_document_data,
    role_code="practitioner"
)
```

## Role Codes

ADP API uses different role codes for different operations:

- `"employee"` - Employee
- `"manager"` - Manager
- `"practitioner"` - Practitioner
- `"administrator"` - Administrator
- `"supervisor"` - Supervisor

## Error Handling

The SDK provides appropriate error handling for all API calls:

```python
try:
    workers, invalid_workers = decidium.workers.get()
    print(f"Successfully retrieved {len(workers)} workers")

    if not invalid_workers.empty:
        print(f"Found {len(invalid_workers)} invalid records")

except ValueError as e:
    print(f"Data validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Data Validation

The SDK validates all input and output data using Pydantic schemas:

```python
# Data validation results
valid_df, invalid_df = decidium.workers.get()

if not invalid_df.empty:
    print("Invalid data found:")
    print(invalid_df)
```

## Supported Document Types

### Identity Documents
- `passport` - Passport
- `SSN` - Social Security Number
- `IDCard` - ID Card
- `visa1` - Visa 1
- `visa2` - Visa 2

### Immigration Documents
- `resPermit` - Residence Permit
- `workPermit` - Work Permit

## Usage Examples

### 1. New Worker Hiring Process
```python
# 1. Prepare worker data
new_worker = {
    "given_name": "Yakup",
    "family_name_1": "Keskin",
    "gender_code": "M",
    "hire_date": "2025-08-01",
    "work_arrangement_code": "900",
    "location_code": "01001",
    "collaboration_type": "CIT",
    "activity": "01",
    "tlm": "Z",
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

# 2. Hire the worker
result = decidium.workers.hire(new_worker, role_code="practitioner")

# 3. Add payroll data
pay_data = {
    "associate_oid": "new_associate_oid",
    "pay_period_start_date": "2025-01-01",
    "pay_inputs": [
        {
            "input_type": "earning",
            "earning_code": "0271",
            "number_of_hours": 40.0
        }
    ]
}
decidium.payroll.add_input_data(pay_data, role_code="manager")
```

### 2. Bulk Worker Information Update
```python
# Get all workers
workers, _ = decidium.workers.get()

# Filter by specific criteria
filtered_workers = workers[workers['location_code'] == '01001']

# Update each worker
for _, worker in filtered_workers.iterrows():
    update_data = {
        "business_email": f"{worker['given_name'].lower()}@company.com"
    }

    decidium.workers.update(
        associate_oid=worker['associate_oid'],
        updates_dict=update_data,
        role_code="administrator"
    )
```
