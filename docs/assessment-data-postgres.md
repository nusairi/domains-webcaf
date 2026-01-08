# Assessment Data Storage (PostgreSQL)

## Where data lives
The core assessment answers are stored in PostgreSQL in the **`webcaf_assessment`** table.
The answers themselves are stored in the **`assessments_data`** JSON field.

Related tables provide the business context:
- **`webcaf_organisation`**: the council or organisation being assessed
- **`webcaf_system`**: the system under assessment (linked to an organisation)
- **`webcaf_userprofile`**: the user’s organisation + role
- **`webcaf_assessment`**: assessment record + JSON answers

## Key tables and columns (business view)

**`webcaf_organisation`**
- `name`, `reference`, `organisation_type`, `contact_name`, `contact_email`

**`webcaf_system`**
- `name`, `reference`, `system_type`, `hosting_type`, `organisation_id`

**`webcaf_userprofile`**
- `user_id`, `organisation_id`, `role`

**`webcaf_assessment`**
- `status` (draft/submitted/completed/cancelled)
- `framework` (e.g., caf32)
- `caf_profile` (baseline/enhanced)
- `assessment_period`
- `review_type`
- `created_on`, `last_updated`
- `system_id` (links to system)
- **`assessments_data` (JSON)** ← **all question answers**

## Diagram (Data Relationships)
```
Organisation (webcaf_organisation)
          |
          v
System (webcaf_system)
          |
          v
Assessment (webcaf_assessment)
          |
          v
assessments_data (JSON answers)

UserProfile (webcaf_userprofile)
          |
          v
Organisation (webcaf_organisation)
```

## What is in assessments_data?
- Each entry is keyed by an outcome code (e.g., `A1.a`, `A1.b`)
- Values store selected statements and comments
- This is the **primary store** for CAF responses
