use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use rayon::prelude::*;
use image::GenericImageView;

pub fn sobel_edge_detection(image_bytes: &[u8], threshold: u8) -> PyResult<Vec<u8>> {
    let img = image::load_from_memory(image_bytes)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    
    let gray = img.to_luma8();
    let (w, h) = img.dimensions();
    
    let sobel_x = [[-1i32, 0, 1], [-2, 0, 2], [-1, 0, 1]];
    let sobel_y = [[-1i32, -2, -1], [0, 0, 0], [1, 2, 1]];
    
    let mut edges = vec![0u8; (w * h) as usize];
    
    edges.par_chunks_mut(w as usize).enumerate().for_each(|(y, row)| {
        if y == 0 || y >= (h as usize - 1) { return; }
        
        for x in 1..(w as usize - 1) {
            let mut gx = 0i32;
            let mut gy = 0i32;
            
            for ky in 0..3 {
                for kx in 0..3 {
                    let px = gray.get_pixel((x + kx - 1) as u32, (y + ky - 1) as u32)[0] as i32;
                    gx += px * sobel_x[ky][kx];
                    gy += px * sobel_y[ky][kx];
                }
            }
            
            let magnitude = ((gx * gx + gy * gy) as f32).sqrt() as u8;
            row[x] = if magnitude > threshold { 255 } else { 0 };
        }
    });
    
    let edge_img = image::ImageBuffer::from_raw(w, h, edges)
        .ok_or_else(|| PyValueError::new_err("Failed to create edge image"))?;
    
    let mut png_data = Vec::new();
    image::DynamicImage::ImageLuma8(edge_img)
        .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    
    Ok(png_data)
}

pub fn canny_edge_detection(_image_bytes: &[u8], _low: u8, _high: u8) -> PyResult<Vec<u8>> {
    Err(PyValueError::new_err("Canny not implemented yet - use Sobel"))
}
