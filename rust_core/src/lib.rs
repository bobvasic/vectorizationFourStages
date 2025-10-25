use pyo3::prelude::*;

mod color_quantization;
mod edge_detection;

#[pymodule]
fn rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(quantize_colors, m)?)?;
    m.add_function(wrap_pyfunction!(detect_edges_sobel, m)?)?;
    m.add_function(wrap_pyfunction!(detect_edges_canny, m)?)?;
    Ok(())
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
