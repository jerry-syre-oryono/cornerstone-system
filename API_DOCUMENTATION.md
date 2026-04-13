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

**Errors (400):**
- `400 Bad Request`: "Passwords do not match."
- `400 Bad Request`: "A user with this email already exists."
- `400 Bad Request`: "A signup request with this email already exists and is pending review."

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

### Responses
**Success (200 OK):**  
```json
{
  "status": "approved",
  "user_id": 13,
  "person_id": 46,
  "temporary_password": "random_password"
}
```

---

## 5. Reject Signup Request
Marks a signup request as `REJECTED`. The details remain in the `SignupRequest` table.

**Endpoint:** `/api/onboarding/signup-requests/{id}/reject/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

---

## 6. Total Signed Up Users
Returns counts of total users and total alumni users in the system.

**Endpoint:** `/api/users/total/`  
**Method:** `GET`  
**Authentication & Permissions:** Admin/Staff only.

---

## 7. Admin Add New User
Directly creates a new user in the system.

**Endpoint:** `/api/users/create/`  
**Method:** `POST`  
**Authentication & Permissions:** Admin/Staff only.

---

## 8. Login User
Authenticates a user via their email and password.

**Endpoint:** `/api/onboarding/login/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

---

## Rate Limiting
- **Registration**: Limited to 10 requests per minute per IP.
- **Login**: Limited to 10 requests per minute per IP.
