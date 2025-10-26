use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::Mutex;
use std::collections::HashMap;

/// Model cache to avoid reloading models on every inference
/// Note: Using String keys for paths instead of Arc<Session> for now
/// Full ONNX integration will be completed in Week 6
static MODEL_CACHE: Mutex<Option<HashMap<String, bool>>> = Mutex::new(None);

/// Initialize the ONNX Runtime environment
pub fn init_onnx_runtime() -> PyResult<()> {
    // ONNX Runtime 1.16 initializes automatically
    // Just initialize our cache
    let mut cache = MODEL_CACHE.lock().unwrap();
    if cache.is_none() {
        *cache = Some(HashMap::new());
    }
    
    Ok(())
}

/// Load ONNX model with caching (stub for Week 6 implementation)
pub fn load_model(model_path: &str) -> PyResult<bool> {
    // Check cache first
    let mut cache = MODEL_CACHE.lock().unwrap();
    let cache_map = cache.as_mut().unwrap();
    
    if let Some(&cached) = cache_map.get(model_path) {
        return Ok(cached);
    }
    
    // Check if model file exists
    let path = PathBuf::from(model_path);
    
    if !path.exists() {
        return Err(PyRuntimeError::new_err(format!(
            "Model file not found: {}. Please download the model first.", 
            model_path
        )));
    }
    
    // Mark as cached (actual loading will be in Week 6)
    cache_map.insert(model_path.to_string(), true);
    
    Ok(true)
}

/// Check if model exists
pub fn model_exists(model_path: &str) -> bool {
    PathBuf::from(model_path).exists()
}

/// Get model version from filename
pub fn get_model_version(model_path: &str) -> Option<String> {
    let path = PathBuf::from(model_path);
    let filename = path.file_stem()?.to_str()?;
    
    // Extract version from filename pattern: model_name_v1.2.3.onnx
    if let Some(version_start) = filename.rfind("_v") {
        return Some(filename[version_start + 2..].to_string());
    }
    
    None
}

/// Clear model cache (useful for updates)
pub fn clear_model_cache() {
    let mut cache = MODEL_CACHE.lock().unwrap();
    if let Some(cache_map) = cache.as_mut() {
        cache_map.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_model_version_extraction() {
        assert_eq!(
            get_model_version("edge_detection_v1.0.0.onnx"),
            Some("1.0.0".to_string())
        );
        assert_eq!(
            get_model_version("color_optimizer_v2.1.3.onnx"),
            Some("2.1.3".to_string())
        );
        assert_eq!(get_model_version("no_version.onnx"), None);
    }

    #[test]
    fn test_model_exists() {
        assert!(!model_exists("nonexistent_model.onnx"));
    }
}
