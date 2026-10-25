import React, { useRef } from 'react';
import { Upload, RotateCw, Image as ImageIcon, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';
import type { VisionAnalysis } from '../types';

interface ZoneAProps {
  imagePreview: string | null;
  onImageSelected: (file: File) => void;
  onRotate: () => void;
  rotation: number;
  analysis: VisionAnalysis | null;
  isAnalyzing: boolean;
}

export const ZoneAImport: React.FC<ZoneAProps> = ({
  imagePreview,
  onImageSelected,
  onRotate,
  rotation,
  analysis,
  isAnalyzing
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onImageSelected(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageSelected(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <ImageIcon className="icon" />
        <h2>Zone A — Importation & Analyse Image</h2>
      </div>

      <div
        className={`dropzone ${imagePreview ? 'has-preview' : ''}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/png, image/jpeg, image/webp"
          style={{ display: 'none' }}
        />

        {imagePreview ? (
          <div className="preview-container">
            <div
              className="image-wrapper"
              style={{ transform: `rotate(${rotation}deg)` }}
            >
              <img src={imagePreview} alt="Aperçu produit" />
            </div>
            <div className="preview-actions">
              <button className="btn btn-secondary" onClick={onRotate}>
                <RotateCw className="icon-sm" /> Rotation (90°)
              </button>
              <button
                className="btn btn-outline"
                onClick={() => fileInputRef.current?.click()}
              >
                Changer d'image
              </button>
            </div>
          </div>
        ) : (
          <div className="dropzone-placeholder" onClick={() => fileInputRef.current?.click()}>
            <Upload className="upload-icon" />
            <p className="primary-text">Glissez-déposez une image ici ou cliquez pour parcourir</p>
            <p className="sub-text">Formats acceptés : PNG, JPG, JPEG, WEBP</p>
          </div>
        )}
      </div>

      {isAnalyzing && (
        <div className="status-box status-loading">
          <Loader2 className="animate-spin icon" />
          <span>Analyse géométrique en cours par IA / Vision...</span>
        </div>
      )}

      {analysis && !isAnalyzing && (
        <div className="analysis-summary">
          <div className="confidence-badge">
            <CheckCircle2 className="icon-sm" />
            <span>
              Indice de confiance géométrique : <strong>{Math.round(analysis.confidence * 100)}%</strong>
            </span>
          </div>

          {analysis.warnings.length > 0 && (
            <div className="warnings-box">
              <div className="warning-title">
                <AlertTriangle className="icon-sm" />
                <span>Avertissements de reconstruction 3D</span>
              </div>
              <ul>
                {analysis.warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
