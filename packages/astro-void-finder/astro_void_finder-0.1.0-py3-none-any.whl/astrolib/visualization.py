"""
Visualization Tools
================

Advanced visualization tools for cosmic voids, particle distributions,
and analysis results. Built on matplotlib with custom enhancements
for astrophysical data.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class VoidVisualizer:
    """
    Visualization tools for cosmic voids and their properties.
    
    Creates publication-quality plots of void slices, profiles,
    and statistical properties.
    """
    def __init__(self, style='dark_background'):
        plt.style.use(style)
        
    def plot_void_slice(self, density_field, void_centers, slice_idx, 
                       cmap='viridis', figsize=(10, 8)):
        """
        Erstellt eine 2D-Scheibe durch das Dichtefeld mit markierten Voids.
        
        Args:
            density_field (np.ndarray): 3D-Dichtefeld
            void_centers (np.ndarray): Array der Void-Zentren
            slice_idx (int): Index der zu zeigenden Scheibe
            cmap (str): Matplotlib Colormap
            figsize (tuple): Größe der Figur
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Zeige Dichtefeld
        im = ax.imshow(density_field[slice_idx], cmap=cmap, 
                      origin='lower', aspect='equal')
        
        # Markiere Void-Zentren
        mask = (void_centers[:, 0] == slice_idx)
        if np.any(mask):
            ax.scatter(void_centers[mask, 1], void_centers[mask, 2], 
                      c='red', marker='o', s=50, label='Void centers')
        
        plt.colorbar(im, label='Density')
        ax.set_title(f'Density Slice at index {slice_idx}')
        ax.legend()
        return fig, ax
    
    def plot_void_profile(self, radii, density, uncertainty, fit_params=None,
                         figsize=(8, 6)):
        """
        Plottet das radiale Dichteprofil eines Voids mit Fits.
        
        Args:
            radii (np.ndarray): Radiale Distanzen
            density (np.ndarray): Gemessene Dichtewerte
            uncertainty (np.ndarray): Unsicherheiten
            fit_params (tuple): Optional, Parameter des Profil-Fits
            figsize (tuple): Größe der Figur
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plotte Daten mit Fehlerbalken
        ax.errorbar(radii, density, yerr=uncertainty, fmt='o', 
                   label='Measured profile')
        
        if fit_params is not None:
            # Plotte gefittetes Profil
            r_smooth = np.linspace(radii.min(), radii.max(), 100)
            delta_c, r_v, alpha = fit_params
            profile = 1 + delta_c * (1 - (r_smooth/r_v)**alpha)
            ax.plot(r_smooth, profile, 'r-', label='Fitted profile')
        
        ax.set_xlabel('Radius [Mpc/h]')
        ax.set_ylabel('δ(r)')
        ax.set_title('Void Density Profile')
        ax.legend()
        return fig, ax
    
    def plot_neutrino_mass_likelihood(self, masses, chi_square, best_fit,
                                    uncertainty, figsize=(8, 6)):
        """
        Visualisiert die Likelihood-Funktion für die Neutrino-Masse.
        
        Args:
            masses (np.ndarray): Array der getesteten Neutrino-Massen
            chi_square (np.ndarray): Chi-Quadrat-Werte
            best_fit (float): Beste Neutrino-Masse
            uncertainty (float): Unsicherheit der Massenbestimmung
            figsize (tuple): Größe der Figur
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Konvertiere Chi-Quadrat in Likelihood
        likelihood = np.exp(-0.5 * (chi_square - chi_square.min()))
        
        # Plotte Likelihood
        ax.plot(masses, likelihood, 'b-', label='Likelihood')
        
        # Markiere besten Fit und Unsicherheit
        ax.axvline(best_fit, color='r', linestyle='--', 
                  label=f'Best fit: {best_fit:.3f} ± {uncertainty:.3f} eV')
        ax.fill_between(masses, 
                       np.zeros_like(masses),
                       likelihood,
                       where=(masses >= best_fit-uncertainty) & 
                             (masses <= best_fit+uncertainty),
                       alpha=0.3, color='r')
        
        ax.set_xlabel('Neutrino mass [eV]')
        ax.set_ylabel('Normalized Likelihood')
        ax.set_title('Neutrino Mass Constraint from Void Analysis')
        ax.legend()
        return fig, ax
