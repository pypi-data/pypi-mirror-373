/**
 * Page Cleanup Script for Multi-Browser-Crawler
 * ==============================================
 * 
 * Removes unnecessary elements to reduce HTML size and improve parsing performance.
 * This is a streamlined version focused on common cleanup tasks.
 */

function cleanupPage(options = {}) {
  const defaults = {
    logResults: false,  // Reduced logging for performance
    removeTags: ['script', 'style', 'iframe', 'noscript', 'meta', 'link', 'object', 'embed', 'form', 'svg'],
    remove1x1Images: true,
    removeStyleAttribute: true,
    removeDeprecatedStyleAttributes: true,
    removeDataAttributes: false,  // More conservative default
    removeBootstrapClasses: true,
    removeTailwindClasses: true,
    removeAds: true,
    removeSvgImages: true
  };
  
  const config = { ...defaults, ...options };
  const logResults = config.logResults;

  const removed = {
    tags: {},
    attributes: { style: 0, deprecated: 0, data: 0 },
    classes: { bootstrap: 0, tailwind: 0 },
    images1x1: 0,
    ads: 0,
    svgImages: 0
  };

  // Initialize tag counters
  config.removeTags.forEach(tag => {
    removed.tags[`${tag}s`] = 0;
  });

  // 1. Remove unwanted tags
  if (config.removeTags && config.removeTags.length > 0) {
    config.removeTags.forEach(tagName => {
      const counterKey = `${tagName}s`;
      document.querySelectorAll(tagName).forEach(element => {
        try {
          element.remove();
          if (removed.tags.hasOwnProperty(counterKey)) {
            removed.tags[counterKey]++;
          }
        } catch (e) {
          if (logResults) console.warn(`Could not remove ${tagName}:`, e);
        }
      });
    });
  }

  // 2. Remove advertisements (using simplified selectors for performance)
  if (config.removeAds) {
    const adSelectors = [
      // Google Ads
      'ins.adsbygoogle', 'div[id*="google_ads_"]', 'div[data-ad-client]',
      'iframe[id*="google_ads_iframe"]', 'div[id*="gpt-ad"]',
      
      // Common ad networks
      'div[id*="taboola"]', 'div[class*="OUTBRAIN"]', 'div[id*="outbrain"]',
      'div[class*="__fs-"]', 'div[id*="freestar"]',
      
      // Generic ad containers
      'div[id*="ad-"]', 'div[id*="-ad"]', 'div[class*="ad-container"]',
      'div[class*="ad-wrapper"]', '.advertisement', '.sponsored-content',
      
      // Sticky ads
      'div[class*="sticky-footer"]', 'div[id*="sticky-footer"]',
      'div[class*="sticky_ad"]', 'div[id*="sticky_ad"]',
      
      // Common ad classes
      '.ad', '.ads', '.adsbygoogle', '.banner-ads', '.sponsored'
    ];
    
    const combinedSelector = adSelectors.join(', ');
    document.querySelectorAll(combinedSelector).forEach(adElement => {
      try {
        adElement.remove();
        removed.ads++;
      } catch (e) {
        try {
          adElement.style.display = 'none';
          removed.ads++;
        } catch (innerError) {
          if (logResults) console.warn('Could not remove ad element:', e);
        }
      }
    });
  }

  // 3. Remove SVG images
  if (config.removeSvgImages) {
    document.querySelectorAll('img').forEach(img => {
      try {
        if (img.src && (img.src.toLowerCase().includes('.svg') || img.src.includes('data:image/svg+xml'))) {
          img.remove();
          removed.svgImages++;
        }
      } catch (e) {
        if (logResults) console.warn('Could not remove SVG image:', e);
      }
    });
  }

  // 4. Clean up attributes and classes
  if (config.removeStyleAttribute || config.removeDeprecatedStyleAttributes || 
      config.removeDataAttributes || config.removeBootstrapClasses || config.removeTailwindClasses) {
    
    const deprecatedAttrs = ['align', 'background', 'bgcolor', 'border', 'cellpadding', 'cellspacing', 'color', 'height', 'width'];
    const bsPrefixes = ['text-', 'bg-', 'border-', 'p-', 'm-', 'btn-', 'alert-', 'badge-'];
    const twPrefixes = ['bg-', 'text-', 'border-', 'p-', 'px-', 'py-', 'm-', 'mx-', 'my-', 'w-', 'h-', 'font-', 'rounded'];

    document.querySelectorAll('*').forEach(element => {
      // Remove style attribute
      if (config.removeStyleAttribute && element.hasAttribute('style')) {
        try {
          element.removeAttribute('style');
          removed.attributes.style++;
        } catch (e) {}
      }

      // Remove deprecated attributes
      if (config.removeDeprecatedStyleAttributes) {
        deprecatedAttrs.forEach(attrName => {
          if (element.hasAttribute(attrName)) {
            try {
              element.removeAttribute(attrName);
              removed.attributes.deprecated++;
            } catch (e) {}
          }
        });
      }

      // Remove data attributes (with image preservation)
      if (config.removeDataAttributes) {
        const preservedImageAttrs = ['data-src', 'data-srcset', 'data-original', 'data-lazy-src'];
        const dataAttrsToRemove = [];
        
        for (let i = 0; i < element.attributes.length; i++) {
          const attrName = element.attributes[i].name;
          if (attrName.startsWith('data-')) {
            if (element.tagName.toLowerCase() === 'img' && preservedImageAttrs.includes(attrName)) {
              continue; // Preserve image-related data attributes
            }
            dataAttrsToRemove.push(attrName);
          }
        }
        
        dataAttrsToRemove.forEach(attrName => {
          try {
            element.removeAttribute(attrName);
            removed.attributes.data++;
          } catch (e) {}
        });
      }

      // Remove framework classes
      if ((config.removeBootstrapClasses || config.removeTailwindClasses) && element.classList.length > 0) {
        const classesToRemove = new Set();
        
        Array.from(element.classList).forEach(className => {
          if (config.removeBootstrapClasses && bsPrefixes.some(prefix => className.startsWith(prefix))) {
            classesToRemove.add(className);
            removed.classes.bootstrap++;
          }
          if (config.removeTailwindClasses && twPrefixes.some(prefix => className.startsWith(prefix))) {
            classesToRemove.add(className);
            removed.classes.tailwind++;
          }
        });

        if (classesToRemove.size > 0) {
          try {
            element.classList.remove(...classesToRemove);
          } catch (e) {}
        }
      }
    });
  }

  // 5. Remove 1x1 images
  if (config.remove1x1Images) {
    document.querySelectorAll('img').forEach(img => {
      const checkAndRemoveImage = (imageElement) => {
        if (imageElement.naturalWidth === 1 || imageElement.naturalHeight === 1) {
          try {
            imageElement.remove();
            removed.images1x1++;
          } catch (e) {}
        }
      };
      
      if (img.complete && img.naturalWidth > 0) {
        checkAndRemoveImage(img);
      } else if (!img.complete) {
        img.addEventListener('load', function() { checkAndRemoveImage(this); }, { once: true });
      }
    });
  }

  // 6. Log summary if requested
  if (logResults) {
    const summary = [];
    Object.entries(removed.tags).forEach(([key, value]) => {
      if (value > 0) summary.push(`${value} ${key}`);
    });
    if (removed.attributes.style > 0) summary.push(`${removed.attributes.style} style attrs`);
    if (removed.ads > 0) summary.push(`${removed.ads} ads`);
    if (removed.images1x1 > 0) summary.push(`${removed.images1x1} 1x1 images`);
    
    if (summary.length > 0) {
      console.log(`Page cleanup: Removed ${summary.join(', ')}`);
    }
  }

  return removed;
}

// Execute cleanup and return results
return cleanupPage();
