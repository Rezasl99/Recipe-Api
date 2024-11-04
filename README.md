# Recipe API Project

## Overview
The Recipe API Project is a backend service for managing recipes, ingredients, and tags. It’s built with Django, Django REST Framework, and uses Docker for containerization.

## Features
- User authentication with Token Authentication
- CRUD operations for recipes, tags, and ingredients
- Image upload support for recipes
- Filter recipes by ingredients and tags
- Test-driven development (TDD) approach Over 60 tests to insure the code is working as expected
- used Swagger for API documentations

## Technologies
- **Django & Django REST Framework** - for API development
- **Docker** - for easy containerization and deployment
- **PostgreSQL** - as the primary database

### Prerequisites
- Docker installed on your system

### Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Rezasl99/Recipe-Api.git
   cd Recipe-Api
   
   docker-compose build
   docker-compose up
The API will be available at http://localhost:8000/api/docs/#/

To ensure everything is working as expected, run:
  docker-compose run --rm app sh -c "python manage.py test"

