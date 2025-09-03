"""
Adaptive Resource Management
========================

Smart system resource management that adapts to available hardware.
Optimizes performance while preventing system overload.
"""

import psutil
import numpy as np
from dataclasses import dataclass
import threading
from typing import Dict, Optional
import time
import logging

@dataclass
class SystemResources:
    """System resource information container."""
    available_memory_mb: float
    cpu_count: int
    cpu_usage: float
    disk_space_mb: float

class ResourceManager:
    """
    Intelligenter Ressourcenmanager für optimale Performanz.
    """
    def __init__(self, 
                 min_memory_mb: float = 500,
                 max_memory_mb: float = 4000,
                 target_cpu_usage: float = 0.75):
        self.min_memory_mb = min_memory_mb
        self.max_memory_mb = max_memory_mb
        self.target_cpu_usage = target_cpu_usage
        self._monitor_thread = None
        self._stop_monitor = threading.Event()
        self.current_resources = self._get_system_resources()
        self._chunk_sizes: Dict[str, int] = {}
        
        # Konfiguriere Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ResourceManager")
    
    def start_monitoring(self):
        """Startet Ressourcenüberwachung im Hintergrund."""
        if self._monitor_thread is None:
            self._stop_monitor.clear()
            self._monitor_thread = threading.Thread(
                target=self._monitor_resources
            )
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stoppt Ressourcenüberwachung."""
        if self._monitor_thread is not None:
            self._stop_monitor.set()
            self._monitor_thread.join()
            self._monitor_thread = None
    
    def _monitor_resources(self):
        """Überwacht Systemressourcen kontinuierlich."""
        while not self._stop_monitor.is_set():
            self.current_resources = self._get_system_resources()
            self._adjust_chunk_sizes()
            time.sleep(5)  # Aktualisiere alle 5 Sekunden
    
    def _get_system_resources(self) -> SystemResources:
        """Ermittelt aktuelle Systemressourcen."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return SystemResources(
            available_memory_mb=memory.available / (1024 * 1024),
            cpu_count=psutil.cpu_count(),
            cpu_usage=psutil.cpu_percent() / 100,
            disk_space_mb=disk.free / (1024 * 1024)
        )
    
    def get_optimal_chunk_size(self, operation: str) -> int:
        """
        Bestimmt optimale Chunk-Größe basierend auf verfügbaren Ressourcen.
        
        Args:
            operation: Art der Operation ('void_finding', 'nbody', etc.)
            
        Returns:
            Optimale Chunk-Größe in Anzahl der Elemente
        """
        base_sizes = {
            'void_finding': 100000,
            'nbody': 10000,
            'density_field': 50000
        }
        
        if operation not in self._chunk_sizes:
            self._chunk_sizes[operation] = base_sizes.get(operation, 50000)
        
        # Anpassung basierend auf verfügbarem Speicher
        memory_factor = min(1.0, self.current_resources.available_memory_mb / 
                          self.max_memory_mb)
        
        # Anpassung basierend auf CPU-Auslastung
        cpu_factor = min(1.0, (1 - self.current_resources.cpu_usage) / 
                        (1 - self.target_cpu_usage))
        
        adjusted_size = int(self._chunk_sizes[operation] * 
                          min(memory_factor, cpu_factor))
        
        return max(1000, adjusted_size)  # Mindestgröße
    
    def get_optimal_thread_count(self) -> int:
        """
        Bestimmt optimale Anzahl von Worker-Threads.
        """
        # Berücksichtige CPU-Kerne und aktuelle Auslastung
        available_cores = max(1, self.current_resources.cpu_count - 1)
        usage_factor = 1 - self.current_resources.cpu_usage
        
        optimal_threads = max(1, int(available_cores * usage_factor))
        return min(optimal_threads, 4)  # Maximum 4 Threads
    
    def _adjust_chunk_sizes(self):
        """Passt Chunk-Größen basierend auf Ressourcennutzung an."""
        for operation in self._chunk_sizes:
            current_size = self._chunk_sizes[operation]
            
            # Erhöhe Größe wenn Ressourcen verfügbar
            if (self.current_resources.available_memory_mb > self.max_memory_mb * 0.7 and
                self.current_resources.cpu_usage < self.target_cpu_usage * 0.8):
                new_size = int(current_size * 1.2)
                self.logger.info(f"Erhöhe Chunk-Größe für {operation}: {new_size}")
            
            # Verringere Größe bei Ressourcenknappheit
            elif (self.current_resources.available_memory_mb < self.min_memory_mb or
                  self.current_resources.cpu_usage > self.target_cpu_usage * 1.2):
                new_size = int(current_size * 0.8)
                self.logger.info(f"Verringere Chunk-Größe für {operation}: {new_size}")
            
            self._chunk_sizes[operation] = new_size
    
    def estimate_memory_usage(self, array_shape: tuple, dtype=np.float64) -> float:
        """
        Schätzt Speicherverbrauch für Arrays.
        
        Args:
            array_shape: Form des Arrays
            dtype: Datentyp des Arrays
            
        Returns:
            Geschätzter Speicherverbrauch in MB
        """
        bytes_per_element = np.dtype(dtype).itemsize
        total_bytes = np.prod(array_shape) * bytes_per_element
        return total_bytes / (1024 * 1024)  # Konvertiere zu MB
    
    def suggest_dtype(self, data_range: tuple) -> np.dtype:
        """
        Schlägt optimalen Datentyp basierend auf Wertebereich vor.
        
        Args:
            data_range: (min_value, max_value) der Daten
            
        Returns:
            Numpy dtype
        """
        min_val, max_val = data_range
        
        if min_val >= 0:
            if max_val <= 255:
                return np.uint8
            elif max_val <= 65535:
                return np.uint16
        
        if min_val >= -32768 and max_val <= 32767:
            return np.int16
        elif min_val >= -2147483648 and max_val <= 2147483647:
            return np.int32
        
        return np.float32  # Standard für Fließkommazahlen
