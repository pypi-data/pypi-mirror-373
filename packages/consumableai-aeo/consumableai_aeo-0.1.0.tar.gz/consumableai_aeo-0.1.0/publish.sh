#!/bin/bash

# Script to publish consumableai-aeo to PyPI
# Usage: ./publish.sh [test|prod]

set -e

echo "🚀 Publishing consumableai-aeo to PyPI..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Check if distribution files exist
if [[ ! -d "dist" ]] || [[ -z "$(ls -A dist/)" ]]; then
    echo "❌ Distribution files not found. Building package first..."
    python -m build
fi

# Function to publish to Test PyPI
publish_test() {
    echo "📦 Publishing to Test PyPI..."
    
    # Check if Test PyPI credentials are set
    if [[ -z "$TEST_PYPI_TOKEN" ]]; then
        echo "❌ TEST_PYPI_TOKEN environment variable not set."
        echo "   Please set it with: export TEST_PYPI_TOKEN=pypi-<your-test-pypi-token>"
        echo "   Get your token from: https://test.pypi.org/manage/account/token/"
        exit 1
    fi
    
    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD=$TEST_PYPI_TOKEN
    export TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/
    
    python -m twine upload --repository testpypi dist/*
    
    echo "✅ Successfully published to Test PyPI!"
    echo "🔗 Test installation: pip install --index-url https://test.pypi.org/simple/ consumableai-aeo"
}

# Function to publish to Production PyPI
publish_prod() {
    echo "📦 Publishing to Production PyPI..."
    
    # Check if Production PyPI credentials are set
    if [[ -z "$PYPI_TOKEN" ]]; then
        echo "❌ PYPI_TOKEN environment variable not set."
        echo "   Please set it with: export PYPI_TOKEN=pypi-<your-main-pypi-token>"
        echo "   Get your token from: https://pypi.org/manage/account/token/"
        exit 1
    fi
    
    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD=$PYPI_TOKEN
    
    python -m twine upload dist/*
    
    echo "✅ Successfully published to Production PyPI!"
    echo "🔗 Install with: pip install consumableai-aeo"
}

# Main logic
case "${1:-test}" in
    "test")
        publish_test
        ;;
    "prod")
        echo "⚠️  Are you sure you want to publish to Production PyPI? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            publish_prod
        else
            echo "❌ Publishing cancelled."
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 [test|prod]"
        echo "  test: Publish to Test PyPI (default)"
        echo "  prod: Publish to Production PyPI"
        exit 1
        ;;
esac
