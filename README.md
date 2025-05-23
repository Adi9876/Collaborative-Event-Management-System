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