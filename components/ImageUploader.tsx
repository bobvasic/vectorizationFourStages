
import React, { useState, useRef, useCallback } from 'react';
import { UploadIcon } from './icons/UploadIcon';

interface ImageUploaderProps {
  onImageSelect: (file: File, previewUrl: string) => void;
  onError: (message: string) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageSelect, onError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileValidation = (file: File) => {
    if (!file) return false;
    const allowedTypes = ['image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      onError('Invalid file type. Please upload a JPG or PNG image.');
      return false;
    }
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      onError('File is too large. Maximum size is 5MB.');
      return false;
    }
    return true;
  };
  
  const processFile = (file: File) => {
    if (handleFileValidation(file)) {
      const previewUrl = URL.createObjectURL(file);
      onImageSelect(file, previewUrl);
    }
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const onBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div 
      className={`w-full max-w-2xl p-8 rounded-3xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center text-center cursor-pointer backdrop-blur-sm
        ${isDragging ? 'border-green-500 bg-green-500/10' : 'border-gray-700/80 bg-white/5'}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={onBrowseClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept="image/png, image/jpeg"
        onChange={handleFileChange}
      />
      <div className="flex flex-col items-center justify-center gap-4 pointer-events-none">
        <div className={`p-4 rounded-full transition-colors duration-300 ${isDragging ? 'bg-green-500/20' : 'bg-gray-700/50'}`}>
          <UploadIcon className={`w-12 h-12 transition-colors duration-300 ${isDragging ? 'text-green-400' : 'text-gray-400'}`}/>
        </div>
        <h2 className="text-2xl font-bold text-white">Drag & drop your image here</h2>
        <p className="text-gray-400">or click to browse files</p>
        <p className="text-sm text-gray-500 mt-2">Supports: PNG, JPG up to 5MB</p>
      </div>
    </div>
  );
};

export default ImageUploader;
