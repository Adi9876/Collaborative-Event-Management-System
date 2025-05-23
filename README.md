# NeoFi Event Management System

A collaborative event management system built with FastAPI, featuring role-based access control, version history, and real-time collaboration features.

## Features

- User authentication with JWT tokens
- Role-based access control (Owner, Editor, Viewer)
- CRUD operations for events
- Recurring events support
- Event sharing with granular permissions
- Version history with diff visualization
- Conflict detection for overlapping events

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd neofi
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=neofi
JWT_SECRET_KEY=your_secret_key
```

5. Create the database:
```bash
createdb neofi
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST /api/auth/register - Register a new user
- POST /api/auth/login - Login and receive an authentication token

### Events
- POST /api/events - Create a new event
- GET /api/events - List all events
- GET /api/events/{id} - Get a specific event
- PUT /api/events/{id} - Update an event
- DELETE /api/events/{id} - Delete an event
- POST /api/events/{id}/share - Share an event
- GET /api/events/{id}/history - Get event history
- GET /api/events/{id}/diff/{version1}/{version2} - Get diff between versions

## Testing

The API can be tested using the Swagger UI at http://localhost:8000/docs or using tools like Postman.

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 


# NeoFi Event Management System API

A RESTful API for collaborative event management with role-based access control and versioning features.

## API Testing Guide

### 1. Authentication

#### 1.1 Register a New User
- **Endpoint**: `POST /api/auth/register`
- **Request Body**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```
- **Expected Response**: 200 OK with user details and JWT token

#### 1.2 Login
- **Endpoint**: `POST /api/auth/login`
- **Request Body**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```
- **Expected Response**: 200 OK with JWT token
- **Important**: Save the JWT token for subsequent requests

#### 1.3 Refresh Token
- **Endpoint**: `POST /api/auth/refresh`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK with new JWT token

#### 1.4 Logout
- **Endpoint**: `POST /api/auth/logout`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK

### 2. Event Management

#### 2.1 Create Event
- **Endpoint**: `POST /api/events`
- **Headers**: Include the JWT token in Authorization header
- **Request Body**:
```json
{
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_time": "2025-05-23T10:00:00Z",
  "end_time": "2025-05-23T11:00:00Z",
  "location": "Conference Room A",
  "is_recurring": false
}
```
- **Expected Response**: 201 Created with event details
- **Note**: Creator automatically gets OWNER permissions

#### 2.2 List Events
- **Endpoint**: `GET /api/events`
- **Headers**: Include the JWT token in Authorization header
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum number of records to return (default: 100)
- **Expected Response**: 200 OK with list of events

#### 2.3 Get Event Details
- **Endpoint**: `GET /api/events/{event_id}`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK with event details
- **Note**: Requires at least VIEWER permissions

#### 2.4 Update Event
- **Endpoint**: `PUT /api/events/{event_id}`
- **Headers**: Include the JWT token in Authorization header
- **Request Body**:
```json
{
  "title": "Updated Team Meeting",
  "description": "Updated description"
}
```
- **Expected Response**: 200 OK with updated event details
- **Note**: Requires EDITOR permissions

#### 2.5 Delete Event
- **Endpoint**: `DELETE /api/events/{event_id}`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 204 No Content
- **Note**: Requires OWNER permissions

### 3. Event Sharing and Permissions

#### 3.1 Share Event
- **Endpoint**: `POST /api/events/{event_id}/share`
- **Headers**: Include the JWT token in Authorization header
- **Request Body**:
```json
{
  "user_id": 2,
  "role": "editor"
}
```
- **Expected Response**: 200 OK with permission details
- **Note**: Requires OWNER permissions
- **Available Roles**: "owner", "editor", "viewer"

#### 3.2 List Event Permissions
- **Endpoint**: `GET /api/events/{event_id}/permissions`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK with list of permissions

### 4. Version History

#### 4.1 Get Event History
- **Endpoint**: `GET /api/events/{event_id}/history`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK with list of versions
- **Note**: Requires at least VIEWER permissions

#### 4.2 Get Version Diff
- **Endpoint**: `GET /api/events/{event_id}/diff/{version1}/{version2}`
- **Headers**: Include the JWT token in Authorization header
- **Expected Response**: 200 OK with diff details
- **Note**: Requires at least VIEWER permissions

### 5. Testing Workflow Example

1. Register a new user
2. Login and save the JWT token
3. Create a new event
4. List events to verify creation
5. Share the event with another user
6. Update the event
7. Check event history
8. Compare versions using diff
9. Delete the event

### 6. Common Issues and Solutions

1. **403 Forbidden**
   - Ensure you have the correct permissions for the operation
   - Check if your JWT token is valid
   - Verify you're the owner for owner-only operations

2. **401 Unauthorized**
   - Check if your JWT token is included in the Authorization header
   - Verify the token hasn't expired
   - Try refreshing the token

3. **404 Not Found**
   - Verify the event ID exists
   - Check if you have access to the event

4. **422 Unprocessable Entity**
   - Verify the request body format
   - Check if all required fields are provided
   - Ensure date formats are correct (ISO 8601)

### 7. Role Hierarchy

- **OWNER**: Can perform all operations (create, read, update, delete, share)
- **EDITOR**: Can read and update events
- **VIEWER**: Can only read events

### 8. Best Practices

1. Always include the JWT token in the Authorization header
2. Use proper date formats (ISO 8601)
3. Handle pagination for large result sets
4. Check permissions before attempting operations
5. Keep track of event versions for important changes