export interface VisionAnalysis {
  detected_primitive: 'box' | 'cylinder' | 'plate_with_hole' | 'stepped_block';
  estimated_width: number;
  estimated_height: number;
  estimated_depth: number;
  hole_detected: boolean;
  hole_diameter: number;
  confidence: number;
  warnings: string[];
  bounding_box_px?: { x: number; y: number; w: number; h: number };
}

export interface DimensionAnnotation {
  id: string;
  view: 'FACE' | 'ARRIÈRE' | 'GAUCHE' | 'DROITE' | 'DESSUS' | 'DESSOUS';
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  value: number;
}

export interface GeometryState {
  primitive_type: 'box' | 'cylinder' | 'plate_with_hole' | 'stepped_block';
  width: number;
  height: number;
  depth: number;
  hole_diameter: number;
  title: string;
  scale: number;
  projection_method: 'FIRST_ANGLE' | 'THIRD_ANGLE';
  orientation: 'landscape' | 'portrait';
  dimensions: DimensionAnnotation[];
}
