import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadBlueprint from './components/UploadBlueprint';
import ProcessTracker from './components/ProcessTracker';

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleUpload = (file) => {
    // In a real app we'd process the file. Here we just swap views to ProcessTracker.
    console.log("File uploaded:", file.name);
    setUploadedFile(file);
  };

  return (
    <div className="min-h-screen flex flex-col font-sans overflow-x-hidden" style={{ backgroundColor: 'var(--color-brand-dark)' }}>
      <Navbar />
      <main className="flex-1 flex flex-col relative w-full h-full">
        {!uploadedFile ? (
          <UploadBlueprint onUpload={handleUpload} />
        ) : (
          <ProcessTracker file={uploadedFile} />
        )}
      </main>
    </div>
  );
}

export default App;
