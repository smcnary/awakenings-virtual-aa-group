@echo off
setlocal enabledelayedexpansion

REM AA Virtual Service Manager for Windows
REM This script manages starting and stopping services for the AA Virtual platform

set "REPO_ROOT=%~dp0.."
set "BACKEND_DIR=%REPO_ROOT%\backend"
set "FRONTEND_DIR=%REPO_ROOT%\frontend"
set "PID_DIR=%REPO_ROOT%\.pids"

REM Create PID directory if it doesn't exist
if not exist "%PID_DIR%" mkdir "%PID_DIR%"

REM PID files
set "BACKEND_PID=%PID_DIR%\backend.pid"
set "FRONTEND_PID=%PID_DIR%\frontend.pid"

REM Service configurations
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"
set "BACKEND_HOST=127.0.0.1"

REM Colors (basic Windows colors)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--help" goto show_help

if "%1"=="setup" goto setup_dev
if "%1"=="status" goto show_status
if "%1"=="start" goto start_services
if "%1"=="stop" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="cleanup" goto cleanup_services
if "%1"=="logs" goto show_logs

echo %RED%[ERROR]%NC% Unknown command: %1
goto show_help

:show_help
echo AA Virtual Service Manager for Windows
echo.
echo Usage: %~nx0 [COMMAND] [SERVICE]
echo.
echo Commands:
echo   start [backend^|frontend^|all]  Start services (default: all)
echo   stop [backend^|frontend^|all]   Stop services (default: all)
echo   restart [backend^|frontend^|all] Restart services (default: all)
echo   status                        Show service status
echo   logs [backend^|frontend]       Show service logs
echo   setup                         Setup development environment
echo   cleanup                       Stop all services and cleanup
echo   help                          Show this help message
echo.
echo Examples:
echo   %~nx0 start                      Start all services
echo   %~nx0 start backend              Start only backend
echo   %~nx0 stop frontend              Stop only frontend
echo   %~nx0 status                     Show current status
goto end

:setup_dev
echo %BLUE%[INFO]%NC% Setting up development environment...

REM Create logs directory
if not exist "%REPO_ROOT%\logs" mkdir "%REPO_ROOT%\logs"

REM Backend setup
echo %BLUE%[INFO]%NC% Setting up backend...
cd /d "%BACKEND_DIR%"

if not exist "venv" (
    echo %BLUE%[INFO]%NC% Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo %GREEN%[SUCCESS]%NC% Backend dependencies installed
) else (
    echo %YELLOW%[WARNING]%NC% Backend virtual environment already exists
)

REM Frontend setup
echo %BLUE%[INFO]%NC% Setting up frontend...
cd /d "%FRONTEND_DIR%"

if not exist "node_modules" (
    echo %BLUE%[INFO]%NC% Installing frontend dependencies...
    npm install
    echo %GREEN%[SUCCESS]%NC% Frontend dependencies installed
) else (
    echo %YELLOW%[WARNING]%NC% Frontend dependencies already installed
)

echo %GREEN%[SUCCESS]%NC% Development environment setup completed!
goto end

:show_status
echo %BLUE%[INFO]%NC% Service Status:
echo.

REM Check backend
if exist "%BACKEND_PID%" (
    set /p backend_pid=<"%BACKEND_PID%"
    tasklist /FI "PID eq !backend_pid!" 2>NUL | find /I "!backend_pid!" >NUL
    if !errorlevel! equ 0 (
        echo %GREEN%[SUCCESS]%NC% Backend: Running (PID: !backend_pid!)
        echo %BLUE%[INFO]%NC%   URL: http://%BACKEND_HOST%:%BACKEND_PORT%
        echo %BLUE%[INFO]%NC%   Docs: http://%BACKEND_HOST%:%BACKEND_PORT%/docs
    ) else (
        echo %RED%[ERROR]%NC% Backend: Not running
        del "%BACKEND_PID%" 2>NUL
    )
) else (
    echo %RED%[ERROR]%NC% Backend: Not running
)

REM Check frontend
if exist "%FRONTEND_PID%" (
    set /p frontend_pid=<"%FRONTEND_PID%"
    tasklist /FI "PID eq !frontend_pid!" 2>NUL | find /I "!frontend_pid!" >NUL
    if !errorlevel! equ 0 (
        echo %GREEN%[SUCCESS]%NC% Frontend: Running (PID: !frontend_pid!)
        echo %BLUE%[INFO]%NC%   URL: http://localhost:%FRONTEND_PORT%
    ) else (
        echo %RED%[ERROR]%NC% Frontend: Not running
        del "%FRONTEND_PID%" 2>NUL
    )
) else (
    echo %RED%[ERROR]%NC% Frontend: Not running
)

echo.
echo %BLUE%[INFO]%NC% Port Status:
netstat -an | find ":%BACKEND_PORT% " >NUL 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%[SUCCESS]%NC% Port %BACKEND_PORT%: In use
) else (
    echo %YELLOW%[WARNING]%NC% Port %BACKEND_PORT%: Available
)

netstat -an | find ":%FRONTEND_PORT% " >NUL 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%[SUCCESS]%NC% Port %FRONTEND_PORT%: In use
) else (
    echo %YELLOW%[WARNING]%NC% Port %FRONTEND_PORT%: Available
)
goto end

:start_services
set "service=%2"
if "%service%"=="" set "service=all"

if "%service%"=="backend" goto start_backend
if "%service%"=="frontend" goto start_frontend
if "%service%"=="all" goto start_all

echo %RED%[ERROR]%NC% Invalid service: %service%
echo %RED%[ERROR]%NC% Use: backend, frontend, or all
goto end

:start_all
call :start_backend
call :start_frontend
goto end

:start_backend
echo %BLUE%[INFO]%NC% Starting backend service...

if exist "%BACKEND_PID%" (
    set /p backend_pid=<"%BACKEND_PID%"
    tasklist /FI "PID eq !backend_pid!" 2>NUL | find /I "!backend_pid!" >NUL
    if !errorlevel! equ 0 (
        echo %YELLOW%[WARNING]%NC% Backend is already running (PID: !backend_pid!)
        goto end
    ) else (
        del "%BACKEND_PID%" 2>NUL
    )
)

REM Check if port is in use
netstat -an | find ":%BACKEND_PORT% " >NUL 2>&1
if !errorlevel! equ 0 (
    echo %YELLOW%[WARNING]%NC% Port %BACKEND_PORT% is already in use
    echo %YELLOW%[WARNING]%NC% Please stop the service using that port first
    goto end
)

REM Activate virtual environment and start backend
cd /d "%BACKEND_DIR%"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo %BLUE%[INFO]%NC% Starting FastAPI backend on %BACKEND_HOST%:%BACKEND_PORT%...
    start /B "" python -m uvicorn main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload > "%REPO_ROOT%\logs\backend.log" 2>&1
    timeout /t 3 /nobreak >NUL
    for /f "tokens=2" %%i in ('netstat -ano ^| find ":%BACKEND_PORT% "') do (
        echo %%i > "%BACKEND_PID%"
        echo %GREEN%[SUCCESS]%NC% Backend started successfully (PID: %%i)
        echo %BLUE%[INFO]%NC% Backend API available at: http://%BACKEND_HOST%:%BACKEND_PORT%
        echo %BLUE%[INFO]%NC% API documentation at: http://%BACKEND_HOST%:%BACKEND_PORT%/docs
    )
) else (
    echo %RED%[ERROR]%NC% Backend virtual environment not found. Run 'setup' first.
)
goto end

:start_frontend
echo %BLUE%[INFO]%NC% Starting frontend service...

if exist "%FRONTEND_PID%" (
    set /p frontend_pid=<"%FRONTEND_PID%"
    tasklist /FI "PID eq !frontend_pid!" 2>NUL | find /I "!frontend_pid!" >NUL
    if !errorlevel! equ 0 (
        echo %YELLOW%[WARNING]%NC% Frontend is already running (PID: !frontend_pid!)
        goto end
    ) else (
        del "%FRONTEND_PID%" 2>NUL
    )
)

REM Check if port is in use
netstat -an | find ":%FRONTEND_PORT% " >NUL 2>&1
if !errorlevel! equ 0 (
    echo %YELLOW%[WARNING]%NC% Port %FRONTEND_PORT% is already in use
    echo %YELLOW%[WARNING]%NC% Please stop the service using that port first
    goto end
)

REM Start frontend
cd /d "%FRONTEND_DIR%"
if exist "node_modules" (
    echo %BLUE%[INFO]%NC% Starting Next.js frontend on port %FRONTEND_PORT%...
    start /B "" npm run dev > "%REPO_ROOT%\logs\frontend.log" 2>&1
    timeout /t 5 /nobreak >NUL
    for /f "tokens=2" %%i in ('netstat -ano ^| find ":%FRONTEND_PORT% "') do (
        echo %%i > "%FRONTEND_PID%"
        echo %GREEN%[SUCCESS]%NC% Frontend started successfully (PID: %%i)
        echo %BLUE%[INFO]%NC% Frontend available at: http://localhost:%FRONTEND_PORT%
    )
) else (
    echo %RED%[ERROR]%NC% Frontend dependencies not found. Run 'setup' first.
)
goto end

:stop_services
set "service=%2"
if "%service%"=="" set "service=all"

if "%service%"=="backend" goto stop_backend
if "%service%"=="frontend" goto stop_frontend
if "%service%"=="all" goto stop_all

echo %RED%[ERROR]%NC% Invalid service: %service%
echo %RED%[ERROR]%NC% Use: backend, frontend, or all
goto end

:stop_all
call :stop_backend
call :stop_frontend
goto end

:stop_backend
echo %BLUE%[INFO]%NC% Stopping backend service...

if exist "%BACKEND_PID%" (
    set /p backend_pid=<"%BACKEND_PID%"
    tasklist /FI "PID eq !backend_pid!" 2>NUL | find /I "!backend_pid!" >NUL
    if !errorlevel! equ 0 (
        taskkill /PID !backend_pid! /F >NUL 2>&1
        echo %GREEN%[SUCCESS]%NC% Backend stopped successfully
    ) else (
        echo %YELLOW%[WARNING]%NC% Backend process not found
    )
    del "%BACKEND_PID%" 2>NUL
) else (
    echo %YELLOW%[WARNING]%NC% No backend PID file found
)

REM Also kill any process using the backend port
for /f "tokens=5" %%i in ('netstat -ano ^| find ":%BACKEND_PORT% "') do (
    taskkill /PID %%i /F >NUL 2>&1
)
goto end

:stop_frontend
echo %BLUE%[INFO]%NC% Stopping frontend service...

if exist "%FRONTEND_PID%" (
    set /p frontend_pid=<"%FRONTEND_PID%"
    tasklist /FI "PID eq !frontend_pid!" 2>NUL | find /I "!frontend_pid!" >NUL
    if !errorlevel! equ 0 (
        taskkill /PID !frontend_pid! /F >NUL 2>&1
        echo %GREEN%[SUCCESS]%NC% Frontend stopped successfully
    ) else (
        echo %YELLOW%[WARNING]%NC% Frontend process not found
    )
    del "%FRONTEND_PID%" 2>NUL
) else (
    echo %YELLOW%[WARNING]%NC% No frontend PID file found
)

REM Also kill any process using the frontend port
for /f "tokens=5" %%i in ('netstat -ano ^| find ":%FRONTEND_PORT% "') do (
    taskkill /PID %%i /F >NUL 2>&1
)
goto end

:restart_services
set "service=%2"
if "%service%"=="" set "service=all"

if "%service%"=="backend" (
    call :stop_backend
    timeout /t 2 /nobreak >NUL
    call :start_backend
)
if "%service%"=="frontend" (
    call :stop_frontend
    timeout /t 2 /nobreak >NUL
    call :start_frontend
)
if "%service%"=="all" (
    call :stop_backend
    call :stop_frontend
    timeout /t 3 /nobreak >NUL
    call :start_backend
    call :start_frontend
)
goto end

:show_logs
set "service=%2"
if "%service%"=="backend" (
    if exist "%REPO_ROOT%\logs\backend.log" (
        echo %BLUE%[INFO]%NC% Backend logs:
        type "%REPO_ROOT%\logs\backend.log"
    ) else (
        echo %YELLOW%[WARNING]%NC% Backend log file not found
    )
)
if "%service%"=="frontend" (
    if exist "%REPO_ROOT%\logs\frontend.log" (
        echo %BLUE%[INFO]%NC% Frontend logs:
        type "%REPO_ROOT%\logs\frontend.log"
    ) else (
        echo %YELLOW%[WARNING]%NC% Frontend log file not found
    )
)
if "%service%"=="" (
    echo %RED%[ERROR]%NC% Usage: %~nx0 logs [backend^|frontend]
)
goto end

:cleanup_services
echo %BLUE%[INFO]%NC% Cleaning up...
call :stop_backend
call :stop_frontend
echo %GREEN%[SUCCESS]%NC% Cleanup completed
goto end

:end
endlocal
