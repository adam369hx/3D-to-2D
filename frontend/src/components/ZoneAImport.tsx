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
  const fileInimport React, { useRef } from 'react';
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
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageSelected(e.target.files[0]);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <ImageIcon className="icon" />
        <h2>Zone A – Importation & Analyse Image</h2>
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
          accept="image/*"
          className="file-input-hidden"
        />

        {imagePreview ? (
          <div className="preview-container">
            <img
              src={imagePreview}
              alt="Aperçu croquis"
              style={{ transform: `rotate(${rotation}deg)` }}
              className="image-preview"
            />
            <div className="preview-actions">
              <button className="btn btn-secondary" onClick={onRotate}>
                <RotateCw className="icon-sm" /> Pivoter 90°
              </button>
              <label className="btn btn-outline cursor-pointer">
                Changer d'image
                <input type="file" accept="image/*" onChange={handleFileChange} hidden />
              </label>
            </div>
          </div>
        ) : (
          <div className="dropzone-placeholder" onClick={() => fileInputRef.current?.click()}>
            <Upload className="icon-lg" />
            <p>Glissez-déposez une image ici ou <strong>parcourez</strong></p>
            <span className="file-types">PNG, JPG, JPEG (max 10MB)</span>
          </div>
        )}
      </div>

      {isAnalyzing && (
        <div className="analysis-status status-loading">
          <Loader2 className="icon-spinner" />
          <span>Analyse de l'image par Vision IA en cours...</span>
        </div>
      )}

      {analysis && !isAnalyzing && (
        <div className={`analysis-status ${analysis.isValid ? 'status-success' : 'status-warning'}`}>
          {analysis.isValid ? (
            <>
              <CheckCircle2 className="icon" />
              <div>
                <strong>Analyse réussie :</strong> {analysis.message}
                <div className="confidence-score">Confiance : {Math.round(analysis.confidence * 100)}%</div>
              </div>
            </>
          ) : (
            <>
              <AlertTriangle className="icon" />
              <div>
                <strong>Avertissement :</strong> {analysis.message}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};putRef = use
