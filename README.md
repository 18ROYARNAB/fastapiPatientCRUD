# Patient Management API

A comprehensive FastAPI-based REST API for managing patient health records with features for creating, viewing, sorting, and analyzing patient data.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Installation](#installation)
5. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
7. [Data Model](#data-model)
8. [Database Structure](#database-structure)
9. [Error Handling](#error-handling)
10. [Project Structure](#project-structure)

---

## Overview

The Patient Management API is a RESTful web service built with FastAPI that manages patient health data. It provides endpoints to:
- Register new patients
- Retrieve patient information
- Sort patients by health metrics
- Calculate BMI and health status automatically

The application uses JSON file-based storage (`db.json`) for data persistence.

---

## Features

### ✅ Core Functionality
- **Patient Registration**: Create new patient records with validation
- **Patient Lookup**: Retrieve individual patient details by ID
- **Data Viewing**: View all patient records
- **Sorting**: Sort patients by height, weight, or BMI
- **Health Metrics**: Automatically compute BMI and health verdict
- **Data Validation**: Pydantic-based input validation with detailed error messages
- **RESTful API**: Follows REST conventions with proper HTTP status codes

### ✅ Data Validation
- Age validation (must be between 0 and 120)
- Gender restriction (male, female, others)
- Height and Weight must be positive values
- Unique patient IDs
- Automatic BMI calculation
- Health status classification (underweight, normal, obese)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Validation | Pydantic |
| Type Hints | Python Typing & Annotated |
| Database | JSON file (`db.json`) |
| Server | Uvicorn (for development) |
| Language | Python 3.8+ |

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Steps

1. **Clone or download the project**
   ```bash
   cd /Users/roy/fastapitutorial
   ```

2. **Create a virtual environment** (if not already created)
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pydantic
   ```

---

## Running the Application

### Development Server

Start the API with Uvicorn:

```bash
uvicorn main:app --reload
```

This will:
- Start the server on `http://localhost:8000`
- Enable auto-reload on file changes (development mode)

### Access Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## API Endpoints

### 1. Home/Welcome Endpoint
**GET** `/`

Returns a welcome message.

**Response (200 OK):**
```json
{
  "message": "Patient management api"
}
```

---

### 2. About Endpoint
**GET** `/about`

Returns information about the API.

**Response (200 OK):**
```json
{
  "message": "A fully functional api"
}
```

---

### 3. View All Patients
**GET** `/view`

Returns all patient records from the database.

**Response (200 OK):**
```json
{
  "P001": {
    "name": "Ananya",
    "city": "Kolkata",
    "age": 28,
    "Gender": "Female",
    "Height": 1.65,
    "weight": 70.5,
    "bmi": 25.9,
    "verdict": "normal"
  },
  ...
}
```

---

### 4. View Single Patient
**GET** `/patient/{patient_id}`

Retrieve a specific patient by their ID.

**Parameters:**
- `patient_id` (path, required): The unique identifier of the patient (e.g., "P001")

**Response (200 OK):**
```json
{
  "name": "Ananya",
  "city": "Kolkata",
  "age": 28,
  "Gender": "Female",
  "Height": 1.65,
  "weight": 70.5,
  "bmi": 25.9,
  "verdict": "normal"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Patient not found"
}
```

---

### 5. Sort Patients
**GET** `/sort`

Sort all patients by a specified metric (height, weight, or BMI).

**Query Parameters:**
- `sort_by` (required): Field to sort by. Must be one of: `height`, `weight`, `bmi`
- `order` (optional, default: `asc`): Sort order. Must be one of: `asc`, `desc`

**Example Requests:**
```
GET /sort?sort_by=bmi&order=desc
GET /sort?sort_by=height&order=asc
GET /sort?sort_by=weight
```

**Response (200 OK):**
```json
[
  {
    "name": "Vikram",
    "city": "Bangalore",
    "age": 42,
    "Gender": "Male",
    "Height": 1.75,
    "weight": 92.0,
    "bmi": 30.0,
    "verdict": "Obese"
  },
  ...
]
```

**Error (400 Bad Request - Invalid sort field):**
```json
{
  "detail": "Invalid fields from ['height', 'weight', 'bmi']"
}
```

**Error (400 Bad Request - Invalid order):**
```json
{
  "detail": "Not in order select asc or desc"
}
```

---

### 6. Create Patient
**POST** `/create`

Register a new patient in the database.

**Request Body (JSON):**
```json
{
  "id": "P013",
  "name": "John Doe",
  "city": "New York",
  "age": 35,
  "Gender": "male",
  "Height": 1.80,
  "Weight": 80.0
}
```

**Response (201 Created):**
```json
{
  "message": "patient registered succefully"
}
```

**Error (400 Bad Request - Patient exists):**
```json
{
  "detail": "patient P013 already exist"
}
```

**Error (422 Unprocessable Entity - Validation error):**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is less than 120",
      "type": "value_error.number.not_less_than"
    }
  ]
}
```

---

## Data Model

### Patient Model

The `Patient` class defines the structure and validation rules for patient data.

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string | Required, unique | Patient identifier (e.g., "P001") |
| `name` | string | Required | Full name of the patient |
| `city` | string | Required | City of residence |
| `age` | integer | Required, 0 < age < 120 | Patient age in years |
| `Gender` | string (Literal) | Required, one of: male, female, others | Patient gender |
| `Height` | float | Required, > 0 | Height in meters |
| `weight` | float | Required, > 0 | Weight in kilograms |
| `bmi` | float | Computed | Body Mass Index (read-only) |
| `verdict` | string | Computed | Health status classification (read-only) |

#### Computed Fields

##### BMI Calculation
- **Formula**: `BMI = weight / (height²)`
- **Precision**: Rounded to 2 decimal places
- **Automatic**: Calculated on every request

##### Health Verdict Classification
- **Underweight**: BMI < 18.5 → `"underweigth"`
- **Normal**: 18.5 ≤ BMI < 30 → `"normal"`
- **Obese**: BMI ≥ 30 → `"Obese"`

---

## Database Structure

### db.json Format

The database is stored as a JSON file with the following structure:

```json
{
  "P001": {
    "name": "Ananya",
    "city": "Kolkata",
    "age": 28,
    "Gender": "Female",
    "Height": 1.65,
    "weight": 70.5,
    "bmi": 25.9,
    "verdict": "normal"
  },
  "P002": {
    "name": "Rajesh",
    "city": "Mumbai",
    "age": 35,
    "Gender": "Male",
    "Height": 1.78,
    "weight": 85.0,
    "bmi": 26.8,
    "verdict": "normal"
  }
}
```

**Key Points:**
- Each patient record is keyed by their unique `id`
- The patient `id` is NOT duplicated in the record itself (only the key)
- Patient data is stored as flat JSON objects
- Supports 12+ patient records currently

---

## Error Handling

The API implements comprehensive error handling with appropriate HTTP status codes:

### Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 OK | Successful GET request | Retrieve patient data |
| 201 Created | Successful resource creation | Patient registered |
| 400 Bad Request | Invalid input or business logic violation | Invalid sort field, duplicate patient ID |
| 404 Not Found | Resource does not exist | Patient ID not in database |
| 422 Unprocessable Entity | Validation error (Pydantic) | Age out of range, invalid gender |

### Example Error Response

```json
{
  "detail": "Patient not found"
}
```

---

## Project Structure

```
fastapitutorial/
├── main.py                 # Main FastAPI application
├── db.json                 # JSON database with patient records
├── README.md              # This file
├── pyproject.toml         # Project configuration
├── .venv/                 # Virtual environment
└── model/                 # Optional: Additional models (if needed)
```

### File Descriptions

- **main.py**: Contains all FastAPI route definitions, Pydantic models, and database helper functions
- **db.json**: Persistent data storage for all patient records
- **README.md**: Documentation (this file)
- **pyproject.toml**: Project metadata and dependencies

---

## Usage Examples

### Example 1: Create a New Patient

```bash
curl -X POST "http://localhost:8000/create" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "P013",
    "name": "Alice Johnson",
    "city": "San Francisco",
    "age": 28,
    "Gender": "female",
    "Height": 1.70,
    "Weight": 65.0
  }'
```

### Example 2: Sort Patients by BMI (Descending)

```bash
curl "http://localhost:8000/sort?sort_by=bmi&order=desc"
```

### Example 3: Retrieve Specific Patient

```bash
curl "http://localhost:8000/patient/P001"
```

### Example 4: Get All Patients

```bash
curl "http://localhost:8000/view"
```

---

## Development Notes

### Type Annotations
The code uses Python's `Annotated` type hints from the `typing` module to provide:
- Enhanced IDE autocomplete support
- Better type checking
- Detailed validation via Pydantic `Field`
- Automatic OpenAPI documentation

### Field Aliases
Some fields use `# type: ignore` comments to suppress type checking warnings where intentional behavior differs from strict type checking.

### File I/O
- Database file `db.json` is read/written synchronously
- Consider implementing async I/O for production use
- No database migrations or schema versioning

---

## Future Enhancements

- [ ] Implement database migration system
- [ ] Add async/await support for file operations
- [ ] Implement user authentication and authorization
- [ ] Add data export (CSV, Excel)
- [ ] Implement database search/filtering
- [ ] Add patient history tracking
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Create test suite
- [ ] Deploy to production (Heroku, AWS, etc.)

---

## Troubleshooting

### Issue: `db.json` not found
**Solution**: Ensure the `db.json` file exists in the same directory as `main.py`. Create an empty JSON file with sample data if missing.

### Issue: Port 8000 already in use
**Solution**: Specify a different port:
```bash
uvicorn main:app --reload --port 8001
```

### Issue: Module not found errors
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

---

## License

This project is provided as-is for educational and tutorial purposes.

---

## Contact & Support

For questions or issues, please refer to the FastAPI documentation at [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Last Updated**: December 2024
