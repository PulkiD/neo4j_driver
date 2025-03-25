# Neo4j Flask Driver

A production-ready Flask application that serves as a driver to connect to Neo4j databases hosted on Neo4j Cloud.

## Features

- Singleton pattern for database connection and logging
- Environment-based configuration
- Structured logging with JSON format
- Separation of concerns (API routes, business logic, database layer)
- Error handling and proper response formatting
- Health check endpoint
- Production-ready code structure

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
gunicorn -w 4 "app:create_app()"
```

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

## Security Considerations

- Database credentials are stored in environment variables
- No sensitive information is exposed in logs
- Input validation for all API requests
- Proper error messages without exposing internal details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 