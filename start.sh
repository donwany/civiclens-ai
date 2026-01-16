#!/bin/bash

# Company Knowledge Assistant - Quick Start Script
# This script helps you set up and run the application

set -e

echo "Welcome! to CivicLens AI: Advancing AI Education, Civic Literacy, and Responsible Governance for America’s Future - Quick Start"
echo "================================================================================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   Run: nano .env (or use your preferred editor)"
    echo ""
    read -p "Press Enter after you've updated .env, or Ctrl+C to exit..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "🐳 Docker is running ✅"
echo ""

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
    echo "✅ Created data/ directory"
    echo ""
    echo "📄 Add your company documents to the data/ folder before ingesting."
    echo ""
fi

# Ask what to do
echo "What would you like to do?"
echo "1) Start the application (fresh)"
echo "2) Start the application (with existing data)"
echo "3) Stop the application"
echo "4) View logs"
echo "5) Reset everything (including database)"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔨 Building and starting services..."
        docker-compose down && docker-compose up --build -d
        echo ""
        echo "✅ Application started!"
        echo ""
        echo "🌐 Open http://localhost:1776 in your browser"
        echo ""
        echo "📋 Next steps:"
        echo "   1. Add documents to the data/ folder"
        echo "   2. In the chat, type: /ingest"
        echo "   3. Wait for ingestion to complete"
        echo "   4. Start asking questions!"
        echo ""
        echo "📊 View logs: docker-compose logs -f app"
        ;;
    2)
        echo ""
        echo "🔨 Starting services (keeping existing data)..."
        docker-compose up -d
        echo ""
        echo "✅ Application started!"
        echo "🌐 Open http://localhost:1776 in your browser"
        ;;
    3)
        echo ""
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Stopped!"
        ;;
    4)
        echo ""
        echo "📊 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    5)
        echo ""
        echo "⚠️  WARNING: This will delete all data including the database!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "🗑️  Removing everything..."
            docker-compose down -v
            echo "✅ Reset complete!"
        else
            echo "Cancelled."
        fi
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
