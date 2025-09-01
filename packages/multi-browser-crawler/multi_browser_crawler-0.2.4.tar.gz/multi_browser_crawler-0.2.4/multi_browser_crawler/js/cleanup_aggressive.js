/**
 * Aggressive Page Cleanup Script
 * ==============================
 *
 * Removes ads, popups, overlays and other unwanted elements
 * for cleaner HTML extraction.
 */

(() => {
  // Remove common ad and popup elements
  const selectors = [
    '[class*="ad"]',
    '[id*="ad"]',
    '[class*="popup"]',
    '[class*="modal"]',
    '[class*="overlay"]',
    '[class*="banner"]',
  ];

  let removed = 0;
  selectors.forEach((selector) => {
    document.querySelectorAll(selector).forEach((el) => {
      el.remove();
      removed++;
    });
  });

  return removed;
})();
