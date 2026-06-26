# ==========================================
# Patient Management API - Main Application
# ==========================================
# This module implements a RESTful API for managing patient health records
# Built with FastAPI for high performance and automatic OpenAPI documentation
# Features: Create, Read, Update, Delete (CRUD) operations on patient data
#
# Run this application with:
#   uvicorn main:app --reload
#
# Access documentation at:
#   - Swagger UI: http://localhost:8000/docs
#   - ReDoc: http://localhost:8000/redoc

# ==========================================
# IMPORTS
# ==========================================

# FastAPI and request handling
from fastapi import FastAPI, Path, HTTPException, Query
# - FastAPI: Main web framework for building APIs
# - Path: For defining path parameters with validation
# - HTTPException: For raising HTTP errors with status codes
# - Query: For defining query string parameters with validation

from fastapi.responses import JSONResponse
# JSONResponse: For returning custom JSON responses with specific status codes

# Pydantic for data validation
from pydantic import BaseModel, Field, computed_field
# - BaseModel: Base class for data validation models
# - Field: For defining field properties, constraints, and documentation
# - computed_field: Decorator for fields calculated from other fields

# Python type hints and utilities
from typing import Annotated, Literal, Optional
# - Annotated: For attaching metadata to type hints (used with Field for validation)
# - Literal: For restricting values to a fixed set of specific options
# - Optional: For fields that may be None (not required)

# Standard library
import json
# JSON: For reading and writing patient data to the JSON file database

# ==========================================
# APPLICATION INITIALIZATION
# ==========================================

# Create the main FastAPI application instance
# This object:
#   - Handles all HTTP routing
#   - Processes incoming requests
#   - Generates automatic API documentation (Swagger UI, ReDoc)
#   - Manages application lifecycle
app = FastAPI(
    title="Patient Management API",
    description="A RESTful API for managing patient health records with CRUD operations",
    version="1.0.0"
)


# ==========================================
# DATA MODELS - Pydantic Models
# ==========================================

class Patient(BaseModel):
    """
    Complete Patient data model with comprehensive validation.
    
    This Pydantic model defines the structure for a full patient record.
    Pydantic automatically validates all input data and provides detailed error
    messages if validation fails. When data is invalid, FastAPI returns a 422
    Unprocessable Entity response with specific validation errors.
    
    Attributes:
        id: Unique patient identifier (e.g., "P001", "P013")
        name: Full name of the patient
        city: City of residence
        age: Age in years - validated to be between 1 and 119
        Gender: Patient gender - restricted to 'male', 'female', or 'others'
        Height: Height in meters - must be positive
        weight: Weight in kilograms - must be positive
        bmi: Computed field - Body Mass Index calculated automatically (read-only)
        verdict: Computed field - Health verdict based on BMI (read-only)
    """
    
    # Unique identifier for each patient
    # ... means this field is required (no default value)
    # examples parameter provides sample data for API documentation
    id: Annotated[str, Field(
        ...,
        description="Unique identifier of the patient (e.g., P001, P013)",
        examples=["P001", "P002", "P013"]
    )]
    
    # Patient's full name - required string field
    name: Annotated[str, Field(
        ...,
        description="Full name of the patient",
        examples=["Arnab", "John Doe", "Alice Johnson"]
    )]
    
    # City where patient lives - required string field
    city: Annotated[str, Field(
        ...,
        description="City where patient resides",
        examples=["Gurgaon", "Mumbai", "New York"]
    )]
    
    # Patient's age with validation constraints
    # gt=0: Age must be GREATER THAN 0
    # lt=120: Age must be LESS THAN 120
    # This ensures age is between 1 and 119 years old
    age: Annotated[int, Field(
        ...,
        gt=0,  # Greater than 0
        lt=120,  # Less than 120
        description="Age of patient in years (must be between 1 and 119)",
        examples=[25, 35, 42]
    )]
    
    # Patient's gender - restricted to specific values
    # Literal['male', 'female', 'others'] ensures only these exact values are accepted
    # If any other value is provided, Pydantic will raise a validation error
    Gender: Annotated[Literal['male', 'female', 'others'], Field(
        ...,
        description="Gender of patient (must be male, female, or others)",
        examples=["male", "female", "others"]
    )]
    
    # Patient's height in meters
    # gt=0: Height must be greater than 0 (positive value)
    # Float type allows decimal values like 1.65, 1.78, 1.80
    Height: Annotated[float, Field(
        ...,
        gt=0,  # Greater than 0
        description="Height of patient in meters",
        examples=[1.65, 1.78, 1.80]
    )]
    
    # Patient's weight in kilograms
    # gt=0: Weight must be greater than 0 (positive value)
    # Float type allows decimal values like 70.5, 85.0, 80.0
    weight: Annotated[float, Field(
        ...,
        gt=0,  # Greater than 0
        description="Weight of patient in kilograms",
        examples=[70.5, 85.0, 80.0]
    )]
    
    # ==========================================
    # COMPUTED FIELDS (READ-ONLY)
    # ==========================================
    # These fields are automatically calculated from other fields
    # They are included in responses but cannot be set by users
    
    @computed_field
    @property
    def bmi(self) -> float:
        """
        Calculate Body Mass Index (BMI).
        
        BMI is a measure of body fat based on height and weight.
        Formula: BMI = weight (kg) / (height (m)²)
        
        Interpretation:
            - < 18.5: Underweight
            - 18.5 - 24.9: Normal weight
            - 25.0 - 29.9: Overweight
            - ≥ 30.0: Obese
        
        Example calculation:
            height = 1.80 m
            weight = 80 kg
            BMI = 80 / (1.80 × 1.80) = 80 / 3.24 = 24.69
        
        Returns:
            float: BMI value rounded to 2 decimal places
        """
        # Calculate BMI using the formula and round to 2 decimal places
        bmi: float = round(self.weight / (self.Height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        """
        Classify patient health status based on BMI.
        
        This property provides a health verdict by categorizing the patient
        based on their Body Mass Index value. The verdict helps determine
        if the patient is underweight, at normal weight, or obese.
        
        Categories used:
            - Underweight: BMI < 18.5 → returns "underweigth"
            - Normal/Overweight: 18.5 ≤ BMI < 30 → returns "normal"
            - Obese: BMI ≥ 30 → returns "Obese"
        
        Note: The verdict groups normal weight and overweight into "normal"
        for simplified categorization.
        
        Returns:
            str: One of ["underweigth", "normal", "Obese"]
        """
        # Check if patient is underweight
        if self.bmi < 18.5:
            return "underweigth"
        # Check if patient is normal/overweight
        elif self.bmi < 30:
            return 'normal'
        # Otherwise patient is obese
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    """
    Partial Patient model for UPDATE operations.
    
    This model is used for PUT requests to update existing patients.
    Unlike the Patient model, all fields are optional (default=None).
    This allows clients to update only specific fields without providing
    all required fields.
    
    Example: Update only the patient's weight
        {"weight": 75.5}
    
    When model_dump(exclude_unset=True) is called, only the fields that
    were explicitly provided are included in the result.
    
    Attributes:
        All attributes are identical to Patient model but optional
    """
    
    # All fields are optional with default=None
    # This allows partial updates where only some fields need to be changed
    
    name: Annotated[Optional[str], Field(
        default=None,
        description="Updated patient name (optional)"
    )]
    
    city: Annotated[Optional[str], Field(
        default=None,
        description="Updated city (optional)"
    )]
    
    # Age validation still applies if provided (must be 0 < age < 120)
    age: Annotated[Optional[int], Field(
        default=None,
        gt=0,
        lt=120,
        description="Updated age (optional, must be between 1 and 119)"
    )]
    
    # Gender validation still applies if provided (must be male/female/others)
    Gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(
        default=None,
        description="Updated gender (optional)"
    )]
    
    # Height validation still applies if provided (must be > 0)
    Height: Annotated[Optional[float], Field(
        default=None,
        gt=0,
        description="Updated height in meters (optional)"
    )]
    
    # Weight validation still applies if provided (must be > 0)
    weight: Annotated[Optional[float], Field(
        default=None,
        gt=0,
        description="Updated weight in kilograms (optional)"
    )] 

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================
# These functions handle reading and writing patient data to the JSON file

def load_data() -> dict:
    """
    Load all patient data from the JSON database file.
    
    This function reads the db.json file and returns it as a Python dictionary.
    
    Database structure:
        {
            "P001": {"name": "Ananya", "city": "Kolkata", ...},
            "P002": {"name": "Rajesh", "city": "Mumbai", ...},
            ...
        }
    
    Returns:
        dict: Dictionary with patient_id as keys and patient records as values.
              Each patient record includes: name, city, age, Gender, Height, 
              weight, bmi, and verdict.
    
    Raises:
        FileNotFoundError: If db.json file doesn't exist in the current directory
        json.JSONDecodeError: If db.json contains invalid JSON syntax
    """
    # Open the JSON file in read mode
    with open('db.json', 'r') as f:
        # Parse JSON content and return as Python dictionary
        data = json.load(f)
    return data


def save_data(data: dict) -> None:
    """
    Save patient data to the JSON database file.
    
    This function overwrites the entire db.json file with the provided data.
    Used after creating, updating, or deleting patients.
    
    Parameters:
        data (dict): Complete patient data dictionary to save
                     Format: {"patient_id": {patient_record}, ...}
    
    Returns:
        None
    """
    # Open the JSON file in write mode (overwrites if exists)
    with open('db.json', 'w') as f:
        # Write the Python dictionary as JSON formatted text
        json.dump(data, f)  # type: ignore


# ==========================================
# API ENDPOINTS - GET ROUTES
# ==========================================
# These endpoints handle data retrieval without modifying the database

@app.get("/", tags=["Info"])
def hello() -> dict:
    """
    Welcome/Home endpoint - Returns a welcome message.
    
    GET /
    
    This is a simple endpoint that confirms the API is running and accessible.
    It returns a basic welcome message.
    
    Returns:
        dict: A dictionary with a welcome message
    
    Response (200 OK):
        {"message": "Patient management api"}
    
    Example:
        curl http://localhost:8000/
    """
    # Return a simple welcome message
    return {'message': 'Patient management api'}


@app.get('/about', tags=["Info"])
def about() -> dict:
    """
    About endpoint - Returns API description.
    
    GET /about
    
    This endpoint provides information about the API's capabilities.
    
    Returns:
        dict: A dictionary with API description
    
    Response (200 OK):
        {"message": "A fully functional api"}
    
    Example:
        curl http://localhost:8000/about
    """
    # Return API description
    return {'message': "A fully functional api"}


@app.get('/view', tags=["Patients"])
def view() -> dict:
    """
    View all patients - Returns all patient records from the database.
    
    GET /view
    
    This endpoint retrieves the complete database of all registered patients.
    Returns all patient records with their complete information including
    computed fields (BMI and health verdict).
    
    Returns:
        dict: Dictionary with all patients
              Format: {"patient_id": {patient_data}, ...}
    
    Response (200 OK):
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
    
    Example:
        curl http://localhost:8000/view
    """
    # Load and return all patient data
    data = load_data()
    return data


@app.get('/patient/{patient_id}', tags=["Patients"])
def view_patient(
    patient_id: str = Path(
        ...,
        description="Unique identifier of the patient to retrieve",
        examples=['P001', 'P002', 'P013']
    )
) -> dict:
    """
    View single patient by ID - Retrieve a specific patient's data.
    
    GET /patient/{patient_id}
    
    This endpoint retrieves a single patient's complete record using their ID.
    If the patient doesn't exist in the database, a 404 error is returned.
    
    Parameters:
        patient_id (str, path): Unique patient identifier (e.g., "P001")
    
    Returns:
        dict: Patient record containing all fields
    
    Response (200 OK):
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
    
    Response (404 Not Found):
        {"detail": "Patient not found"}
    
    Examples:
        curl http://localhost:8000/patient/P001
        curl http://localhost:8000/patient/P005
    """
    # Load all patient data
    data = load_data()
    
    # Check if the requested patient_id exists in the database
    if patient_id in data:
        # Return the patient's data
        return data[patient_id]
    
    # If patient not found, raise a 404 HTTP exception
    # This automatically sends a 404 response to the client
    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )


@app.get('/sort', tags=["Patients"])
def sort_patients(
    sort_by: str = Query(
        ...,
        description="Field to sort by: height, weight, or bmi",
        examples=["bmi", "height", "weight"]
    ),
    order: str = Query(
        'asc',
        description="Sort order: asc (ascending) or desc (descending)",
        examples=["asc", "desc"]
    )
) -> list:
    """
    Sort patients by metric - Returns sorted list of all patients.
    
    GET /sort?sort_by={field}&order={order}
    
    This endpoint returns all patients sorted by a specified field and order.
    The sorted list can be useful for finding patients with extreme values
    (tallest, heaviest, highest BMI, etc.).
    
    Parameters:
        sort_by (str, query, required): Field to sort by
                                        Valid options: 'height', 'weight', 'bmi'
        order (str, query, optional):   Sort order
                                        Valid options: 'asc', 'desc'
                                        Default: 'asc' (ascending)
    
    Returns:
        list: List of patient records sorted by specified field and order
    
    Response (200 OK):
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
        ]
    
    Response (400 Bad Request - Invalid sort field):
        {"detail": "Invalid fields from ['height', 'weight', 'bmi']"}
    
    Response (400 Bad Request - Invalid order):
        {"detail": "Not in order select asc or desc"}
    
    Examples:
        curl "http://localhost:8000/sort?sort_by=bmi&order=desc"        # Highest BMI first
        curl "http://localhost:8000/sort?sort_by=height&order=asc"      # Shortest first
        curl "http://localhost:8000/sort?sort_by=weight"                # Lightest first (default asc)
        curl "http://localhost:8000/sort?sort_by=weight&order=desc"     # Heaviest first
    """
    
    # Define the list of valid fields that can be sorted by
    valid_fields = ['height', 'weight', 'bmi']
    
    # Validate that sort_by parameter is one of the valid fields
    if sort_by not in valid_fields:
        # If invalid, raise a 400 Bad Request error
        raise HTTPException(
            status_code=400,
            detail=f'Invalid fields from {valid_fields}'
        )
    
    # Validate that order parameter is either 'asc' or 'desc'
    if order not in ['asc', 'desc']:
        # If invalid, raise a 400 Bad Request error
        raise HTTPException(
            status_code=400,
            detail='Not in order select asc or desc'
        )
    
    # Load all patient data from database
    data = load_data()
    
    # Determine reverse sorting: True for descending, False for ascending
    # If order is 'desc', reverse=True means highest values first
    # If order is 'asc', reverse=False means lowest values first
    sort_order = True if order == 'desc' else False
    
    # Sort patients by the specified field
    # data.values() gets just the patient records (not the IDs)
    # key=lambda x: x.get(sort_by, 0) extracts the value to sort by
    #   - For BMI, height, weight - gets the numeric value
    #   - If field doesn't exist, uses 0 as default
    # reverse=sort_order determines sort direction
    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by, 0),
        reverse=sort_order
    )
    
    # Return the sorted list of patients
    return sorted_data



# ==========================================
# API ENDPOINTS - POST ROUTE (CREATE)
# ==========================================

@app.post('/create', tags=["Patients"], status_code=201)
def create_patient(patient: Patient) -> JSONResponse:
    """
    Create patient - Register a new patient in the database.
    
    POST /create
    Content-Type: application/json
    
    This endpoint creates a new patient record and stores it in the database.
    The request body must contain all required Patient fields.
    Pydantic automatically validates the input data.
    
    Request Body (JSON):
        {
            "id": "P013",
            "name": "John Doe",
            "city": "New York",
            "age": 35,
            "Gender": "male",
            "Height": 1.80,
            "weight": 80.0
        }
    
    Returns:
        JSONResponse: Success message with 201 Created status code
    
    Response (201 Created):
        {"message": "patient registered succefully"}
    
    Response (400 Bad Request - Patient already exists):
        {"detail": "patient P013 already exist"}
    
    Response (422 Unprocessable Entity - Validation error):
        This occurs when input doesn't meet validation rules (e.g., age > 120)
        {
            "detail": [
                {
                    "loc": ["body", "age"],
                    "msg": "ensure this value is less than 120",
                    "type": "value_error.number.not_less_than"
                }
            ]
        }
    
    Example:
        curl -X POST "http://localhost:8000/create" \\
             -H "Content-Type: application/json" \\
             -d '{
                   "id": "P013",
                   "name": "Jane Smith",
                   "city": "Boston",
                   "age": 29,
                   "Gender": "female",
                   "Height": 1.70,
                   "weight": 65.0
                 }'
    """
    
    # Load existing patient data from the JSON database
    data = load_data()
    
    # Check if a patient with this ID already exists
    # This prevents duplicate patient IDs in the database
    if patient.id in data:
        # If patient already exists, raise a 400 Bad Request error
        raise HTTPException(
            status_code=400,
            detail=f'patient {patient.id} already exist'
        )
    
    # Convert the Pydantic Patient model to a dictionary
    # exclude=['id'] removes the ID field because it will be used as the dictionary key
    # This prevents duplicating the ID inside the stored data
    patient_dict = patient.model_dump(exclude=['id'])  # type: ignore
    
    # Add the new patient to the dictionary
    # The patient ID becomes the key, the patient data becomes the value
    data[patient.id] = patient_dict
    
    # Save the updated data back to the JSON file
    save_data(data)
    
    # Return a success response with 201 Created status code
    # 201 status indicates that a new resource was successfully created
    return JSONResponse(
        status_code=201,
        content={'message': 'patient registered succefully'}
    )




# ==========================================
# API ENDPOINTS - PUT ROUTE (UPDATE)
# ==========================================

@app.put('/edit/{patient_id}', tags=["Patients"])
def update_patient(
    patient_id: str = Path(
        ...,
        description="Unique identifier of the patient to update",
        examples=['P001', 'P002', 'P013']
    ),
    patient_update: PatientUpdate = None
) -> JSONResponse:
    """
    Update patient - Modify specific fields of an existing patient.
    
    PUT /edit/{patient_id}
    Content-Type: application/json
    
    This endpoint allows partial updates to patient records.
    Only the fields provided in the request body will be updated.
    Omitted fields remain unchanged. All fields are optional in the request.
    
    After updating, the modified patient data is validated against the full
    Patient model constraints to ensure data integrity.
    
    Parameters:
        patient_id (str, path): Unique patient identifier to update
    
    Request Body (JSON - all fields optional):
        {
            "name": "Updated Name",
            "age": 30,
            "weight": 75.5
        }
    
    Returns:
        JSONResponse: Success message with 200 OK status code
    
    Response (200 OK):
        {"message": "patient updated"}
    
    Response (404 Not Found):
        {"detail": "Patient doesnt exist in database"}
    
    Response (422 Unprocessable Entity - Validation error):
        If updated data violates constraints (e.g., age > 120), validation fails
    
    Notes:
        - Only provided fields will be updated
        - Fields not provided in request are not changed
        - Updated data must still meet all validation constraints
        - Computed fields (bmi, verdict) are automatically recalculated
    
    Examples:
        # Update only the patient's weight
        curl -X PUT "http://localhost:8000/edit/P001" \\
             -H "Content-Type: application/json" \\
             -d '{"weight": 75.5}'
        
        # Update name and age
        curl -X PUT "http://localhost:8000/edit/P001" \\
             -H "Content-Type: application/json" \\
             -d '{"name": "Updated Name", "age": 30}'
    """
    
    # Load all patient data from database
    data = load_data()
    
    # Check if the patient exists in the database
    if patient_id not in data:
        # If patient not found, raise a 404 Not Found error
        raise HTTPException(
            status_code=404,
            detail="Patient doesnt exist in database"
        )
    
    # Get the existing patient's information
    existing_patient_info = data[patient_id]
    
    # Convert the PatientUpdate model to a dictionary
    # exclude_unset=True ensures only the fields that were explicitly provided
    # in the request body are included (fields not provided are excluded)
    updated_patient_info = patient_update.model_dump(exclude_unset=True)
    
    # Update only the provided fields in the existing patient record
    # Fields not provided in the request are left unchanged
    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
    
    # Add the patient ID back to the record
    # This is needed for validation in the next step
    existing_patient_info['id'] = patient_id
    
    # Recreate a full Patient object to validate all constraints
    # This ensures:
    #   - All validation rules are applied (age range, positive heights/weights, etc.)
    #   - Computed fields (bmi, verdict) are recalculated with new values
    patient_pydantic_obj = Patient(**existing_patient_info)
    
    # Convert back to dictionary, excluding the id field
    # The id field is excluded because it's stored as the dictionary key, not in the value
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')  # type: ignore
    
    # Update the patient record in the database with the validated data
    data[patient_id] = existing_patient_info
    
    # Save all changes back to the JSON file
    save_data(data)
    
    # Return success response with 200 OK status code
    return JSONResponse(
        status_code=200,
        content={'message': 'patient updated'}
    )



# ==========================================
# API ENDPOINTS - DELETE ROUTE
# ==========================================

@app.delete('/delete/{patient_id}', tags=["Patients"])
def delete_patient_data(
    patient_id: str = Path(
        ...,
        description="Unique identifier of the patient to delete",
        examples=['P001', 'P002', 'P013']
    )
) -> JSONResponse:
    """
    Delete patient - Remove a patient record from the database.
    
    DELETE /delete/{patient_id}
    
    This endpoint permanently deletes a patient record from the database.
    After deletion, the patient data cannot be recovered unless backed up.
    
    Parameters:
        patient_id (str, path): Unique patient identifier to delete
    
    Returns:
        JSONResponse: Confirmation message with 200 OK status code
    
    Response (200 OK):
        "patient detail deleted"
    
    Response (404 Not Found):
        {"detail": "Patient not found in database"}
    
    Important Notes:
        - This operation is PERMANENT and cannot be undone
        - The patient record is completely removed from the database
        - No backup is created automatically
        - Consider implementing soft deletes or audit trails in production
    
    Example:
        curl -X DELETE "http://localhost:8000/delete/P001"
    """
    
    # Load all patient data from database
    data = load_data()
    
    # Check if the patient exists in the database
    if patient_id not in data:
        # If patient not found, raise a 404 Not Found error
        raise HTTPException(
            status_code=404,
            detail='Patient not found in database'
        )
    
    # Delete the patient record from the dictionary
    # This removes the entry with the key patient_id
    del data[patient_id]
    
    # Save the updated data (without the deleted patient) back to the JSON file
    save_data(data)
    
    # Return success response confirming deletion
    return JSONResponse(
        status_code=200,
        content='patient detail deleted'
    )

# ==========================================
# END OF APPLICATION
# ==========================================
# 
# To run this application, use the command:
#   uvicorn main:app --reload
#
# This will start a development server at http://localhost:8000
#
# Access automatic API documentation:
#   - Swagger UI (interactive): http://localhost:8000/docs
#   - ReDoc (read-only): http://localhost:8000/redoc
#
# The --reload flag enables auto-restart when code changes (development only)
#
# For production deployment, remove --reload:
#   uvicorn main:app