#!/bin/bash
set -e

# Prompt for Python executable
read -p "Enter path to Python 3 executable [python3]: " PYTHON_EXEC
PYTHON_EXEC=${PYTHON_EXEC:-python3}

# Verify python version
if ! "$PYTHON_EXEC" -c "import sys; exit(0 if sys.version_info >= (3,6) else 1)" 2>/dev/null; then
    echo "Error: $PYTHON_EXEC is not a valid Python 3.6+ interpreter."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment using $PYTHON_EXEC..."
    "$PYTHON_EXEC" -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete."
echo "To start using the tool, run:"
echo "  source venv/bin/activate"
echo "  python ddi-cli.py"
