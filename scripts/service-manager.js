#!/usr/bin/env node

/**
 * AA Virtual Service Manager
 * Cross-platform Node.js script to manage starting and stopping services
 */

const { spawn, exec, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Colors for output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

// Configuration
const REPO_ROOT = path.resolve(__dirname, '..');
const BACKEND_DIR = path.join(REPO_ROOT, 'backend');
const FRONTEND_DIR = path.join(REPO_ROOT, 'frontend');
const PID_DIR = path.join(REPO_ROOT, '.pids');
const LOGS_DIR = path.join(REPO_ROOT, 'logs');

// PID files
const BACKEND_PID = path.join(PID_DIR, 'backend.pid');
const FRONTEND_PID = path.join(PID_DIR, 'frontend.pid');

// Service configurations
const BACKEND_PORT = 8000;
const FRONTEND_PORT = 3000;
const BACKEND_HOST = '0.0.0.0';

// Ensure directories exist
if (!fs.existsSync(PID_DIR)) {
    fs.mkdirSync(PID_DIR, { recursive: true });
}
if (!fs.existsSync(LOGS_DIR)) {
    fs.mkdirSync(LOGS_DIR, { recursive: true });
}

// Utility functions
function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logInfo(message) {
    log(`[INFO] ${message}`, 'blue');
}

function logSuccess(message) {
    log(`[SUCCESS] ${message}`, 'green');
}

function logWarning(message) {
    log(`[WARNING] ${message}`, 'yellow');
}

function logError(message) {
    log(`[ERROR] ${message}`, 'red');
}

function isWindows() {
    return os.platform() === 'win32';
}

function isPortInUse(port) {
    try {
        const command = isWindows() 
            ? `netstat -an | find ":${port} "`
            : `lsof -Pi :${port} -sTCP:LISTEN -t`;
        
        execSync(command, { stdio: 'ignore' });
        return true;
    } catch (error) {
        return false;
    }
}

function getPidByPort(port) {
    try {
        const command = isWindows()
            ? `netstat -ano | find ":${port} "`
            : `lsof -ti :${port}`;
        
        const output = execSync(command, { encoding: 'utf8' });
        
        if (isWindows()) {
            const lines = output.trim().split('\n');
            for (const line of lines) {
                const parts = line.trim().split(/\s+/);
                if (parts.length >= 5) {
                    return parts[4];
                }
            }
        } else {
            return output.trim().split('\n')[0];
        }
        return null;
    } catch (error) {
        return null;
    }
}

function isProcessRunning(pid) {
    if (!pid) return false;
    
    try {
        if (isWindows()) {
            execSync(`tasklist /FI "PID eq ${pid}"`, { stdio: 'ignore' });
            return true;
        } else {
            process.kill(pid, 0);
            return true;
        }
    } catch (error) {
        return false;
    }
}

function isBackendRunning() {
    if (fs.existsSync(BACKEND_PID)) {
        const pid = fs.readFileSync(BACKEND_PID, 'utf8').trim();
        if (isProcessRunning(pid)) {
            return true;
        } else {
            fs.unlinkSync(BACKEND_PID);
            return false;
        }
    }
    return false;
}

function isFrontendRunning() {
    if (fs.existsSync(FRONTEND_PID)) {
        const pid = fs.readFileSync(FRONTEND_PID, 'utf8').trim();
        if (isProcessRunning(pid)) {
            return true;
        } else {
            fs.unlinkSync(FRONTEND_PID);
            return false;
        }
    }
    return false;
}

function killProcess(pid) {
    if (!pid) return;
    
    try {
        if (isWindows()) {
            execSync(`taskkill /PID ${pid} /F`, { stdio: 'ignore' });
        } else {
            process.kill(pid, 'SIGTERM');
            setTimeout(() => {
                try {
                    process.kill(pid, 'SIGKILL');
                } catch (e) {
                    // Process already dead
                }
            }, 2000);
        }
    } catch (error) {
        // Process might already be dead
    }
}

function startBackend() {
    logInfo('Starting backend service...');
    
    if (isBackendRunning()) {
        const pid = fs.readFileSync(BACKEND_PID, 'utf8').trim();
        logWarning(`Backend is already running (PID: ${pid})`);
        return;
    }
    
    if (isPortInUse(BACKEND_PORT)) {
        const pid = getPidByPort(BACKEND_PORT);
        logWarning(`Port ${BACKEND_PORT} is already in use (PID: ${pid})`);
        logWarning('Attempting to kill existing process...');
        killProcess(pid);
        
        // Wait for port to be free
        let attempts = 0;
        while (isPortInUse(BACKEND_PORT) && attempts < 10) {
            setTimeout(() => {}, 1000);
            attempts++;
        }
    }
    
    // Check if virtual environment exists
    const venvPath = path.join(BACKEND_DIR, 'venv');
    const venvPathAlt = path.join(BACKEND_DIR, '.venv');
    
    if (!fs.existsSync(venvPath) && !fs.existsSync(venvPathAlt)) {
        logInfo('Creating Python virtual environment...');
        try {
            execSync('python3 -m venv venv', { cwd: BACKEND_DIR, stdio: 'inherit' });
            
            const activateScript = isWindows() 
                ? path.join(venvPath, 'Scripts', 'activate.bat')
                : path.join(venvPath, 'bin', 'activate');
            
            execSync('python -m pip install --upgrade pip', { 
                cwd: BACKEND_DIR, 
                env: { ...process.env, PATH: `${path.join(venvPath, 'Scripts')};${process.env.PATH}` },
                stdio: 'inherit' 
            });
            
            execSync('pip install -r requirements.txt', { 
                cwd: BACKEND_DIR,
                env: { ...process.env, PATH: `${path.join(venvPath, 'Scripts')};${process.env.PATH}` },
                stdio: 'inherit' 
            });
        } catch (error) {
            logError('Failed to setup Python virtual environment');
            return;
        }
    }
    
    // Start backend
    const logFile = path.join(LOGS_DIR, 'backend.log');
    const command = isWindows() ? 'python' : 'python3';
    const args = ['-m', 'uvicorn', 'main:app', '--host', BACKEND_HOST, '--port', BACKEND_PORT.toString(), '--reload'];
    
    const child = spawn(command, args, {
        cwd: BACKEND_DIR,
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: true,
        env: { ...process.env, PATH: `${path.join(BACKEND_DIR, 'venv', 'Scripts')};${process.env.PATH}` }
    });
    
    // Log output to file
    const logStream = fs.createWriteStream(logFile);
    child.stdout.pipe(logStream);
    child.stderr.pipe(logStream);
    
    child.unref();
    
    // Wait a moment and check if it started
    setTimeout(() => {
        if (isPortInUse(BACKEND_PORT)) {
            const pid = getPidByPort(BACKEND_PORT);
            fs.writeFileSync(BACKEND_PID, pid);
            logSuccess(`Backend started successfully (PID: ${pid})`);
            logInfo(`Backend API available at: http://${BACKEND_HOST}:${BACKEND_PORT}`);
            logInfo(`API documentation at: http://${BACKEND_HOST}:${BACKEND_PORT}/docs`);
        } else {
            logError('Failed to start backend service');
        }
    }, 3000);
}

function startFrontend() {
    logInfo('Starting frontend service...');
    
    if (isFrontendRunning()) {
        const pid = fs.readFileSync(FRONTEND_PID, 'utf8').trim();
        logWarning(`Frontend is already running (PID: ${pid})`);
        return;
    }
    
    if (isPortInUse(FRONTEND_PORT)) {
        const pid = getPidByPort(FRONTEND_PORT);
        logWarning(`Port ${FRONTEND_PORT} is already in use (PID: ${pid})`);
        logWarning('Attempting to kill existing process...');
        killProcess(pid);
        
        // Wait for port to be free
        let attempts = 0;
        while (isPortInUse(FRONTEND_PORT) && attempts < 10) {
            setTimeout(() => {}, 1000);
            attempts++;
        }
    }
    
    // Check if node_modules exists
    if (!fs.existsSync(path.join(FRONTEND_DIR, 'node_modules'))) {
        logInfo('Installing frontend dependencies...');
        try {
            execSync('npm install', { cwd: FRONTEND_DIR, stdio: 'inherit' });
        } catch (error) {
            logError('Failed to install frontend dependencies');
            return;
        }
    }
    
    // Start frontend
    const logFile = path.join(LOGS_DIR, 'frontend.log');
    const child = spawn('npm', ['run', 'dev'], {
        cwd: FRONTEND_DIR,
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: true
    });
    
    // Log output to file
    const logStream = fs.createWriteStream(logFile);
    child.stdout.pipe(logStream);
    child.stderr.pipe(logStream);
    
    child.unref();
    
    // Wait a moment and check if it started
    setTimeout(() => {
        if (isPortInUse(FRONTEND_PORT)) {
            const pid = getPidByPort(FRONTEND_PORT);
            fs.writeFileSync(FRONTEND_PID, pid);
            logSuccess(`Frontend started successfully (PID: ${pid})`);
            logInfo(`Frontend available at: http://localhost:${FRONTEND_PORT}`);
        } else {
            logError('Failed to start frontend service');
        }
    }, 5000);
}

function stopBackend() {
    logInfo('Stopping backend service...');
    
    if (fs.existsSync(BACKEND_PID)) {
        const pid = fs.readFileSync(BACKEND_PID, 'utf8').trim();
        if (isProcessRunning(pid)) {
            killProcess(pid);
            logSuccess('Backend stopped successfully');
        } else {
            logWarning('Backend process not found');
        }
        fs.unlinkSync(BACKEND_PID);
    } else {
        logWarning('No backend PID file found');
    }
    
    // Also kill any process using the backend port
    const portPid = getPidByPort(BACKEND_PORT);
    if (portPid) {
        logInfo(`Killing process using port ${BACKEND_PORT} (PID: ${portPid})`);
        killProcess(portPid);
    }
}

function stopFrontend() {
    logInfo('Stopping frontend service...');
    
    if (fs.existsSync(FRONTEND_PID)) {
        const pid = fs.readFileSync(FRONTEND_PID, 'utf8').trim();
        if (isProcessRunning(pid)) {
            killProcess(pid);
            logSuccess('Frontend stopped successfully');
        } else {
            logWarning('Frontend process not found');
        }
        fs.unlinkSync(FRONTEND_PID);
    } else {
        logWarning('No frontend PID file found');
    }
    
    // Also kill any process using the frontend port
    const portPid = getPidByPort(FRONTEND_PORT);
    if (portPid) {
        logInfo(`Killing process using port ${FRONTEND_PORT} (PID: ${portPid})`);
        killProcess(portPid);
    }
}

function showStatus() {
    logInfo('Service Status:');
    console.log();
    
    // Backend status
    if (isBackendRunning()) {
        const pid = fs.readFileSync(BACKEND_PID, 'utf8').trim();
        logSuccess(`Backend: Running (PID: ${pid})`);
        logInfo(`  URL: http://${BACKEND_HOST}:${BACKEND_PORT}`);
        logInfo(`  Docs: http://${BACKEND_HOST}:${BACKEND_PORT}/docs`);
    } else {
        logError('Backend: Not running');
    }
    
    // Frontend status
    if (isFrontendRunning()) {
        const pid = fs.readFileSync(FRONTEND_PID, 'utf8').trim();
        logSuccess(`Frontend: Running (PID: ${pid})`);
        logInfo(`  URL: http://localhost:${FRONTEND_PORT}`);
    } else {
        logError('Frontend: Not running');
    }
    
    console.log();
    
    // Port status
    logInfo('Port Status:');
    if (isPortInUse(BACKEND_PORT)) {
        const pid = getPidByPort(BACKEND_PORT);
        logSuccess(`Port ${BACKEND_PORT}: In use (PID: ${pid})`);
    } else {
        logWarning(`Port ${BACKEND_PORT}: Available`);
    }
    
    if (isPortInUse(FRONTEND_PORT)) {
        const pid = getPidByPort(FRONTEND_PORT);
        logSuccess(`Port ${FRONTEND_PORT}: In use (PID: ${pid})`);
    } else {
        logWarning(`Port ${FRONTEND_PORT}: Available`);
    }
}

function showLogs(service) {
    const logFile = path.join(LOGS_DIR, `${service}.log`);
    
    if (fs.existsSync(logFile)) {
        logInfo(`${service} logs:`);
        console.log(fs.readFileSync(logFile, 'utf8'));
    } else {
        logWarning(`${service} log file not found`);
    }
}

function setupDev() {
    logInfo('Setting up development environment...');
    
    // Backend setup
    logInfo('Setting up backend...');
    const venvPath = path.join(BACKEND_DIR, 'venv');
    
    if (!fs.existsSync(venvPath)) {
        logInfo('Creating Python virtual environment...');
        try {
            execSync('python3 -m venv venv', { cwd: BACKEND_DIR, stdio: 'inherit' });
            
            execSync('python -m pip install --upgrade pip', { 
                cwd: BACKEND_DIR,
                env: { ...process.env, PATH: `${path.join(venvPath, 'Scripts')};${process.env.PATH}` },
                stdio: 'inherit' 
            });
            
            execSync('pip install -r requirements.txt', { 
                cwd: BACKEND_DIR,
                env: { ...process.env, PATH: `${path.join(venvPath, 'Scripts')};${process.env.PATH}` },
                stdio: 'inherit' 
            });
            
            logSuccess('Backend dependencies installed');
        } catch (error) {
            logError('Failed to setup backend');
            return;
        }
    } else {
        logWarning('Backend virtual environment already exists');
    }
    
    // Frontend setup
    logInfo('Setting up frontend...');
    const nodeModulesPath = path.join(FRONTEND_DIR, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
        logInfo('Installing frontend dependencies...');
        try {
            execSync('npm install', { cwd: FRONTEND_DIR, stdio: 'inherit' });
            logSuccess('Frontend dependencies installed');
        } catch (error) {
            logError('Failed to setup frontend');
            return;
        }
    } else {
        logWarning('Frontend dependencies already installed');
    }
    
    logSuccess('Development environment setup completed!');
}

function showHelp() {
    console.log('AA Virtual Service Manager');
    console.log();
    console.log('Usage: node service-manager.js [COMMAND] [SERVICE]');
    console.log();
    console.log('Commands:');
    console.log('  start [backend|frontend|all]  Start services (default: all)');
    console.log('  stop [backend|frontend|all]   Stop services (default: all)');
    console.log('  restart [backend|frontend|all] Restart services (default: all)');
    console.log('  status                        Show service status');
    console.log('  logs [backend|frontend]       Show service logs');
    console.log('  setup                         Setup development environment');
    console.log('  help                          Show this help message');
    console.log();
    console.log('Examples:');
    console.log('  node service-manager.js start                      Start all services');
    console.log('  node service-manager.js start backend              Start only backend');
    console.log('  node service-manager.js stop frontend              Stop only frontend');
    console.log('  node service-manager.js status                     Show current status');
    console.log('  node service-manager.js logs backend               Show backend logs');
}

// Main function
function main() {
    const command = process.argv[2];
    const service = process.argv[3];
    
    switch (command) {
        case 'start':
            switch (service) {
                case 'backend':
                    startBackend();
                    break;
                case 'frontend':
                    startFrontend();
                    break;
                case 'all':
                case undefined:
                    startBackend();
                    startFrontend();
                    break;
                default:
                    logError(`Invalid service: ${service}`);
                    logError('Use: backend, frontend, or all');
                    process.exit(1);
            }
            break;
            
        case 'stop':
            switch (service) {
                case 'backend':
                    stopBackend();
                    break;
                case 'frontend':
                    stopFrontend();
                    break;
                case 'all':
                case undefined:
                    stopBackend();
                    stopFrontend();
                    break;
                default:
                    logError(`Invalid service: ${service}`);
                    logError('Use: backend, frontend, or all');
                    process.exit(1);
            }
            break;
            
        case 'restart':
            switch (service) {
                case 'backend':
                    stopBackend();
                    setTimeout(startBackend, 2000);
                    break;
                case 'frontend':
                    stopFrontend();
                    setTimeout(startFrontend, 2000);
                    break;
                case 'all':
                case undefined:
                    stopBackend();
                    stopFrontend();
                    setTimeout(() => {
                        startBackend();
                        startFrontend();
                    }, 3000);
                    break;
                default:
                    logError(`Invalid service: ${service}`);
                    logError('Use: backend, frontend, or all');
                    process.exit(1);
            }
            break;
            
        case 'status':
            showStatus();
            break;
            
        case 'logs':
            if (!service || (service !== 'backend' && service !== 'frontend')) {
                logError('Usage: node service-manager.js logs [backend|frontend]');
                process.exit(1);
            }
            showLogs(service);
            break;
            
        case 'setup':
            setupDev();
            break;
            
        case 'help':
        case '-h':
        case '--help':
        case undefined:
            showHelp();
            break;
            
        default:
            logError(`Unknown command: ${command}`);
            showHelp();
            process.exit(1);
    }
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
    logInfo('Cleaning up...');
    stopBackend();
    stopFrontend();
    logSuccess('Cleanup completed');
    process.exit(0);
});

// Run main function
main();
