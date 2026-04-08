# Cornerstone System Backend Documentation

This document provides complete instructions for setting up, running, and testing the backend of the Cornerstone System.

## 1. Project Setup

These steps will guide you through the initial setup of the project and its dependencies.

### 1.1. Create a Virtual Environment

From the `backend` directory, create a virtual environment to isolate the project's dependencies:

```bash
py -m venv venv
```

### 1.2. Activate the Virtual Environment

Activate the virtual environment in your terminal. This will ensure that you are using the correct Python interpreter and packages.

```bash
source venv/Scripts/activate
```

Your terminal prompt should now be prefixed with `(venv)`.

### 1.3. Install Dependencies

Install all the required Python packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## 2. Running the Application

To run the application, you'll need to have both a Redis server and the Django development server running.

### 2.1. Start the Redis Server

The application uses Redis for caching. You'll need to have a Redis server running on your machine. If you're using Docker Desktop, you can start a Redis server with the following commands:

```bash
# Update the package index
apk update

# Install Redis
apk add redis

# Start the Redis server
redis-server
```

Keep the terminal window with the Redis server running.

### 2.2. Start the Django Development Server

From the `backend` directory, run the Django development server:

```bash
python manage.py runserver
```

The backend will now be running and accessible at `http://127.0.0.1:8000/`.

## 3. Database Setup

These steps will prepare your database with the necessary tables and data.

### 3.1. Run Migrations

Apply the database migrations to create the necessary tables:

```bash
python manage.py migrate
```

### 3.2. Import Alumni Data

Run the `import_alumni` script to populate the database with alumni records from the Excel file:

```bash
python manage.py shell -c "from scripts.import_alumni import run; run()"
```

## 4. Admin Access

To access the Django admin panel, you'll need a superuser account.

### 4.1. Create a Superuser

Create a superuser account by running the following command and following the prompts:

```bash
python manage.py createsuperuser
```

Once created, you can log in to the admin panel at `http://127.0.0.1:8000/admin/`.

## 5. API Documentation & Testing

### 5.1. Interactive Swagger Docs
Once the server is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### 5.2. Testing with Postman

1. **Download Postman**: If you haven't already, download and install [Postman](https://www.postman.com/downloads/).
2. **Create a New Collection**: Create a collection named "Cornerstone System" to group your requests.
3. **Set Up Base URL Variable**:
   - Go to your collection settings -> **Variables**.
   - Add a variable named `base_url` with the value `http://127.0.0.1:8000`.
4. **Testing Endpoints**:

#### A. Register Alumni (POST)
- **URL**: `{{base_url}}/api/onboarding/register/`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body (raw JSON)**:
  ```json
  {
      "full_name": "John Doe",
      "graduation_year": 2020,
      "email": "john@example.com",
      "password": "yourpassword123"
  }
  ```

#### B. Login (POST)
- **URL**: `{{base_url}}/api/onboarding/login/`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body (raw JSON)**:
  ```json
  {
      "email": "john@example.com",
      "password": "yourpassword123"
  }
  ```

#### C. List Alumni (GET)
- **URL**: `{{base_url}}/api/alumni/`
- **Method**: `GET`
- **Description**: Returns a list of all alumni records imported from the Excel database.

#### D. Password Reset (POST)
- **URL**: `{{base_url}}/api/onboarding/password-reset/`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body (raw JSON)**:
  ```json
  {
      "email": "john@example.com"
  }
  ```

### 5.3. Testing with curl

#### Register Alumni
```bash
curl -X POST http://localhost:8000/api/onboarding/register/ \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","graduation_year":2020,"email":"john@example.com","password":"yourpassword123"}'
```

#### List Alumni
```bash
curl -X GET http://localhost:8000/api/alumni/
```

