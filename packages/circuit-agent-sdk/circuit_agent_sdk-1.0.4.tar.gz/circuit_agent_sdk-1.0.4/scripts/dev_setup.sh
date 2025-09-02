#!/bin/bash

# Circuit Agent Python SDK - Development Setup Script
# This script sets up the development environment for the Circuit Agent Python SDK

set -e

echo "🚀 Setting up Circuit Agent Python SDK development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc  # or source ~/.zshrc for zsh users
fi

echo "✅ uv is installed"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Install Ruff tool
echo "🔧 Installing Ruff..."
uv tool install ruff@latest

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
uv run pre-commit install

# Run initial quality checks
echo "🔍 Running initial quality checks..."
uv run black .
uv run ruff check .
uv run mypy src/

echo "✅ Development environment setup complete!"
echo ""
echo "📋 Available commands:"
echo "  uv run black .                    # Format code"
echo "  uv run ruff check .               # Lint code"
echo "  uv run mypy src/                  # Type checking"
echo "  uv run pytest                     # Run tests"
echo "  uv run pytest --cov=src/agent_sdk --cov-report=html  # Run tests with coverage"
echo "  uv build                          # Build package"
echo "  uv run pre-commit run --all-files # Run all quality checks"
echo ""
echo "🎯 To run the basic example:"
echo "  uv run python examples/basic_agent.py"
echo ""
echo "🎯 To run the advanced example:"
echo "  uv run python examples/advanced_agent.py"
