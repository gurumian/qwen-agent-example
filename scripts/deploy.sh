#!/bin/bash

# Qwen-Agent Chatbot Deployment Script
# This script provides easy deployment options for the chatbot system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="qwen-agent-chatbot"
DEFAULT_PORT=8002
DEFAULT_HOST="0.0.0.0"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Qwen-Agent Chatbot Deployment${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION is installed"
        else
            print_error "Python 3.10+ is required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check uv
    if command -v uv &> /dev/null; then
        print_success "uv is installed"
    else
        print_warning "uv is not installed, installing now..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
    else
        print_warning "Docker is not installed (optional for containerized deployment)"
    fi
}

setup_environment() {
    print_info "Setting up environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_success ".env file already exists"
    fi
    
    # Create necessary directories
    mkdir -p workspace temp_uploads
    print_success "Created workspace directories"
}

install_dependencies() {
    print_info "Installing dependencies..."
    
    if [ -f uv.lock ]; then
        uv sync
        print_success "Dependencies installed using uv"
    else
        print_error "uv.lock file not found. Please run 'uv sync' first"
        exit 1
    fi
}

check_ollama() {
    print_info "Checking Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is installed"
        
        # Check if Ollama service is running
        if curl -s http://localhost:11434/v1/models &> /dev/null; then
            print_success "Ollama service is running"
            
            # Check if qwen3:14b model is available
            if ollama list | grep -q "qwen3:14b"; then
                print_success "qwen3:14b model is available"
            else
                print_warning "qwen3:14b model not found, pulling now..."
                ollama pull qwen3:14b
                print_success "qwen3:14b model downloaded"
            fi
        else
            print_warning "Ollama service is not running, starting now..."
            ollama serve &
            sleep 5
            print_success "Ollama service started"
        fi
    else
        print_warning "Ollama is not installed"
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        print_success "Ollama installed"
        
        print_info "Starting Ollama service..."
        ollama serve &
        sleep 5
        
        print_info "Downloading qwen3:14b model..."
        ollama pull qwen3:14b
        print_success "Setup complete"
    fi
}

deploy_development() {
    print_info "Deploying in development mode..."
    
    # Start the API server
    print_info "Starting API server on http://$DEFAULT_HOST:$DEFAULT_PORT"
    uv run python main.py --mode api &
    API_PID=$!
    
    print_success "API server started (PID: $API_PID)"
    print_info "API Documentation: http://$DEFAULT_HOST:$DEFAULT_PORT/docs"
    print_info "Health Check: http://$DEFAULT_HOST:$DEFAULT_PORT/health"
    
    # Wait for server to start
    sleep 3
    
    # Test health endpoint
    if curl -s http://localhost:$DEFAULT_PORT/health &> /dev/null; then
        print_success "API server is responding"
    else
        print_error "API server is not responding"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    print_info "Press Ctrl+C to stop the server"
    wait $API_PID
}

deploy_docker() {
    print_info "Deploying with Docker Compose..."
    
    if [ ! -f docker-compose.yml ]; then
        print_error "docker-compose.yml not found"
        exit 1
    fi
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Docker services started"
    print_info "API: http://localhost:$DEFAULT_PORT"
    print_info "Ollama: http://localhost:11434"
    
    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 10
    
    # Check health
    if curl -s http://localhost:$DEFAULT_PORT/health &> /dev/null; then
        print_success "Deployment successful"
    else
        print_error "Deployment failed"
        docker-compose logs
        exit 1
    fi
}

run_tests() {
    print_info "Running tests..."
    
    if uv run python run_tests.py; then
        print_success "All tests passed"
    else
        print_error "Some tests failed"
        exit 1
    fi
}

show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev          Deploy in development mode"
    echo "  docker       Deploy using Docker Compose"
    echo "  test         Run tests"
    echo "  setup        Setup environment and dependencies"
    echo "  check        Check system requirements"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # Setup environment and install dependencies"
    echo "  $0 dev       # Start development server"
    echo "  $0 docker    # Deploy with Docker"
    echo "  $0 test      # Run test suite"
}

# Main script
main() {
    print_header
    
    case "${1:-help}" in
        "setup")
            check_requirements
            setup_environment
            install_dependencies
            check_ollama
            print_success "Setup complete!"
            ;;
        "dev")
            check_requirements
            setup_environment
            install_dependencies
            check_ollama
            deploy_development
            ;;
        "docker")
            check_requirements
            deploy_docker
            ;;
        "test")
            check_requirements
            install_dependencies
            run_tests
            ;;
        "check")
            check_requirements
            check_ollama
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@" 