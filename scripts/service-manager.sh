#!/bin/bash

# AA Virtual Service Manager
# This script manages starting and stopping services for the AA Virtual platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
PID_DIR="$REPO_ROOT/.pids"

# Create PID directory if it doesn't exist
mkdir -p "$PID_DIR"

# PID files
BACKEND_PID="$PID_DIR/backend.pid"
FRONTEND_PID="$PID_DIR/frontend.pid"

# Service configurations
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_HOST="0.0.0.0"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get PID using port
get_pid_by_port() {
    local port=$1
    lsof -ti :$port 2>/dev/null || echo ""
}

# Function to check if backend is running
is_backend_running() {
    if [ -f "$BACKEND_PID" ]; then
        local pid=$(cat "$BACKEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$BACKEND_PID"
            return 1
        fi
    fi
    return 1
}

# Function to check if frontend is running
is_frontend_running() {
    if [ -f "$FRONTEND_PID" ]; then
        local pid=$(cat "$FRONTEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$FRONTEND_PID"
            return 1
        fi
    fi
    return 1
}

# Function to start backend
start_backend() {
    print_status "Starting backend service..."
    
    if is_backend_running; then
        print_warning "Backend is already running (PID: $(cat "$BACKEND_PID"))"
        return 0
    fi
    
    if check_port $BACKEND_PORT; then
        local existing_pid=$(get_pid_by_port $BACKEND_PORT)
        print_warning "Port $BACKEND_PORT is already in use (PID: $existing_pid)"
        print_warning "Attempting to kill existing process..."
        kill -9 "$existing_pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$BACKEND_DIR/venv" ] && [ ! -d "$BACKEND_DIR/.venv" ]; then
        print_status "Creating Python virtual environment..."
        cd "$BACKEND_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    
    # Activate virtual environment and start backend
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    print_status "Starting FastAPI backend on $BACKEND_HOST:$BACKEND_PORT..."
    print_status "Backend logs will be written to: $REPO_ROOT/logs/backend.log"
    nohup python -m uvicorn main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload --log-level info > "$REPO_ROOT/logs/backend.log" 2>&1 &
    local backend_pid=$!
    echo "$backend_pid" > "$BACKEND_PID"
    
    # Log startup information
    echo "$(date): Backend started with PID $backend_pid" >> "$REPO_ROOT/logs/service-manager.log"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if is_backend_running; then
        print_success "Backend started successfully (PID: $backend_pid)"
        print_status "Backend API available at: http://$BACKEND_HOST:$BACKEND_PORT"
        print_status "API documentation at: http://$BACKEND_HOST:$BACKEND_PORT/docs"
    else
        print_error "Failed to start backend service"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend service..."
    
    if is_frontend_running; then
        print_warning "Frontend is already running (PID: $(cat "$FRONTEND_PID"))"
        return 0
    fi
    
    if check_port $FRONTEND_PORT; then
        local existing_pid=$(get_pid_by_port $FRONTEND_PORT)
        print_warning "Port $FRONTEND_PORT is already in use (PID: $existing_pid)"
        print_warning "Attempting to kill existing process..."
        kill -9 "$existing_pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Check if node_modules exists
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_status "Installing frontend dependencies..."
        cd "$FRONTEND_DIR"
        npm install
    fi
    
    # Start frontend
    cd "$FRONTEND_DIR"
    print_status "Starting Next.js frontend on port $FRONTEND_PORT..."
    nohup npm run dev > "$REPO_ROOT/logs/frontend.log" 2>&1 &
    local frontend_pid=$!
    echo "$frontend_pid" > "$FRONTEND_PID"
    
    # Wait a moment and check if it started successfully
    sleep 5
    if is_frontend_running; then
        print_success "Frontend started successfully (PID: $frontend_pid)"
        print_status "Frontend available at: http://localhost:$FRONTEND_PORT"
    else
        print_error "Failed to start frontend service"
        return 1
    fi
}

# Function to stop backend
stop_backend() {
    print_status "Stopping backend service..."
    
    if [ -f "$BACKEND_PID" ]; then
        local pid=$(cat "$BACKEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null || true
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Force killing backend process..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            print_success "Backend stopped successfully"
        else
            print_warning "Backend process not found"
        fi
        rm -f "$BACKEND_PID"
    else
        print_warning "No backend PID file found"
    fi
    
    # Also kill any process using the backend port
    local port_pid=$(get_pid_by_port $BACKEND_PORT)
    if [ -n "$port_pid" ]; then
        print_status "Killing process using port $BACKEND_PORT (PID: $port_pid)"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

# Function to stop frontend
stop_frontend() {
    print_status "Stopping frontend service..."
    
    if [ -f "$FRONTEND_PID" ]; then
        local pid=$(cat "$FRONTEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null || true
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Force killing frontend process..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            print_success "Frontend stopped successfully"
        else
            print_warning "Frontend process not found"
        fi
        rm -f "$FRONTEND_PID"
    else
        print_warning "No frontend PID file found"
    fi
    
    # Also kill any process using the frontend port
    local port_pid=$(get_pid_by_port $FRONTEND_PORT)
    if [ -n "$port_pid" ]; then
        print_status "Killing process using port $FRONTEND_PORT (PID: $port_pid)"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    echo
    
    # Backend status
    if is_backend_running; then
        local backend_pid=$(cat "$BACKEND_PID")
        print_success "Backend: Running (PID: $backend_pid)"
        print_status "  URL: http://$BACKEND_HOST:$BACKEND_PORT"
        print_status "  Docs: http://$BACKEND_HOST:$BACKEND_PORT/docs"
    else
        print_error "Backend: Not running"
    fi
    
    # Frontend status
    if is_frontend_running; then
        local frontend_pid=$(cat "$FRONTEND_PID")
        print_success "Frontend: Running (PID: $frontend_pid)"
        print_status "  URL: http://localhost:$FRONTEND_PORT"
    else
        print_error "Frontend: Not running"
    fi
    
    echo
    
    # Port status
    print_status "Port Status:"
    if check_port $BACKEND_PORT; then
        local backend_port_pid=$(get_pid_by_port $BACKEND_PORT)
        print_success "Port $BACKEND_PORT: In use (PID: $backend_port_pid)"
    else
        print_warning "Port $BACKEND_PORT: Available"
    fi
    
    if check_port $FRONTEND_PORT; then
        local frontend_port_pid=$(get_pid_by_port $FRONTEND_PORT)
        print_success "Port $FRONTEND_PORT: In use (PID: $frontend_port_pid)"
    else
        print_warning "Port $FRONTEND_PORT: Available"
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend")
            if [ -f "$REPO_ROOT/logs/backend.log" ]; then
                print_status "Backend logs:"
                tail -f "$REPO_ROOT/logs/backend.log"
            else
                print_warning "Backend log file not found"
            fi
            ;;
        "frontend")
            if [ -f "$REPO_ROOT/logs/frontend.log" ]; then
                print_status "Frontend logs:"
                tail -f "$REPO_ROOT/logs/frontend.log"
            else
                print_warning "Frontend log file not found"
            fi
            ;;
        *)
            print_error "Usage: $0 logs [backend|frontend]"
            exit 1
            ;;
    esac
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    stop_backend
    stop_frontend
    print_success "Cleanup completed"
}

# Function to setup development environment
setup_dev() {
    print_status "Setting up development environment..."
    
    # Create logs directory
    mkdir -p "$REPO_ROOT/logs"
    
    # Backend setup
    print_status "Setting up backend..."
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Backend dependencies installed"
    else
        print_warning "Backend virtual environment already exists"
    fi
    
    # Frontend setup
    print_status "Setting up frontend..."
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_warning "Frontend dependencies already installed"
    fi
    
    print_success "Development environment setup completed!"
}

# Function to show help
show_help() {
    echo "AA Virtual Service Manager"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start [backend|frontend|all]  Start services (default: all)"
    echo "  stop [backend|frontend|all]   Stop services (default: all)"
    echo "  restart [backend|frontend|all] Restart services (default: all)"
    echo "  status                        Show service status"
    echo "  logs [backend|frontend]       Show service logs"
    echo "  setup                         Setup development environment"
    echo "  cleanup                       Stop all services and cleanup"
    echo "  help                          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                      Start all services"
    echo "  $0 start backend              Start only backend"
    echo "  $0 stop frontend              Stop only frontend"
    echo "  $0 status                     Show current status"
    echo "  $0 logs backend               Follow backend logs"
}

# Main script logic
main() {
    local command=$1
    local service=$2
    
    # Create logs directory if it doesn't exist
    mkdir -p "$REPO_ROOT/logs"
    
    case $command in
        "start")
            case $service in
                "backend")
                    start_backend
                    ;;
                "frontend")
                    start_frontend
                    ;;
                "all"|"")
                    start_backend
                    start_frontend
                    ;;
                *)
                    print_error "Invalid service: $service"
                    print_error "Use: backend, frontend, or all"
                    exit 1
                    ;;
            esac
            ;;
        "stop")
            case $service in
                "backend")
                    stop_backend
                    ;;
                "frontend")
                    stop_frontend
                    ;;
                "all"|"")
                    stop_backend
                    stop_frontend
                    ;;
                *)
                    print_error "Invalid service: $service"
                    print_error "Use: backend, frontend, or all"
                    exit 1
                    ;;
            esac
            ;;
        "restart")
            case $service in
                "backend")
                    stop_backend
                    sleep 2
                    start_backend
                    ;;
                "frontend")
                    stop_frontend
                    sleep 2
                    start_frontend
                    ;;
                "all"|"")
                    stop_backend
                    stop_frontend
                    sleep 3
                    start_backend
                    start_frontend
                    ;;
                *)
                    print_error "Invalid service: $service"
                    print_error "Use: backend, frontend, or all"
                    exit 1
                    ;;
            esac
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs $service
            ;;
        "setup")
            setup_dev
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap cleanup INT

# Run main function with all arguments
main "$@"
