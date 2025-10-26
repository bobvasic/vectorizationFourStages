use pyo3::prelude::*;
use image::GenericImageView;

mod color_quantization;
mod edge_detection;
mod model_loader;
mod ai_edge_detection;
mod color_lab;
mod semantic_segmentation;
mod simd_ops;

#[pymodule]
fn rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(quantize_colors, m)?)?;
    m.add_function(wrap_pyfunction!(detect_edges_sobel, m)?)?;
    m.add_function(wrap_pyfunction!(detect_edges_canny, m)?)?;
    m.add_function(wrap_pyfunction!(detect_edges_ai, m)?)?;
    m.add_function(wrap_pyfunction!(quantize_colors_lab, m)?)?;
    m.add_function(wrap_pyfunction!(init_onnx, m)?)?;
    m.add_function(wrap_pyfunction!(check_model_exists, m)?)?;
    m.add_function(wrap_pyfunction!(get_model_info, m)?)?;
    m.add_function(wrap_pyfunction!(segment_image, m)?)?;
    m.add_function(wrap_pyfunction!(detect_salient_regions, m)?)?;
    Ok(())
}

#[pyfunction]
fn segment_image<'py>(
    py: Python<'py>,
    image_bytes: Vec<u8>,
    num_regions: usize
) -> PyResult<Vec<u8>> {
    py.allow_threads(|| {
        semantic_segmentation::segment_image(&image_bytes, num_regions)
    })
}

#[pyfunction]
fn detect_salient_regions<'py>(
    py: Python<'py>,
    image_bytes: Vec<u8>
) -> PyResult<Vec<u8>> {
    py.allow_threads(|| {
        semantic_segmentation::detect_salient_regions(&image_bytes)
    })
}

#[pyfunction]
fn quantize_colors<'py>(py: Python<'py>, image_bytes: Vec<u8>, k: usize, max_iter: usize) -> PyResult<Vec<u8>> {
    py.allow_threads(|| color_quantization::quantize(&image_bytes, k, max_iter))
}

#[pyfunction]
fn detect_edges_sobel<'py>(py: Python<'py>, image_bytes: Vec<u8>, threshold: u8) -> PyResult<Vec<u8>> {
    py.allow_threads(|| edge_detection::sobel_edge_detection(&image_bytes, threshold))
}

#[pyfunction]
fn detect_edges_canny<'py>(py: Python<'py>, image_bytes: Vec<u8>, low: u8, high: u8) -> PyResult<Vec<u8>> {
    py.allow_threads(|| edge_detection::canny_edge_detection(&image_bytes, low, high))
}

#[pyfunction]
fn init_onnx(_py: Python) -> PyResult<()> {
    model_loader::init_onnx_runtime()
}

#[pyfunction]
fn check_model_exists(_py: Python, model_path: String) -> PyResult<bool> {
    Ok(model_loader::model_exists(&model_path))
}

#[pyfunction]
fn get_model_info(_py: Python, model_path: String) -> PyResult<Option<String>> {
    Ok(model_loader::get_model_version(&model_path))
}

#[pyfunction]
#[pyo3(signature = (image_bytes, threshold, model_path=None))]
fn detect_edges_ai<'py>(
    py: Python<'py>,
    image_bytes: Vec<u8>,
    threshold: u8,
    model_path: Option<String>
) -> PyResult<Vec<u8>> {
    py.allow_threads(|| {
        ai_edge_detection::ai_edge_detection(
            &image_bytes,
            model_path.as_deref(),
            threshold
        )
    })
}

#[pyfunction]
fn quantize_colors_lab<'py>(
    py: Python<'py>,
    image_bytes: Vec<u8>,
    k: usize,
    max_iter: usize
) -> PyResult<Vec<u8>> {
    py.allow_threads(|| {
        // Load image
        let img = image::load_from_memory(&image_bytes)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        let rgb = img.to_rgb8();
        let (w, h) = img.dimensions();
        
        // Extract RGB pixels
        let pixels: Vec<(u8, u8, u8)> = rgb.pixels()
            .map(|p| (p[0], p[1], p[2]))
            .collect();
        
        // Perform LAB k-means
        let centroids = color_lab::kmeans_lab(&pixels, k, max_iter);
        
        // Map each pixel to nearest centroid
        let quantized: Vec<u8> = rgb.pixels()
            .flat_map(|p| {
                let (r, g, b) = (p[0], p[1], p[2]);
                let (pl, pa, pb) = color_lab::rgb_to_lab(r, g, b);
                
                // Find nearest centroid in LAB space
                let mut min_dist = f32::MAX;
                let mut best_color = centroids[0];
                
                for &(cr, cg, cb) in &centroids {
                    let (cl, ca, cb_lab) = color_lab::rgb_to_lab(cr, cg, cb);
                    let dist = color_lab::color_distance_lab(pl, pa, pb, cl, ca, cb_lab);
                    if dist < min_dist {
                        min_dist = dist;
                        best_color = (cr, cg, cb);
                    }
                }
                
                vec![best_color.0, best_color.1, best_color.2]
            })
            .collect();
        
        // Create output image
        let img_buf = image::ImageBuffer::<image::Rgb<u8>, _>::from_raw(w, h, quantized)
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Failed to create image"))?;
        
        let mut png_data = Vec::new();
        image::DynamicImage::ImageRgb8(img_buf)
            .write_to(&mut std::io::Cursor::new(&mut png_data), image::ImageFormat::Png)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        Ok(png_data)
    })
}
