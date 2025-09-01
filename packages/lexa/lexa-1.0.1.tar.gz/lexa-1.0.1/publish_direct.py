#!/usr/bin/env python3
"""
Direct Lexa SDK PyPI Publishing Script (Production Only)
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

    if "YOUR_PYPI_TOKEN_HERE" in content or "pypi-" not in content:
        print("❌ Please update ~/.pypirc with your real PyPI token!")
        return False

    print("✅ PyPI credentials configured")
    return True

def main():
    """Direct production publishing workflow."""
    print("🚀 Direct Lexa SDK Production PyPI Publishing")
    print("=" * 50)

    # Check credentials
    if not check_credentials():
        print("\n💡 Your .pypirc should contain:")
        print("   [pypi]")
        print("   username = __token__")
        print("   password = pypi-YourActualTokenHere")
        return

    # Confirm production upload
    print("\n⚠️  This will upload directly to PRODUCTION PyPI")
    print("   Your package will be publicly available as: pip install lexa")
    response = input("   Are you sure you want to proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("   ❌ Upload cancelled")
        return

    # Clean and rebuild
    print("\n📦 Cleaning and rebuilding package...")
    os.system("rm -rf dist/")
    if not run_command("python3 -m build", "Building package"):
        print("❌ Build failed!")
        return

    # Upload directly to production PyPI
    print("\n📤 Uploading to production PyPI...")
    if run_command("python3 -m twine upload dist/*", "Uploading to PyPI"):
        print("\n🎉 SUCCESS! Your package is now live!")
        print("   📦 Available at: https://pypi.org/project/lexa/")
        print("   🛠️  Install with: pip install lexa")
        print("\n   You can test it with:")
        print("   pip install lexa")
        print("   python3 -c \"from lexa_sdk import Lexa; print('✅ Works!')\"")
    else:
        print("\n❌ Upload failed!")
        print("   Possible issues:")
        print("   - Check your PyPI token is correct")
        print("   - Verify you have upload permissions")
        print("   - Make sure package name 'lexa' is available")

if __name__ == "__main__":
    main()
