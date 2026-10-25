import React from 'react';
import { Box } from 'lucide-react';
import type { GeometryState, VisionAnalysis } from '../types';

interface ZoneBProps {
  geometry: GeometryState;
  onChange: (updated: GeometryState) => void;
  analysis: VisionAnalysis | null;
}

export const ZoneBAnalysis: React.FC<ZoneBProps> = ({ geometry, onChange }) => {
  const handleNumChange = (field: keyof GeometryState, val: string) => {
    const num = parseFloat(val) || 0;
    onChange({ ...geometry, [field]: num });
  };

  const handlePrimitiveChange = (type: GeometryState['primitive_type']) => {
    onChange({ ...geometry, primitive_type: type });
  };

  return (
    <div className="card">
      <div className="card-header">
        <Box className="icon" />
        <h2>Zone B — Modèle 3D & Dimensions Connues</h2>
      </div>

      <div className="form-section">
        <label className="section-label">Forme Géométrique Estimée</label>
        <div className="primitive-selector">
          <button
            className={`btn-type ${geometry.primitive_type === 'box' ? 'active' : ''}`}
            onClick={() => handlePrimitiveChange('box')}
          >
            Pavé / Cube
          </button>
          <button
            className={`btn-type ${geometry.primitive_type === 'cylinder' ? 'active' : ''}`}
            onClick={() => handlePrimitiveChange('cylinder')}
          >
            Cylindre
          </button>
          <button
            className={`btn-type ${geometry.primitive_type === 'plate_with_hole' ? 'active' : ''}`}
            onClick={() => handlePrimitiveChange('plate_with_hole')}
          >
            Plaque Trouée
          </button>
          <button
            className={`btn-type ${geometry.primitive_type === 'stepped_block' ? 'active' : ''}`}
            onClick={() => handlePrimitiveChange('stepped_block')}
          >
            Bloc Étagé (L)
          </button>
        </div>

        <div className="dimensions-grid">
          <div className="form-group">
            <label>Largeur (X) mm :</label>
            <input
              type="number"
              value={geometry.width}
              onChange={(e) => handleNumChange('width', e.target.value)}
              min="1"
            />
          </div>

          <div className="form-group">
            <label>Hauteur (Y) mm :</label>
            <input
              type="number"
              value={geometry.height}
              onChange={(e) => handleNumChange('height', e.target.value)}
              min="1"
            />
          </div>

          <div className="form-group">
            <label>Profondeur (Z) mm :</label>
            <input
              type="number"
              value={geometry.depth}
              onChange={(e) => handleNumChange('depth', e.target.value)}
              min="1"
            />
          </div>

          {geometry.primitive_type === 'plate_with_hole' && (
            <div className="form-group">
              <label>Diamètre du Trou (mm) :</label>
              <input
                type="number"
                value={geometry.hole_diameter}
                onChange={(e) => handleNumChange('hole_diameter', e.target.value)}
                min="1"
              />
            </div>
          )}
        </div>

        <div className="form-group margin-top">
          <label>Titre du Dessin Technique :</label>
          <input
            type="text"
            value={geometry.title}
            onChange={(e) => onChange({ ...geometry, title: e.target.value })}
          />
        </div>
      </div>
    </div>
  );
};
