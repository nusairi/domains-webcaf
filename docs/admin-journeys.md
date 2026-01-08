# Admin Portal User Journeys

## Journey 1 — Admin login
- Actor: Admin user (Django superuser)
- Preconditions: Admin account exists; app is running
- Steps:
  - Navigate to `/admin/`
  - Enter admin username + password
- Outputs: Admin dashboard access

## Journey 2 — Create Organisation
- Actor: Admin user
- Preconditions: Admin logged in
- Steps:
  - Admin → Organisations → Add
  - Enter organisation name, type, optional reference
  - Save
- Outputs: Organisation record created

## Journey 3 — Create User Profile (enable access)
- Actor: Admin user
- Preconditions: End user has logged in at least once (user record exists)
- Steps:
  - Admin → Users → locate user by email
  - Admin → User Profiles → Add
  - Set User, Organisation, Role
  - Save
- Outputs: User can access “My account” and assessment workflows

## Journey 4 — Manage Systems
- Actor: Admin user
- Preconditions: Organisation exists
- Steps:
  - Admin → Systems → Add
  - Enter system details (name, type, org, description)
  - Save
- Outputs: System available for assessment

## Journey 5 — Manage Assessments
- Actor: Admin user
- Preconditions: Systems exist
- Steps:
  - Admin → Assessments → View/filter by status/org/system
  - Review status or details
- Outputs: Oversight of self-assessments

## Journey 6 — Configure Assessment Period
- Actor: Admin user
- Preconditions: Admin logged in
- Steps:
  - Admin → Configuration → Edit
  - Set current period and end date
  - Save
- Outputs: System-wide assessment period updated

## Journey 7 — Bulk Import Organisations
- Actor: Admin user
- Preconditions: Admin logged in; CSV prepared
- Steps:
  - Admin → Organisations → Import CSV
  - Upload CSV template
  - Submit
- Outputs: Organisations and users created/linked in bulk
