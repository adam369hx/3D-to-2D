import React from 'react';
import { Settings2, RefreshCw } from 'lucide-react';
import type { GeometryState } from '../types';

interface ZoneCProps {
  geometry: GeometryState;
  onChange: (updated: GeometryState) => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

export const ZoneCGeneration: React.FC<ZoneCProps> = ({
  geometry,
  onChange,
  onGenerate,
  isGenerating
}) => {
  return (
    <div className="card">
      <div className="card-header">
        <Settings2 className="icon" />
        <h2>Zone C — Options ISO & Génération</h2>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label>Méthode de Projection (Norme NF EN ISO 5456-2) :</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="projection"
                value="FIRST_ANGLE"
                checked={geometry.projection_method === 'FIRST_ANGLE'}
                onChange={() => onChange({ ...geometry, projection_method: 'FIRST_ANGLE' })}
              />
              <span>1er Dièdre / Européenne (Par défaut)</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="projection"
                value="THIRD_ANGLE"
                checked={geometry.projection_method === 'THIRD_ANGLE'}
                onChange={() => onChange({ ...geometry, projection_method: 'THIRD_ANGLE' })}
              />
              <span>3ème Dièdre / Américaine</span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label>Orientation de la Feuille A4 :</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="orientation"
                value="landscape"
                checked={geometry.orientation === 'landscape'}
                onChange={() => onChange({ ...geometry, orientation: 'landscape' })}
              />
              <span>Paysage (297 × 210 mm)</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="orientation"
                value="portrait"
                checked={geometry.orientation === 'portrait'}
                onChange={() => onChange({ ...geometry, orientation: 'portrait' })}
              />
              <span>Portrait (210 × 297 mm)</span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label>Échelle Normalisée :</label>
          <select
            value={geometry.scale}
            onChange={(e) => onChange({ ...geometry, scale: parseFloat(e.target.value) })}
          >
            <option value="2.0">2:1 (Agrandissement)</option>
            <option value="1.0">1:1 (Vraie grandeur)</option>
            <option value="0.5">1:2 (Réduction)</option>
            <option value="0.2">1:5 (Réduction)</option>
            <option value="0.1">1:10 (Réduction)</option>
          </select>
        </div>
      </div>

      <button
        className="btn btn-primary btn-block margin-top"
        onClick={onGenerate}
        disabled={isGenerating}
      >
        <RefreshCw className={`icon-sm ${isGenerating ? 'animate-spin' : ''}`} />
        {isGenerating ? 'Calcul des 6 Vues Vectorielles...' : 'Générer les 6 Vues Orthogonales Synchronisées'}
      </button>
    </div>
  );
};
