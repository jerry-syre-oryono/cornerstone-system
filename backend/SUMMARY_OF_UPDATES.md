# Summary of Updates - Alumni Registration & Authentication System

This document summarizes the architectural and functional updates made to the Cornerstone System backend on April 1, 2026.

## 1. Architectural Changes
### Link Table Implementation
- **New Model: `AlumniAccount`**: Introduced a dedicated model in `alumni/models.py` to act as a bridge between the Django `User` (authentication) and the `Person` record (historical alumni data).
  - Uses `OneToOneField` to ensure each alumni record is linked to exactly one user account.
  - Relates `User` as `alumni_profile` and `Person` as `alumni_account`.

### Model Compatibility
- Updated registration logic to support the latest `Person` model schema (using `sir_name` instead of `last_name`).
- Ensured compatibility with Proxy Models (`AYLFAlumni`, `COSAAlumni`, `YouthCorpsAlumni`) by targeting the base `Person` model for searches and links.

## 2. Functional Updates
### Enhanced Registration Flow
- **Verification**: Uses fuzzy matching to find existing alumni records by name and graduation year.
- **Auto-Population**: When a user registers, their email is automatically synced to the `Person` record if it was previously missing.
- **Account Linking**: Automatically creates the `AlumniAccount` bridge during registration.
- **Instant Login**: Users are automatically logged into their new session upon successful registration.

### Authentication & Login
- Updated the login view to return the `person_id` of the linked alumni record, allowing the frontend to easily retrieve profile information.
- Maintained rate limiting on sensitive endpoints to protect against brute-force attacks.

## 3. Administrative Updates
- Registered `AlumniAccount` in the Django Admin portal.
- Admin users can now view and search for links between system users and alumni records via `user__email` or `person__full_name`.

## 4. Quality Assurance
- **Automated Tests**: Created `onboarding/tests.py` covering:
  - Successful registration and data syncing.
  - Prevention of duplicate registrations for the same alumni record.
- **Bug Fixes**: 
  - Resolved `NoReverseMatch` errors by adding names to URL patterns in `config/urls.py`.
  - Fixed environment dependencies (installed `whitenoise` and `dj-database-url`).
  - Configured `LocMemCache` for test environments where Redis is unavailable.

---
*Date: April 1, 2026*
