/**
 * Removes specified elements, attributes, and CSS classes from the page.
 * WARNING: Use with extreme caution. Removing tags, attributes (especially data-*),
 * and framework classes can severely break page functionality and appearance.
 *
 * @param {object} options - Configuration options.
 * @param {boolean} [options.logResults=true] - Log removal actions and summary to console.
 * @param {string[]} [options.removeTags=['script', 'style', 'iframe', 'noscript', 'meta', 'link', 'object', 'embed', 'form']] - Tags to remove entirely. Set to [] to skip tag removal.
 * @param {boolean} [options.remove1x1Images=true] - Remove <img> tags that render as 1x1 pixels.
 * @param {boolean} [options.removeStyleAttribute=true] - Remove inline 'style' attributes from all elements.
 * @param {boolean} [options.removeDeprecatedStyleAttributes=false] - Remove common deprecated HTML styling attributes (e.g., bgcolor, align).
 * @param {boolean} [options.removeDataAttributes=false] - **HIGH RISK** Remove all 'data-*' attributes from all elements. Likely breaks site functionality.
 * @param {boolean} [options.removeBootstrapClasses=false] - Attempt to remove common Bootstrap styling classes (experimental).
 * @param {boolean} [options.removeTailwindClasses=false] - Attempt to remove common Tailwind utility classes (experimental).
 * @param {boolean} [options.removeAds=true] - Remove ads from multiple ad networks including Google, Taboola, Outbrain, etc.
 * @param {boolean} [options.removeSvgImages=true] - Remove any <img> tags with SVG sources.
 * @return {Object} Count of elements, attributes, and classes removed.
 */
function cleanupPageAdvanced(options = {}) {
  // --- Configuration ---
  const defaults = {
    logResults: true,
    removeTags: ['script', 'style', 'iframe', 'noscript', 'meta', 'link', 'object', 'embed', 'form', 'svg'],
    remove1x1Images: true,
    removeStyleAttribute: true,
    removeDeprecatedStyleAttributes: true,
    removeDataAttributes: true, 
    removeBootstrapClasses: true,
    removeTailwindClasses: true,
    removeAds: true,
    removeSvgImages: true
  };
  // Force all options to true for testing
  const config = { ...defaults, ...options };
  const logResults = config.logResults;

  // --- Counters ---
  const removed = {
    tags: {}, // Store tag counts like { scripts: 0, styles: 0, ... }
    attributes: {
      style: 0,
      deprecated: 0,
      data: 0
    },
    classes: {
      bootstrap: 0,
      tailwind: 0
    },
    images1x1: 0,
    ads: 0, // Counter for all ad types
    svgImages: 0 // Counter for SVG images
  };

  // Initialize tag counters
  config.removeTags.forEach(tag => {
    // Simple pluralization; might need adjustment for edge cases if tags change
    removed.tags[`${tag}s`] = 0;
  });

  // --- 1. Tag Removal ---
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
          if (logResults) console.warn(`Could not remove ${tagName}:`, element, e);
        }
      });
    });
  }

  // --- 2. Advertisement Removal ---
  if (config.removeAds) {
    // Target common ad network selectors
    const adSelectors = [
      // ---- Google Ad Products ----
      'ins.adsbygoogle',
      'div[id*="google_ads_"]',
      'div[id*="googlead"]',
      'div[id*="adsense"]',
      'div[id*="adunit"]',
      'div[data-ad-client]',
      'div[data-ad-slot]',
      'div[data-google-query-id]',
      // Google Ad iframes
      'iframe[id*="google_ads_iframe"]',
      'div[id*="google_ads_iframe"]',
      // Google Publisher Tags
      'div[id*="gpt-ad"]',
      
      // ---- Video Ad Players ----
      // Specifics for Primis and other problematic video players
      'div[id*="primisPlayerContainerDiv"]',
      'div[id*="primis_container"]',
      'div[id="placeHolder"]',
      'div[id*="Player-Div"]',
      'div[id*="Video-Div"]',
      'div[id*="adVpaid"]',
      'div[id*="adIma"]',
      'div[id*="adDisplayBanner"]',
      'div[id*="pixelsDiv"]',
      'img[src*="pl.primis.tech"]',
      // JW Player (when used for ads)
      'div[class*="jwplayer"][data-advertising]',
      // Brightcove Ads
      'div[data-video-player-id][data-account][data-ad-config-id]',
      // Outstream video ads
      'div[class*="video-ad-"]',
      'div[id*="video-ad-"]',
      
      // ---- Sticky Ads and Footers ----
      // Sticky footer ads
      'div[class*="sticky-footer"]',
      'div[id*="sticky-footer"]',
      'div[class*="fs-sticky"]',
      'div[id*="fs-sticky"]',
      '.fs-sticky-footer',
      '#fs-sticky-footer',
      'div[id*="sticky_footer"]',
      'div[class*="sticky_footer"]',
      'div[id*="stickyFooter"]',
      'div[class*="stickyFooter"]',
      'div[class*="sticky_ad"]',
      'div[id*="sticky_ad"]',
      'div[class*="stickyAd"]',
      'div[id*="stickyAd"]',
      // Freestar specific
      'div[id*="wenxuecity_sticky"]',
      'div[class*="fs-sticky-parent"]',
      'div[class*="fs-sticky-wrapper"]',
      'div[class*="fs-sticky-slot"]',
      '.fs-close-button',
      // Generic sticky elements
      'div[class*="adhesion"]',
      'div[id*="adhesion"]',
      'div[class*="anchor-ad"]',
      'div[id*="anchor-ad"]',
      'div[class*="bottom-banner"]',
      'div[id*="bottom-banner"]',
      
      // ---- Common Ad Networks ----
      // Taboola
      'div[id*="taboola"]',
      // Outbrain
      'div[class*="OUTBRAIN"]', 
      'div[id*="outbrain"]',
      // Freestar
      'div[class*="__fs-"]',
      'div[id*="freestar"]',
      // Zergnet
      'div[id*="zergnet"]',
      // RevContent
      'div[id*="rcjsload"]',
      'div[id*="rev_content"]',
      // Criteo
      'div[id*="criteo"]',
      // MediaNet
      'div[id*="mnet"]',
      'div[id*="medianet"]',
      // AdSense
      'div[class*="adsbygoogle"]',
      // AppNexus / Xandr
      'div[id*="apn_ad"]',
      'iframe[id*="apn_ad"]',
      // Amazon
      'div[id*="amzn_assoc"]',
      'iframe[id*="amzn_assoc"]',
      // PubMatic
      'div[id*="pubmatic"]',
      // Rubicon
      'div[id*="rubicon"]',
      // OpenX
      'div[id*="openx"]',
      // Teads
      'div[id*="teads"]',
      // Sovrn
      'div[id*="sovrn"]',
      // Index Exchange
      'div[id*="ix_"]',
      
      // --- Generic ad containers (added back) ---
      'div[id*="ad-"]',
      'div[id*="-ad"]',
      'div[id*="_ad_"]',
      'div[id*="adslot"]',
      'div[class*="ad-container"]',
      'div[class*="ad-wrapper"]',
      'div[class*="ad-unit"]',
      'div[class*="adbox"]',
      'div[class*="ad-box"]',
      'div[class*="advert"]',
      'div[id*="banner"]',
      'div[id*="Banner"]',
      'div[id*="skyskraper"]',
      'div[id*="skyscraper"]',
      'aside[id*="ad-"]',
      'aside[class*="ad-"]',
      
      // ---- Common iframe sources ----
      'iframe[src*="googleadservices.com"]',
      'iframe[src*="googlesyndication.com"]',
      'iframe[src*="doubleclick.net"]',
      'iframe[src*="2mdn.net"]',
      'iframe[src*="serving-sys.com"]',
      'iframe[src*="adnxs.com"]',
      'iframe[src*="advertising.com"]',
      'iframe[src*="freestar.io"]',
      'iframe[src*="adsrvr.org"]',
      'iframe[src*="criteo.com"]',
      'iframe[src*="openx.net"]',
      'iframe[src*="rubiconproject.com"]',
      'iframe[src*="pubmatic.com"]',
      'iframe[src*="innovid.com"]',
      'iframe[src*="teads.tv"]',
      'iframe[src*="outbrain.com"]',
      'iframe[src*="taboola.com"]',
      
      // ---- Common ad class names ----
      '.ad',
      '.ads',
      '.adsbygoogle',
      '.advertisement',
      '.banner-ads',
      '.ad-container',
      '.ad-wrapper',
      '.adblock',
      '.ad-banner',
      '.sponsored-content',
      '.advertisement-wrapper',
      '.ad-placement',
      '.pub_300x250',
      '.pub_300x250m',
      '.pub_728x90',
      '.text-ad',
      '.text_ad',
      '.text_ads',
      '.text-ads',
      '.ad-text',
      '.sticky-ad',
      '.ad-sticky',
      '.ad-topbanner',
      '.ad-box',
      '.ad-billboard',
      '.adunitContainer',
      '.dfp-ad',
      '.partner-ads',
      '.sponsored',
      '.promoted',
      '.adv',
      '.advertisement-container',
      '.top-ads',
      '.side-ads',
      '.right-ads',
      '.bottom-ads',
      '.footer-ads',
      '.header-ads',
      '.ad-section',
      '.ad-zone',
      '.afs_ads',
      '.native-ad',
      '.ad-slot',
      '.ad-panel',
      '.ad-break',
      '.video-ads',
      '.video-ad-container'
    ];
    
    // --- Usage in the code ---
    if (config.removeAds) {
      const combinedSelector = adSelectors.join(', ');
      document.querySelectorAll(combinedSelector).forEach(adElement => {
        try {
          // Special handling for iframes to avoid errors like "Iframe width is less than or equal to 1"
          if (adElement.tagName.toLowerCase() === 'iframe') {
            // Set a minimum width/height before removal to avoid errors
            if (adElement.width <= 1) adElement.width = 2;
            if (adElement.height <= 1) adElement.height = 2;
          }
          
          // Add additional error handling for Mixed Content errors
          // This helps with errors like "Mixed Content: The page was loaded over HTTPS, but requested an insecure script"
          try {
            adElement.remove();
            removed.ads++;
          } catch (e) {
            // If removal fails, try to hide it instead
            try {
              adElement.style.display = 'none';
              removed.ads++;
            } catch (innerError) {
              if (logResults) console.warn('Could not remove or hide ad element:', adElement, e, innerError);
            }
          }
        } catch (e) {
          if (logResults) console.warn('Error processing ad element:', adElement, e);
        }
      });
    }
  }

  // --- 3. SVG Image Removal ---
  if (config.removeSvgImages) {
    document.querySelectorAll('img').forEach(img => {
      try {
        // Check if src attribute contains .svg
        if (img.src && (img.src.toLowerCase().endsWith('.svg') || img.src.toLowerCase().includes('.svg?'))) {
          img.remove();
          removed.svgImages++;
        }
        // Also check for image/svg+xml in src
        else if (img.src && img.src.includes('data:image/svg+xml')) {
          img.remove();
          removed.svgImages++;
        }
      } catch (e) {
        if (logResults) console.warn('Could not remove SVG image:', img, e);
      }
    });
  }

  // --- 4. Attribute and Class Removal ---
  // Iterate through all elements (*) ONCE for efficiency if any attribute/class removal is enabled
  if (config.removeStyleAttribute || config.removeDeprecatedStyleAttributes || config.removeDataAttributes || config.removeBootstrapClasses || config.removeTailwindClasses) {

    const deprecatedAttrs = ['align', 'background', 'bgcolor', 'border', 'cellpadding', 'cellspacing', 'color', 'height', 'width', 'size', 'text', 'vlink', 'alink']; // Common deprecated ones

    // --- Bootstrap class patterns (EXAMPLES - not exhaustive, may remove layout) ---
    // Focus on color, spacing, border, typography, buttons, alerts, badges (common styling targets)
    const bsPrefixes = ['text-', 'bg-', 'border-', 'p-', 'm-', 'px-', 'py-', 'mx-', 'my-', 'fs-', 'fw-', 'lh-', 'btn-', 'alert-', 'badge-', 'opacity-'];
    const bsExactClasses = ['rounded', 'rounded-pill', 'shadow', 'shadow-sm', 'shadow-lg', 'text-decoration-none', 'text-wrap', 'text-nowrap', 'text-break', 'text-lowercase', 'text-uppercase', 'text-capitalize', 'font-monospace', 'fst-italic', 'fw-bold', 'fw-normal', 'fw-light', 'btn', 'alert', 'badge']; // Add more specific common styling classes if needed

    // --- Tailwind class patterns (EXAMPLES - not exhaustive, HIGHLY likely to remove layout) ---
    // Focus on color, spacing, border, typography, effects. Avoids flex/grid explicitly but prefixes might overlap.
    const twPrefixes = [
        'bg-', 'text-', 'border-', 'divide-',                // Color, Border, Divide
        'p-', 'px-', 'py-', 'pt-', 'pr-', 'pb-', 'pl-',      // Padding
        'm-', 'mx-', 'my-', 'mt-', 'mr-', 'mb-', 'ml-', 'space-', // Margin, Space
        'w-', 'h-', 'min-w-', 'max-w-', 'min-h-', 'max-h-',  // Sizing (can affect layout)
        'font-', 'text-xs', 'text-sm', 'text-base', 'text-lg', 'text-xl', // Font & Text Size (add larger sizes if needed)
        'italic', 'not-italic',                             // Font Style
        'font-thin', 'font-extralight', 'font-light', 'font-normal', 'font-medium', 'font-semibold', 'font-bold', 'font-extrabold', 'font-black', // Font Weight
        'uppercase', 'lowercase', 'capitalize', 'normal-case', // Text Transform
        'leading-', 'tracking-', 'whitespace-', 'break-',   // Text Formatting
        'list-', 'decoration-',                             // List & Decoration
        'placeholder-', 'outline-', 'ring-', 'shadow-', 'opacity-', 'mix-blend-', 'bg-blend-', // Effects
        'rounded', 'rounded-s-', 'rounded-e-', 'rounded-t-', 'rounded-r-', 'rounded-b-', 'rounded-l-', // Rounded corners
        'cursor-', 'select-'                                // Interactivity utils often for styling
    ];
    // Regex to potentially catch prefixes with modifiers (sm:, hover:, etc.) - this makes it broader
    const twModifierRegex = /^(sm:|md:|lg:|xl:|2xl:|hover:|focus:|active:|disabled:|visited:|dark:|motion-safe:|motion-reduce:|first:|last:|odd:|even:)/;


    document.querySelectorAll('*').forEach(element => {
      // Skip removal for tags we plan to remove entirely anyway? Maybe not needed, querySelectorAll runs once.

      // Remove inline style attribute
      if (config.removeStyleAttribute && element.hasAttribute('style')) {
        try {
          element.removeAttribute('style');
          removed.attributes.style++;
        } catch (e) { if (logResults) console.warn('Could not remove style attribute:', element, e); }
      }

      // Remove deprecated styling attributes
      if (config.removeDeprecatedStyleAttributes) {
        deprecatedAttrs.forEach(attrName => {
          if (element.hasAttribute(attrName)) {
            try {
              element.removeAttribute(attrName);
              removed.attributes.deprecated++;
            } catch (e) { if (logResults) console.warn(`Could not remove deprecated attribute ${attrName}:`, element, e); }
          }
        });
      }

      // Remove data-* attributes (HIGH RISK)
      if (config.removeDataAttributes) {
        // Define a list of data attributes to preserve specifically for <img> tags
        const preservedImageRelatedDataAttributes = [
          'data-lazyload',
          'data-src',
          'data-srcset',
          'data-original',
          'data-lazy-src',
          'data-lowsrc',
          'data-url', // Generic, but often used for images
          'data-image-url',
          'data-fullsrc',
          'data-hirespic'
          // Add any other image-specific data attributes you want to preserve
        ];

        const dataAttrsToRemove = [];
        for (let i = 0; i < element.attributes.length; i++) {
          const attrName = element.attributes[i].name;
          if (attrName.startsWith('data-')) {
            // Check if the element is an <img> tag and the attribute is in our preserved list
            if (element.tagName.toLowerCase() === 'img' && preservedImageRelatedDataAttributes.includes(attrName)) {
              // If it's an img tag and a preserved attribute, do nothing (don't add to removal list)
              if (logResults) console.log(`Preserving data attribute '${attrName}' for image:`, element);
            } else {
              dataAttrsToRemove.push(attrName);
            }
          }
        }
        dataAttrsToRemove.forEach(attrName => {
          try {
            element.removeAttribute(attrName);
            removed.attributes.data++;
          } catch (e) { if (logResults) console.warn(`Could not remove data attribute ${attrName}:`, element, e); }
        });
      }

      // Remove framework classes
      if ((config.removeBootstrapClasses || config.removeTailwindClasses) && element.classList.length > 0) {
         const classesToRemove = new Set();
         const currentClasses = Array.from(element.classList);

         currentClasses.forEach(className => {
             // Bootstrap Checks
             if (config.removeBootstrapClasses) {
                 if (bsExactClasses.includes(className) || bsPrefixes.some(prefix => className.startsWith(prefix))) {
                     classesToRemove.add(className);
                 }
             }

             // Tailwind Checks
             if (config.removeTailwindClasses) {
                 const baseClassName = className.replace(twModifierRegex, ''); // Get class name without modifiers for prefix check
                 if (twPrefixes.some(prefix => baseClassName.startsWith(prefix))) {
                    classesToRemove.add(className);
                 }
             }
         });

         if (classesToRemove.size > 0) {
            try {
                element.classList.remove(...classesToRemove);
                // Increment counts based on which framework's patterns matched
                // This isn't perfect if classes match both, but gives an idea
                classesToRemove.forEach(removedClass => {
                    const baseClassName = removedClass.replace(twModifierRegex, '');
                    if (config.removeBootstrapClasses && (bsExactClasses.includes(removedClass) || bsPrefixes.some(prefix => removedClass.startsWith(prefix)))) {
                         removed.classes.bootstrap++;
                    } else if (config.removeTailwindClasses && (twPrefixes.some(prefix => baseClassName.startsWith(prefix)))) {
                         // Check if it wasn't already counted as Bootstrap
                         removed.classes.tailwind++;
                    }
                    // Note: A class could potentially be counted twice if patterns overlap significantly and both are enabled.
                });
            } catch (e) { if (logResults) console.warn(`Could not remove classes [${[...classesToRemove].join(', ')}]:`, element, e); }
         }
      } // End framework class check
    }); // End querySelectorAll('*').forEach
  } // End if(attribute/class removal enabled)


  // --- 5. 1x1 Image Removal (Run after general cleanup) ---
  if (config.remove1x1Images) {
    document.querySelectorAll('img').forEach(img => {
        const checkAndRemoveImage = (imageElement) => {
            if (imageElement.naturalWidth === 1 || imageElement.naturalHeight === 1) {
                try {
                    const src = imageElement.src;
                    imageElement.remove();
                    removed.images1x1++;
                    if (logResults) console.log('Removed 1x1 image:', src);
                } catch (e) {
                    if (logResults) console.warn('Could not remove 1x1 image:', imageElement.src, e);
                }
            }
        };
        if (img.complete && img.naturalWidth > 0) {
            checkAndRemoveImage(img);
        } else if (!img.complete) {
            img.addEventListener('load', function() { checkAndRemoveImage(this); }, { once: true });
            img.addEventListener('error', function() { /* Handle error if needed */ }, { once: true });
        }
    });
  }

  // --- 6. Log Summary ---
  if (logResults) {
    const summary = [];
    // Tags
    Object.entries(removed.tags).forEach(([key, value]) => {
      if (value > 0) summary.push(`${value} ${key}`);
    });
    // Attributes
    if (removed.attributes.style > 0) summary.push(`${removed.attributes.style} style attributes`);
    if (removed.attributes.deprecated > 0) summary.push(`${removed.attributes.deprecated} deprecated attributes`);
    if (removed.attributes.data > 0) summary.push(`${removed.attributes.data} data attributes`);
    // Classes
    if (removed.classes.bootstrap > 0) summary.push(`${removed.classes.bootstrap} Bootstrap classes`);
    if (removed.classes.tailwind > 0) summary.push(`${removed.classes.tailwind} Tailwind classes`);
    // Images
    if (removed.images1x1 > 0) summary.push(`${removed.images1x1} 1x1 images`);
    // Google Ads
    if (removed.ads > 0) summary.push(`${removed.ads} advertisements`);
    // SVG Images
    if (removed.svgImages > 0) summary.push(`${removed.svgImages} SVG images`);

    if (summary.length > 0) {
      console.log(`Cleanup complete [${new Date().toLocaleString()}] Removed: ${summary.join(', ')}`);
    } else {
      console.log(`Cleanup complete [${new Date().toLocaleString()}]: No targeted elements, attributes, or classes found or removed based on current options.`);
    }
  }

  // --- 7. Return Counts ---
  return removed;
}

// Export the function if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = cleanupPageAdvanced;
} 