/**
 * DeFi MCP Server - Main JavaScript Module
 * Handles client-side functionality for the web interface
 */

// Global variables
let currentApiKey = null;
let portfolioChart = null;
let toastContainer = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Initialize toast container
    toastContainer = document.getElementById('toastContainer');
    
    // Load API key from localStorage
    loadApiKey();
    
    // Initialize feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Setup global error handling
    setupErrorHandling();
    
    // Initialize page-specific functionality
    const path = window.location.pathname;
    if (path.includes('dashboard')) {
        initializeDashboard();
    }
}

/**
 * Setup global error handling
 */
function setupErrorHandling() {
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        showToast('An unexpected error occurred', 'danger');
    });
    
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showToast('A network error occurred', 'danger');
    });
}

/**
 * API Key Management
 */
function loadApiKey() {
    const storedApiKey = localStorage.getItem('defi_mcp_api_key');
    if (storedApiKey) {
        currentApiKey = storedApiKey;
        updateApiKeyDisplay();
    }
}

function saveApiKey(apiKey) {
    currentApiKey = apiKey;
    localStorage.setItem('defi_mcp_api_key', apiKey);
    updateApiKeyDisplay();
}

function updateApiKeyDisplay() {
    const apiKeyInput = document.getElementById('currentApiKey');
    if (apiKeyInput && currentApiKey) {
        apiKeyInput.value = currentApiKey;
        apiKeyInput.type = 'password';
    }
}

function generateApiKey() {
    // Generate a client-side API key (in production, this would be done server-side)
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-';
    let result = 'aya_';
    for (let i = 0; i < 32; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    saveApiKey(result);
    showToast('New API key generated successfully', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('apiKeyModal'));
    if (modal) {
        modal.hide();
    }
}

function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('currentApiKey');
    const toggleIcon = document.getElementById('apiKeyToggle');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        toggleIcon.setAttribute('data-feather', 'eye-off');
    } else {
        apiKeyInput.type = 'password';
        toggleIcon.setAttribute('data-feather', 'eye');
    }
    
    feather.replace();
}

/**
 * Modal Management
 */
function showApiKeyModal() {
    const modal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
    modal.show();
}

function showWalletModal() {
    const modal = new bootstrap.Modal(document.getElementById('walletModal'));
    modal.show();
}

function showSwapModal() {
    const modal = new bootstrap.Modal(document.getElementById('swapModal'));
    modal.show();
}

function showLendModal() {
    const modal = new bootstrap.Modal(document.getElementById('lendModal'));
    modal.show();
}

function showFarmModal() {
    const modal = new bootstrap.Modal(document.getElementById('farmModal'));
    modal.show();
}

/**
 * Wallet Management
 */
function generateWallet() {
    const blockchain = document.getElementById('walletBlockchain').value;
    
    if (!blockchain) {
        showToast('Please select a blockchain', 'warning');
        return;
    }
    
    // In a real implementation, this would call the server to generate a wallet
    showToast(`Wallet generation for ${blockchain} requires server-side implementation`, 'info');
}

function importWallet() {
    const privateKey = document.getElementById('importPrivateKey').value;
    const blockchain = document.getElementById('importBlockchain').value;
    
    if (!privateKey || !blockchain) {
        showToast('Please enter private key and select blockchain', 'warning');
        return;
    }
    
    // Basic validation
    if (blockchain === 'solana') {
        // Solana private keys are base58 encoded
        if (privateKey.length < 32) {
            showToast('Invalid Solana private key format', 'danger');
            return;
        }
    } else {
        // Ethereum/Polygon private keys
        const cleanKey = privateKey.startsWith('0x') ? privateKey.slice(2) : privateKey;
        if (cleanKey.length !== 64 || !/^[a-fA-F0-9]+$/.test(cleanKey)) {
            showToast('Invalid private key format', 'danger');
            return;
        }
    }
    
    showToast(`Wallet import for ${blockchain} requires server-side implementation`, 'info');
    
    // Clear the input for security
    document.getElementById('importPrivateKey').value = '';
}

/**
 * Toast Notification System
 */
function showToast(message, type = 'info', duration = 5000) {
    if (!toastContainer) {
        toastContainer = document.getElementById('toastContainer');
    }
    
    const toastId = 'toast_' + Date.now();
    const iconMap = {
        success: 'check-circle',
        danger: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
    };
    
    const bgColorMap = {
        success: 'bg-success',
        danger: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgColorMap[type]} text-white">
                <i data-feather="${iconMap[type]}" class="me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: duration > 0,
        delay: duration
    });
    
    // Replace feather icons in the new toast
    feather.replace();
    
    toast.show();
    
    // Auto-remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * API Communication Helpers
 */
async function makeApiRequest(endpoint, options = {}) {
    if (!currentApiKey) {
        throw new Error('API key not configured. Please generate an API key first.');
    }
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-API-Key': currentApiKey
    };
    
    const config = {
        headers: { ...defaultHeaders, ...options.headers },
        ...options
    };
    
    try {
        const response = await fetch(endpoint, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * DeFi Operations
 */
async function executeSwap(swapData) {
    try {
        showToast('Executing swap...', 'info');
        
        const result = await makeApiRequest('/api/v1/swap', {
            method: 'POST',
            body: JSON.stringify(swapData)
        });
        
        if (result.success) {
            showToast(`Swap executed successfully! TX: ${result.tx_hash}`, 'success');
            return result;
        } else {
            throw new Error(result.error || 'Swap failed');
        }
    } catch (error) {
        showToast(`Swap failed: ${error.message}`, 'danger');
        throw error;
    }
}

async function executeLend(lendData) {
    try {
        showToast('Executing lending operation...', 'info');
        
        const result = await makeApiRequest('/api/v1/lend', {
            method: 'POST',
            body: JSON.stringify(lendData)
        });
        
        if (result.success) {
            showToast(`Lending executed successfully! TX: ${result.tx_hash}`, 'success');
            return result;
        } else {
            throw new Error(result.error || 'Lending failed');
        }
    } catch (error) {
        showToast(`Lending failed: ${error.message}`, 'danger');
        throw error;
    }
}

async function executeFarm(farmData) {
    try {
        showToast('Adding liquidity...', 'info');
        
        const result = await makeApiRequest('/api/v1/farm', {
            method: 'POST',
            body: JSON.stringify(farmData)
        });
        
        if (result.success) {
            showToast(`Liquidity added successfully! TX: ${result.tx_hash}`, 'success');
            return result;
        } else {
            throw new Error(result.error || 'Farming failed');
        }
    } catch (error) {
        showToast(`Farming failed: ${error.message}`, 'danger');
        throw error;
    }
}

/**
 * Portfolio and Data Loading
 */
async function loadPortfolio(walletAddress) {
    try {
        const result = await makeApiRequest(`/api/v1/portfolio/${walletAddress}`);
        return result.portfolio || null;
    } catch (error) {
        console.error('Failed to load portfolio:', error);
        return null;
    }
}

async function loadPositions(walletAddress) {
    try {
        const result = await makeApiRequest(`/api/v1/positions/${walletAddress}`);
        return result.positions || [];
    } catch (error) {
        console.error('Failed to load positions:', error);
        return [];
    }
}

async function loadTransactions(walletAddress, page = 1, perPage = 50) {
    try {
        const result = await makeApiRequest(`/api/v1/transactions/${walletAddress}?page=${page}&per_page=${perPage}`);
        return result.transactions || [];
    } catch (error) {
        console.error('Failed to load transactions:', error);
        return [];
    }
}

/**
 * Dashboard Functionality
 */
function initializeDashboard() {
    // Load dashboard data
    loadDashboardData();
    
    // Setup form handlers
    setupFormHandlers();
}

function setupFormHandlers() {
    // Swap form
    const swapForm = document.getElementById('swapForm');
    if (swapForm) {
        swapForm.addEventListener('submit', handleSwapSubmit);
    }
    
    // Lend form
    const lendForm = document.getElementById('lendForm');
    if (lendForm) {
        lendForm.addEventListener('submit', handleLendSubmit);
    }
    
    // Farm form
    const farmForm = document.getElementById('farmForm');
    if (farmForm) {
        farmForm.addEventListener('submit', handleFarmSubmit);
    }
}

async function handleSwapSubmit(event) {
    event.preventDefault();
    
    if (!currentApiKey) {
        showToast('Please configure an API key first', 'warning');
        showApiKeyModal();
        return;
    }
    
    const formData = new FormData(event.target);
    const swapData = Object.fromEntries(formData.entries());
    
    try {
        await executeSwap(swapData);
        
        // Close modal and refresh dashboard
        const modal = bootstrap.Modal.getInstance(document.getElementById('swapModal'));
        if (modal) {
            modal.hide();
        }
        
        refreshDashboard();
    } catch (error) {
        // Error already handled in executeSwap
    }
}

async function handleLendSubmit(event) {
    event.preventDefault();
    
    if (!currentApiKey) {
        showToast('Please configure an API key first', 'warning');
        showApiKeyModal();
        return;
    }
    
    const formData = new FormData(event.target);
    const lendData = Object.fromEntries(formData.entries());
    
    try {
        await executeLend(lendData);
        
        // Close modal and refresh dashboard
        const modal = bootstrap.Modal.getInstance(document.getElementById('lendModal'));
        if (modal) {
            modal.hide();
        }
        
        refreshDashboard();
    } catch (error) {
        // Error already handled in executeLend
    }
}

async function handleFarmSubmit(event) {
    event.preventDefault();
    
    if (!currentApiKey) {
        showToast('Please configure an API key first', 'warning');
        showApiKeyModal();
        return;
    }
    
    const formData = new FormData(event.target);
    const farmData = Object.fromEntries(formData.entries());
    
    try {
        await executeFarm(farmData);
        
        // Close modal and refresh dashboard
        const modal = bootstrap.Modal.getInstance(document.getElementById('farmModal'));
        if (modal) {
            modal.hide();
        }
        
        refreshDashboard();
    } catch (error) {
        // Error already handled in executeFarm
    }
}

function loadDashboardData() {
    // Update stats
    updateDashboardStats();
    
    // Load portfolio chart
    loadPortfolioChart();
    
    // Load recent data
    loadRecentTransactions();
    loadActivePositions();
}

function updateDashboardStats() {
    // In a real implementation, these would be calculated from actual data
    const elements = {
        'totalPortfolioValue': '$0.00',
        'activePositions': '0',
        'pendingTransactions': '0',
        'averageApy': '0.00%'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

function loadPortfolioChart() {
    const chartCanvas = document.getElementById('portfolioChart');
    const emptyState = document.getElementById('portfolioEmpty');
    const chartContainer = document.getElementById('portfolioChartContainer');
    
    if (!chartCanvas) return;
    
    // Show empty state by default
    if (chartContainer) chartContainer.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
    
    // In a real implementation, this would load actual portfolio data
    // and create a Chart.js chart if data is available
}

function loadRecentTransactions() {
    const tableElement = document.getElementById('transactionsTable');
    const emptyElement = document.getElementById('transactionsEmpty');
    const tbody = document.getElementById('transactionsBody');
    
    if (!tbody) return;
    
    // Clear existing data
    tbody.innerHTML = '';
    
    // Show empty state
    if (tableElement) tableElement.style.display = 'none';
    if (emptyElement) emptyElement.style.display = 'block';
    
    // In a real implementation, this would load actual transaction data
}

function loadActivePositions() {
    const tableElement = document.getElementById('positionsTable');
    const emptyElement = document.getElementById('positionsEmpty');
    const tbody = document.getElementById('positionsBody');
    
    if (!tbody) return;
    
    // Clear existing data
    tbody.innerHTML = '';
    
    // Show empty state
    if (tableElement) tableElement.style.display = 'none';
    if (emptyElement) emptyElement.style.display = 'block';
    
    // In a real implementation, this would load actual positions data
}

function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    loadDashboardData();
    
    // Re-initialize feather icons
    setTimeout(() => {
        feather.replace();
    }, 100);
}

/**
 * Utility Functions
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

function formatAddress(address, length = 8) {
    if (!address || address.length <= length) return address;
    return `${address.slice(0, length / 2)}...${address.slice(-length / 2)}`;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'danger');
    });
}

/**
 * Validation Functions
 */
function validateAddress(address, blockchain) {
    if (!address) return false;
    
    if (blockchain === 'solana') {
        // Solana addresses are base58 encoded, 32-44 characters
        return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
    } else {
        // Ethereum/Polygon addresses
        return /^0x[a-fA-F0-9]{40}$/.test(address);
    }
}

function validateAmount(amount) {
    const num = parseFloat(amount);
    return !isNaN(num) && num > 0;
}

/**
 * Loading States
 */
function setLoading(element, loading = true) {
    if (loading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

function showSpinner(element) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    spinner.setAttribute('role', 'status');
    element.prepend(spinner);
}

function hideSpinner(element) {
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
}

/**
 * Export functions for global access
 */
window.DeFiMCP = {
    showApiKeyModal,
    showWalletModal,
    generateApiKey,
    toggleApiKeyVisibility,
    generateWallet,
    importWallet,
    showToast,
    refreshDashboard,
    executeSwap,
    executeLend,
    executeFarm,
    loadPortfolio,
    loadPositions,
    loadTransactions,
    validateAddress,
    validateAmount,
    formatCurrency,
    formatPercentage,
    formatAddress,
    formatTimestamp,
    copyToClipboard
};
