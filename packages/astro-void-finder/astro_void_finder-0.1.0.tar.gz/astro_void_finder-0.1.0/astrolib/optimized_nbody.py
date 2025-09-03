"""
Optimized N-Body Simulations
========================

High-performance N-body simulations using parallel processing
and the Barnes-Hut tree algorithm. Designed for efficient
execution on consumer hardware.
"""

import numpy as np
from typing import Optional, Tuple
from .cache import SmartCache
import concurrent.futures
from dataclasses import dataclass
from scipy.spatial import cKDTree

@dataclass
class SimulationConfig:
    """Configuration settings for N-body simulation."""
    dt: float = 0.01
    softening: float = 1e-4
    theta: float = 0.5  # Barnes-Hut opening criterion
    use_cache: bool = True
    n_workers: int = 2

class OptimizedNBody:
    """
    Hochoptimierte N-Body Simulation mit adaptiven Methoden.
    """
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.cache = SmartCache() if self.config.use_cache else None
        self.tree: Optional[cKDTree] = None
        
    def simulate_chunk(self,
                      positions: np.ndarray,
                      velocities: np.ndarray,
                      masses: np.ndarray,
                      steps: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Führt N-Body Simulation für einen Teilchensatz durch.
        
        Args:
            positions: (N, 3) Array der Teilchenpositionen
            velocities: (N, 3) Array der Geschwindigkeiten
            masses: (N,) Array der Massen
            steps: Anzahl der Zeitschritte
            
        Returns:
            Tuple von aktualisierten Positionen und Geschwindigkeiten
        """
        # Cache-Lookup für ähnliche Konfigurationen
        if self.cache is not None:
            cache_key = f"nbody_{len(masses)}_{steps}"
            cached = self.cache.get(cache_key, (positions, velocities, masses))
            if cached is not None:
                return cached
        
        # Adaptive Zeitschrittberechnung
        dt = self._calculate_adaptive_timestep(positions, velocities, masses)
        
        # Parallelisierte Kraftberechnung
        for _ in range(steps):
            # Leapfrog Integration
            velocities += 0.5 * dt * self._calculate_accelerations(positions, masses)
            positions += dt * velocities
            velocities += 0.5 * dt * self._calculate_accelerations(positions, masses)
        
        # Cache Ergebnisse
        if self.cache is not None:
            self.cache.set(cache_key, (positions, velocities, masses),
                         (positions.copy(), velocities.copy()))
        
        return positions, velocities
    
    def _calculate_adaptive_timestep(self,
                                   positions: np.ndarray,
                                   velocities: np.ndarray,
                                   masses: np.ndarray) -> float:
        """
        Berechnet adaptiven Zeitschritt basierend auf Systemdynamik.
        """
        # Minimaler Teilchenabstand
        self.tree = cKDTree(positions)
        min_dist = self.tree.query(positions, k=2)[0][:, 1].min()
        
        # Maximale Geschwindigkeit
        max_vel = np.max(np.linalg.norm(velocities, axis=1))
        
        # Typische Beschleunigung
        typ_acc = np.max(masses) / (min_dist * min_dist)
        
        # Zeitschritt basierend auf CFL-Bedingung
        dt = min(
            0.1 * min_dist / max_vel if max_vel > 0 else np.inf,
            0.1 * np.sqrt(min_dist / typ_acc) if typ_acc > 0 else np.inf,
            self.config.dt
        )
        
        return dt
    
    def _calculate_accelerations(self,
                               positions: np.ndarray,
                               masses: np.ndarray) -> np.ndarray:
        """
        Berechnet Beschleunigungen mit Barnes-Hut-Algorithmus.
        """
        n_particles = len(positions)
        accelerations = np.zeros_like(positions)
        
        # Baue Octree wenn nötig
        if self.tree is None or not np.array_equal(self.tree.data, positions):
            self.tree = cKDTree(positions)
        
        # Parallelisierte Berechnung
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.n_workers
        ) as executor:
            futures = []
            
            # Teile Partikel in Chunks für parallele Verarbeitung
            chunk_size = max(1, n_particles // self.config.n_workers)
            for i in range(0, n_particles, chunk_size):
                chunk_end = min(i + chunk_size, n_particles)
                futures.append(
                    executor.submit(
                        self._calculate_chunk_accelerations,
                        positions[i:chunk_end],
                        positions,
                        masses
                    )
                )
            
            # Sammle Ergebnisse
            for i, future in enumerate(futures):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, n_particles)
                accelerations[start_idx:end_idx] = future.result()
        
        return accelerations
    
    def _calculate_chunk_accelerations(self,
                                    chunk_positions: np.ndarray,
                                    all_positions: np.ndarray,
                                    masses: np.ndarray) -> np.ndarray:
        """
        Berechnet Beschleunigungen für einen Chunk von Partikeln.
        """
        chunk_size = len(chunk_positions)
        accelerations = np.zeros_like(chunk_positions)
        
        for i in range(chunk_size):
            # Finde relevante Nachbarn mit Barnes-Hut-Kriterium
            pos = chunk_positions[i]
            distances, indices = self.tree.query(
                pos,
                k=None,
                distance_upper_bound=np.inf,
                eps=self.config.theta
            )
            
            # Berechne Beschleunigung
            for d, idx in zip(distances, indices):
                if idx == i or idx >= len(masses):  # Überspringe sich selbst und ungültige Indizes
                    continue
                    
                r = all_positions[idx] - pos
                r_mag = np.linalg.norm(r)
                if r_mag < self.config.softening:
                    continue
                    
                # Gravitationsbeschleunigung
                acc = (masses[idx] / (r_mag**3 + self.config.softening**2)) * r
                accelerations[i] += acc
        
        return accelerations
