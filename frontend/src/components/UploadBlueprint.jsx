import React, { useRef, useState } from 'react';
import { FileUp } from 'lucide-react';

export default function UploadBlueprint({ onUpload }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  // const uploadFile = async (file) => {
  //   onUpload(file);
  //   const formData = new FormData();
  //   formData.append('file', file);
  //   try {
  //     await fetch('http://localhost:8000/start', {
  //       method: 'POST',
  //       body: formData,
  //     });
  //   } catch (error) {
  //     console.error("Error uploading file:", error);
  //   }
  // };

  const uploadFile = (file) => {
    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (e.dataTransfer.files[0].type === "application/pdf") {
        uploadFile(e.dataTransfer.files[0]);
      } else {
        alert("Please upload a PDF file.");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center min-h-[calc(100vh-73px)] p-6 z-10 w-full" style={{
      /* A very dark gray background map gradient as seen in the screenshots */
      backgroundImage: `linear-gradient(to right, #1b2024 1px, transparent 1px), linear-gradient(to bottom, #1b2024 1px, transparent 1px)`,
      backgroundSize: '40px 40px',
      backgroundColor: 'var(--color-brand-dark)'
    }}>
      <div
        className={`relative w-full max-w-3xl flex flex-col items-center p-16 transition-colors duration-300 ${isDragging ? 'bg-[#1e2328]' : 'bg-[#1a1d21]/80 hover:bg-[#1a1d21]'} border border-[#2b3036] rounded-sm`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          boxShadow: 'inset 0 0 100px rgba(0,0,0,0.5)'
        }}
      >
        <div className="w-24 h-24 bg-[#23272b] flex items-center justify-center mb-8 shadow-inner shadow-black/40">
          <FileUp size={48} className="text-brand-cyan drop-shadow-[0_0_12px_rgba(0,210,211,0.6)]" strokeWidth={2.5} />
        </div>

        <h2 className="text-2xl font-bold tracking-widest text-[#e2e8f0] mb-4">PRIMARY BLUEPRINT INPUT</h2>
        <p className="text-[#8e9ba9] mb-6 tracking-wide font-medium">Drop engineering PDF or technical schematics here</p>

        <p className="font-mono text-[#586470] text-xs tracking-widest mb-10">MAX_FILE_SIZE: 128MB</p>

        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-6 py-3 bg-[#24292f] hover:bg-[#2c3238] border border-[#31383f] transition-colors rounded-sm text-sm font-bold tracking-widest text-[#d1d5db]"
        >
          BROWSE TERMINAL
        </button>
        <input
          type="file"
          accept="application/pdf"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
      </div>
    </div>
  );
}
