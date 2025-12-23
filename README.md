# FastAPI Application

A modern FastAPI application with document processing capabilities including OCR, classification, and extraction services.

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── documents.py   # Document-related endpoints
│   │   │   └── health.py      # Health check endpoints
│   ├── core/
│   │   └── config.py          # Application configuration
│   ├── models/
│   │   └── document.py        # Database models
│   ├── schemas/
│   │   └── document.py        # Pydantic schemas
│   ├── services/
│   │   ├── ocr_service.py           # OCR service
│   │   ├── classification_service.py # Document classification
│   │   └── extraction_service.py    # Data extraction
│   └── utils/
│       └── file_utils.py       # File utility functions
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## Features

- Document processing with OCR
- Document classification
- Data extraction from documents
- RESTful API endpoints
- Health check endpoints
- Docker support

## Installation

### Prerequisites

- Python 3.8+
- pip or poetry

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example` if available):
```bash
cp .env.example .env
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Docker

### Build the image:
```bash
docker build -t fastapi-app .
```

### Run the container:
```bash
docker run -p 8000:8000 fastapi-app
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8 .
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
# Application
APP_NAME=FastAPI Application
DEBUG=True
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database (if needed)
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

## License

MIT

