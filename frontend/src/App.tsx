import React, { useState, useEffect } from 'react';
import { Compass } from 'lucide-react';
import type { GeometryState, VisionAnalysis, DimensionAnnotation } from './types';
import { ZoneAImport } from './components/ZoneAImport';
import { ZoneBAnalysis } from './components/ZoneBAnalysis';
import { ZoneCGeneration } from './components/ZoneCGeneration';
import { ZoneDPreview } from './components/ZoneDPreview';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const App: React.FC = () => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [rotation, setRotation] = useState<number>(0);
  const [analysis, setAnalysis] = useState<VisionAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [geometry, setGeometry] = useState<GeometryState>({
    primitive_type: 'box',
    width: 100,
    height: 80,
    depth: 60,
    hole_diameter: 30,
    title: 'PIÈCE MÉCANIQUE',
    scale: 1.0,
    projection_method: 'FIRST_ANGLE',
    orientation: 'landscape',
    dimensions: []
  });

  const handleImageSelected = async (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Call API vision analysis
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE_URL}/analyze-image`, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        const a: VisionAnalysis = data.analysis;
        setAnalysis(a);

        // Update geometry state from vision estimation
        setGeometry((prev) => ({
          ...prev,
          primitive_type: a.detected_primitive,
          width: a.estimated_widimport React, { useState, useEffect } from 'react';
import ZoneAImport from './components/ZoneAImport';
import ZoneBParameters from './components/ZoneBParameters';
import ZoneCISOOptions from './components/ZoneCISOOptions';
import ZoneDPreview from './components/ZoneDPreview';
import { GeometryState, DimensionAnnotation } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [rotation, setRotation] = useState<number>(0);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [geometry, setGeometry] = useState<GeometryState>({
    primitive_type: 'box',
    width: 100,
    height: 60,
    depth: 40,
    hole_diameter: 30,
    title: 'PIÈCE MÉCANIQUE',
    scale: 1.0,
    projection_method: 'FIRST_ANGLE',
    orientation: 'landscape',
    dimensions: []
  });

  const [svgContent, setSvgContent] = useState<string>('');

  const handleImageSelected = async (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setRotation(0);
    setIsAnalyzing(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze-image`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        const a = data.analysis;
        setGeometry((prev) => ({
          ...prev,
          primitive_type: a.detected_primitive || prev.primitive_type,
          width: a.estimated_width || prev.width,
          height: a.estimated_height || prev.height,
          depth: a.estimated_depth || prev.depth,
          hole_diameter: a.hole_diameter || prev.hole_diameter || 30,
          dimensions: a.dimensions || prev.dimensions || []
        }));
      }
    } catch (err) {
      console.warn('Erreur lors de la connexion API vision:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRotate = () => {
    setRotation((r) => (r + 90) % 360);
    setGeometry((prev) => ({
      ...prev,
      width: prev.height,
      height: prev.width,
    }));
  };

  const handleGenerateSVG = async (currentGeometry: GeometryState = geometry) => {
    setIsGenerating(true);
    setErrorMessage(null);
    try {
      const res = await fetch(`${API_BASE_URL}/generate-svg`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentGeometry)
      });

      if (res.ok) {
        const svgText = await res.text();
        setSvgContent(svgText);
      } else {
        const errText = await res.text();
        setErrorMessage(`Erreur serveur (${res.status}): impossible de générer les vues vectorielles. ${errText}`);
      }
    } catch (err) {
      console.error('Erreur lors de la génération du SVG:', err);
      setErrorMessage('Impossible de contacter le serveur backend. Veuillez vérifier que le backend est démarré sur http://localhost:8000.');
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    handleGenerateSVG(geometry);
  }, [
    geometry.primitive_type,
    geometry.width,
    geometry.height,
    geometry.depth,
    geometry.hole_diameter,
    geometry.title,
    geometry.scale,
    geometry.projection_method,
    geometry.orientation,
    geometry.dimensions
  ]);

  const handleAddDimension = (dim: DimensionAnnotation) => {
    const updated = {
      ...geometry,
      dimensions: [...(geometry.dimensions || []), dim]
    };
    setGeometry(updated);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <header className="bg-slate-800 border-b border-slate-700 py-4 px-6 shadow-md flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white shadow">
            3D
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">Générateur de Vues Orthogonales ISO</h1>
            <p className="text-xs text-slate-400">ISO 5456-2 / ISO 128 - Projection 2D interactive depuis modèles 3D</p>
          </div>
        </div>
      </header>

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1800px] w-full mx-auto">
        <div className="lg:col-span-4 flex flex-col gap-6">
          <ZoneAImport
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            rotation={rotation}
            isAnalyzing={isAnalyzing}
            onImageSelect={handleImageSelected}
            onRotate={handleRotate}
          />

          <ZoneBParameters
            geometry={geometry}
            onChange={setGeometry}
          />

          <ZoneCISOOptions
            geometry={geometry}
            onChange={setGeometry}
          />
        </div>

        <div className="lg:col-span-8 flex flex-col gap-4">
          {errorMessage && (
            <div className="p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200 text-sm">
              {errorMessage}
            </div>
          )}

          <ZoneDPreview
            svgContent={svgContent}
            geometry={geometry}
            onAddDimension={handleAddDimension}
            orientation={geometry.orientation}
          />
        </div>
      </main>
    </div>
  );
};

export default App;th,
          height: a.estimated_height,
          depth: a.estimated_depth,
          hole_diameter: a.hole_diameter || 30
        }));
      }
    } catch (err) {
      console.warn('Erreur lors de la connexion API vision:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRotate = () => {
    setRotation((r) => (r + 90) % 360);
  };

  const handleGenerateSVG = async (currentGeometry: GeometryState = geometry) => {
    setIsGenerating(true);
    setErrorMessage(null);
    try {
      const res = await fetch(`${API_BASE_URL}/generate-svg`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentGeometry)
      });

      if (res.ok) {
        const svgText = await res.text();
        setSvgContent(svgText);
      } else {
        const errText = await res.text();
        setErrorMessage(`Erreur serveur (${res.status}): impossible de générer les vues vectorielles. ${errText}`);
      }
    } catch (err) {
      console.error('Erreur lors de la génération du SVG:', err);
      setErrorMessage('Impossible de contacter le serveur backend. Veuillez vérifier que le backend est démarré sur le port 8000.');
    } finally {
      setIsGenerating(false);
    }
  };

  // Initial auto-generation of SVG preview
  useEffect(() => {
    handleGenerateSVG(geometry);
  }, [
    geometry.primitive_type,
    geometry.width,
    geometry.height,
    geometry.depth,
    geometry.hole_diameter,
    geometry.title,
    geometry.scale,
    geometry.projection_method,
    geometry.orientation,
    geometry.dimensions
  ]);

  const handleAddDimension = (dim: DimensionAnnotation) => {
    const updated = {
      ...geometry,
      dimensions: [...geometry.dimensions, dim]
    };
    setGeometry(updated);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-brand">
          <Compass className="brand-icon" />
          <div>
            <h1>Générateur Automatique de Vues Orthogonales</h1>
            <p className="subtitle">Dessin Technique ISO 5456-2 / NF EN ISO 128 / NF EN ISO 7200</p>
          </div>
        </div>
      </header>

      {errorMessage && (
        <div style={{ backgroundColor: '#FEE2E2', border: '1px solid #EF4444', color: '#991B1B', padding: '12px 24px', margin: '0 24px 16px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} style={{ background: 'none', border: 'none', color: '#991B1B', fontWeight: 'bold', cursor: 'pointer', fontSize: '16px' }}>✕</button>
        </div>
      )}

      <main className="app-main">
        <div className="left-panel">
          <ZoneAImport
            imagePreview={imagePreview}
            onImageSelected={handleImageSelected}
            onRotate={handleRotate}
            rotation={rotation}
            analysis={analysis}
            isAnalyzing={isAnalyzing}
          />

          <ZoneBAnalysis
            geometry={geometry}
            onChange={setGeometry}
            analysis={analysis}
          />

          <ZoneCGeneration
            geometry={geometry}
            onChange={setGeometry}
            onGenerate={() => handleGenerateSVG(geometry)}
            isGenerating={isGenerating}
          />
        </div>

        <div className="right-panel">
          <ZoneDPreview
            svgContent={svgContent}
            geometry={geometry}
            onAddDimension={handleAddDimension}
          />
        </div>
      </main>
    </div>
  );
};

export default App;
