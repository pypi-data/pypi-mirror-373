#!/usr/bin/env python3
"""
Lexa SDK PyPI Publishing Script
"""

import os
import subprocess
import sys

def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"🔧 {description}")
    print(f"   Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False

def check_credentials():
    """Check if PyPI credentials are configured."""
    pypirc_path = os.path.expanduser("~/.pypirc")
    if not os.path.exists(pypirc_path):
        print("❌ No .pypirc file found!")
        return False

    with open(pypirc_path, 'r') as f:
        content = f.read()

    if "YOUR_PYPI_TOKEN_HERE" in content:
        print("❌ Please update ~/.pypirc with your real PyPI token!")
        print("   Replace YOUR_PYPI_TOKEN_HERE with your actual PyPI API token")
        return False

    print("✅ PyPI credentials configured")
    return True

def main():
    """Main publishing workflow."""
    print("🚀 Lexa SDK PyPI Publishing Script")
    print("=" * 40)

    # Check credentials
    if not check_credentials():
        print("\n💡 To get your PyPI token:")
        print("   1. Go to: https://pypi.org/manage/account/#api-tokens")
        print("   2. Create a new API token")
        print("   3. Copy the token (starts with 'pypi-')")
        print("   4. Replace YOUR_PYPI_TOKEN_HERE in ~/.pypirc")
        return

    # Clean and rebuild
    print("\n📦 Cleaning and rebuilding package...")
    os.system("rm -rf dist/")
    if not run_command("python3 -m build", "Building package"):
        print("❌ Build failed!")
        return

    # Upload to TestPyPI first
    print("\n🧪 Uploading to TestPyPI...")
    if run_command("python3 -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI"):
        print("✅ TestPyPI upload successful!")
        print("   Test your package: pip install --index-url https://test.pypi.org/simple/ lexa")

        # Ask for production upload
        response = input("\n🎯 Upload to production PyPI? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("\n📤 Uploading to production PyPI...")
            if run_command("python3 -m twine upload dist/*", "Uploading to production PyPI"):
                print("🎉 Production upload successful!")
                print("   Your package is now available: pip install lexa")
                print("   PyPI URL: https://pypi.org/project/lexa/")
            else:
                print("❌ Production upload failed!")
        else:
            print("✅ Staying with TestPyPI only")
    else:
        print("❌ TestPyPI upload failed!")
        print("   Please check your credentials and try again")

if __name__ == "__main__":
    main()
