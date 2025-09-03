/**
 * Image Extraction Script
 * =======================
 *
 * Extracts image data from the page as base64 for downloading.
 * Searches for images by URL and converts them to base64 format.
 */

// This function will be called with the imageUrl parameter from Python
async (imageUrl) => {
  const img =
    document.querySelector(`img[src*="${imageUrl.split("/").pop()}"]`) ||
    document.querySelector(`img[src="${imageUrl}"]`);

  if (!img) return null;

  // Create canvas to get image data
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  canvas.width = img.naturalWidth || img.width;
  canvas.height = img.naturalHeight || img.height;

  // Draw image to canvas
  ctx.drawImage(img, 0, 0);

  // Get base64 data
  try {
    const dataURL = canvas.toDataURL("image/png");
    return {
      dataURL: dataURL,
      width: canvas.width,
      height: canvas.height,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
    };
  } catch (e) {
    // Handle CORS or other canvas errors
    return null;
  }
};
