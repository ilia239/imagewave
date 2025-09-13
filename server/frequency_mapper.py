import csv
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FrequencyMapper:
    def __init__(self, csv_path=None):
        if csv_path is None:
            csv_path = Path(__file__).parent / "config" / "frequency_map.csv"
        
        self.intensities = []
        self.frequencies = []
        self._load_mapping(csv_path)
    
    def _load_mapping(self, csv_path):
        logger.debug(f"Loading frequency mapping from: {csv_path}")
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.intensities.append(float(row['intensity']))
                self.frequencies.append(float(row['frequency']))
        
        # Sort by intensity for interpolation
        sorted_pairs = sorted(zip(self.intensities, self.frequencies))
        self.intensities, self.frequencies = zip(*sorted_pairs)
        self.intensities = list(self.intensities)
        self.frequencies = list(self.frequencies)
        
        logger.debug(f"Loaded {len(self.intensities)} mapping points:")
        for i, f in zip(self.intensities, self.frequencies):
            logger.debug(f"  Intensity {i} -> Frequency {f}")
        
        logger.debug(f"Intensity range: {min(self.intensities)} - {max(self.intensities)}")
        logger.debug(f"Frequency range: {min(self.frequencies)} - {max(self.frequencies)}")
    
    def get_frequency(self, intensity):
        """Convert pixel intensity (0-255) to sine wave frequency using linear interpolation"""
        if intensity <= self.intensities[0]:
            return self.frequencies[0]
        if intensity >= self.intensities[-1]:
            return self.frequencies[-1]
        
        # Linear interpolation
        return np.interp(intensity, self.intensities, self.frequencies)
    
    def get_frequencies_batch(self, intensities):
        """Convert multiple intensities to frequencies efficiently"""
        return np.interp(intensities, self.intensities, self.frequencies)