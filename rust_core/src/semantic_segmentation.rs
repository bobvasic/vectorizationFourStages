use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use image::{DynamicImage, GenericImageView, ImageBuffer, Rgb};
use std::collections::HashMap;

/// Semantic segmentation for object-aware vectorization
/// Provides region classification: background, foreground, object boundaries

/// Simple threshold-based segmentation (stub for future ML model)
pub fn segment_image(
    image_bytes: &[u8],
    num_regions: usize
) -> PyResult<Vec<u8>> {
    let img = image::load_from_memory(image_bytes)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to load image: {}", e)))?;
    
    let (width, height) = img.dimensions();
    let rgb = img.to_rgb8();
    
    // K-means-based region segmentation
    let segments = kmeans_segmentation(&rgb, num_regions);
    
    // Create segmentation mask (each pixel assigned to region ID)
    let mask: Vec<u8> = segments.iter()
        .map(|&region_id| ((region_id as f32 / num_regions as f32) * 255.0) as u8)
        .collect();
    
    // Convert to PNG
    let mask_img = ImageBuffer::<image::Luma<u8>, _>::from_raw(width, height, mask)
        .ok_or_else(|| PyRuntimeError::new_err("Failed to create mask image"))?;
    
    let mut png_data = Vec::new();
    DynamicImage::ImageLuma8(mask_img)
        .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    Ok(png_data)
}

/// K-means segmentation in LAB color space
fn kmeans_segmentation(img: &ImageBuffer<Rgb<u8>, Vec<u8>>, k: usize) -> Vec<usize> {
    let (width, height) = img.dimensions();
    let pixels: Vec<(f32, f32, f32)> = img.pixels()
        .map(|p| {
            let lab = crate::color_lab::rgb_to_lab(p[0], p[1], p[2]);
            lab
        })
        .collect();
    
    // Initialize centroids randomly
    let mut centroids: Vec<(f32, f32, f32)> = (0..k)
        .map(|i| {
            let idx = (i * pixels.len() / k) % pixels.len();
            pixels[idx]
        })
        .collect();
    
    let mut assignments = vec![0usize; pixels.len()];
    
    // K-means iterations
    for _iter in 0..10 {
        // Assign pixels to nearest centroid
        for (i, &(l, a, b)) in pixels.iter().enumerate() {
            let mut min_dist = f32::MAX;
            let mut best_k = 0;
            
            for (k_idx, &(cl, ca, cb)) in centroids.iter().enumerate() {
                let dist = crate::color_lab::color_distance_lab(l, a, b, cl, ca, cb);
                if dist < min_dist {
                    min_dist = dist;
                    best_k = k_idx;
                }
            }
            
            assignments[i] = best_k;
        }
        
        // Update centroids
        let mut sums = vec![(0.0f32, 0.0f32, 0.0f32); k];
        let mut counts = vec![0usize; k];
        
        for (i, &(l, a, b)) in pixels.iter().enumerate() {
            let k_idx = assignments[i];
            sums[k_idx].0 += l;
            sums[k_idx].1 += a;
            sums[k_idx].2 += b;
            counts[k_idx] += 1;
        }
        
        for k_idx in 0..k {
            if counts[k_idx] > 0 {
                centroids[k_idx] = (
                    sums[k_idx].0 / counts[k_idx] as f32,
                    sums[k_idx].1 / counts[k_idx] as f32,
                    sums[k_idx].2 / counts[k_idx] as f32,
                );
            }
        }
    }
    
    assignments
}

/// Extract object layers from segmentation mask
pub fn extract_layers(
    image_bytes: &[u8],
    mask_bytes: &[u8]
) -> PyResult<Vec<Vec<u8>>> {
    let img = image::load_from_memory(image_bytes)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to load image: {}", e)))?;
    
    let mask = image::load_from_memory(mask_bytes)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to load mask: {}", e)))?;
    
    let (width, height) = img.dimensions();
    let rgb = img.to_rgb8();
    let mask_gray = mask.to_luma8();
    
    // Group pixels by region
    let mut regions: HashMap<u8, Vec<(u32, u32)>> = HashMap::new();
    
    for y in 0..height {
        for x in 0..width {
            let region_id = mask_gray.get_pixel(x, y)[0];
            regions.entry(region_id).or_insert_with(Vec::new).push((x, y));
        }
    }
    
    // Create separate images for each layer
    let mut layers = Vec::new();
    
    for (_region_id, coords) in regions.iter() {
        let mut layer_data = vec![0u8; (width * height * 4) as usize]; // RGBA
        
        for &(x, y) in coords {
            let pixel = rgb.get_pixel(x, y);
            let idx = ((y * width + x) * 4) as usize;
            layer_data[idx] = pixel[0];     // R
            layer_data[idx + 1] = pixel[1]; // G
            layer_data[idx + 2] = pixel[2]; // B
            layer_data[idx + 3] = 255;      // A
        }
        
        // Convert to PNG
        let layer_img = ImageBuffer::<image::Rgba<u8>, _>::from_raw(width, height, layer_data)
            .ok_or_else(|| PyRuntimeError::new_err("Failed to create layer image"))?;
        
        let mut png_data = Vec::new();
        DynamicImage::ImageRgba8(layer_img)
            .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        
        layers.push(png_data);
    }
    
    Ok(layers)
}

/// Detect salient objects using contrast and color analysis
pub fn detect_salient_regions(
    image_bytes: &[u8]
) -> PyResult<Vec<u8>> {
    let img = image::load_from_memory(image_bytes)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to load image: {}", e)))?;
    
    let (width, height) = img.dimensions();
    let rgb = img.to_rgb8();
    
    // Compute saliency map (sequential due to shared reference)
    let mut saliency = vec![0u8; (width * height) as usize];
    
    for y in 0..height {
        for x in 0..width {
            let idx = (y * width + x) as usize;
            saliency[idx] = compute_local_saliency(&rgb, x, y, width, height);
        }
    }
    
    // Convert to PNG
    let saliency_img = ImageBuffer::<image::Luma<u8>, _>::from_raw(width, height, saliency)
        .ok_or_else(|| PyRuntimeError::new_err("Failed to create saliency map"))?;
    
    let mut png_data = Vec::new();
    DynamicImage::ImageLuma8(saliency_img)
        .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    
    Ok(png_data)
}

/// Compute local saliency using color and luminance contrast
fn compute_local_saliency(
    img: &ImageBuffer<Rgb<u8>, Vec<u8>>,
    x: u32,
    y: u32,
    width: u32,
    height: u32
) -> u8 {
    let center = img.get_pixel(x, y);
    let (cl, ca, cb) = crate::color_lab::rgb_to_lab(center[0], center[1], center[2]);
    
    let window_size = 5;
    let mut contrast_sum = 0.0f32;
    let mut count = 0;
    
    for dy in -(window_size as i32)..=(window_size as i32) {
        for dx in -(window_size as i32)..=(window_size as i32) {
            let nx = (x as i32 + dx).max(0).min(width as i32 - 1) as u32;
            let ny = (y as i32 + dy).max(0).min(height as i32 - 1) as u32;
            
            if nx == x && ny == y {
                continue;
            }
            
            let neighbor = img.get_pixel(nx, ny);
            let (nl, na, nb) = crate::color_lab::rgb_to_lab(neighbor[0], neighbor[1], neighbor[2]);
            
            let dist = crate::color_lab::color_distance_lab(cl, ca, cb, nl, na, nb);
            contrast_sum += dist;
            count += 1;
        }
    }
    
    let saliency = if count > 0 {
        (contrast_sum / count as f32).min(255.0)
    } else {
        0.0
    };
    
    saliency as u8
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_segmentation() {
        // Basic smoke test
        let img = image::RgbImage::new(100, 100);
        let segments = kmeans_segmentation(&img, 5);
        assert_eq!(segments.len(), 100 * 100);
    }
}
