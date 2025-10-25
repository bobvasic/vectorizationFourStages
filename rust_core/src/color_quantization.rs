use pyo3::exceptions::PyValueError;
use image::GenericImageView;
use pyo3::prelude::*;
use rayon::prelude::*;

pub fn quantize(image_bytes: &[u8], k: usize, max_iter: usize) -> PyResult<Vec<u8>> {
    let img = image::load_from_memory(image_bytes)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    
    let rgba = img.to_rgba8();
    let (w, h) = img.dimensions();
    let raw_pixels = rgba.as_raw();
    
    let pixels: Vec<[f32; 3]> = (0..raw_pixels.len())
        .step_by(4)
        .map(|i| [raw_pixels[i] as f32, raw_pixels[i+1] as f32, raw_pixels[i+2] as f32])
        .collect();

    if k == 0 || pixels.is_empty() {
        return Err(PyValueError::new_err("Invalid k or empty image"));
    }

    let step = (pixels.len() / k).max(1);
    let mut centroids: Vec<[f32; 3]> = pixels.iter().step_by(step).take(k).cloned().collect();
    if centroids.len() < k {
        centroids.resize(k, pixels[0]);
    }

    let mut assignments = vec![0usize; pixels.len()];
    
    for _ in 0..max_iter {
        assignments.par_iter_mut().enumerate().for_each(|(i, a)| {
            let p = pixels[i];
            let mut best_idx = 0;
            let mut min_dist = f32::MAX;
            
            for (ci, c) in centroids.iter().enumerate() {
                let dist = (p[0]-c[0]).powi(2) + (p[1]-c[1]).powi(2) + (p[2]-c[2]).powi(2);
                if dist < min_dist {
                    min_dist = dist;
                    best_idx = ci;
                }
            }
            *a = best_idx;
        });

        let mut sums = vec![[0f32; 3]; k];
        let mut counts = vec![0u32; k];
        
        for (idx, pixel) in assignments.iter().zip(&pixels) {
            sums[*idx][0] += pixel[0];
            sums[*idx][1] += pixel[1];
            sums[*idx][2] += pixel[2];
            counts[*idx] += 1;
        }
        
        for i in 0..k {
            if counts[i] > 0 {
                let c = counts[i] as f32;
                centroids[i] = [sums[i][0]/c, sums[i][1]/c, sums[i][2]/c];
            }
        }
    }

    let mut output = Vec::with_capacity((w * h * 4) as usize);
    for idx in assignments {
        let c = centroids[idx];
        output.push(c[0].round() as u8);
        output.push(c[1].round() as u8);
        output.push(c[2].round() as u8);
        output.push(255);
    }

    let img_buf = image::ImageBuffer::<image::Rgba<u8>, _>::from_raw(w, h, output)
        .ok_or_else(|| PyValueError::new_err("Failed to create image buffer"))?;
    
    let mut png_data = Vec::new();
    image::DynamicImage::ImageRgba8(img_buf)
        .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    
    Ok(png_data)
}
