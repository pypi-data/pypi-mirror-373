"""
Hochoptimierte Void-Analyse mit Streaming-Verarbeitung
================================================
"""

import numpy as np
from typing import Iterator, Tuple, List, Optional
from .cache import SmartCache
import concurrent.futures
from collections import deque

class StreamingVoidFinder:
    """
    Memory-effiziente Void-Finding-Implementation mit Streaming-Verarbeitung.
    """
    def __init__(self, chunk_size: int = 1000000, n_workers: int = 2):
        self.chunk_size = chunk_size
        self.n_workers = n_workers
        self.cache = SmartCache()
        
    def find_voids_streaming(self, 
                           data_iterator: Iterator[np.ndarray],
                           box_size: float) -> Iterator[dict]:
        """
        Findet Voids in einem Datenstrom von Galaxienpositionen.
        
        Args:
            data_iterator: Iterator über Chunks von Galaxienpositionen
            box_size: Größe der Simulationsbox
            
        Yields:
            Void-Eigenschaften für jeden gefundenen Void
        """
        grid_cells = self._estimate_optimal_grid(box_size)
        density_grid = np.zeros((grid_cells, grid_cells, grid_cells))
        
        # Verarbeite Daten in Chunks
        for chunk in data_iterator:
            # Aktualisiere Dichtegitter für aktuellen Chunk
            self._update_density_grid(density_grid, chunk, box_size)
            
            # Identifiziere Void-Kandidaten im aktualisierten Gitter
            void_candidates = self._find_void_candidates(density_grid)
            
            # Validiere und verfeinere Void-Kandidaten
            for void in self._validate_voids(void_candidates, chunk):
                yield void
    
    def _estimate_optimal_grid(self, box_size: float) -> int:
        """Schätzt optimale Gittergröße basierend auf verfügbarem Speicher."""
        # Heuristik für Gittergröße basierend auf Box-Größe und typischer Void-Größe
        return max(32, min(256, int(box_size / 5.0)))
    
    def _update_density_grid(self,
                           grid: np.ndarray,
                           positions: np.ndarray,
                           box_size: float):
        """Aktualisiert das Dichtegitter mit neuen Positionen."""
        grid_cells = grid.shape[0]
        
        # Berechne Gitterpositionen
        grid_pos = np.floor(positions / box_size * grid_cells).astype(int)
        grid_pos %= grid_cells  # Periodische Randbedingungen
        
        # Zähle Galaxien pro Zelle
        for pos in grid_pos:
            grid[tuple(pos)] += 1
    
    def _find_void_candidates(self,
                            density_grid: np.ndarray,
                            threshold: float = 0.2) -> List[dict]:
        """
        Findet Void-Kandidaten im Dichtegitter mit Watershed-Algorithmus.
        """
        # Cache-Lookup für bereits berechnete ähnliche Regionen
        cache_key = "void_candidates"
        cached_result = self.cache.get(cache_key, density_grid)
        if cached_result is not None:
            return cached_result
        
        # Implementiere Watershed-Algorithmus mit Speichereffizienz
        candidates = self._watershed_streaming(density_grid, threshold)
        
        # Cache Ergebnisse
        self.cache.set(cache_key, density_grid, candidates)
        return candidates
    
    def _watershed_streaming(self,
                           density_grid: np.ndarray,
                           threshold: float) -> List[dict]:
        """
        Speichereffiziente Implementierung des Watershed-Algorithmus.
        """
        candidates = []
        visited = np.zeros_like(density_grid, dtype=bool)
        min_points = deque()
        
        # Finde lokale Minima
        for i in range(1, density_grid.shape[0]-1):
            for j in range(1, density_grid.shape[1]-1):
                for k in range(1, density_grid.shape[2]-1):
                    if self._is_local_minimum(density_grid, i, j, k):
                        min_points.append((i, j, k))
        
        # Verarbeite Minima parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = []
            for minimum in min_points:
                futures.append(
                    executor.submit(
                        self._grow_void_region,
                        density_grid,
                        visited,
                        minimum,
                        threshold
                    )
                )
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    candidates.append(result)
        
        return candidates
    
    def _is_local_minimum(self,
                         grid: np.ndarray,
                         i: int,
                         j: int,
                         k: int) -> bool:
        """Prüft, ob ein Punkt ein lokales Minimum ist."""
        center = grid[i, j, k]
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                for dk in [-1, 0, 1]:
                    if di == dj == dk == 0:
                        continue
                    if grid[i+di, j+dj, k+dk] < center:
                        return False
        return True
    
    def _grow_void_region(self,
                         grid: np.ndarray,
                         visited: np.ndarray,
                         seed: Tuple[int, int, int],
                         threshold: float) -> Optional[dict]:
        """
        Lässt eine Void-Region von einem Saatpunkt aus wachsen.
        """
        region = set([seed])
        edge = set([seed])
        volume = 0
        center = np.array(seed)
        
        while edge:
            new_edge = set()
            for point in edge:
                i, j, k = point
                for di, dj, dk in self._get_neighbors():
                    ni, nj, nk = i+di, j+dj, k+dk
                    if not visited[ni, nj, nk] and grid[ni, nj, nk] < threshold:
                        new_point = (ni, nj, nk)
                        new_edge.add(new_point)
                        region.add(new_point)
                        visited[ni, nj, nk] = True
                        volume += 1
                        center += np.array([ni, nj, nk])
            
            edge = new_edge
        
        if volume > 0:
            center = center / len(region)
            return {
                'center': center,
                'volume': volume,
                'radius': (3 * volume / (4 * np.pi))**(1/3)
            }
        return None
    
    @staticmethod
    def _get_neighbors():
        """Generiert Nachbarschaftsverschiebungen."""
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                for dk in [-1, 0, 1]:
                    if di == dj == dk == 0:
                        continue
                    yield (di, dj, dk)
    
    def _validate_voids(self,
                       candidates: List[dict],
                       positions: np.ndarray) -> Iterator[dict]:
        """
        Validiert Void-Kandidaten gegen echte Galaxienpositionen.
        """
        for void in candidates:
            if self._is_valid_void(void, positions):
                yield void
    
    def _is_valid_void(self,
                      void: dict,
                      positions: np.ndarray,
                      min_radius: float = 10.0) -> bool:
        """
        Überprüft die Gültigkeit eines Void-Kandidaten.
        """
        if void['radius'] < min_radius:
            return False
            
        # Prüfe Galaxiendichte im Void
        center = void['center']
        radius = void['radius']
        
        distances = np.linalg.norm(positions - center, axis=1)
        galaxies_inside = np.sum(distances < radius)
        
        # Maximal erlaubte Galaxiendichte im Void
        max_density = 0.2  # 20% der mittleren Dichte
        volume = 4/3 * np.pi * radius**3
        if galaxies_inside / volume > max_density:
            return False
            
        return True
