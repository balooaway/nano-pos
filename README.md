POS Nano

A lightweight Point-of-Sale (POS) application built with Python FastAPI and PostgreSQL.

Quick Start
1. Set up PostgreSQL with Docker
bash
docker run --name posnano-db \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=posnano \
    -p 5432:5432 \
    -d postgres:16
2. Clone and set up the project
bash
git clone https://github.com/balooaway/pos-nano.git
cd pos-nano
3. Set up Python environment
bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

4. Database setup
bash
# Run migrations
alembic upgrade head

5. Start the application
bash
uvicorn app.main:app --reload
The application will be available at http://localhost:8000

Requirements
The project uses the following Python packages (see requirements.txt):

text
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
python-dotenv==1.0.0

Access the Application

Main Application: http://localhost:8000

API Documentation: http://localhost:8000/docs

Health: http://localhost:8000/health