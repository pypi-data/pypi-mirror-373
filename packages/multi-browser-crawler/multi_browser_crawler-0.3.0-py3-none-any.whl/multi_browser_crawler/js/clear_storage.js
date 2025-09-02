/**
 * Storage Cleanup Script
 * ======================
 * 
 * Clears browser storage (localStorage, sessionStorage, window.name)
 * for clean browser state between requests.
 */

(() => {
    try {
        localStorage.clear();
        sessionStorage.clear();
        window.name = '';
        return { status: 'cleared', storage_types: ['localStorage', 'sessionStorage', 'window.name'] };
    } catch(e) {
        // Ignore errors if storage is not accessible
        return { status: 'error', error: e.message };
    }
})();
