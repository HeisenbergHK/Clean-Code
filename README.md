# 🚀 FastAPI Affiliate Payout Management System

A robust, production-ready FastAPI application for managing affiliate payouts with JWT authentication, MongoDB integration, and comprehensive pagination features. This system provides secure admin-only access to payout records with advanced filtering and wallet balance management.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development Journey](#-development-journey)
- [Security Features](#-security-features)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔐 Authentication & Authorization
- **JWT-based Authentication**: Secure token-based authentication system
- **Admin Role Management**: Role-based access control with admin verification
- **Token Validation**: Comprehensive token validation with expiration handling
- **Secure Password Hashing**: bcrypt-based password encryption

### 💰 Payout Management
- **Advanced Filtering**: Filter payouts by status, date ranges, user types, and payment dates
- **Pagination Support**: Efficient pagination with customizable page sizes
- **Real-time Balance Calculation**: Dynamic wallet balance computation
- **Transaction Processing**: Automated transaction processing with date-based availability

### 🗄️ Database Operations
- **Async MongoDB Integration**: High-performance async database operations using Motor
- **Connection Management**: Robust connection handling with retry mechanisms
- **Collection Management**: Organized collection structure for users, wallets, and payouts
- **Data Validation**: ObjectId validation and error handling

### 🐳 DevOps & Deployment
- **Docker Support**: Complete containerization with Docker Compose
- **Environment Configuration**: Flexible environment-based configuration
- **Database Initialization**: Automated user creation and database setup
- **Health Checks**: Connection monitoring and validation

## 🏗️ Architecture

The application follows a clean, modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Authentication │────│    Database     │
│   (main.py)     │    │   (JWT_auth.py) │    │  (database.py)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│     Tools       │──────────────┘
                        │   (tools.py)    │
                        └─────────────────┘
```

### Key Components:

1. **Authentication Layer**: JWT token management and user authorization
2. **Database Layer**: Async MongoDB operations with connection pooling
3. **Business Logic**: Pagination, filtering, and data processing utilities
4. **API Layer**: RESTful endpoints with comprehensive error handling

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.10+**: Latest Python features and performance improvements

### Database
- **MongoDB 6.0**: NoSQL database for flexible document storage
- **Motor**: Async MongoDB driver for Python

### Authentication
- **PyJWT**: JSON Web Token implementation
- **bcrypt**: Password hashing library

### DevOps
- **Docker & Docker Compose**: Containerization and orchestration
- **uvicorn**: ASGI server for FastAPI applications

### Development Tools
- **python-dotenv**: Environment variable management
- **Pydantic**: Data validation and settings management

### Testing Framework
- **pytest**: Modern testing framework with fixtures and async support
- **pytest-asyncio**: Async test support for FastAPI endpoints
- **httpx**: HTTP client for integration testing

## 📁 Project Structure

```
Clean Code/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application and routes
│   ├── database.py              # MongoDB connection and collections
│   ├── JWT_authentication.py    # Authentication and authorization
│   └── tools.py                 # Utility functions and pagination
├── scripts/                     # Utility scripts
│   ├── create_users.py         # Database user initialization
│   └── generate_token.py       # JWT token generation utility
├── tests/                       # Test suite
│   ├── __init__.py             # Test package initialization
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_jwt_authentication.py  # Authentication tests
│   ├── test_database.py        # Database connection tests
│   ├── test_tools.py           # Utility functions tests
│   ├── test_main.py            # Main application tests
│   └── test_integration.py     # Integration tests
├── temp/                        # Temporary files and legacy code
│   ├── temp_database.py        # Legacy database implementation
│   └── temp.txt                # Temporary token storage
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Application container definition
├── docker-entrypoint.sh       # Container startup script
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Pytest configuration
├── run_tests.py               # Test runner script
├── .env                        # Environment variables
├── .gitignore                 # Git ignore patterns
└── .dockerignore              # Docker ignore patterns
```

## 🚀 Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)
- Git

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Clean Code"
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Verify installation**
   ```bash
   curl http://localhost:8001/docs
   ```

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start MongoDB** (using Docker)
   ```bash
   docker run -d --name mongo -p 27017:27017 \
     -e MONGO_INITDB_ROOT_USERNAME=root \
     -e MONGO_INITDB_ROOT_PASSWORD=example \
     mongo:6.0
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:router --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGO_HOST=mongo                    # MongoDB host (use 'localhost' for local dev)
MONGO_PORT=27017                   # MongoDB port
MONGO_INITDB_DATABASE=mydatabase   # Database name
MONGO_INITDB_ROOT_USERNAME=root    # MongoDB username
MONGO_INITDB_ROOT_PASSWORD=example # MongoDB password

# JWT Configuration
JWT_SECRET=your-super-secret-key   # JWT signing secret (generate a strong key)
JWT_ALGORITHM=HS256               # JWT algorithm
JWT_EXPIRATION_MINUTES=30         # Token expiration time

# Docker Host Ports
FASTAPI_HOST_PORT=8001           # FastAPI external port
MONGO_HOST_PORT=27018            # MongoDB external port
```

### Security Considerations

- **JWT Secret**: Generate a strong, random secret key for production
- **Database Credentials**: Use strong passwords and consider using Docker secrets
- **Environment Files**: Never commit `.env` files to version control

## 📖 Usage

### Authentication

1. **Generate Admin Token**
   ```bash
   python3 scripts/generate_token.py
   ```

2. **Use Token in Requests**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8001/payout
   ```

### API Endpoints

#### Get Paginated Payouts
```http
GET /payout?page=1&statuses=pending,approved&user_type=affiliate
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `page` (optional): Page number for pagination
- `statuses` (optional): Comma-separated status values
- `start_date` (optional): Filter records created after this date
- `end_date` (optional): Filter records created before this date
- `user_type` (optional): Filter by user type
- `payment_start_date` (optional): Filter by payment date after this date
- `payment_end_date` (optional): Filter by payment date before this date

**Response Format:**
```json
{
  "page": 1,
  "pageSize": 3,
  "totalPages": 10,
  "totalDocs": 30,
  "results": [
    {
      "id": "507f1f77bcf86cd799439011",
      "userId": "507f1f77bcf86cd799439012",
      "amount": 150.00,
      "status": "pending",
      "userType": "affiliate",
      "created": "2024-01-15T10:30:00Z",
      "paymentDate": "2024-01-20T10:30:00Z",
      "availableBalance": 1250.00,
      "pendingBalance": 300.00
    }
  ]
}
```

## 📚 API Documentation

### Interactive Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Authentication Flow

1. **User Creation**: Users are automatically created during container startup
2. **Token Generation**: Use the generate_token.py script to create JWT tokens
3. **API Access**: Include the token in the Authorization header for all requests
4. **Admin Verification**: The system verifies admin privileges for all payout endpoints

### Error Handling

The API provides comprehensive error responses:

```json
{
  "detail": "Token expired",
  "status_code": 401
}
```

Common error codes:
- `400`: Bad Request (invalid parameters, malformed data)
- `401`: Unauthorized (invalid or expired token)
- `404`: Not Found (user or resource not found)
- `500`: Internal Server Error

## 🔄 Development Journey

This project has undergone significant evolution, as evidenced by the git history:

### Phase 1: Initial Implementation (32eebb8)
- Basic code structure with minimal organization
- Direct database connections and simple authentication

### Phase 2: Modularization (8921df2 - da3f0ff)
- Added proper project structure with `.gitignore`
- Renamed modules for clarity (`d_1.py` → `JWT_authentication.py`)
- Introduced scripts directory for utilities
- Added Docker support with compose configuration

### Phase 3: Async Integration (6626e95 - 332381f)
- Migrated from synchronous PyMongo to async Motor
- Updated imports and dependencies
- Enhanced database connection handling

### Phase 4: Architecture Restructuring (9c8e447)
- **Breaking Change**: Complete project reorganization
- Moved all application code to `app/` package
- Updated Docker configuration for new structure
- Enhanced script functionality

### Phase 5: Clean Code Implementation (a4d1463 - d41e0a4)
- Applied Object-Oriented Programming principles
- Added comprehensive docstrings to all modules
- Implemented proper class hierarchies and separation of concerns
- Fixed typos and improved code quality

### Key Improvements Made:

1. **Code Organization**: Transformed from scattered files to a well-structured package
2. **Async Performance**: Migrated to async/await patterns for better performance
3. **Clean Architecture**: Implemented SOLID principles and clean code practices
4. **Documentation**: Added comprehensive docstrings and type hints
5. **Error Handling**: Robust error handling and validation
6. **Security**: Enhanced JWT handling and password encryption

## 🔒 Security Features

### Authentication Security
- **JWT Token Validation**: Comprehensive token validation with expiration checks
- **Password Hashing**: bcrypt-based password hashing with salt
- **Role-Based Access**: Admin-only access to sensitive endpoints
- **Token Extraction**: Secure token extraction from Authorization headers

### Database Security
- **Connection Security**: Authenticated MongoDB connections
- **Input Validation**: ObjectId validation and sanitization
- **Error Handling**: Secure error messages without information leakage

### Application Security
- **Environment Variables**: Sensitive data stored in environment variables
- **Docker Security**: Proper container isolation and networking
- **CORS Configuration**: Configurable cross-origin resource sharing

## 🧪 Testing

The project includes a comprehensive test suite with unit tests, integration tests, and fixtures for all major components.

### Test Structure

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_jwt_authentication.py  # Authentication and JWT tests
├── test_database.py            # Database connection tests
├── test_tools.py               # Utility functions tests
├── test_main.py                # Main application endpoint tests
└── test_integration.py         # End-to-end integration tests
```

### Running Tests

#### Using the Test Runner Script (Recommended)
```bash
# Run all tests
python3 run_tests.py --all

# Run only unit tests
python3 run_tests.py --unit

# Run only integration tests
python3 run_tests.py --integration

# Run tests with coverage report
python3 run_tests.py --coverage

# Run specific test file
python3 run_tests.py --file test_jwt_authentication.py

# Run tests in verbose mode
python3 run_tests.py --verbose
```

#### Using Pytest Directly
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_jwt_authentication.py
pytest tests/test_database.py
pytest tests/test_tools.py

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run tests in verbose mode
pytest -v

# Run only unit tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration
```

### Test Categories

#### Unit Tests
- **Authentication Tests**: JWT token validation, user authorization, config management
- **Database Tests**: Connection handling, collection access, error scenarios
- **Tools Tests**: Pagination, ObjectId validation, string conversion utilities
- **Main Tests**: Endpoint logic, query parameter processing, filter application

#### Integration Tests
- **End-to-End API Tests**: Complete request/response cycles
- **Authentication Flow**: Token generation to endpoint access
- **Error Handling**: Invalid tokens, unauthorized access, malformed requests
- **Health Checks**: OpenAPI documentation accessibility

### Test Fixtures

The test suite includes comprehensive fixtures for:
- Mock configuration managers
- Mock database collections
- Sample user and payout data
- Authentication services
- JWT handlers

### Test Coverage

The test suite covers:
- ✅ **JWT Authentication**: Token validation, user verification, admin checks
- ✅ **Database Operations**: Connection management, collection access
- ✅ **Pagination Logic**: Page calculation, result formatting, filtering
- ✅ **API Endpoints**: Request handling, response formatting, error cases
- ✅ **Utility Functions**: String conversion, ObjectId validation, balance calculation
- ✅ **Integration Flows**: Complete authentication and data retrieval workflows

### Manual Testing

1. **Start the application**
   ```bash
   docker-compose up -d
   ```

2. **Generate test token**
   ```bash
   python3 scripts/generate_token.py
   ```

3. **Test authentication**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8001/payout
   ```

### Database Testing

The application includes automatic user creation for testing:
- Admin user: `admin@example.com` / `adminpassword123`
- Regular user: `user@example.com` / `userpassword123`

### Continuous Integration

To set up CI/CD with the test suite:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python3 run_tests.py --coverage
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Follow the existing code style**
5. **Write tests for new functionality**
   ```bash
   # Run tests to ensure nothing is broken
   python3 run_tests.py --all
   
   # Add tests for your new code
   # Follow existing test patterns in tests/ directory
   ```
6. **Ensure all tests pass**
   ```bash
   python3 run_tests.py --coverage
   ```
7. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new feature"
   ```
7. **Push and create a pull request**

### Code Style Guidelines

- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Add comprehensive docstrings for all classes and methods
- Implement proper error handling and logging
- Write self-documenting code with meaningful variable names

### Commit Message Convention

This project follows conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks
- `docs:` Documentation updates

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Built with ❤️ using FastAPI, MongoDB, and modern Python practices**

*This README reflects the current state of the project after significant refactoring and clean code implementation. The project has evolved from a simple script-based application to a production-ready, well-architected system.*