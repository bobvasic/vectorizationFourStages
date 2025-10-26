
import React, { useState, useCallback } from 'react';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import { SpinnerIcon } from './components/icons/SpinnerIcon';
import { ArrowPathIcon, ArrowDownTrayIcon, PhotoIcon } from './components/icons/UIIcons';

type Status = 'idle' | 'processing' | 'success' | 'error';
type QualityLevel = 'fast' | 'balanced' | 'high' | 'ultra';

const App: React.FC = () => {
  const [status, setStatus] = useState<Status>('idle');
  const [originalImage, setOriginalImage] = useState<File | null>(null);
  const [originalPreview, setOriginalPreview] = useState<string | null>(null);
  const [vectorizedPreview, setVectorizedPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedQuality, setSelectedQuality] = useState<QualityLevel>('high');
  const [useLab, setUseLab] = useState<boolean>(true);
  const [useAi, setUseAi] = useState<boolean>(true);

  const handleImageSelect = useCallback((file: File, previewUrl: string) => {
    setOriginalImage(file);
    setOriginalPreview(previewUrl);
    setStatus('idle');
    setError(null);
    setVectorizedPreview(null);
  }, []);
  
  const handleError = useCallback((message: string) => {
    setError(message);
    setStatus('error');
    setOriginalImage(null);
    setOriginalPreview(null);
  }, []);

  const handleVectorize = async () => {
    if (!originalImage) return;

    setStatus('processing');
    setError(null);
    setVectorizedPreview(null);
    
    try {
      // Upload image to backend API
      const formData = new FormData();
      formData.append('file', originalImage);
      formData.append('quality', selectedQuality);
      formData.append('use_lab', String(useLab));
      formData.append('use_ai', String(useAi));
      
      const uploadResponse = await fetch(`http://localhost:8000/api/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }
      
      const uploadData = await uploadResponse.json();
      const jobId = uploadData.job_id;
      
      // Poll for status
      let completed = false;
      while (!completed) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
        
        const statusResponse = await fetch(`http://localhost:8000/api/status/${jobId}`);
        const statusData = await statusResponse.json();
        
        if (statusData.status === 'completed') {
          completed = true;
          
          // Download vectorized SVG
          const downloadUrl = `http://localhost:8000/api/download/${jobId}`;
          setVectorizedPreview(downloadUrl);
          setStatus('success');
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.message || 'Processing failed');
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during vectorization';
      setError(errorMessage);
      setStatus('error');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setOriginalImage(null);
    setOriginalPreview(null);
    setVectorizedPreview(null);
    setError(null);
  };

  return (
    <div className="relative min-h-screen w-full bg-black text-gray-200 font-sans overflow-hidden">
      {/* Dotted Background */}
      <div className="absolute inset-0 z-0 bg-[radial-gradient(#16a34a_1px,transparent_1px)] [background-size:24px_24px] opacity-10"></div>
      
      {/* Aurora Glow */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-green-500/20 rounded-full blur-[200px] z-0"
      ></div>

      <div className="relative z-10 flex flex-col min-h-screen px-4 sm:px-6 lg:px-8">
        <Header />

        <main className="flex-grow flex flex-col items-center justify-center py-12">
          {!originalPreview ? (
            <ImageUploader onImageSelect={handleImageSelect} onError={handleError} />
          ) : (
            <div className="w-full max-w-5xl flex flex-col items-center">
              {/* Quality Selection */}
              <div className="mb-8 w-full flex flex-col items-center">
                <h3 className="text-sm font-medium text-gray-400 mb-3 tracking-wide">QUALITY LEVEL</h3>
                <div className="flex gap-3">
                  {(['fast', 'balanced', 'high', 'ultra'] as QualityLevel[]).map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setSelectedQuality(level)}
                      disabled={status === 'processing'}
                      className={`
                        px-6 py-2.5 rounded-full font-semibold text-sm transition-all duration-300
                        ${selectedQuality === level 
                          ? 'bg-green-600 text-black shadow-[0_0_20px_rgba(22,163,74,0.5)] border-2 border-green-500' 
                          : 'bg-gray-700/50 text-gray-300 border-2 border-gray-600 hover:bg-gray-600/50 hover:text-white'}
                        disabled:opacity-50 disabled:cursor-not-allowed
                      `}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  {selectedQuality === 'fast' && 'Quick results with lower color count'}
                  {selectedQuality === 'balanced' && 'Good quality with reasonable processing time'}
                  {selectedQuality === 'high' && 'Recommended: Very good quality and detail'}
                  {selectedQuality === 'ultra' && 'Maximum quality with longer processing time'}
                </p>
              </div>
              
              {/* Premium Features */}
              <div className="mb-8 w-full flex justify-center gap-6">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={useLab}
                    onChange={(e) => setUseLab(e.target.checked)}
                    disabled={status === 'processing'}
                    className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-green-600 focus:ring-green-500 focus:ring-offset-gray-900 disabled:opacity-50"
                  />
                  <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                    ✨ LAB Color Science <span className="text-green-500 font-semibold">(+40% quality)</span>
                  </span>
                </label>
                
                <label className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={useAi}
                    onChange={(e) => setUseAi(e.target.checked)}
                    disabled={status === 'processing'}
                    className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-green-600 focus:ring-green-500 focus:ring-offset-gray-900 disabled:opacity-50"
                  />
                  <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                    ✨ AI Edge Detection <span className="text-green-500 font-semibold">(+20% sharper)</span>
                  </span>
                </label>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
                {/* Original Image */}
                <div className="flex flex-col items-center">
                  <h2 className="text-lg font-semibold text-gray-400 mb-4">Original Raster</h2>
                  <div className="w-full aspect-square bg-black/30 rounded-2xl border border-gray-700/50 p-4 backdrop-blur-sm">
                    <img src={originalPreview} alt="Original Upload" className="w-full h-full object-contain rounded-lg" />
                  </div>
                </div>

                {/* Vectorized Image */}
                <div className="flex flex-col items-center">
                  <h2 className="text-lg font-semibold text-gray-400 mb-4">Vectorized Output</h2>
                   <div className="relative w-full aspect-square bg-black/30 rounded-2xl border border-gray-700/50 p-4 backdrop-blur-sm flex items-center justify-center">
                    {status === 'processing' && (
                      <div className="flex flex-col items-center text-gray-400">
                        <SpinnerIcon className="w-12 h-12 mb-4" />
                        <span className="text-lg font-medium">Vectorizing...</span>
                      </div>
                    )}
                    {status === 'success' && vectorizedPreview && (
                      <img src={vectorizedPreview} alt="Vectorized" className="w-full h-full object-contain rounded-lg" />
                    )}
                    {status !== 'processing' && status !== 'success' && (
                       <div className="flex flex-col items-center text-gray-500">
                        <PhotoIcon className="w-16 h-16 mb-4" />
                        <span className="text-lg font-medium">Output will appear here</span>
                       </div>
                    )}
                   </div>
                </div>
              </div>
              
              {error && <p className="text-red-500 mt-6 text-center">{error}</p>}
              
              {/* Action Buttons */}
              <div className="mt-10 flex items-center space-x-4">
                <button
                  onClick={handleReset}
                  className="group flex items-center justify-center gap-2 px-6 py-3 bg-gray-700/50 text-gray-300 rounded-full border border-gray-600 hover:bg-gray-600/50 hover:text-white transition-all duration-300"
                >
                  <ArrowPathIcon className="w-5 h-5 group-hover:rotate-180 transition-transform duration-300" />
                  Start Over
                </button>
                {status === 'success' ? (
                  <button
                    className="group flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-black font-semibold rounded-full hover:bg-green-500 transition-colors duration-300 shadow-[0_0_20px_rgba(22,163,74,0.5)]"
                  >
                    <ArrowDownTrayIcon className="w-5 h-5" />
                    Download SVG
                  </button>
                ) : (
                  <button
                    onClick={handleVectorize}
                    disabled={status === 'processing'}
                    className="group relative flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-black font-semibold rounded-full hover:bg-green-500 transition-colors duration-300 disabled:bg-green-800 disabled:text-gray-400 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(22,163,74,0.5)]"
                  >
                    {status === 'processing' ? 'Processing...' : 'Vectorize Image'}
                  </button>
                )}
              </div>
            </div>
          )}
        </main>
        
        <footer className="text-center py-6 text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} vectorizer.dev. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
