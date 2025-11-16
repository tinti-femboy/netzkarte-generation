// Module-level cache
let cachedImagePath = null;
let cachedCanvas = null;
let cachedCtx = null;
let cachedPixelData = null;
let cachedWidth = 0;
let cachedHeight = 0;

export async function getPixelValue(imagePath, x, y) {
  // If this is a new image, rebuild the cache
  if (imagePath !== cachedImagePath) {
    const img = await loadImage(imagePath);

    cachedCanvas = document.createElement("canvas");
    cachedCanvas.width = img.width;
    cachedCanvas.height = img.height;
    cachedCtx = cachedCanvas.getContext("2d");
    cachedCtx.drawImage(img, 0, 0);

    const imageData = cachedCtx.getImageData(0, 0, img.width, img.height);
    cachedPixelData = imageData.data; // Uint8ClampedArray
    cachedWidth = img.width;
    cachedHeight = img.height;

    cachedImagePath = imagePath;
  }

  // Lookup pixel directly from cachedPixelData
  const index = (y * cachedWidth + x) * 4;
  return {
    r: cachedPixelData[index],
    g: cachedPixelData[index + 1],
    b: cachedPixelData[index + 2],
    a: cachedPixelData[index + 3]
  };
}

// Helper: load image as Promise
function loadImage(src) {
    console.log("loading new image")
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
  });
}


// export function getPixelValue(imagePath, x, y) {
//     return new Promise((resolve, reject) => {
//     const img = new Image();
//     img.crossOrigin = "Anonymous"; // Needed if image is from another domain

//     img.onload = () => {
//         // Off-screen canvas
//         const canvas = document.createElement("canvas");
//         canvas.width = img.width;
//         canvas.height = img.height;

//         const ctx = canvas.getContext("2d");
//         ctx.drawImage(img, 0, 0);

//         const pixelData = ctx.getImageData(x, y, 1, 1).data;
//         resolve({
//         r: pixelData[0],
//         g: pixelData[1],
//         b: pixelData[2],
//         a: pixelData[3]
//         });
//     };

//     img.onerror = (err) => reject(err);
//     img.src = imagePath;
//     });
// }
