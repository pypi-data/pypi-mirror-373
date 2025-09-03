/**
 * Minimal Page Cleanup Script
 * ===========================
 *
 * Removes only obvious advertisement elements
 * for basic HTML cleanup.
 */

(() => {
  let removed = 0;
  document.querySelectorAll('[class*="advertisement"]').forEach((el) => {
    el.remove();
    removed++;
  });

  return removed;
})();
