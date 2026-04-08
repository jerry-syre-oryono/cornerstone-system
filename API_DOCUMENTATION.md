# API Documentation: Onboarding & Authentication

This document details the API endpoints for user authentication within the Cornerstone system.

---

## 1. Register Alumni
Creates a new `User` account linked to an existing `Person` record.

**Endpoint:** `/api/onboarding/register/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

### Request Payload (JSON)
| Field | Type | Description |
|---|---|---|
| `full_name` | String | Exactly matches the existing alumni person name (using fuzzy matching, 80% similarity threshold). |
| `graduation_year` | Integer | The year the alumni graduated or completed their program. |
| `email` | String | Valid email address. This will be assigned as their system login in the backend. |
| `password` | String | A secure password. |
| `password_again` | String | A confirmation of the `password`. Must match. |

### Responses
**Success (200 OK):**  
```json
{
  "status": "account_created",
  "user_id": 12
}
```

**Errors (400 / 404):**
- `400 Bad Request`: "All fields are required." (Missing parameters)
- `400 Bad Request`: "Passwords do not match."
- `400 Bad Request`: "Account already exists for this alumni." (They have already signed up)
- `400 Bad Request`: "A user with this email already exists."
- `404 Not Found`: "Alumni record not found. Please verify your name and graduation year." (No matching Name+Year in the `Person` model)

---

## 2. Login User
Authenticates a user via their email and password and creates an active server session.

**Endpoint:** `/api/onboarding/login/`  
**Method:** `POST`  
**Authentication & Permissions:** None required

### Request Payload (JSON)
| Field | Type | Description |
|---|---|---|
| `email` | String | The email address they registered with. |
| `password` | String | Their chosen password. |

### Responses
**Success (200 OK):**  
```json
{
  "status": "logged_in",
  "user_id": 12,
  "person_id": 45,
  "is_alumni": true
}
```

**Errors (400 / 401):**
- `400 Bad Request`: "Email and password are required."
- `401 Unauthorized`: "Invalid email or password."

---

## 3. List Alumni by Gender
Returns a list of all alumni filtered by gender.

**Endpoints:** 
- `/api/alumni/male/` (All Male Alumni)
- `/api/alumni/female/` (All Female Alumni)

**Method:** `GET`  
**Authentication & Permissions:** Authenticated user required.

### Responses
**Success (200 OK):**  
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "graduation_year": 2020,
    "email": "john@example.com",
    "phone_primary": "123456789",
    "status": "Signed Up"
  }
]
```

---

## 4. List Registered Users by Gender
Returns a list of all registered system users filtered by gender.

**Endpoints:** 
- `/api/users/male/` (All Male Users)
- `/api/users/female/` (All Female Users)

**Method:** `GET`  
**Authentication & Permissions:** Authenticated user required.

### Responses
**Success (200 OK):**  
```json
[
  {
    "id": 1,
    "username": "jdoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_alumni": true,
    "gender": "M"
  }
]
```

---

## Rate Limiting
- **Registration**: Limited to 10 requests per minute per IP.
- **Login**: Limited to 10 requests per minute per IP.
