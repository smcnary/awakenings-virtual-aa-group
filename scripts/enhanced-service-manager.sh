#!/bin/bash

# AA Virtual Enhanced Service Manager
# Environment-specific service management with comprehensive logging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$REPO_ROOT/scripts/config.env"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
PID_DIR="$REPO_ROOT/.pids"
LOGS_DIR="$REPO_ROOT/logs"

# Create directories if they don't exist
mkdir -p "$PID_DIR" "$LOGS_DIR"

# Load configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo -e "${RED}[ERROR]${NC} Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Environment setup
ENVIRONMENT=${1:-$DEFAULT_ENV}
shift # Remove environment from arguments

# Validate environment
case $ENVIRONMENT in
    "development"|"dev")
        ENVIRONMENT="development"
        ENV_PREFIX="DEV"
        ;;
    "staging"|"stage")
        ENVIRONMENT="staging"
        ENV_PREFIX="STAGING"
        ;;
    "production"|"prod")
        ENVIRONMENT="production"
        ENV_PREFIX="PROD"
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Invalid environment: $ENVIRONMENT"
        echo -e "${YELLOW}[INFO]${NC} Valid environments: development, staging, production"
        exit 1
        ;;
esac

# Set environment-specific variables
BACKEND_PORT=$(eval echo \$${ENV_PREFIX}_BACKEND_PORT)
FRONTEND_PORT=$(eval echo \$${ENV_PREFIX}_FRONTEND_PORT)
BACKEND_HOST=$(eval echo \$${ENV_PREFIX}_BACKEND_HOST)
BACKEND_LOG_LEVEL=$(eval echo \$${ENV_PREFIX}_BACKEND_LOG_LEVEL)
FRONTEND_LOG_LEVEL=$(eval echo \$${ENV_PREFIX}_FRONTEND_LOG_LEVEL)
DATABASE_URL=$(eval echo \$${ENV_PREFIX}_DATABASE_URL)
ENABLE_HOT_RELOAD=$(eval echo \$${ENV_PREFIX}_ENABLE_HOT_RELOAD)

# PID files with environment suffix
BACKEND_PID="$PID_DIR/backend-${ENVIRONMENT}.pid"
FRONTEND_PID="$PID_DIR/frontend-${ENVIRONMENT}.pid"

# Log files with environment suffix
BACKEND_LOG="$LOGS_DIR/backend-${ENVIRONMENT}.log"
FRONTEND_LOG="$LOGS_DIR/frontend-${ENVIRONMENT}.log"
SERVICE_LOG="$LOGS_DIR/service-manager-${ENVIRONMENT}.log"

# Function to log with timestamp and environment
log_with_env() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] [$ENVIRONMENT] [$level] $message"
    
    echo -e "$log_entry"
    echo "$log_entry" >> "$SERVICE_LOG"
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log_with_env "INFO" "$1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log_with_env "SUCCESS" "$1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log_with_env "WARNING" "$1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log_with_env "ERROR" "$1"
}

print_debug() {
    if [ "$BACKEND_LOG_LEVEL" = "debug" ] || [ "$ENVIRONMENT" = "development" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
        log_with_env "DEBUG" "$1"
    fi
}

print_environment_info() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  AA Virtual Service Manager${NC}"
    echo -e "${PURPLE}  Environment: $ENVIRONMENT${NC}"
    echo -e "${PURPLE}========================================${NC}"
    print_status "Configuration:"
    print_status "  Backend Port: $BACKEND_PORT"
    print_status "  Frontend Port: $FRONTEND_PORT"
    print_status "  Backend Host: $BACKEND_HOST"
    print_status "  Backend Log Level: $BACKEND_LOG_LEVEL"
    print_status "  Hot Reload: $ENABLE_HOT_RELOAD"
    print_status "  Database: $(echo $DATABASE_URL | sed 's/:[^:]*@/:***@/')"
    echo -e "${PURPLE}========================================${NC}"
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

# Function to setup environment-specific configuration
setup_environment() {
    print_status "Setting up $ENVIRONMENT environment..."
    
    # Create environment-specific directories
    mkdir -p "$LOGS_DIR" "$PID_DIR"
    
    # Set environment variables for services
    export ENVIRONMENT=$ENVIRONMENT
    export DATABASE_URL=$DATABASE_URL
    export LOG_LEVEL=$BACKEND_LOG_LEVEL
    
    # Create environment-specific .env files
    cat > "$BACKEND_DIR/.env.$ENVIRONMENT" << EOF
ENVIRONMENT=$ENVIRONMENT
DATABASE_URL=$DATABASE_URL
LOG_LEVEL=$BACKEND_LOG_LEVEL
PORT=$BACKEND_PORT
HOST=$BACKEND_HOST
EOF

    cat > "$FRONTEND_DIR/.env.$ENVIRONMENT" << EOF
NEXT_PUBLIC_ENVIRONMENT=$ENVIRONMENT
NEXT_PUBLIC_API_URL=http://$BACKEND_HOST:$BACKEND_PORT
NEXT_PUBLIC_LOG_LEVEL=$FRONTEND_LOG_LEVEL
PORT=$FRONTEND_PORT
EOF

    print_success "Environment configuration created"
}

# Function to start backend
start_backend() {
    print_status "Starting backend service in $ENVIRONMENT mode..."
    
    if is_backend_running; then
        local pid=$(cat "$BACKEND_PID")
        print_warning "Backend is already running (PID: $pid)"
        return 0
    fi
    
    if check_port $BACKEND_PORT; then
        local existing_pid=$(get_pid_by_port $BACKEND_PORT)
        print_warning "Port $BACKEND_PORT is already in use (PID: $existing_pid)"
        print_warning "Attempting to kill existing process..."
        kill -9 "$existing_pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Setup environment
    setup_environment
    
    # Check if virtual environment exists
    if [ ! -d "$BACKEND_DIR/venv" ] && [ ! -d "$BACKEND_DIR/.venv" ]; then
        print_status "Creating Python virtual environment for $ENVIRONMENT..."
        cd "$BACKEND_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Install environment-specific dependencies
        if [ "$ENVIRONMENT" = "development" ]; then
            pip install pytest pytest-asyncio black flake8 mypy
        fi
    fi
    
    # Activate virtual environment and start backend
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Build uvicorn command with environment-specific options
    local uvicorn_cmd="python -m uvicorn main:app --host $BACKEND_HOST --port $BACKEND_PORT --log-level $BACKEND_LOG_LEVEL"
    
    if [ "$ENABLE_HOT_RELOAD" = "true" ]; then
        uvicorn_cmd="$uvicorn_cmd --reload"
        print_debug "Hot reload enabled for $ENVIRONMENT"
    fi
    
    print_status "Starting FastAPI backend: $uvicorn_cmd"
    print_status "Backend logs: $BACKEND_LOG"
    
    # Start with comprehensive logging
    {
        echo "=========================================="
        echo "AA Virtual Backend - $ENVIRONMENT Environment"
        echo "Started: $(date)"
        echo "Command: $uvicorn_cmd"
        echo "PID: $$"
        echo "Environment Variables:"
        env | grep -E "(ENVIRONMENT|DATABASE|LOG_LEVEL|PORT|HOST)" | sort
        echo "=========================================="
        echo ""
    } > "$BACKEND_LOG"
    
    nohup $uvicorn_cmd >> "$BACKEND_LOG" 2>&1 &
    local backend_pid=$!
    echo "$backend_pid" > "$BACKEND_PID"
    
    # Log startup information
    log_with_env "INFO" "Backend started with PID $backend_pid in $ENVIRONMENT mode"
    
    # Wait and verify startup
    local attempts=0
    local max_attempts=10
    
    while [ $attempts -lt $max_attempts ]; do
        sleep 1
        if is_backend_running && check_port $BACKEND_PORT; then
            print_success "Backend started successfully (PID: $backend_pid)"
            print_status "Backend API: http://$BACKEND_HOST:$BACKEND_PORT"
            print_status "API Documentation: http://$BACKEND_HOST:$BACKEND_PORT/docs"
            print_status "Health Check: http://$BACKEND_HOST:$BACKEND_PORT/health"
            return 0
        fi
        attempts=$((attempts + 1))
    done
    
    print_error "Backend failed to start after $max_attempts attempts"
    print_error "Check logs: $BACKEND_LOG"
    return 1
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend service in $ENVIRONMENT mode..."
    
    if is_frontend_running; then
        local pid=$(cat "$FRONTEND_PID")
        print_warning "Frontend is already running (PID: $pid)"
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
        print_status "Installing frontend dependencies for $ENVIRONMENT..."
        cd "$FRONTEND_DIR"
        npm install
        
        # Install environment-specific dependencies
        if [ "$ENVIRONMENT" = "development" ]; then
            npm install --save-dev @types/node typescript eslint prettier
        fi
    fi
    
    # Start frontend
    cd "$FRONTEND_DIR"
    
    # Set environment variables
    export NODE_ENV=$ENVIRONMENT
    export NEXT_PUBLIC_ENVIRONMENT=$ENVIRONMENT
    export NEXT_PUBLIC_API_URL="http://$BACKEND_HOST:$BACKEND_PORT"
    
    local npm_cmd="npm run dev"
    if [ "$ENVIRONMENT" = "production" ]; then
        npm_cmd="npm run build && npm start"
    fi
    
    print_status "Starting Next.js frontend: $npm_cmd"
    print_status "Frontend logs: $FRONTEND_LOG"
    
    # Start with comprehensive logging
    {
        echo "=========================================="
        echo "AA Virtual Frontend - $ENVIRONMENT Environment"
        echo "Started: $(date)"
        echo "Command: $npm_cmd"
        echo "PID: $$"
        echo "Environment Variables:"
        env | grep -E "(NODE_ENV|NEXT_PUBLIC|PORT)" | sort
        echo "=========================================="
        echo ""
    } > "$FRONTEND_LOG"
    
    nohup $npm_cmd >> "$FRONTEND_LOG" 2>&1 &
    local frontend_pid=$!
    echo "$frontend_pid" > "$FRONTEND_PID"
    
    # Log startup information
    log_with_env "INFO" "Frontend started with PID $frontend_pid in $ENVIRONMENT mode"
    
    # Wait and verify startup
    local attempts=0
    local max_attempts=15
    
    while [ $attempts -lt $max_attempts ]; do
        sleep 2
        if is_frontend_running && check_port $FRONTEND_PORT; then
            print_success "Frontend started successfully (PID: $frontend_pid)"
            print_status "Frontend URL: http://localhost:$FRONTEND_PORT"
            return 0
        fi
        attempts=$((attempts + 1))
    done
    
    print_error "Frontend failed to start after $max_attempts attempts"
    print_error "Check logs: $FRONTEND_LOG"
    return 1
}

# Function to stop backend
stop_backend() {
    print_status "Stopping backend service in $ENVIRONMENT mode..."
    
    if [ -f "$BACKEND_PID" ]; then
        local pid=$(cat "$BACKEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_debug "Sending SIGTERM to backend process $pid"
            kill "$pid" 2>/dev/null || true
            sleep 3
            
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Force killing backend process $pid"
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            log_with_env "INFO" "Backend stopped (PID: $pid)"
            print_success "Backend stopped successfully"
        else
            print_warning "Backend process not found"
        fi
        rm -f "$BACKEND_PID"
    else
        print_warning "No backend PID file found for $ENVIRONMENT"
    fi
    
    # Also kill any process using the backend port
    local port_pid=$(get_pid_by_port $BACKEND_PORT)
    if [ -n "$port_pid" ]; then
        print_debug "Killing process using port $BACKEND_PORT (PID: $port_pid)"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

# Function to stop frontend
stop_frontend() {
    print_status "Stopping frontend service in $ENVIRONMENT mode..."
    
    if [ -f "$FRONTEND_PID" ]; then
        local pid=$(cat "$FRONTEND_PID")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_debug "Sending SIGTERM to frontend process $pid"
            kill "$pid" 2>/dev/null || true
            sleep 3
            
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Force killing frontend process $pid"
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            log_with_env "INFO" "Frontend stopped (PID: $pid)"
            print_success "Frontend stopped successfully"
        else
            print_warning "Frontend process not found"
        fi
        rm -f "$FRONTEND_PID"
    else
        print_warning "No frontend PID file found for $ENVIRONMENT"
    fi
    
    # Also kill any process using the frontend port
    local port_pid=$(get_pid_by_port $FRONTEND_PORT)
    if [ -n "$port_pid" ]; then
        print_debug "Killing process using port $FRONTEND_PORT (PID: $port_pid)"
        kill -9 "$port_pid" 2>/dev/null || true
    fi
}

# Function to show status
show_status() {
    print_environment_info
    
    print_status "Service Status:"
    echo
    
    # Backend status
    if is_backend_running; then
        local backend_pid=$(cat "$BACKEND_PID")
        print_success "Backend: Running (PID: $backend_pid)"
        print_status "  URL: http://$BACKEND_HOST:$BACKEND_PORT"
        print_status "  Docs: http://$BACKEND_HOST:$BACKEND_PORT/docs"
        print_status "  Logs: $BACKEND_LOG"
        
        # Check health
        if command -v curl >/dev/null 2>&1; then
            if curl -s "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1; then
                print_success "  Health: OK"
            else
                print_warning "  Health: Unhealthy"
            fi
        fi
    else
        print_error "Backend: Not running"
    fi
    
    # Frontend status
    if is_frontend_running; then
        local frontend_pid=$(cat "$FRONTEND_PID")
        print_success "Frontend: Running (PID: $frontend_pid)"
        print_status "  URL: http://localhost:$FRONTEND_PORT"
        print_status "  Logs: $FRONTEND_LOG"
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
    
    echo
    print_status "Log Files:"
    print_status "  Service Manager: $SERVICE_LOG"
    print_status "  Backend: $BACKEND_LOG"
    print_status "  Frontend: $FRONTEND_LOG"
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend")
            if [ -f "$BACKEND_LOG" ]; then
                print_status "Backend logs ($ENVIRONMENT):"
                echo -e "${CYAN}==========================================${NC}"
                tail -f "$BACKEND_LOG"
            else
                print_warning "Backend log file not found: $BACKEND_LOG"
            fi
            ;;
        "frontend")
            if [ -f "$FRONTEND_LOG" ]; then
                print_status "Frontend logs ($ENVIRONMENT):"
                echo -e "${CYAN}==========================================${NC}"
                tail -f "$FRONTEND_LOG"
            else
                print_warning "Frontend log file not found: $FRONTEND_LOG"
            fi
            ;;
        "service")
            if [ -f "$SERVICE_LOG" ]; then
                print_status "Service manager logs ($ENVIRONMENT):"
                echo -e "${CYAN}==========================================${NC}"
                tail -f "$SERVICE_LOG"
            else
                print_warning "Service manager log file not found: $SERVICE_LOG"
            fi
            ;;
        *)
            print_error "Usage: $0 $ENVIRONMENT logs [backend|frontend|service]"
            exit 1
            ;;
    esac
}

# Function to setup development environment
setup_dev() {
    print_status "Setting up $ENVIRONMENT environment..."
    
    # Create directories
    mkdir -p "$LOGS_DIR" "$PID_DIR"
    
    # Backend setup
    print_status "Setting up backend for $ENVIRONMENT..."
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Environment-specific dependencies
        case $ENVIRONMENT in
            "development")
                pip install pytest pytest-asyncio black flake8 mypy
                ;;
            "staging")
                pip install pytest
                ;;
            "production")
                pip install gunicorn
                ;;
        esac
        
        print_success "Backend dependencies installed for $ENVIRONMENT"
    else
        print_warning "Backend virtual environment already exists"
    fi
    
    # Frontend setup
    print_status "Setting up frontend for $ENVIRONMENT..."
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        
        # Environment-specific dependencies
        case $ENVIRONMENT in
            "development")
                npm install --save-dev @types/node typescript eslint prettier
                ;;
            "production")
                npm install --save-dev @types/node typescript
                ;;
        esac
        
        print_success "Frontend dependencies installed for $ENVIRONMENT"
    else
        print_warning "Frontend dependencies already installed"
    fi
    
    # Setup environment configuration
    setup_environment
    
    print_success "$ENVIRONMENT environment setup completed!"
}

# Function to show help
show_help() {
    echo "AA Virtual Enhanced Service Manager"
    echo
    echo "Usage: $0 [ENVIRONMENT] [COMMAND] [SERVICE]"
    echo
    echo "Environments:"
    echo "  development (default)  - Development environment with hot reload"
    echo "  staging               - Staging environment for testing"
    echo "  production            - Production environment"
    echo
    echo "Commands:"
    echo "  start [backend|frontend|all]  Start services (default: all)"
    echo "  stop [backend|frontend|all]   Stop services (default: all)"
    echo "  restart [backend|frontend|all] Restart services (default: all)"
    echo "  status                        Show service status"
    echo "  logs [backend|frontend|service] Show service logs"
    echo "  setup                         Setup environment"
    echo "  cleanup                       Stop all services and cleanup"
    echo "  help                          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 development start                      Start all services in development"
    echo "  $0 staging start backend                  Start only backend in staging"
    echo "  $0 production stop frontend               Stop only frontend in production"
    echo "  $0 development status                     Show development status"
    echo "  $0 staging logs backend                   Follow staging backend logs"
    echo "  $0 production setup                       Setup production environment"
}

# Main script logic
main() {
    local command=$1
    local service=$2
    
    # Initialize logging
    log_with_env "INFO" "Service manager started for $ENVIRONMENT environment"
    
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
            log_with_env "INFO" "Cleaning up $ENVIRONMENT environment"
            stop_backend
            stop_frontend
            print_success "Cleanup completed for $ENVIRONMENT"
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
    
    log_with_env "INFO" "Service manager command completed: $command $service"
}

# Handle Ctrl+C gracefully
trap 'log_with_env "INFO" "Service manager interrupted by user"; cleanup; exit 130' INT

# Run main function with all arguments
main "$@"
