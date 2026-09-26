// ===== SECURITY FUNCTIONS =====

// CSRF Token Helper
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Sanitize HTML to prevent XSS
function sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

// Escape HTML special characters
function escapeHTML(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ===== TOAST NOTIFICATION FUNCTION =====
function showToast(title, message, type = 'info') {
    const toastId = 'toast-' + Date.now();
    const toastHTML = document.createElement('div');
    toastHTML.id = toastId;
    toastHTML.className = `toast align-items-center text-white bg-${type} border-0`;
    toastHTML.setAttribute('role', 'alert');
    toastHTML.setAttribute('aria-live', 'assertive');
    toastHTML.setAttribute('aria-atomic', 'true');
    
    toastHTML.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${escapeHTML(title)}</strong><br>${escapeHTML(message)}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    toastContainer.appendChild(toastHTML);
    
    try {
        const toast = new bootstrap.Toast(toastHTML);
        toast.show();
        
        toastHTML.addEventListener('hidden.bs.toast', () => {
            toastHTML.remove();
        });
    } catch (e) {
        console.error('Toast error:', e);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Initialize Bootstrap Tooltips and Popovers
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Smooth Scroll Behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format Date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// Handle Form Submission with Loading State
function handleFormSubmit(formId, callback) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner spinner-border spinner-border-sm me-2"></span>Processing...';

        callback(form).then(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }).catch(error => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            showToast('Error', error.message || 'An error occurred', 'danger');
        });
    });
}

// Debounce Function
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Validate Email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate Password Strength
function getPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    const strengthLevels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
    return strengthLevels[strength] || 'Very Weak';
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Success', 'Copied to clipboard', 'success');
    }).catch(() => {
        showToast('Error', 'Failed to copy', 'danger');
    });
}

// Local Storage Helper
const Storage = {
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    get: (key) => {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch {
            return null;
        }
    },
    remove: (key) => localStorage.removeItem(key),
    clear: () => localStorage.clear()
};

// API Call Helper
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

// Notification Handler
class Notifier {
    static success(message, title = 'Success') {
        showToast(title, message, 'success');
    }

    static error(message, title = 'Error') {
        showToast(title, message, 'danger');
    }

    static info(message, title = 'Info') {
        showToast(title, message, 'info');
    }

    static warning(message, title = 'Warning') {
        showToast(title, message, 'warning');
    }
}

// Modal Handler
class Modal {
    static show(elementId) {
        const modalElement = document.getElementById(elementId);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    static hide(elementId) {
        const modalElement = document.getElementById(elementId);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        }
    }
}

// Table Sorter
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.tbody.rows);
    const isAscending = table.dataset.sortAscending === 'true';

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        if (!isNaN(aValue) && !isNaN(bValue)) {
            return isAscending ? aValue - bValue : bValue - aValue;
        }

        return isAscending 
            ? aValue.localeCompare(bValue) 
            : bValue.localeCompare(aValue);
    });

    rows.forEach(row => table.tbody.appendChild(row));
    table.dataset.sortAscending = !isAscending;
}

// Pre-loading Handler
const PageLoader = {
    show: () => {
        const loader = document.getElementById('page-loader');
        if (loader) loader.style.display = 'flex';
    },
    hide: () => {
        const loader = document.getElementById('page-loader');
        if (loader) loader.style.display = 'none';
    }
};

// Confirm Dialog
function confirmAction(message = 'Are you sure?', onConfirm) {
    if (confirm(message)) {
        onConfirm();
    }
}

// Export to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    const csv = [];
    
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => {
            let text = cell.textContent.trim();
            text = text.replace(/"/g, '""');
            return `"${text}"`;
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Keyboard Shortcuts
const KeyboardShortcuts = {
    register: (key, callback) => {
        document.addEventListener('keydown', (e) => {
            if (e.key === key) {
                e.preventDefault();
                callback();
            }
        });
    },
    registerCombo: (keys, callback) => {
        const activeKeys = new Set();
        
        document.addEventListener('keydown', (e) => {
            activeKeys.add(e.key);
            if (keys.every(key => activeKeys.has(key))) {
                e.preventDefault();
                callback();
            }
        });

        document.addEventListener('keyup', (e) => {
            activeKeys.delete(e.key);
        });
    }
};

// Animation Helper
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease-in`;
    
    setTimeout(() => {
        element.style.opacity = '1';
    }, 10);
}

function fadeOut(element, duration = 300) {
    element.style.transition = `opacity ${duration}ms ease-out`;
    element.style.opacity = '0';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// ===== ENHANCED SECURITY & UX =====

// Password Strength Meter with Real-time Feedback
function setupPasswordStrengthMeter(inputSelector) {
    const passwordInput = document.querySelector(inputSelector);
    if (!passwordInput) return;

    let strengthContainer = document.querySelector('.password-strength-container');
    
    if (!strengthContainer) {
        strengthContainer = document.createElement('div');
        strengthContainer.className = 'password-strength-container';
        passwordInput.parentNode.insertBefore(strengthContainer, passwordInput.nextSibling);
    }

    passwordInput.addEventListener('input', function() {
        const strength = getPasswordStrength(this.value);
        const strengthMap = {
            'Very Weak': 'strength-very-weak',
            'Weak': 'strength-weak',
            'Fair': 'strength-fair',
            'Good': 'strength-good',
            'Strong': 'strength-strong',
            'Very Strong': 'strength-strong'
        };

        strengthContainer.className = `password-strength-container ${strengthMap[strength]}`;
        strengthContainer.innerHTML = `
            <div class="password-strength-bar">
                <div class="password-strength-fill"></div>
            </div>
            <div class="password-strength-text">${strength}</div>
        `;
    });
}

// Email Validation with Real-time Feedback
function setupEmailValidation(inputSelector) {
    const emailInput = document.querySelector(inputSelector);
    if (!emailInput) return;

    emailInput.addEventListener('blur', function() {
        if (this.value && !isValidEmail(this.value)) {
            this.classList.add('is-invalid');
            this.classList.remove('is-valid');
        } else if (this.value) {
            this.classList.add('is-valid');
            this.classList.remove('is-invalid');
        }
    });

    emailInput.addEventListener('input', function() {
        this.classList.remove('is-valid', 'is-invalid');
    });
}

// Form Validation with Better UX
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            
            if (input.type === 'email' && !isValidEmail(input.value)) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        }
    });

    return isValid;
}

// Search Table with Debounce
function searchTable(inputSelector, tableSelector) {
    const searchInput = document.querySelector(inputSelector);
    if (!searchInput) return;

    searchInput.addEventListener('keyup', debounce(function() {
        const searchTerm = this.value.toLowerCase();
        const table = document.querySelector(tableSelector);
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }, 300));
}

// Modal Helpers
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        new bootstrap.Modal(modal).show();
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const instance = bootstrap.Modal.getInstance(modal);
        if (instance) instance.hide();
    }
}

// Theme Toggle (Dark Mode)
function initializeThemeToggle() {
    const savedTheme = Storage.get('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        const updateThemeToggle = (theme) => {
            const isDark = theme === 'dark';
            themeToggle.innerHTML = `<i class="bi ${isDark ? 'bi-sun' : 'bi-moon-stars'}" aria-hidden="true"></i>`;
            themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            themeToggle.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
        };

        updateThemeToggle(savedTheme);
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            Storage.set('theme', newTheme);
            updateThemeToggle(newTheme);
        });
    }
}

// Network State Handler
window.addEventListener('online', () => {
    Notifier.success('Connection restored!', 'Online');
});

window.addEventListener('offline', () => {
    Notifier.warning('You are offline. Some features may not work.', 'Offline');
});

// Keyboard Shortcuts Handler
document.addEventListener('keydown', function(event) {
    // Ctrl+Shift+A: Show Admin Login
    if (event.ctrlKey && event.shiftKey && event.code === 'KeyA') {
        const adminCard = document.getElementById('adminCard');
        if (adminCard) {
            adminCard.style.display = adminCard.style.display === 'none' ? 'block' : 'none';
        }
    }

    // Ctrl+K: Focus Search
    if (event.ctrlKey && event.code === 'KeyK') {
        event.preventDefault();
        const searchInput = document.querySelector('[data-search]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Esc: Close modals
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            const instance = bootstrap.Modal.getInstance(modal);
            if (instance) instance.hide();
        });
    }
});

// Performance Monitoring
if (window.performance && window.performance.timing) {
    window.addEventListener('load', function() {
        const pageLoadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log('Page Load Time: ' + pageLoadTime + 'ms');
    });
}

// Error Handling
window.addEventListener('error', (event) => {
    console.error('Global Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});

// Print Page Function
function printPage(containerId) {
    const element = document.getElementById(containerId) || document.body;
    const printWindow = window.open('', '', 'width=900,height=600');
    
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<link rel="stylesheet" href="' + 
        document.querySelector('link[href*="bootstrap"]').href + '">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(element.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    
    printWindow.print();
}

// Throttle Function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize on Page Load
document.addEventListener('DOMContentLoaded', function() {
    initializeThemeToggle();
});

