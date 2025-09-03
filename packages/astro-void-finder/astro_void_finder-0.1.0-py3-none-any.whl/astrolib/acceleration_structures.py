"""
Acceleration Structures
===================

Fast spatial search algorithms and data structures for particle systems.
Optimized for both memory efficiency and query speed.
"""

import numpy as np
from typing import List, Tuple, Optional
import threading
from dataclasses import dataclass
from .resource_manager import ResourceManager

@dataclass
class GridCell:
    """A cell in the adaptive grid structure."""
    indices: List[int]
    center: np.ndarray
    size: float
    density: float

class AdaptiveGrid:
    """
    Adaptives Gitter für effiziente räumliche Berechnungen.
    """
    def __init__(self, box_size: float, base_resolution: int = 32):
        self.box_size = box_size
        self.base_resolution = base_resolution
        self.cell_size = box_size / base_resolution
        self.grid: List[List[GridCell]] = []
        self.resource_manager = ResourceManager()
        self._refinement_lock = threading.Lock()
    
    def build(self, positions: np.ndarray, masses: Optional[np.ndarray] = None):
        """
        Baut adaptives Gitter aus Teilchenpositionen.
        
        Args:
            positions: (N, 3) Array der Teilchenpositionen
            masses: Optional, (N,) Array der Teilchenmassen
        """
        if masses is None:
            masses = np.ones(len(positions))
        
        # Initialisiere Basis-Gitter
        self.grid = []
        base_cells = self._create_base_grid(positions, masses)
        
        # Verfeinere Gitter adaptiv
        self._refine_grid(base_cells, positions, masses)
    
    def _create_base_grid(self, positions: np.ndarray, 
                         masses: np.ndarray) -> List[GridCell]:
        """Erstellt Basis-Gitter-Zellen."""
        cells = []
        grid_indices = (positions / self.cell_size).astype(int)
        
        # Finde einzigartige Gitterzellen
        unique_indices = np.unique(grid_indices, axis=0)
        
        for idx in unique_indices:
            # Finde Teilchen in dieser Zelle
            mask = np.all(grid_indices == idx, axis=1)
            cell_positions = positions[mask]
            cell_masses = masses[mask]
            
            center = idx * self.cell_size + self.cell_size/2
            density = np.sum(cell_masses) / self.cell_size**3
            
            cells.append(GridCell(
                indices=list(idx),
                center=center,
                size=self.cell_size,
                density=density
            ))
        
        return cells
    
    def _refine_grid(self, cells: List[GridCell], 
                     positions: np.ndarray, 
                     masses: np.ndarray,
                     max_level: int = 3):
        """
        Verfeinert Gitter basierend auf Teilchendichte.
        
        Args:
            cells: Liste von Gitterzellen
            positions: Teilchenpositionen
            masses: Teilchenmassen
            max_level: Maximale Verfeinerungstiefe
        """
        refined_cells = []
        
        for cell in cells:
            if len(refined_cells) >= self.resource_manager.get_optimal_chunk_size('grid'):
                # Füge Batch von verfeinerten Zellen zum Gitter hinzu
                with self._refinement_lock:
                    self.grid.extend(refined_cells)
                refined_cells = []
            
            # Prüfe Verfeinerungskriterien
            if self._should_refine(cell, positions, masses) and max_level > 0:
                # Teile Zelle in 8 kleinere Zellen
                new_size = cell.size / 2
                for i in range(2):
                    for j in range(2):
                        for k in range(2):
                            new_center = cell.center + new_size/2 * np.array([i-0.5, j-0.5, k-0.5])
                            
                            # Finde Teilchen in der neuen Zelle
                            mask = self._particles_in_cell(positions, new_center, new_size)
                            if np.any(mask):
                                new_density = np.sum(masses[mask]) / new_size**3
                                new_cell = GridCell(
                                    indices=cell.indices + [i + 2*j + 4*k],
                                    center=new_center,
                                    size=new_size,
                                    density=new_density
                                )
                                refined_cells.append(new_cell)
            else:
                refined_cells.append(cell)
        
        # Füge verbleibende verfeinerte Zellen hinzu
        with self._refinement_lock:
            self.grid.extend(refined_cells)
    
    def _should_refine(self, cell: GridCell, 
                       positions: np.ndarray, 
                       masses: np.ndarray) -> bool:
        """
        Entscheidet, ob eine Zelle verfeinert werden soll.
        """
        # Kriterien für Verfeinerung:
        # 1. Hohe Teilchendichte
        density_threshold = np.mean(masses) / self.cell_size**3 * 2
        if cell.density > density_threshold:
            return True
        
        # 2. Große Dichtegradienten
        mask = self._particles_in_cell(positions, cell.center, cell.size * 1.5)
        if np.any(mask):
            local_density = np.sum(masses[mask]) / (cell.size * 1.5)**3
            if abs(local_density - cell.density) > cell.density * 0.5:
                return True
        
        return False
    
    @staticmethod
    def _particles_in_cell(positions: np.ndarray, 
                          center: np.ndarray, 
                          size: float) -> np.ndarray:
        """
        Findet Teilchen innerhalb einer Zelle.
        """
        return np.all(
            np.abs(positions - center) <= size/2,
            axis=1
        )
    
    def find_neighbors(self, position: np.ndarray, 
                      radius: float) -> List[GridCell]:
        """
        Findet Nachbarzellen innerhalb eines Radius.
        
        Args:
            position: (3,) Array der Suchposition
            radius: Suchradius
            
        Returns:
            Liste von Nachbarzellen
        """
        neighbors = []
        
        for cell in self.grid:
            if np.linalg.norm(cell.center - position) <= radius + cell.size/2:
                neighbors.append(cell)
        
        return neighbors
    
    def get_density_field(self) -> Tuple[np.ndarray, float]:
        """
        Erstellt Dichtefeld aus adaptivem Gitter.
        
        Returns:
            Tuple von (Dichtefeld, Zellengröße)
        """
        # Finde minimale Zellengröße
        min_size = min(cell.size for cell in self.grid)
        resolution = int(self.box_size / min_size)
        
        # Erstelle Dichtefeld
        density_field = np.zeros((resolution, resolution, resolution))
        
        for cell in self.grid:
            # Konvertiere Zellposition zu Gitterindizes
            indices = (cell.center / min_size).astype(int)
            cell_res = int(cell.size / min_size)
            
            # Fülle Dichtefeld
            i, j, k = indices
            density_field[i:i+cell_res, j:j+cell_res, k:k+cell_res] = cell.density
        
        return density_field, min_size
