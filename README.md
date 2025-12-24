# Chatbot Support Web Application

A full-stack FastAPI application for a customer support chatbot.

## Features

- **User Authentication**: Registration and Login with JWT and password hashing.
- **Chat Sessions**: Create and manage chat sessions.
- **Real-time Messaging**: WebSocket support for sending messages and receiving bot responses.
- **Message History**: Persistent storage of chat history in SQLite (or any SQLAlchemy-supported DB).
- **Bot Logic**: Simple keyword-based auto-replies.
- **Documentation**: Swagger UI integration.

## Project Structure

- `app/`: Main application source code.
  - `api/`: API endpoints (auth, chat).
  - `core/`: Configuration and security settings.
  - `db/`: Database models and connection.
  - `schemas/`: Pydantic models for data validation.
  - `services/`: Business logic (bot service).
- `alembic/`: Database migrations.
- `tests/`: Automated tests.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd practic
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Database Migrations

Initialize the database using Alembic:

```bash
alembic upgrade head
```

This will create the SQLite database `chat.db` with the required tables.

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

Run the automated tests:

```bash
pytest
```

## WebSocket Usage

Connect to `ws://localhost:8000/api/v1/chat/ws/{session_id}?token={access_token}`.
Send JSON messages: `{"content": "Hello"}`.
Receive JSON responses.

## Development

- **Add a migration**: `alembic revision --autogenerate -m "message"`
- **Apply migrations**: `alembic upgrade head`
