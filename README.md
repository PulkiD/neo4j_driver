# Neo4j FastAPI Driver

A production-ready FastAPI application that serves as a driver to connect to Neo4j databases hosted on Neo4j Cloud.

## Features

- FastAPI for high-performance async API development
- Automatic API documentation (Swagger UI and ReDoc)
- Singleton pattern for database connection and logging
- Environment-based configuration
- Structured logging with JSON format
- Separation of concerns (API routes, business logic, database layer)
- Error handling and proper response formatting
- Health check endpoint
- Production-ready code structure
- Async database operations
- Pydantic models for request/response validation
- CORS middleware support

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and fill in your Neo4j credentials:
   ```bash
   cp .env.example .env
   ```
5. Edit the `.env` file with your Neo4j credentials:
   ```
   NEO4J_URI=bolt://your-neo4j-instance.cloud.neo4j.io:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   NEO4J_DATABASE=neo4j
   LOG_LEVEL=INFO
   ```

## Running the Application

### Development
```bash
python run.py
```

### Production
```bash
uvicorn app:app --host 0.0.0.0 --port 5001 --workers 4
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:5001/docs`
- ReDoc: `http://localhost:5001/redoc`

## API Endpoints

### Health Check
- **GET** `/health`
  - Returns the health status of the application

### Execute Query
- **POST** `/api/v1/query`
  - Execute a Cypher query against the Neo4j database
  - Request body:
    ```json
    {
        "query": "MATCH (n) RETURN n LIMIT 5",
        "parameters": {}  // Optional query parameters
    }
    ```
  - Response:
    ```json
    {
        "status": "success",
        "count": 5,
        "results": [...],
        "metadata": {
            "query": "MATCH (n) RETURN n LIMIT 5",
            "parameters": {}
        }
    }
    ```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── query_routes.py
│   ├── core/
│   │   ├── db.py
│   │   └── query_service.py
│   ├── models/
│   │   └── query.py
│   ├── utils/
│   │   └── logger.py
│   └── logs/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## Logging

Logs are written to both console and file:
- File logs are stored in `app/logs/app.log`
- Logs are in JSON format for better parsing
- Log files are rotated when they reach 10MB
- Keeps 5 backup log files

## Error Handling

The application includes comprehensive error handling:
- Database connection errors
- Query execution errors
- Invalid request format
- General server errors
- Automatic HTTP status code mapping
- Detailed error messages in development mode

## Security Considerations

- Database credentials are stored in environment variables
- No sensitive information is exposed in logs
- Input validation using Pydantic models
- CORS middleware for API access control
- Proper error messages without exposing internal details

## Performance Features

- Async database operations
- FastAPI's high-performance async framework
- Connection pooling with Neo4j driver
- Efficient JSON serialization
- Automatic response compression

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 