import React, { useState } from 'react';
import { Eye, Download, ZoomIn, ZoomOut, Move, PlusCircle, Check } from 'lucide-react';
import type { GeometryState, DimensionAnnotation } from '../types';

interface ZoneDProps {
  svgContent: string | null;
  geometry: GeometryState;
  onAddDimension: (dim: DimensionAnnotation) => void;
}

export const ZoneDPreview: React.FC<ZoneDProps> = ({ svgContent, geometry, onAddDimension }) => {
  const [zoom, setZoom] = useState<number>(1.0);
  const [showAddDimModal, setShowAddDimModal] = useState<boolean>(false);

  // Dimension Modal state
  const [dimView, setDimView] = useState<DimensionAnnotation['view']>('FACE');
  const [x1, setX1] = useState<number>(-50);
  const [y1, setY1] = useState<number>(0);
  const [x2, setX2] = useState<number>(50);
  const [y2, setY2] = useState<number>(0);
  const [val, setVal] = useState<number>(geometry.width);

  const handleCreateDim = () => {
    onAddDimension({
      id: Date.now().toString(),
      view: dimView,
      x1,
      y1,
      x2,
      y2,
      value: val
    });
    setShowAddDimModal(false);
  };

  const downloadSvg = () => {
    if (!svgContent) return;
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dessin-technique-6-vues-${geometry.title.toLowerCase().replace(/\s+/g, '-')}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card full-height">
      <div className="card-header space-between">
        <div className="flex-align">
          <Eye className="icon" />
          <h2>Zone D & E — Visualisation Feuille A4 & Exportation SVG</h2>
        </div>
        <div className="toolbar">
          <button className="btn btn-sm btn-outline" onClick={() => setZoom(Math.max(0.5, zoom - 0.2))}>
            <ZoomOut className="icon-sm" />
          </button>
          <span className="zoom-text">{Math.round(zoom * 100)}%</span>
          <button className="btn btn-sm btn-outline" onClick={() => setZoom(Math.min(2.5, zoom + 0.2))}>
            <ZoomIn className="icon-sm" />
          </button>
          <button className="btn btn-sm btn-secondary" onClick={() => setShowAddDimModal(true)}>
            <PlusCircle className="icon-sm" /> Ajouter Cotation
          </button>
          <button className="btn btn-sm btn-success" onClick={downloadSvg} disabled={!svgContent}>
            <Download className="icon-sm" /> Exporter SVG A4
          </button>
        </div>
      </div>

      <div className="drawing-sheet-viewport">
        {svgContent ? (
          <div
            className="drawing-sheet-canvas"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        ) : (
          <div className="placeholder-canvas">
            <Move className="placeholder-icon" />
            <p>Cliquez sur « Générer les 6 Vues Orthogonales » pour afficher la feuille ISO A4</p>
          </div>
        )}
      </div>

      {showAddDimModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Ajouter une Ligne de Cote (Cotation ISO)</h3>
            <div className="form-group">
              <label>Vue Cible :</label>
              <select value={dimView} onChange={(e) => setDimView(e.target.value as any)}>
                <option value="FACE">Vue de Face</option>
                <option value="DESSUS">Vue de Dessus</option>
                <option value="GAUCHE">Vue de Gauche</option>
                <option value="DROITE">Vue de Droite</option>
                <option value="ARRIÈRE">Vue Arrière</option>
                <option value="DESSOUS">Vue de Dessous</option>
              </select>
            </div>

            <div className="dimensions-grid">
              <div className="form-group">
                <label>X1 (mm) :</label>
                <input type="number" value={x1} onChange={(e) => setX1(parseFloat(e.target.value) || 0)} />
              </div>
              <div className="form-group">
                <label>Y1 (mm) :</label>
                <input type="number" value={y1} onChange={(e) => setY1(parseFloat(e.target.value) || 0)} />
              </div>
              <div className="form-group">
                <label>X2 (mm) :</label>
                <input type="number" value={x2} onChange={(e) => setX2(parseFloat(e.target.value) || 0)} />
              </div>
              <div className="form-group">
                <label>Y2 (mm) :</label>
                <input type="number" value={y2} onChange={(e) => setY2(parseFloat(e.target.value) || 0)} />
              </div>
            </div>

            <div className="form-group">
              <label>Valeur Numérique Mesurée (mm) :</label>
              <input type="number" value={val} onChange={(e) => setVal(parseFloat(e.target.value) || 0)} />
            </div>

            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setShowAddDimModal(false)}>Annuler</button>
              <button className="btn btn-primary" onClick={handleCreateDim}>
                <Check className="icon-sm" /> Valider la Cotation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
