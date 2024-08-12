
# Movie Listing API

This is a Movie Listing API developed using FastAPI. The API allows users to list movies, view listed movies, rate them, and add comments. The application is secured using JWT (JSON Web Tokens), ensuring that only the user who listed a movie can edit it. The API is designed to be scalable and can be deployed on any cloud platform.

## Tools and Technologies Used

- **Language & Framework**: Python, FastAPI
- **Authentication**: JSON Web Tokens (JWT)
- **Database**: SQL
- **Documentation**: OpenAPI/Swagger
- **Logging**: Python logging module

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- A SQL database

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/meshach5667/movieListingApi
   cd movieListingApi

   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**

   ```bash
   uvicorn main:app --reload
   ```

4. **Access API Documentation**

   ```bash
   127.0.0.1:8000/docs
   ```

5. **Running Tests**

   ```bash
   pytest
   ```