/// LAB color space conversion for perceptually uniform color processing
/// LAB color space is designed to approximate human vision - equal distances
/// in LAB space correspond to roughly equal perceived color differences.

const D65_X: f32 = 95.047;
const D65_Y: f32 = 100.0;
const D65_Z: f32 = 108.883;

/// RGB to LAB color space conversion
/// Input: RGB values in [0, 255]
/// Output: (L, a, b) where L in [0, 100], a/b in [-128, 127]
pub fn rgb_to_lab(r: u8, g: u8, b: u8) -> (f32, f32, f32) {
    // Step 1: RGB to linear RGB
    let r_linear = gamma_to_linear(r as f32 / 255.0);
    let g_linear = gamma_to_linear(g as f32 / 255.0);
    let b_linear = gamma_to_linear(b as f32 / 255.0);
    
    // Step 2: Linear RGB to XYZ (D65 illuminant)
    let x = r_linear * 0.4124564 + g_linear * 0.3575761 + b_linear * 0.1804375;
    let y = r_linear * 0.2126729 + g_linear * 0.7151522 + b_linear * 0.0721750;
    let z = r_linear * 0.0193339 + g_linear * 0.1191920 + b_linear * 0.9503041;
    
    // Step 3: XYZ to LAB
    xyz_to_lab(x * 100.0, y * 100.0, z * 100.0)
}

/// LAB to RGB color space conversion
/// Input: (L, a, b) where L in [0, 100], a/b in [-128, 127]
/// Output: RGB values in [0, 255]
pub fn lab_to_rgb(l: f32, a: f32, b: f32) -> (u8, u8, u8) {
    // Step 1: LAB to XYZ
    let (x, y, z) = lab_to_xyz(l, a, b);
    
    // Step 2: XYZ to linear RGB
    let x = x / 100.0;
    let y = y / 100.0;
    let z = z / 100.0;
    
    let r_linear = x *  3.2404542 + y * -1.5371385 + z * -0.4985314;
    let g_linear = x * -0.9692660 + y *  1.8760108 + z *  0.0415560;
    let b_linear = x *  0.0556434 + y * -0.2040259 + z *  1.0572252;
    
    // Step 3: Linear RGB to sRGB
    let r = (linear_to_gamma(r_linear) * 255.0).round().clamp(0.0, 255.0) as u8;
    let g = (linear_to_gamma(g_linear) * 255.0).round().clamp(0.0, 255.0) as u8;
    let b = (linear_to_gamma(b_linear) * 255.0).round().clamp(0.0, 255.0) as u8;
    
    (r, g, b)
}

/// Calculate perceptual color distance in LAB space (Delta E)
/// This is much more accurate than Euclidean distance in RGB
pub fn color_distance_lab(l1: f32, a1: f32, b1: f32, l2: f32, a2: f32, b2: f32) -> f32 {
    let dl = l1 - l2;
    let da = a1 - a2;
    let db = b1 - b2;
    
    (dl * dl + da * da + db * db).sqrt()
}

/// K-means clustering in LAB space for perceptually uniform color quantization
/// This produces much better results than RGB-based k-means
pub fn kmeans_lab(pixels_rgb: &[(u8, u8, u8)], k: usize, max_iter: usize) -> Vec<(u8, u8, u8)> {
    if pixels_rgb.is_empty() || k == 0 {
        return Vec::new();
    }
    
    // Convert all pixels to LAB
    let pixels_lab: Vec<(f32, f32, f32)> = pixels_rgb.iter()
        .map(|&(r, g, b)| rgb_to_lab(r, g, b))
        .collect();
    
    // Initialize centroids (k-means++ would be better, but simple sampling for now)
    let step = (pixels_lab.len() / k).max(1);
    let mut centroids: Vec<(f32, f32, f32)> = pixels_lab.iter()
        .step_by(step)
        .take(k)
        .cloned()
        .collect();
    
    // Ensure we have exactly k centroids
    while centroids.len() < k {
        centroids.push(pixels_lab[0]);
    }
    
    let mut assignments = vec![0usize; pixels_lab.len()];
    
    // K-means iterations
    for _ in 0..max_iter {
        // Assignment step
        for (i, &(l, a, b)) in pixels_lab.iter().enumerate() {
            let mut min_dist = f32::MAX;
            let mut best_cluster = 0;
            
            for (ci, &(cl, ca, cb)) in centroids.iter().enumerate() {
                let dist = color_distance_lab(l, a, b, cl, ca, cb);
                if dist < min_dist {
                    min_dist = dist;
                    best_cluster = ci;
                }
            }
            
            assignments[i] = best_cluster;
        }
        
        // Update step
        let mut sums = vec![(0.0f32, 0.0f32, 0.0f32); k];
        let mut counts = vec![0u32; k];
        
        for (i, &(l, a, b)) in pixels_lab.iter().enumerate() {
            let cluster = assignments[i];
            sums[cluster].0 += l;
            sums[cluster].1 += a;
            sums[cluster].2 += b;
            counts[cluster] += 1;
        }
        
        for i in 0..k {
            if counts[i] > 0 {
                let count = counts[i] as f32;
                centroids[i] = (
                    sums[i].0 / count,
                    sums[i].1 / count,
                    sums[i].2 / count
                );
            }
        }
    }
    
    // Convert centroids back to RGB
    centroids.iter()
        .map(|&(l, a, b)| lab_to_rgb(l, a, b))
        .collect()
}

// Helper functions

fn gamma_to_linear(c: f32) -> f32 {
    if c <= 0.04045 {
        c / 12.92
    } else {
        ((c + 0.055) / 1.055).powf(2.4)
    }
}

fn linear_to_gamma(c: f32) -> f32 {
    if c <= 0.0031308 {
        c * 12.92
    } else {
        1.055 * c.powf(1.0 / 2.4) - 0.055
    }
}

fn xyz_to_lab(x: f32, y: f32, z: f32) -> (f32, f32, f32) {
    let fx = lab_f(x / D65_X);
    let fy = lab_f(y / D65_Y);
    let fz = lab_f(z / D65_Z);
    
    let l = 116.0 * fy - 16.0;
    let a = 500.0 * (fx - fy);
    let b = 200.0 * (fy - fz);
    
    (l, a, b)
}

fn lab_to_xyz(l: f32, a: f32, b: f32) -> (f32, f32, f32) {
    let fy = (l + 16.0) / 116.0;
    let fx = a / 500.0 + fy;
    let fz = fy - b / 200.0;
    
    let x = D65_X * lab_f_inv(fx);
    let y = D65_Y * lab_f_inv(fy);
    let z = D65_Z * lab_f_inv(fz);
    
    (x, y, z)
}

fn lab_f(t: f32) -> f32 {
    let delta = 6.0 / 29.0;
    if t > delta * delta * delta {
        t.cbrt()
    } else {
        t / (3.0 * delta * delta) + 4.0 / 29.0
    }
}

fn lab_f_inv(t: f32) -> f32 {
    let delta = 6.0 / 29.0;
    if t > delta {
        t * t * t
    } else {
        3.0 * delta * delta * (t - 4.0 / 29.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rgb_to_lab_white() {
        let (l, a, b) = rgb_to_lab(255, 255, 255);
        assert!((l - 100.0).abs() < 0.1);  // White should have L ≈ 100
        assert!(a.abs() < 1.0);            // a ≈ 0
        assert!(b.abs() < 1.0);            // b ≈ 0
    }

    #[test]
    fn test_rgb_to_lab_black() {
        let (l, a, b) = rgb_to_lab(0, 0, 0);
        assert!((l - 0.0).abs() < 0.1);    // Black should have L ≈ 0
        assert!(a.abs() < 1.0);
        assert!(b.abs() < 1.0);
    }

    #[test]
    fn test_lab_roundtrip() {
        let test_colors = vec![
            (255, 0, 0),     // Red
            (0, 255, 0),     // Green
            (0, 0, 255),     // Blue
            (128, 128, 128), // Gray
        ];
        
        for (r, g, b) in test_colors {
            let (l, a, b_lab) = rgb_to_lab(r, g, b);
            let (r2, g2, b2) = lab_to_rgb(l, a, b_lab);
            
            // Allow small rounding errors
            assert!((r as i32 - r2 as i32).abs() <= 2);
            assert!((g as i32 - g2 as i32).abs() <= 2);
            assert!((b as i32 - b2 as i32).abs() <= 2);
        }
    }

    #[test]
    fn test_color_distance() {
        // Distance from white to black should be large
        let (l1, a1, b1) = rgb_to_lab(255, 255, 255);
        let (l2, a2, b2) = rgb_to_lab(0, 0, 0);
        let dist = color_distance_lab(l1, a1, b1, l2, a2, b2);
        assert!(dist > 90.0);  // Should be close to 100
        
        // Distance from a color to itself should be 0
        let (l, a, b) = rgb_to_lab(128, 64, 192);
        let dist = color_distance_lab(l, a, b, l, a, b);
        assert!(dist < 0.001);
    }
}
