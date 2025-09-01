#!/bin/bash

echo "🚀 Lexa SDK PyPI Publishing Script"
echo "=================================="

# Check if .pypirc exists and has real credentials
if ! grep -q "YOUR_PYPI_TOKEN_HERE" ~/.pypirc 2>/dev/null; then
    echo "✅ PyPI credentials found!"
else
    echo "❌ Please update ~/.pypirc with your real PyPI token first!"
    echo "   Edit ~/.pypirc and replace YOUR_PYPI_TOKEN_HERE with your actual token"
    exit 1
fi

# Clean and rebuild
echo "📦 Rebuilding package..."
rm -rf dist/
python3 -m build

# Test upload to TestPyPI first
echo "🧪 Uploading to TestPyPI..."
python3 -m twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    echo "✅ TestPyPI upload successful!"
    echo "   Test your package: pip install --index-url https://test.pypi.org/simple/ lexa"

    # Ask if they want to upload to production
    read -p "🎯 Upload to production PyPI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading to production PyPI..."
        python3 -m twine upload dist/*
        if [ $? -eq 0 ]; then
            echo "🎉 Production upload successful!"
            echo "   Your package is now available: pip install lexa"
            echo "   PyPI URL: https://pypi.org/project/lexa/"
        else
            echo "❌ Production upload failed!"
        fi
    else
        echo "✅ Staying with TestPyPI only"
    fi
else
    echo "❌ TestPyPI upload failed!"
    echo "   Please check your credentials and try again"
fi
