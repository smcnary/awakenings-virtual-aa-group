#!/bin/bash

# AA Virtual Test & Debug Suite
# Comprehensive testing and debugging tools for all services

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
LOGS_DIR="$REPO_ROOT/logs"
TEST_DIR="$REPO_ROOT/tests"
RESULTS_DIR="$REPO_ROOT/test-results"

# Load configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo -e "${RED}[ERROR]${NC} Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Function to check required dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    if ! command -v curl >/dev/null 2>&1; then
        missing_deps+=("curl")
    fi
    
    if ! command -v jq >/dev/null 2>&1; then
        missing_deps+=("jq")
    fi
    
    if ! command -v bc >/dev/null 2>&1; then
        missing_deps+=("bc")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}[ERROR]${NC} Missing required dependencies: ${missing_deps[*]}"
        echo -e "${YELLOW}[INFO]${NC} Please install missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            case $dep in
                "curl")
                    echo "  - curl: apt-get install curl (Ubuntu/Debian) or brew install curl (macOS)"
                    ;;
                "jq")
                    echo "  - jq: apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
                    ;;
                "bc")
                    echo "  - bc: apt-get install bc (Ubuntu/Debian) or brew install bc (macOS)"
                    ;;
            esac
        done
        exit 1
    fi
}

# Check dependencies at startup
check_dependencies

# Environment setup
ENVIRONMENT=${1:-development}
if [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "dev" ]; then
    ENV_PREFIX="DEV"
elif [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "stage" ]; then
    ENV_PREFIX="STAGING"
elif [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "prod" ]; then
    ENV_PREFIX="PROD"
else
    echo -e "${RED}[ERROR]${NC} Invalid environment: $ENVIRONMENT"
    echo -e "${YELLOW}[INFO]${NC} Valid environments: development, staging, production"
    exit 1
fi

# Set environment-specific variables
BACKEND_PORT=$(eval echo \$${ENV_PREFIX}_BACKEND_PORT)
FRONTEND_PORT=$(eval echo \$${ENV_PREFIX}_FRONTEND_PORT)
BACKEND_HOST=$(eval echo \$${ENV_PREFIX}_BACKEND_HOST)

# Create directories
mkdir -p "$LOGS_DIR" "$TEST_DIR" "$RESULTS_DIR"

# Test result files
API_TEST_RESULTS="$RESULTS_DIR/api-tests-$(date +%Y%m%d-%H%M%S).json"
INTEGRATION_TEST_RESULTS="$RESULTS_DIR/integration-tests-$(date +%Y%m%d-%H%M%S).json"
PERFORMANCE_TEST_RESULTS="$RESULTS_DIR/performance-tests-$(date +%Y%m%d-%H%M%S).json"
USER_INTERACTION_LOG="$LOGS_DIR/user-interactions-$(date +%Y%m%d-%H%M%S).log"

# Function to log with timestamp
log_test() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message"
    echo "[$timestamp] [$level] $message" >> "$USER_INTERACTION_LOG"
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log_test "INFO" "$1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log_test "SUCCESS" "$1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log_test "WARNING" "$1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log_test "ERROR" "$1"
}

print_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
    log_test "DEBUG" "$1"
}

# Function to check if services are running
check_services() {
    print_status "Checking if services are running..."
    
    local backend_running=false
    local frontend_running=false
    
    # Check backend
    if curl -s "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1; then
        backend_running=true
        print_success "Backend is running on $BACKEND_HOST:$BACKEND_PORT"
    else
        print_error "Backend is not responding on $BACKEND_HOST:$BACKEND_PORT"
    fi
    
    # Check frontend
    if curl -s "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
        frontend_running=true
        print_success "Frontend is running on localhost:$FRONTEND_PORT"
    else
        print_error "Frontend is not responding on localhost:$FRONTEND_PORT"
    fi
    
    if [ "$backend_running" = false ] || [ "$frontend_running" = false ]; then
        print_error "Some services are not running. Please start them first."
        return 1
    fi
    
    return 0
}

# Function to test API endpoints
test_api_endpoints() {
    print_status "Testing API endpoints..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    local test_results=()
    
    # Define test cases
    declare -A api_tests=(
        ["GET /"]="Root endpoint"
        ["GET /health"]="Health check"
        ["GET /docs"]="API documentation"
        ["GET /api/v1/group/"]="Get group info"
        ["GET /api/v1/trusted-servants/"]="Get trusted servants"
        ["GET /api/v1/trusted-servants/positions"]="Get service positions"
        ["GET /api/v1/meetings/"]="Get meetings"
        ["GET /api/v1/resources/"]="Get resources"
        ["GET /api/v1/auth/anonymous"]="Anonymous account creation"
        ["POST /api/v1/auth/anonymous"]="Anonymous account creation (POST)"
        ["GET /api/v1/chatbot/resources"]="Get chatbot resources"
    )
    
    # Test each endpoint
    for endpoint in "${!api_tests[@]}"; do
        local method=$(echo $endpoint | cut -d' ' -f1)
        local path=$(echo $endpoint | cut -d' ' -f2)
        local description="${api_tests[$endpoint]}"
        
        print_debug "Testing $method $path - $description"
        
        local url="$api_base$path"
        local start_time=$(date +%s.%N)
        
        if [ "$method" = "GET" ]; then
            local response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$url" || echo "CURL_ERROR")
        else
            local response=$(curl -s -X "$method" -w "\n%{http_code}\n%{time_total}" "$url" || echo "CURL_ERROR")
        fi
        
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        
        if [ "$response" = "CURL_ERROR" ]; then
            print_error "Failed to connect to $url"
            test_results+=("{\"endpoint\":\"$endpoint\",\"description\":\"$description\",\"status\":\"FAILED\",\"error\":\"Connection failed\",\"duration\":$duration}")
        else
            local http_code=$(echo "$response" | tail -n 2 | head -n 1)
            local time_total=$(echo "$response" | tail -n 1)
            local body=$(echo "$response" | head -n -2)
            
            if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
                print_success "$method $path - $description (HTTP $http_code, ${time_total}s)"
                test_results+=("{\"endpoint\":\"$endpoint\",\"description\":\"$description\",\"status\":\"PASSED\",\"http_code\":$http_code,\"duration\":$duration}")
            else
                print_warning "$method $path - $description (HTTP $http_code, ${time_total}s)"
                test_results+=("{\"endpoint\":\"$endpoint\",\"description\":\"$description\",\"status\":\"FAILED\",\"http_code\":$http_code,\"duration\":$duration}")
            fi
        fi
    done
    
    # Save results to JSON file
    echo "[" > "$API_TEST_RESULTS"
    local first=true
    for result in "${test_results[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$API_TEST_RESULTS"
        fi
        echo "$result" >> "$API_TEST_RESULTS"
    done
    echo "]" >> "$API_TEST_RESULTS"
    
    print_success "API test results saved to: $API_TEST_RESULTS"
}

# Function to test database connectivity
test_database() {
    print_status "Testing database connectivity..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    
    # Test endpoints that require database access
    local db_endpoints=(
        "GET /api/v1/group/"
        "GET /api/v1/trusted-servants/"
        "GET /api/v1/meetings/"
        "GET /api/v1/resources/"
    )
    
    local db_working=true
    
    for endpoint in "${db_endpoints[@]}"; do
        local method=$(echo $endpoint | cut -d' ' -f1)
        local path=$(echo $endpoint | cut -d' ' -f2)
        
        print_debug "Testing database endpoint: $method $path"
        
        local response=$(curl -s -w "\n%{http_code}" "$api_base$path" || echo "CURL_ERROR")
        
        if [ "$response" = "CURL_ERROR" ]; then
            print_error "Database endpoint $path failed to connect"
            db_working=false
        else
            local http_code=$(echo "$response" | tail -n 1)
            if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 500 ]; then
                print_success "Database endpoint $path responding (HTTP $http_code)"
            else
                print_warning "Database endpoint $path returned HTTP $http_code"
                if [ "$http_code" -ge 500 ]; then
                    db_working=false
                fi
            fi
        fi
    done
    
    if [ "$db_working" = true ]; then
        print_success "Database connectivity test passed"
    else
        print_error "Database connectivity issues detected"
    fi
}

# Function to test authentication flows
test_authentication() {
    print_status "Testing authentication flows..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    local auth_token=""
    
    # Test anonymous account creation
    print_debug "Testing anonymous account creation..."
    local anonymous_response=$(curl -s -X POST "$api_base/api/v1/auth/anonymous" \
        -H "Content-Type: application/json" \
        -w "\n%{http_code}")
    
    local anonymous_http_code=$(echo "$anonymous_response" | tail -n 1)
    local anonymous_body=$(echo "$anonymous_response" | head -n -1)
    
    if [ "$anonymous_http_code" = "200" ] || [ "$anonymous_http_code" = "201" ]; then
        print_success "Anonymous account creation works (HTTP $anonymous_http_code)"
        
        # Extract token from response
        auth_token=$(echo "$anonymous_body" | jq -r '.access_token' 2>/dev/null || echo "")
        
        if [ -n "$auth_token" ] && [ "$auth_token" != "null" ]; then
            print_success "Access token received: ${auth_token:0:20}..."
            
            # Test authenticated endpoints
            local auth_endpoints=(
                "GET /api/v1/auth/me"
                "GET /api/v1/members/profile"
            )
            
            for auth_endpoint in "${auth_endpoints[@]}"; do
                local method=$(echo $auth_endpoint | cut -d' ' -f1)
                local path=$(echo $auth_endpoint | cut -d' ' -f2)
                
                print_debug "Testing authenticated endpoint: $method $path"
                local auth_response=$(curl -s -H "Authorization: Bearer $auth_token" \
                    "$api_base$path" \
                    -w "\n%{http_code}")
                
                local auth_http_code=$(echo "$auth_response" | tail -n 1)
                local auth_body=$(echo "$auth_response" | head -n -1)
                
                if [ "$auth_http_code" = "200" ]; then
                    print_success "Authenticated endpoint $path works (HTTP $auth_http_code)"
                    if [ "$path" = "/api/v1/auth/me" ]; then
                        local user_role=$(echo "$auth_body" | jq -r '.role' 2>/dev/null || echo "Unknown")
                        print_debug "User role: $user_role"
                    fi
                else
                    print_warning "Authenticated endpoint $path failed (HTTP $auth_http_code)"
                fi
            done
            
            # Test token refresh if available
            print_debug "Testing token refresh..."
            local refresh_token=$(echo "$anonymous_body" | jq -r '.refresh_token' 2>/dev/null || echo "")
            if [ -n "$refresh_token" ] && [ "$refresh_token" != "null" ]; then
                local refresh_response=$(curl -s -X POST "$api_base/api/v1/auth/refresh" \
                    -H "Content-Type: application/json" \
                    -d "{\"refresh_token\":\"$refresh_token\"}" \
                    -w "\n%{http_code}")
                
                local refresh_http_code=$(echo "$refresh_response" | tail -n 1)
                if [ "$refresh_http_code" = "200" ]; then
                    print_success "Token refresh works (HTTP $refresh_http_code)"
                else
                    print_warning "Token refresh failed (HTTP $refresh_http_code)"
                fi
            fi
            
        else
            print_warning "No access token in response"
        fi
    else
        print_error "Anonymous account creation failed (HTTP $anonymous_http_code)"
        print_debug "Response: $anonymous_body"
    fi
    
    # Test authentication error handling
    print_debug "Testing authentication error handling..."
    local invalid_token_response=$(curl -s -H "Authorization: Bearer invalid_token" \
        "$api_base/api/v1/auth/me" \
        -w "\n%{http_code}")
    
    local invalid_http_code=$(echo "$invalid_token_response" | tail -n 1)
    if [ "$invalid_http_code" = "401" ] || [ "$invalid_http_code" = "403" ]; then
        print_success "Authentication error handling works (HTTP $invalid_http_code)"
    else
        print_warning "Authentication error handling unexpected (HTTP $invalid_http_code)"
    fi
}

# Function to test trusted servants functionality
test_trusted_servants() {
    print_status "Testing trusted servants functionality..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    
    # Test getting service positions
    print_debug "Testing service positions endpoint..."
    local positions_response=$(curl -s "$api_base/api/v1/trusted-servants/positions" -w "\n%{http_code}")
    local positions_http_code=$(echo "$positions_response" | tail -n 1)
    local positions_body=$(echo "$positions_response" | head -n -1)
    
    if [ "$positions_http_code" = "200" ]; then
        print_success "Service positions endpoint works (HTTP $positions_http_code)"
        local position_count=$(echo "$positions_body" | jq '. | length' 2>/dev/null || echo "0")
        print_debug "Found $position_count service positions"
    else
        print_error "Service positions endpoint failed (HTTP $positions_http_code)"
    fi
    
    # Test getting trusted servants
    print_debug "Testing trusted servants endpoint..."
    local servants_response=$(curl -s "$api_base/api/v1/trusted-servants/" -w "\n%{http_code}")
    local servants_http_code=$(echo "$servants_response" | tail -n 1)
    local servants_body=$(echo "$servants_response" | head -n -1)
    
    if [ "$servants_http_code" = "200" ]; then
        print_success "Trusted servants endpoint works (HTTP $servants_http_code)"
        local servant_count=$(echo "$servants_body" | jq '. | length' 2>/dev/null || echo "0")
        print_debug "Found $servant_count trusted servants"
    else
        print_error "Trusted servants endpoint failed (HTTP $servants_http_code)"
    fi
}

# Function to test chatbot functionality
test_chatbot() {
    print_status "Testing chatbot functionality..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    
    # Test chatbot resources endpoint
    print_debug "Testing chatbot resources endpoint..."
    local resources_response=$(curl -s "$api_base/api/v1/chatbot/resources" -w "\n%{http_code}")
    local resources_http_code=$(echo "$resources_response" | tail -n 1)
    local resources_body=$(echo "$resources_response" | head -n -1)
    
    if [ "$resources_http_code" = "200" ]; then
        print_success "Chatbot resources endpoint works (HTTP $resources_http_code)"
        local resource_count=$(echo "$resources_body" | jq '. | length' 2>/dev/null || echo "0")
        print_debug "Found $resource_count chatbot resources"
    else
        print_warning "Chatbot resources endpoint failed (HTTP $resources_http_code)"
    fi
    
    # Test chatbot chat endpoint with a simple message
    print_debug "Testing chatbot chat endpoint..."
    local chat_response=$(curl -s -X POST "$api_base/api/v1/chatbot/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, this is a test message", "session_id": "test-session-123"}' \
        -w "\n%{http_code}")
    
    local chat_http_code=$(echo "$chat_response" | tail -n 1)
    local chat_body=$(echo "$chat_response" | head -n -1)
    
    if [ "$chat_http_code" = "200" ]; then
        print_success "Chatbot chat endpoint works (HTTP $chat_http_code)"
        local response_message=$(echo "$chat_body" | jq -r '.response' 2>/dev/null || echo "No response")
        print_debug "Chatbot response: ${response_message:0:100}..."
    else
        print_warning "Chatbot chat endpoint failed (HTTP $chat_http_code)"
        print_debug "Response: $chat_body"
    fi
    
    # Test rate limiting (if implemented)
    print_debug "Testing chatbot rate limiting..."
    local rate_limit_working=true
    for i in {1..5}; do
        local rate_response=$(curl -s -X POST "$api_base/api/v1/chatbot/chat" \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"Rate limit test $i\", \"session_id\": \"rate-test-session\"}" \
            -w "\n%{http_code}")
        
        local rate_http_code=$(echo "$rate_response" | tail -n 1)
        if [ "$rate_http_code" = "429" ]; then
            print_success "Rate limiting is working (HTTP 429)"
            rate_limit_working=false
            break
        fi
    done
    
    if [ "$rate_limit_working" = true ]; then
        print_debug "Rate limiting not triggered or not implemented"
    fi
}

# Function to test admin endpoints (requires admin authentication)
test_admin_endpoints() {
    print_status "Testing admin endpoints..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    
    # First, we need to get an admin token or create an admin user
    print_debug "Attempting to test admin endpoints..."
    
    # Try to get users endpoint (admin only)
    print_debug "Testing admin users endpoint..."
    local users_response=$(curl -s "$api_base/api/v1/admin/users" -w "\n%{http_code}")
    local users_http_code=$(echo "$users_response" | tail -n 1)
    
    if [ "$users_http_code" = "401" ] || [ "$users_http_code" = "403" ]; then
        print_success "Admin endpoint properly protected (HTTP $users_http_code)"
    elif [ "$users_http_code" = "200" ]; then
        print_warning "Admin endpoint accessible without authentication (HTTP $users_http_code)"
        print_debug "This may indicate missing authentication middleware"
    else
        print_debug "Admin endpoint returned HTTP $users_http_code"
    fi
    
    # Test admin endpoints with invalid token
    print_debug "Testing admin endpoints with invalid token..."
    local admin_invalid_response=$(curl -s -H "Authorization: Bearer invalid_admin_token" \
        "$api_base/api/v1/admin/users" \
        -w "\n%{http_code}")
    
    local admin_invalid_http_code=$(echo "$admin_invalid_response" | tail -n 1)
    if [ "$admin_invalid_http_code" = "401" ] || [ "$admin_invalid_http_code" = "403" ]; then
        print_success "Admin endpoint properly rejects invalid tokens (HTTP $admin_invalid_http_code)"
    else
        print_warning "Admin endpoint unexpected response to invalid token (HTTP $admin_invalid_http_code)"
    fi
    
    # Test other admin endpoints
    local admin_endpoints=(
        "GET /api/v1/admin/users"
        "GET /api/v1/admin/users/stats"
    )
    
    for endpoint in "${admin_endpoints[@]}"; do
        local method=$(echo $endpoint | cut -d' ' -f1)
        local path=$(echo $endpoint | cut -d' ' -f2)
        
        print_debug "Testing admin endpoint: $method $path"
        local admin_response=$(curl -s "$api_base$path" -w "\n%{http_code}")
        local admin_http_code=$(echo "$admin_response" | tail -n 1)
        
        if [ "$admin_http_code" = "401" ] || [ "$admin_http_code" = "403" ]; then
            print_success "Admin endpoint $path properly protected (HTTP $admin_http_code)"
        else
            print_debug "Admin endpoint $path returned HTTP $admin_http_code"
        fi
    done
}

# Function to test frontend routes
test_frontend_routes() {
    print_status "Testing frontend routes..."
    
    local frontend_base="http://localhost:$FRONTEND_PORT"
    
    # Define frontend routes to test
    local routes=("/" "/trusted-servants" "/members" "/calendar" "/downloads" "/7th-tradition" "/login")
    
    for route in "${routes[@]}"; do
        print_debug "Testing frontend route: $route"
        
        local response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$frontend_base$route" || echo "CURL_ERROR")
        
        if [ "$response" = "CURL_ERROR" ]; then
            print_error "Failed to connect to $frontend_base$route"
        else
            local http_code=$(echo "$response" | tail -n 2 | head -n 1)
            local time_total=$(echo "$response" | tail -n 1)
            
            if [ "$http_code" = "200" ]; then
                print_success "Frontend route $route works (HTTP $http_code, ${time_total}s)"
                
                # Check for Next.js specific content
                local body=$(echo "$response" | head -n -2)
                if echo "$body" | grep -q "next.js\|_next\|__NEXT_DATA__" 2>/dev/null; then
                    print_debug "Next.js content detected on $route"
                fi
                
                # Check for React hydration
                if echo "$body" | grep -q "react\|React" 2>/dev/null; then
                    print_debug "React content detected on $route"
                fi
                
            else
                print_warning "Frontend route $route returned HTTP $http_code"
            fi
        fi
    done
    
    # Test frontend API proxy (if configured)
    print_debug "Testing frontend API proxy..."
    local proxy_response=$(curl -s -w "\n%{http_code}" "$frontend_base/api/health" || echo "CURL_ERROR")
    
    if [ "$proxy_response" != "CURL_ERROR" ]; then
        local proxy_http_code=$(echo "$proxy_response" | tail -n 1)
        if [ "$proxy_http_code" = "200" ]; then
            print_success "Frontend API proxy works (HTTP $proxy_http_code)"
        else
            print_debug "Frontend API proxy returned HTTP $proxy_http_code (may not be configured)"
        fi
    fi
}

# Function to test performance
test_performance() {
    print_status "Running performance tests..."
    
    local api_base="http://$BACKEND_HOST:$BACKEND_PORT"
    local frontend_base="http://localhost:$FRONTEND_PORT"
    
    # Test API performance
    print_debug "Testing API performance..."
    local api_times=()
    for i in {1..10}; do
        local start_time=$(date +%s.%N)
        curl -s "$api_base/health" >/dev/null
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        api_times+=($duration)
    done
    
    # Calculate average API response time
    local api_sum=0
    for time in "${api_times[@]}"; do
        api_sum=$(echo "$api_sum + $time" | bc -l 2>/dev/null || echo "$api_sum")
    done
    local api_avg=$(echo "scale=3; $api_sum / ${#api_times[@]}" | bc -l 2>/dev/null || echo "0")
    
    print_success "Average API response time: ${api_avg}s"
    
    # Test frontend performance
    print_debug "Testing frontend performance..."
    local frontend_times=()
    for i in {1..5}; do
        local start_time=$(date +%s.%N)
        curl -s "$frontend_base" >/dev/null
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        frontend_times+=($duration)
    done
    
    # Calculate average frontend response time
    local frontend_sum=0
    for time in "${frontend_times[@]}"; do
        frontend_sum=$(echo "$frontend_sum + $time" | bc -l 2>/dev/null || echo "$frontend_sum")
    done
    local frontend_avg=$(echo "scale=3; $frontend_sum / ${#frontend_times[@]}" | bc -l 2>/dev/null || echo "0")
    
    print_success "Average frontend response time: ${frontend_avg}s"
    
    # Save performance results
    cat > "$PERFORMANCE_TEST_RESULTS" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "environment": "$ENVIRONMENT",
    "api_performance": {
        "average_response_time": $api_avg,
        "test_count": ${#api_times[@]},
        "response_times": [$(IFS=','; echo "${api_times[*]}")]
    },
    "frontend_performance": {
        "average_response_time": $frontend_avg,
        "test_count": ${#frontend_times[@]},
        "response_times": [$(IFS=','; echo "${frontend_times[*]}")]
    }
}
EOF
    
    print_success "Performance test results saved to: $PERFORMANCE_TEST_RESULTS"
}

# Function to monitor logs in real-time
monitor_logs() {
    print_status "Starting real-time log monitoring..."
    print_status "Press Ctrl+C to stop monitoring"
    
    # Monitor multiple log files simultaneously
    if command -v multitail >/dev/null 2>&1; then
        multitail -cT ANSI \
            -l "tail -f $LOGS_DIR/backend-*.log" \
            -l "tail -f $LOGS_DIR/frontend-*.log" \
            -l "tail -f $LOGS_DIR/service-manager-*.log" \
            -l "tail -f $USER_INTERACTION_LOG"
    else
        print_warning "multitail not found, using simple tail. Install multitail for better log monitoring."
        tail -f "$LOGS_DIR"/*.log
    fi
}

# Function to check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # Check disk space
    local disk_usage=$(df -h "$REPO_ROOT" | tail -n 1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 80 ]; then
        print_success "Disk usage: ${disk_usage}% (healthy)"
    else
        print_warning "Disk usage: ${disk_usage}% (high)"
    fi
    
    # Check memory usage
    if command -v free >/dev/null 2>&1; then
        local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        if (( $(echo "$memory_usage < 80" | bc -l) )); then
            print_success "Memory usage: ${memory_usage}% (healthy)"
        else
            print_warning "Memory usage: ${memory_usage}% (high)"
        fi
    fi
    
    # Check if ports are available
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep -q ":$BACKEND_PORT "; then
            print_success "Backend port $BACKEND_PORT is in use"
        else
            print_warning "Backend port $BACKEND_PORT is not in use"
        fi
        
        if netstat -tuln | grep -q ":$FRONTEND_PORT "; then
            print_success "Frontend port $FRONTEND_PORT is in use"
        else
            print_warning "Frontend port $FRONTEND_PORT is not in use"
        fi
    fi
    
    # Check log file sizes
    if [ -d "$LOGS_DIR" ]; then
        local log_size=$(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1 || echo "0")
        print_debug "Log directory size: $log_size"
    fi
}

# Function to generate test report
generate_report() {
    print_status "Generating comprehensive test report..."
    
    local report_file="$RESULTS_DIR/test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# AA Virtual Test Report

**Generated:** $(date)
**Environment:** $ENVIRONMENT
**Backend:** $BACKEND_HOST:$BACKEND_PORT
**Frontend:** localhost:$FRONTEND_PORT

## Test Results Summary

### API Tests
- **Results File:** $API_TEST_RESULTS
- **Status:** $(if [ -f "$API_TEST_RESULTS" ]; then echo "Completed"; else echo "Failed"; fi)

### Performance Tests
- **Results File:** $PERFORMANCE_TEST_RESULTS
- **Status:** $(if [ -f "$PERFORMANCE_TEST_RESULTS" ]; then echo "Completed"; else echo "Failed"; fi)

### User Interaction Log
- **Log File:** $USER_INTERACTION_LOG
- **Status:** $(if [ -f "$USER_INTERACTION_LOG" ]; then echo "Active"; else echo "Not found"; fi)

## Service Status

### Backend
- **URL:** http://$BACKEND_HOST:$BACKEND_PORT
- **Health:** $(curl -s "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy")
- **API Docs:** http://$BACKEND_HOST:$BACKEND_PORT/docs

### Frontend
- **URL:** http://localhost:$FRONTEND_PORT
- **Status:** $(curl -s "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not responding")

## Log Files
- Backend: $LOGS_DIR/backend-*.log
- Frontend: $LOGS_DIR/frontend-*.log
- Service Manager: $LOGS_DIR/service-manager-*.log
- User Interactions: $USER_INTERACTION_LOG

## Quick Commands

### Start Services
\`\`\`bash
./scripts/enhanced-service-manager.sh $ENVIRONMENT start
\`\`\`

### Stop Services
\`\`\`bash
./scripts/enhanced-service-manager.sh $ENVIRONMENT stop
\`\`\`

### Monitor Logs
\`\`\`bash
./scripts/test-debug-suite.sh $ENVIRONMENT monitor
\`\`\`

### Run Tests
\`\`\`bash
./scripts/test-debug-suite.sh $ENVIRONMENT test
\`\`\`

EOF

    print_success "Test report generated: $report_file"
    
    # Open report if possible
    if command -v open >/dev/null 2>&1; then
        open "$report_file"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$report_file"
    fi
}

# Function to show help
show_help() {
    echo "AA Virtual Test & Debug Suite"
    echo
    echo "Usage: $0 [ENVIRONMENT] [COMMAND]"
    echo
    echo "Environments:"
    echo "  development (default)  - Development environment"
    echo "  staging               - Staging environment"
    echo "  production            - Production environment"
    echo
    echo "Commands:"
    echo "  check                 Check if services are running"
    echo "  health                Check services and system resources"
    echo "  test                  Run all tests (API, database, auth, chatbot, admin, frontend)"
    echo "  api                   Test API endpoints only"
    echo "  database|db           Test database connectivity only"
    echo "  auth                  Test authentication flows only"
    echo "  chatbot               Test chatbot functionality only"
    echo "  admin                 Test admin endpoint security only"
    echo "  frontend              Test frontend routes only"
    echo "  performance           Run performance tests"
    echo "  monitor               Monitor logs in real-time"
    echo "  report                Generate test report"
    echo "  all                   Run all tests and generate report"
    echo "  help                  Show this help message"
    echo
    echo "Examples:"
    echo "  $0 development check              Check if development services are running"
    echo "  $0 development health             Check services and system resources"
    echo "  $0 staging test                   Run all tests in staging"
    echo "  $0 production monitor             Monitor production logs"
    echo "  $0 development all                Run comprehensive testing suite"
    echo "  $0 development api                Test only API endpoints"
    echo "  $0 development auth               Test only authentication"
    echo "  $0 development chatbot            Test only chatbot functionality"
    echo "  $0 development admin              Test only admin endpoint security"
}

# Main function
main() {
    local command=$2  # Second argument is the command
    
    # Initialize logging
    log_test "INFO" "Test & Debug Suite started for $ENVIRONMENT environment"
    
    case $command in
        "check")
            check_services
            ;;
        "health")
            check_services
            check_system_resources
            ;;
        "test")
            check_services || exit 1
            test_api_endpoints
            test_database
            test_authentication
            test_trusted_servants
            test_chatbot
            test_admin_endpoints
            test_frontend_routes
            ;;
        "api")
            check_services || exit 1
            test_api_endpoints
            ;;
        "database"|"db")
            check_services || exit 1
            test_database
            ;;
        "auth")
            check_services || exit 1
            test_authentication
            ;;
        "chatbot")
            check_services || exit 1
            test_chatbot
            ;;
        "admin")
            check_services || exit 1
            test_admin_endpoints
            ;;
        "frontend")
            check_services || exit 1
            test_frontend_routes
            ;;
        "performance")
            check_services || exit 1
            test_performance
            ;;
        "monitor")
            monitor_logs
            ;;
        "report")
            generate_report
            ;;
        "all")
            check_services || exit 1
            test_api_endpoints
            test_database
            test_authentication
            test_trusted_servants
            test_chatbot
            test_admin_endpoints
            test_frontend_routes
            test_performance
            generate_report
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
    
    log_test "INFO" "Test & Debug Suite command completed: $command"
}

# Handle Ctrl+C gracefully
trap 'log_test "INFO" "Test & Debug Suite interrupted by user"; exit 130' INT

# Run main function
main "$@"
