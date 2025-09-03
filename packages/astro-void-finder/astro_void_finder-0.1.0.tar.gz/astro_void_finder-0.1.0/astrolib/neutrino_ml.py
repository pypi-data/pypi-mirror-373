"""
Machine Learning for Neutrino Physics
=================================

Advanced ML methods to constrain neutrino masses using cosmic voids
and large-scale structure formation. Combines statistical analysis
with modern machine learning techniques.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .resource_manager import ResourceManager
from .cache import SmartCache

class NeutrinoMassEstimator:
    """
    ML-based neutrino mass estimation from void statistics.
    
    Uses Random Forest regression to analyze void properties
    and extract constraints on neutrino masses.
    """
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.cache = SmartCache()
        self.model = None
        self.scaler = StandardScaler()
        
    def extract_void_features(self, voids: List[dict]) -> np.ndarray:
        """
        Extrahiert Features aus Void-Katalog.
        
        Args:
            voids: Liste von Void-Eigenschaften
            
        Returns:
            Array von Features
        """
        features = []
        
        for void in voids:
            # Basis-Features
            void_features = [
                void['radius'],
                void['volume'],
                void.get('density_contrast', 0),
                void.get('ellipticity', 1.0)
            ]
            
            # Erweiterte Features
            if 'density_profile' in void:
                profile = void['density_profile']
                void_features.extend([
                    np.mean(profile),
                    np.std(profile),
                    np.min(profile),
                    np.max(profile)
                ])
            
            features.append(void_features)
        
        return np.array(features)
    
    def train(self, void_catalogs: List[List[dict]], 
              neutrino_masses: np.ndarray,
              n_estimators: int = 100):
        """
        Trainiert ML-Modell zur Neutrino-Massenvorhersage.
        
        Args:
            void_catalogs: Liste von Void-Katalogen
            neutrino_masses: Wahre Neutrino-Massen
            n_estimators: Anzahl der Entscheidungsbäume
        """
        # Extrahiere Features
        X = np.vstack([
            self.extract_void_features(voids)
            for voids in void_catalogs
        ])
        y = np.repeat(neutrino_masses, [len(voids) for voids in void_catalogs])
        
        # Normalisiere Features
        X_scaled = self.scaler.fit_transform(X)
        
        # Trainiere Modell
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            n_jobs=self.resource_manager.get_optimal_thread_count()
        )
        self.model.fit(X_scaled, y)
    
    def predict(self, voids: List[dict]) -> Tuple[float, float]:
        """
        Schätzt Neutrino-Masse aus Void-Katalog.
        
        Args:
            voids: Liste von Void-Eigenschaften
            
        Returns:
            Tuple von (geschätzte Masse, Unsicherheit)
        """
        if self.model is None:
            raise RuntimeError("Modell muss erst trainiert werden")
        
        # Extrahiere und normalisiere Features
        X = self.extract_void_features(voids)
        X_scaled = self.scaler.transform(X)
        
        # Vorhersagen von einzelnen Bäumen
        predictions = np.array([
            tree.predict(X_scaled)
            for tree in self.model.estimators_
        ])
        
        # Mittlere Vorhersage und Unsicherheit
        mean_mass = np.mean(predictions)
        uncertainty = np.std(predictions)
        
        return mean_mass, uncertainty

class VoidNeutrinoAnalyzer:
    """
    Fortgeschrittene Void-Neutrino-Analyse.
    """
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.cache = SmartCache()
    
    def analyze_void_population(self, voids: List[dict], 
                              z: float) -> Dict[str, float]:
        """
        Analysiert Void-Population für Neutrino-Effekte.
        
        Args:
            voids: Liste von Void-Eigenschaften
            z: Rotverschiebung
            
        Returns:
            Dictionary mit statistischen Kennzahlen
        """
        # Cache-Lookup
        cache_key = f"void_stats_{len(voids)}_{z:.2f}"
        cached_result = self.cache.get(cache_key, voids)
        if cached_result is not None:
            return cached_result
        
        # Berechne Statistiken
        radii = np.array([void['radius'] for void in voids])
        volumes = np.array([void['volume'] for void in voids])
        
        stats = {
            'mean_radius': np.mean(radii),
            'std_radius': np.std(radii),
            'void_number_density': len(voids) / np.sum(volumes),
            'volume_fraction': np.sum(volumes) / (4/3 * np.pi * np.max(radii)**3),
            'size_function_slope': self._fit_size_function(radii)
        }
        
        # Cache Ergebnisse
        self.cache.set(cache_key, voids, stats)
        return stats
    
    def _fit_size_function(self, radii: np.ndarray) -> float:
        """
        Fittet Steigung der Größenverteilungsfunktion.
        """
        hist, edges = np.histogram(radii, bins='auto')
        centers = (edges[1:] + edges[:-1]) / 2
        
        # Log-Log Fit
        mask = hist > 0
        if np.sum(mask) < 2:
            return 0.0
            
        log_x = np.log10(centers[mask])
        log_y = np.log10(hist[mask])
        
        # Linear Fit
        coeffs = np.polyfit(log_x, log_y, 1)
        return coeffs[0]
    
    def estimate_neutrino_effects(self, 
                                void_stats: Dict[str, float],
                                z: float) -> Dict[str, float]:
        """
        Schätzt Neutrino-Effekte aus Void-Statistiken.
        
        Args:
            void_stats: Void-Populationsstatistiken
            z: Rotverschiebung
            
        Returns:
            Dictionary mit geschätzten Neutrino-Effekten
        """
        # Theoretische Vorhersagen für verschiedene Neutrino-Massen
        effects = {
            'size_suppression': self._estimate_size_suppression(
                void_stats['mean_radius'],
                void_stats['size_function_slope'],
                z
            ),
            'abundance_modification': self._estimate_abundance_modification(
                void_stats['void_number_density'],
                z
            ),
            'shape_distortion': self._estimate_shape_distortion(
                void_stats['volume_fraction'],
                z
            )
        }
        
        return effects
    
    def _estimate_size_suppression(self, 
                                 mean_radius: float,
                                 slope: float,
                                 z: float) -> float:
        """
        Schätzt Größenunterdrückung durch Neutrinos.
        """
        # Vereinfachtes Modell basierend auf linearer Theorie
        return -0.05 * slope * (1 + z)**(-1)
    
    def _estimate_abundance_modification(self,
                                      number_density: float,
                                      z: float) -> float:
        """
        Schätzt Modifikation der Void-Häufigkeit.
        """
        # Basierend auf Press-Schechter-Formalismus
        return -0.1 * np.log10(number_density) * (1 + z)**(-0.5)
    
    def _estimate_shape_distortion(self,
                                 volume_fraction: float,
                                 z: float) -> float:
        """
        Schätzt Formverzerrung durch Neutrino-Free-Streaming.
        """
        # Empirisches Modell
        return 0.03 * volume_fraction * (1 + z)**(-1.5)
