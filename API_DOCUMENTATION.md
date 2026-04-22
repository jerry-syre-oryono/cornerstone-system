# API Documentation: Onboarding & Authentication

This document details the API endpoints for user authentication and management within the Cornerstone system.

---

## 1. Register Alumni
Creates a new `User` account linked to an existing `Person` record. If the alumni record is NOT found, it automatically creates a `SignupRequest` for admin review.

**Endpoint:** `/api/onboarding/register/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

### Request Payload (JSON)
| Field | Type | Description |
|---|---|---|
| `full_name` | String | Exactly matches the existing alumni person name. |
| `graduation_year` | Integer | The year the alumni graduated or completed their program. |
| `email` | String | Valid email address. This will be assigned as their system login. |
| `password` | String | A secure password. |
| `password_again` | String | A confirmation of the `password`. Must match. |
| `phone` | String | (Optional) Phone number for SignupRequest. |
| `gender` | String | (Optional) 'M' or 'F' for SignupRequest. |
| `course` | String | (Optional) Course studied for SignupRequest. |

### Responses
**Success (200 OK):** (When alumni record is FOUND)
```json
{
  "status": "account_created",
  "user_id": 12
}
```

**Success (202 Accepted):** (When alumni record is NOT FOUND)
```json
{
  "status": "request_submitted",
  "message": "Alumni record not found. Your details have been submitted for admin review."
}
```

---

## 2. Submit Signup Request
Explicitly submit a signup request. This is also handled automatically by the `/api/onboarding/register/` endpoint if a record isn't found.

**Endpoint:** `/api/onboarding/signup-request/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

---

## 3. List Pending Signup Requests
Returns a list of all signup requests with status `PENDING`.

**Endpoint:** `/api/onboarding/signup-requests/pending/`  
**Method:** `GET`  
**Authentication & Permissions:** Admin/Staff only.

---

## 4. Approve Signup Request
Approves a signup request, creates a `Person` and `User` record, and links them.

**Endpoint:** `/api/onboarding/signup-requests/{id}/approve/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

---

## 5. Reject Signup Request
Marks a signup request as `REJECTED`. The details remain in the `SignupRequest` table.

**Endpoint:** `/api/onboarding/signup-requests/{id}/reject/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

---

## 6. Delete Signup Request
Permanently removes a signup request from the database.

**Endpoint:** `/api/onboarding/signup-requests/{id}/delete/`  
**Method:** `DELETE`  
**Authentication & Permissions:** Admin/Staff only.

---

## 7. Total Signed Up Users
Returns counts of total users and total alumni users in the system.

**Endpoint:** `/api/users/total/`  
**Method:** `GET`  
**Authentication & Permissions:** Admin/Staff only.

---

## 8. Admin Add New User
Directly creates a new user in the system.

**Endpoint:** `/api/users/create/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

---

## 9. Login User
Authenticates a user via their email and password.

**Endpoint:** `/api/onboarding/login/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

---

## 10. Password Reset (OTP Flow)

### Step 1: Request OTP
Generates a 6-digit OTP and sends it to the user's email.

**Endpoint:** `/api/onboarding/password-reset-otp/`  
**Method:** `POST`  
**Payload:** `{"email": "user@example.com"}`

### Step 2: Verify OTP
Validates the OTP sent to the email.

**Endpoint:** `/api/onboarding/password-reset-verify/`  
**Method:** `POST`  
**Payload:** `{"email": "user@example.com", "otp": "123456"}`

### Step 3: Set New Password
Sets a new password using the verified OTP.

**Endpoint:** `/api/onboarding/password-reset-set-password/`  
**Method:** `POST`  
**Payload:** 
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "newpassword123",
  "new_password_again": "newpassword123"
}
```

---

## 11. Update User Profile
Updates the currently authenticated user's profile across the 4 frontend interfaces. Supports both JSON and Multipart (for image uploads).

**Endpoint:** `/api/users/me/update/`  
**Method:** `PATCH` / `PUT`  
**Authentication & Permissions:** Required (Authenticated user)

### Request Payload (Multipart/Form-Data or JSON)

#### Interface 1: Alumni Details
| Field | Type | Description |
|---|---|---|
| `profile_photo` | File | Image file (max 2MB). |
| `first_name` | String | User's first name. |
| `last_name` | String | User's last name. |
| `phone_number` | String | User's primary contact number. |
| `gender` | String | 'M' for Male, 'F' for Female. |
| `nationality` | String | User's country of citizenship. |
| `bio` | String | Short professional or personal biography. |
| `marital_status` | String | 'Single' or 'Married'. |
| `spouse_full_name` | String | (Visible if Married) Full name of spouse. |
| `spouse_phone` | String | (Visible if Married) Contact number of spouse. |
| `spouse_email` | Email | (Visible if Married) Email address of spouse. |
| `spouse_occupation`| String | (Visible if Married) Occupation of spouse. |

#### Interface 2: Qualifications
| Field | Type | Description |
|---|---|---|
| `cla_campus` | String | 'CLA Boys' or 'CLA Girls'. |
| `high_school_graduation_year` | Integer | Year of graduation from CLA. |
| `academic_status` | String | 'University Graduate', 'Still at University', or 'Not Enrolled'. |
| `university_institution` | String | Name of the University/Institution. |
| `university_course` | String | Course or Programme of study. |
| `university_graduation_year` | Integer | (For Graduates) Year of graduation. |
| `expected_graduation_year` | Integer | (For Students) Expected graduation year. |

#### Interface 3: Address Details
| Field | Type | Description |
|---|---|---|
| `address_country` | String | Country of residence. |
| `address_district_region` | String | District, Region or Province. |
| `address_city_town` | String | City or Town. |
| `address_po_box` | String | (Optional) P.O. Box address. |
| `address_physical_street` | String | Physical/Street address. |

#### Interface 4: Work & Employment
| Field | Type | Description |
|---|---|---|
| `employment_status` | String | 'Employed', 'Self-Employed', 'Unemployed', or 'Still a Student'. |
| `employer_company_name` | String | Name of Employer or Business. |
| `job_title_role` | String | Job Title or Role. |
| `industry_sector` | String | Sector (e.g., Technology, Finance, Education, etc.). |
| `work_location` | String | Physical location of work. |
| `work_year_started` | Integer | Year started in this role/business. |
| `work_email` | Email | (Optional) Work email address. |
| `work_phone` | String | (Optional) Work phone number. |
| `linkedin_profile` | URL | (Optional) Full LinkedIn profile URL. |

### Responses
**Success (200 OK):**
Returns the full updated user object.

---

## 11. Events API

### Admin: Create Event
**Endpoint:** `/api/events/admin/events/`  
**Method:** `POST`  
**Auth:** Admin Only  
**Payload:**
```json
{
  "title": "Annual Alumni Reunion",
  "event_type": "Reunion",
  "start_date": "2026-12-20T10:00:00Z",
  "end_date": "2026-12-20T18:00:00Z",
  "capacity": 200,
  "location": "Main Hall, Campus",
  "description": "Celebrating 20 years of excellence."
}
```

### Admin: Update/Delete Event
**Endpoint:** `/api/events/admin/events/{id}/`  
**Method:** `PUT` / `PATCH` / `DELETE`  
**Auth:** Admin Only  

### User: List Events
**Endpoint:** `/api/events/user/events/`  
**Method:** `GET`  
**Auth:** Public/Authenticated  
Returns list of events with `rsvp_count` and `is_rsvped` (if authenticated).

### User: RSVP to Event
**Endpoint:** `/api/events/user/events/{id}/rsvp/`  
**Method:** `POST`  
**Auth:** Authenticated Users Only  
Toggles RSVP. If already RSVPed, it removes the user from the event.

---

## 12. Alumni Management (Admin Only)

### Add Alumni Record
Adds a new alumni record to the database.

**Endpoint:** `/api/alumni/add/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.  
**Payload:** Full `Person` object fields.

### Edit Alumni Record
Updates an existing alumni record.

**Endpoint:** `/api/alumni/{id}/edit/`  
**Method:** `PUT` / `PATCH`  
**Authentication & Permissions:** Admin/Staff only.  
**Payload:** Fields to update.

### Archive Alumni Record
Changes an alumni's status to archived. Archived records are hidden from the main alumni list.

**Endpoint:** `/api/alumni/{id}/archive/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

### Unarchive Alumni Record
Restores an archived alumni record to active status.

**Endpoint:** `/api/alumni/{id}/unarchive/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

### List Archived Alumni
Returns a list of all archived alumni records.

**Endpoint:** `/api/alumni/archived/`  
**Method:** `GET`  
**Authentication & Permissions:** Admin/Staff only.

---

## 13. Dashboard Statistics (Admin Only)
Returns high-level overview statistics for the admin dashboard.

**Endpoint:** `/api/users/dashboard-stats/`  
**Method:** `GET`  
**Authentication & Permissions:** Admin/Staff only.

### Response Payload (JSON)
```json
{
  "total_alumni": 1250,
  "total_users_signed_up": 450,
  "total_male_users": 210,
  "total_female_users": 240,
  "total_at_university": 150,
  "total_who_have_graduated": 300,
  "total_employed": 280,
  "total_pending_approvals": 15
}
```

---

## Rate Limiting
- **Registration**: Limited to 10 requests per minute per IP.
- **Login**: Limited to 10 requests per minute per IP.
