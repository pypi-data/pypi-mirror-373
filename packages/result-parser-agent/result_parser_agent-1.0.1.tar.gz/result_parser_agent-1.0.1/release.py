#!/usr/bin/env python3
"""
Release script for Result Parser Agent
Automates version bumping and release preparation
"""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    major, minor, patch = map(int, version.split("."))

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version in a file."""
    content = file_path.read_text()
    content = content.replace(
        f'version = "{old_version}"', f'version = "{new_version}"'
    )
    file_path.write_text(content)
    print(f"✅ Updated version in {file_path}")


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)

    if result.stdout:
        print(result.stdout)

    return result


def check_git_status() -> None:
    """Check if git repository is clean."""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("❌ Git repository has uncommitted changes")
        print("Please commit or stash your changes before releasing")
        sys.exit(1)
    print("✅ Git repository is clean")


def create_release(bump_type: str) -> None:
    """Create a new release."""
    print(f"🚀 Creating {bump_type} release...")

    # Check git status
    check_git_status()

    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"📋 New version: {new_version}")

    # Update version in pyproject.toml
    update_version_in_file(Path("pyproject.toml"), current_version, new_version)

    # Run tests
    print("🧪 Running tests...")
    run_command("uv run pytest")

    # Run linting
    print("🔍 Running linting...")
    run_command("uv run ruff check .")
    run_command("uv run black --check .")
    run_command("uv run isort --check-only .")

    # Build package
    print("📦 Building package...")
    run_command("uv run python -m build")

    # Commit changes
    print("💾 Committing changes...")
    run_command("git add pyproject.toml uv.lock")
    run_command(f'git commit -m "Bump version to {new_version}"')

    # Create tag
    print("🏷️ Creating git tag...")
    run_command(f'git tag -a v{new_version} -m "Release v{new_version}"')

    # Push changes
    print("📤 Pushing changes...")
    run_command("git push origin main")
    run_command(f"git push origin v{new_version}")

    print(f"\n🎉 Release {new_version} created successfully!")
    print("\n📋 Next steps:")
    print("1. Go to GitHub → Releases")
    print(f"2. Edit the draft release for v{new_version}")
    print("3. Add release notes")
    print("4. Click 'Publish release'")
    print("5. The CI/CD pipeline will automatically publish to PyPI")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <bump_type>")
        print("bump_type: major, minor, or patch")
        sys.exit(1)

    bump_type = sys.argv[1].lower()
    if bump_type not in ["major", "minor", "patch"]:
        print("Error: bump_type must be major, minor, or patch")
        sys.exit(1)

    try:
        create_release(bump_type)
    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
