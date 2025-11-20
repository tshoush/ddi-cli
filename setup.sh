#!/bin/bash
set -e

# Prompt for Python executable
read -p "Enter path to Python 3 executable [python3]: " PYTHON_EXEC
PYTHON_EXEC=${PYTHON_EXEC:-python3}

# Check if the input is a directory
if [ -d "$PYTHON_EXEC" ]; then
    # Try adding python3 or python to the path
    if [ -f "$PYTHON_EXEC/python3" ]; then
        PYTHON_EXEC="$PYTHON_EXEC/python3"
    elif [ -f "$PYTHON_EXEC/python" ]; then
        PYTHON_EXEC="$PYTHON_EXEC/python"
    fi
fi

# Verify python version
if ! "$PYTHON_EXEC" -c "import sys; exit(0 if sys.version_info >= (3,6) else 1)" 2>/dev/null; then
    echo "Error: '$PYTHON_EXEC' is not a valid Python 3.6+ interpreter."
    echo "Please ensure you provide the full path to the python executable (e.g. /path/to/python3) or a directory containing it."
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
