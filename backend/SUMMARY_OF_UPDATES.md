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
- **Swagger Assets**: Configured `drf-spectacular-sidecar` to ensure all documentation assets (CSS/JS) are served directly from the backend, fixing the "blank page" issue on Render.
- **CORS Configuration**: Installed and configured `django-cors-headers` to allow the React frontend to securely communicate with the API.
- **Bug Fixes**: 
  - Resolved `NoReverseMatch` errors by adding names to URL patterns in `config/urls.py`.
  - Fixed environment dependencies (installed `whitenoise` and `dj-database-url`).
  - Configured `LocMemCache` for test environments where Redis is unavailable.

---
*Date: April 1, 2026*

## 5. SMTP & Email System Update (April 22, 2026)
### SMTP Configuration
- Configured production SMTP settings using `mail.mak.ac.ug`.
- Updated `backend/config/settings.py` to use environment-aware defaults for email hosting, port, and credentials.
- Set `DEFAULT_FROM_EMAIL` to "Cornerstone System <syre.jerry@mak.ac.ug>".

### Password Reset Enhancements
- **OTP Flow**: Implemented a 3-step OTP-based password reset flow (Request -> Verify -> Set).
- **Professional Email Templates**:
  - Created a modern, responsive HTML email template for OTP delivery (`onboarding/templates/onboarding/emails/password_reset_otp.html`).
  - Features include high-contrast headers, clear OTP display, and mobile-friendly styling.
- **View Integration**: Updated `onboarding/views.py` to render and send multi-part (HTML + Plain Text) emails using Django's template engine.

### Documentation & Environment
- Updated `.env.example` with the latest SMTP configuration variables.
- Added comprehensive documentation for the Password Reset OTP API endpoints in `API_DOCUMENTATION.md`.
