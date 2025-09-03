"""
Kosmologische Werkzeuge für die Void-Analyse
==========================================

Dieses Modul stellt Hilfsfunktionen für kosmologische Berechnungen bereit.
"""

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import InterpolatedUnivariateSpline

class Cosmology:
    """
    Klasse für kosmologische Berechnungen mit Neutrino-Effekten.
    """
    def __init__(self, H0=70.0, Om0=0.3, Ode0=0.7, Ob0=0.05, Tcmb0=2.725):
        """
        Initialisiert eine Kosmologie mit gegebenen Parametern.
        
        Args:
            H0 (float): Hubble-Konstante in km/s/Mpc
            Om0 (float): Materiedichte-Parameter heute
            Ode0 (float): Dunkle-Energie-Dichte-Parameter heute
            Ob0 (float): Baryonen-Dichte-Parameter heute
            Tcmb0 (float): CMB-Temperatur heute in K
        """
        self.H0 = H0
        self.Om0 = Om0
        self.Ode0 = Ode0
        self.Ob0 = Ob0
        self.Tcmb0 = Tcmb0
        
    def neutrino_density(self, m_nu, T_nu=1.95):
        """
        Berechnet die Neutrino-Energiedichte.
        
        Args:
            m_nu (float): Neutrino-Masse in eV
            T_nu (float): Neutrino-Temperatur in K
            
        Returns:
            float: Neutrino-Energiedichte in kritischen Einheiten
        """
        # Konstanten
        kB = 8.617333262e-5  # Boltzmann-Konstante in eV/K
        h = 4.135667696e-15  # Planck-Konstante in eV·s
        c = 299792458        # Lichtgeschwindigkeit in m/s
        
        # Berechnung der Neutrino-Energiedichte
        def integrand(p, m, T):
            E = np.sqrt(p**2 + m**2)
            return p**2 * E / (np.exp(E/(kB*T)) + 1)
        
        result, _ = quad(integrand, 0, np.inf, args=(m_nu, T_nu))
        
        # Konvertiere in kritische Dichte
        rho_c = 3 * (self.H0 * 1000/(c*1e6))**2 / (8 * np.pi * 6.674e-11)
        return result * 8 * np.pi / (h * c)**3 / rho_c
    
    def growth_factor(self, z, m_nu=0.0):
        """
        Berechnet den linearen Wachstumsfaktor mit Neutrino-Effekten.
        
        Args:
            z (float): Rotverschiebung
            m_nu (float): Summe der Neutrino-Massen in eV
            
        Returns:
            float: Linearer Wachstumsfaktor D(z)
        """
        def growth_integrand(a):
            # Scale factor a = 1/(1+z)
            Om_a = self.Om0 / (a**3) / self.E(a)**2
            return 1 / (a * self.E(a))**3
        
        a = 1 / (1 + z)
        norm = self.H0 * np.sqrt(self.Om0)
        
        # Integriere von früher Zeit bis a
        result, _ = quad(growth_integrand, 1e-7, a)
        
        # Normiere auf a=1
        norm_result, _ = quad(growth_integrand, 1e-7, 1.0)
        
        return result / norm_result
    
    def E(self, a):
        """
        Normierter Hubble-Parameter E(a) = H(a)/H0.
        """
        return np.sqrt(self.Om0/a**3 + self.Ode0)
    
    def linear_power_spectrum(self, k, z, m_nu=0.0):
        """
        Berechnet das lineare Leistungsspektrum mit Neutrino-Effekten.
        
        Args:
            k (np.ndarray): Wellenzahlen in h/Mpc
            z (float): Rotverschiebung
            m_nu (float): Summe der Neutrino-Massen in eV
            
        Returns:
            np.ndarray: P(k) in (Mpc/h)^3
        """
        # Basis-Eisenstein & Hu Transfer-Funktion
        ns = 0.96  # spektraler Index
        As = 2.1e-9  # Amplitude der Primordialfluktuationen
        
        # Einfache Implementierung - kann durch genauere ersetzt werden
        T = 1 / (1 + (k/0.02)**2)  
        
        # Neutrino-Free-Streaming-Dämpfung
        if m_nu > 0:
            f_nu = self.neutrino_density(m_nu) / self.Om0
            k_fs = 0.018 * np.sqrt(m_nu) * (1+z)**0.5  # Free-Streaming-Skala
            T *= (1 - 0.8 * f_nu * (1 + (k/k_fs)**2))
        
        # Gesamtes Leistungsspektrum
        P_k = As * (k/0.05)**(ns-1) * T**2 * self.growth_factor(z, m_nu)**2
        
        return P_k
