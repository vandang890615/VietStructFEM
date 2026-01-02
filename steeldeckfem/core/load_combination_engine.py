# -*- coding: utf-8 -*-
"""
Load Combination Engine
TCVN 2737:2023 - Vietnamese Building Code for Loads
"""

from enum import Enum
from typing import Dict, List, Tuple


class LoadType(Enum):
    """Standard load types per TCVN 2737:2023"""
    DEAD = "D"          # Tĩnh tải (Dead load)
    LIVE = "L"          # Hoạt tải (Live load)
    WIND = "W"          # Gió (Wind)
    SEISMIC = "E"       # Động đất (Earthquake/Seismic)
    CRANE = "C"         # Cầu trục (Crane)
    SNOW = "S"          # Tuyết (Snow)
    TEMP = "T"          # Nhiệt độ (Temperature)


class LimitState(Enum):
    """Limit states for design"""
    ULS = "Ultimate Limit State"          # Trạng thái giới hạn cường độ
    SLS = "Serviceability Limit State"    # Trạng thái giới hạn sử dụng


class LoadCombination:
    """Represents a single load combination"""
    
    def __init__(self, name: str, factors: Dict[LoadType, float], limit_state: LimitState):
        """
        Args:
            name: Combination name (e.g., "LC1: 1.1D + 1.3L")
            factors: Dictionary mapping LoadType to factor
            limit_state: ULS or SLS
        """
        self.name = name
        self.factors = factors
        self.limit_state = limit_state
    
    def calculate(self, loads: Dict[LoadType, float]) -> float:
        """
        Calculate the total factored load.
        
        Args:
            loads: Dictionary of actual load values {LoadType: magnitude}
        
        Returns:
            Total factored load
        """
        total = 0.0
        for load_type, factor in self.factors.items():
            load_value = loads.get(load_type, 0.0)
            total += factor * load_value
        return total
    
    def get_formula(self) -> str:
        """Get the combination formula as a readable string"""
        terms = []
        for load_type, factor in self.factors.items():
            if factor != 0:
                sign = "+" if factor > 0 else "-"
                if abs(factor) == 1.0:
                    terms.append(f"{sign} {load_type.value}")
                else:
                    terms.append(f"{sign} {abs(factor):.1f}{load_type.value}")
        
        formula = " ".join(terms)
        if formula.startswith("+ "):
            formula = formula[2:]  # Remove leading +
        return formula


class LoadCombinationEngine:
    """Engine for generating TCVN 2737:2023 load combinations"""
    
    @staticmethod
    def get_uls_combinations() -> List[LoadCombination]:
        """
        Get all Ultimate Limit State (ULS) combinations per TCVN 2737:2023
        
        Returns:
            List of LoadCombination objects for ULS
        """
        combinations = []
        
        # LC1: 1.1D + 1.3L (Permanent + Variable - Basic)
        combinations.append(LoadCombination(
            "LC1: 1.1D + 1.3L",
            {LoadType.DEAD: 1.1, LoadType.LIVE: 1.3},
            LimitState.ULS
        ))
        
        # LC2: 1.1D + 1.3L + 0.8W (Permanent + Variable + Wind)
        combinations.append(LoadCombination(
            "LC2: 1.1D + 1.3L + 0.8W",
            {LoadType.DEAD: 1.1, LoadType.LIVE: 1.3, LoadType.WIND: 0.8},
            LimitState.ULS
        ))
        
        # LC3: 1.1D + 0.8L + 1.3W (Wind dominant)
        combinations.append(LoadCombination(
            "LC3: 1.1D + 0.8L + 1.3W",
            {LoadType.DEAD: 1.1, LoadType.LIVE: 0.8, LoadType.WIND: 1.3},
            LimitState.ULS
        ))
        
        # LC4: 1.1D + 1.3W (Permanent + Wind only)
        combinations.append(LoadCombination(
            "LC4: 1.1D + 1.3W",
            {LoadType.DEAD: 1.1, LoadType.WIND: 1.3},
            LimitState.ULS
        ))
        
        # LC5: 1.0D + 0.5L + 1.0E (Seismic combination - positive)
        combinations.append(LoadCombination(
            "LC5: 1.0D + 0.5L + 1.0E",
            {LoadType.DEAD: 1.0, LoadType.LIVE: 0.5, LoadType.SEISMIC: 1.0},
            LimitState.ULS
        ))
        
        # LC6: 1.0D + 0.5L - 1.0E (Seismic combination - negative)
        combinations.append(LoadCombination(
            "LC6: 1.0D + 0.5L - 1.0E",
            {LoadType.DEAD: 1.0, LoadType.LIVE: 0.5, LoadType.SEISMIC: -1.0},
            LimitState.ULS
        ))
        
        # LC7: 1.0D + 1.0C (Crane load)
        combinations.append(LoadCombination(
            "LC7: 1.0D + 1.0C",
            {LoadType.DEAD: 1.0, LoadType.CRANE: 1.0},
            LimitState.ULS
        ))
        
        # LC8: 0.9D + 1.3W (Uplift check - minimum dead load)
        combinations.append(LoadCombination(
            "LC8: 0.9D + 1.3W (Uplift)",
            {LoadType.DEAD: 0.9, LoadType.WIND: 1.3},
            LimitState.ULS
        ))
        
        return combinations
    
    @staticmethod
    def get_sls_combinations() -> List[LoadCombination]:
        """
        Get all Serviceability Limit State (SLS) combinations
        
        Returns:
            List of LoadCombination objects for SLS
        """
        combinations = []
        
        # SLS1: 1.0D + 1.0L (Characteristic combination)
        combinations.append(LoadCombination(
            "SLS1: 1.0D + 1.0L",
            {LoadType.DEAD: 1.0, LoadType.LIVE: 1.0},
            LimitState.SLS
        ))
        
        # SLS2: 1.0D + 0.7L + 0.7W (Frequent combination)
        combinations.append(LoadCombination(
            "SLS2: 1.0D + 0.7L + 0.7W",
            {LoadType.DEAD: 1.0, LoadType.LIVE: 0.7, LoadType.WIND: 0.7},
            LimitState.SLS
        ))
        
        # SLS3: 1.0D + 0.7W (Wind deflection check)
        combinations.append(LoadCombination(
            "SLS3: 1.0D + 0.7W",
            {LoadType.DEAD: 1.0, LoadType.WIND: 0.7},
            LimitState.SLS
        ))
        
        # SLS4: 1.0D (Quasi-permanent - for long-term deflection)
        combinations.append(LoadCombination(
            "SLS4: 1.0D (Permanent only)",
            {LoadType.DEAD: 1.0},
            LimitState.SLS
        ))
        
        return combinations
    
    @staticmethod
    def get_governing_case(loads: Dict[LoadType, float], 
                          limit_state: LimitState = LimitState.ULS) -> Tuple[LoadCombination, float]:
        """
        Get the governing (maximum) load combination.
        
        Args:
            loads: Dictionary of load values
            limit_state: ULS or SLS
        
        Returns:
            Tuple of (governing LoadCombination, maximum value)
        """
        if limit_state == LimitState.ULS:
            combinations = LoadCombinationEngine.get_uls_combinations()
        else:
            combinations = LoadCombinationEngine.get_sls_combinations()
        
        max_combo = None
        max_value = float('-inf')
        
        for combo in combinations:
            value = combo.calculate(loads)
            if value > max_value:
                max_value = value
                max_combo = combo
        
        return max_combo, max_value
    
    @staticmethod
    def calculate_all(loads: Dict[LoadType, float], 
                     limit_state: LimitState = LimitState.ULS) -> List[Tuple[LoadCombination, float]]:
        """
        Calculate all combinations for given loads.
        
        Args:
            loads: Dictionary of load values
            limit_state: ULS or SLS
        
        Returns:
            List of (LoadCombination, calculated value) tuples
        """
        if limit_state == LimitState.ULS:
            combinations = LoadCombinationEngine.get_uls_combinations()
        else:
            combinations = LoadCombinationEngine.get_sls_combinations()
        
        results = []
        for combo in combinations:
            value = combo.calculate(loads)
            results.append((combo, value))
        
        return results
