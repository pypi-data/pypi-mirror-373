/**
 * Network Monitoring JavaScript
 * =============================
 * 
 * Monitors fetch() and XMLHttpRequest calls to capture API calls
 * for parser development and debugging purposes.
 * 
 * This script intercepts network requests and stores them in window._apiCalls
 * for later retrieval by the Python browser automation code.
 */

// Initialize API calls storage
window._apiCalls = window._apiCalls || [];

// Monitor fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    const options = args[1] || {};

    window._apiCalls.push({
        url_path: url,
        method: options.method || 'GET',
        timestamp: Date.now(),
        type: 'fetch'
    });

    return originalFetch.apply(this, args);
};

// Monitor XMLHttpRequest
const originalXHROpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url, ...args) {
    this._url = url;
    this._method = method;
    return originalXHROpen.apply(this, [method, url, ...args]);
};

const originalXHRSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function(...args) {
    if (this._url) {
        window._apiCalls.push({
            url_path: this._url,
            method: this._method || 'GET',
            timestamp: Date.now(),
            type: 'xhr'
        });
    }
    return originalXHRSend.apply(this, args);
};

// Helper function to get captured API calls
window.getApiCalls = function() {
    return window._apiCalls || [];
};

// Helper function to clear captured API calls
window.clearApiCalls = function() {
    window._apiCalls = [];
};
