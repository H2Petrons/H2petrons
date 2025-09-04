#!/bin/bash

# This script automates the setup of the H2PETRONS backend for local development.
# It assumes you have Python 3.11+ and pip installed.

echo "Starting H2PETRONS project setup..."

# 1. Navigate to the backend directory
# This script assumes it's run from the root of the h2petrons-backend directory
# If you run it from elsewhere, adjust this path:
# cd /path/to/your/h2petrons-backend

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please ensure you are in the h2petrons-backend directory."
    exit 1
fi

# 2. Create a Python virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment. Do you have Python 3.11+ installed?"
    exit 1
fi

# 3. Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# 4. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies. Please check your internet connection or requirements.txt."
    deactivate
    exit 1
fi

# 5. Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with placeholder secrets..."
    echo "SECRET_KEY=\"your_flask_app_secret_key_here_CHANGE_ME\"" > .env
    echo "JWT_SECRET_KEY=\"your_jwt_secret_key_here_CHANGE_ME\"" >> .env
    echo "DATABASE_URL=\"sqlite:///./src/database/app.db\"" >> .env
    echo "Remember to update the .env file with your actual secrets!"
else
    echo ".env file already exists. Skipping creation."
fi

# 6. Ensure database directory exists
mkdir -p src/database

echo "Setup complete!"
echo ""
echo "To run the H2PETRONS backend:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the Flask application: python src/main.py"
echo ""
echo "The backend will typically run on http://127.0.0.1:5000"
echo ""
echo "For frontend integration, refer to the 'integration_guide.md' file."

# Deactivate the virtual environment for now, user will activate it when running the app
deactivate


