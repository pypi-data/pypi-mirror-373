"""
Hyper-Properties Validator

This module implements validation logic to ensure that generated quantum field
configurations and material structures are physically consistent and can actually
sustain the target hyper-properties.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import logging
from enum import Enum
from abc import ABC, abstractmethod
import warnings

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Different levels of validation rigor."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    RIGOROUS = "rigorous"
    EXPERIMENTAL = "experimental"

class ValidationResult(Enum):
    """Validation result status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNKNOWN = "unknown"

@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    overall_status: ValidationResult
    individual_tests: Dict[str, ValidationResult]
    warnings: List[str]
    errors: List[str] 
    confidence_score: float
    physical_consistency: float
    recommendations: List[str]
    test_details: Dict[str, Any]

class PhysicalConstraints:
    """Physical constraints and limits for validation."""
    
    # Energy scales (in eV)
    MIN_BINDING_ENERGY = -100.0
    MAX_BINDING_ENERGY = 100.0
    
    # Length scales (in Angstroms)
    MIN_BOND_LENGTH = 0.5
    MAX_BOND_LENGTH = 10.0
    
    # Mass constraints
    MIN_EFFECTIVE_MASS = -10.0  # Allow for negative mass hyper-materials
    MAX_EFFECTIVE_MASS = 1000.0
    
    # Magnetic constraints
    MAX_MAGNETIC_MOMENT = 100.0  # Bohr magnetons
    
    # Temperature constraints (in K)
    MIN_STABLE_TEMPERATURE = 1.0
    MAX_STABLE_TEMPERATURE = 5000.0
    
    # Density constraints (g/cm³)
    MIN_DENSITY = 0.001
    MAX_DENSITY = 50.0

class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.INTERMEDIATE):
        self.validation_level = validation_level
        self.constraints = PhysicalConstraints()
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationReport:
        """Validate the given data and return a report."""
        pass
    
    def _create_base_report(self) -> ValidationReport:
        """Create a base validation report."""
        return ValidationReport(
            overall_status=ValidationResult.UNKNOWN,
            individual_tests={},
            warnings=[],
            errors=[],
            confidence_score=0.0,
            physical_consistency=0.0,
            recommendations=[],
            test_details={}
        )

class QuantumFieldValidator(BaseValidator):
    """Validator for quantum field theory configurations."""
    
    def validate(self, field_data: Dict[str, Any]) -> ValidationReport:
        """Validate quantum field configuration."""
        report = self._create_base_report()
        
        # Extract field components
        lagrangian_coeffs = field_data.get('lagrangian_coefficients', np.array([]))
        field_config = field_data.get('field_config', {})
        target_properties = field_data.get('target_properties', [])
        
        # Run validation tests
        report.individual_tests['unitarity'] = self._test_unitarity(lagrangian_coeffs)
        report.individual_tests['causality'] = self._test_causality(lagrangian_coeffs)
        report.individual_tests['energy_bounds'] = self._test_energy_bounds(lagrangian_coeffs)
        report.individual_tests['symmetry'] = self._test_symmetry_preservation(field_config)
        report.individual_tests['renormalization'] = self._test_renormalization(lagrangian_coeffs)
        
        if self.validation_level in [ValidationLevel.RIGOROUS, ValidationLevel.EXPERIMENTAL]:
            report.individual_tests['stability'] = self._test_field_stability(lagrangian_coeffs)
            report.individual_tests['exotic_consistency'] = self._test_exotic_properties(target_properties)
        
        # Compile overall results
        self._compile_field_results(report)
        
        return report
    
    def _test_unitarity(self, lagrangian_coeffs: np.ndarray) -> ValidationResult:
        """Test unitarity constraints."""
        if len(lagrangian_coeffs) == 0:
            return ValidationResult.FAIL
        
        # Check for complex coefficients (simplified test)
        if np.any(np.iscomplex(lagrangian_coeffs)):
            # For complex coefficients, check unitarity condition
            norm_squared = np.sum(np.abs(lagrangian_coeffs) ** 2)
            if abs(norm_squared - 1.0) < 0.1:  # Allow some tolerance
                return ValidationResult.PASS
            else:
                return ValidationResult.WARNING
        
        # For real coefficients, check boundedness
        if np.all(np.abs(lagrangian_coeffs) < 10.0):
            return ValidationResult.PASS
        else:
            return ValidationResult.WARNING
    
    def _test_causality(self, lagrangian_coeffs: np.ndarray) -> ValidationResult:
        """Test causality constraints."""
        if len(lagrangian_coeffs) == 0:
            return ValidationResult.FAIL
        
        # Check for faster-than-light propagation indicators
        # This is a simplified test - in reality, causality is more complex
        
        # Check that kinetic energy terms have correct sign
        kinetic_terms = lagrangian_coeffs[:min(10, len(lagrangian_coeffs))]  # First terms are typically kinetic
        
        if np.any(kinetic_terms < -1.0):  # Allow some negative terms for exotic physics
            return ValidationResult.WARNING
        
        # Check for stable propagation
        if np.all(np.abs(kinetic_terms) < 100.0):
            return ValidationResult.PASS
        else:
            return ValidationResult.WARNING
    
    def _test_energy_bounds(self, lagrangian_coeffs: np.ndarray) -> ValidationResult:
        """Test energy boundedness."""
        if len(lagrangian_coeffs) == 0:
            return ValidationResult.FAIL
        
        # Check if energy can be bounded from below
        potential_terms = lagrangian_coeffs[10:min(30, len(lagrangian_coeffs))]
        
        if len(potential_terms) == 0:
            return ValidationResult.WARNING
        
        # For stability, we need the potential to have a minimum
        # This is a simplified check
        if np.any(potential_terms > 0):  # At least some positive terms for stability
            return ValidationResult.PASS
        else:
            return ValidationResult.WARNING
    
    def _test_symmetry_preservation(self, field_config: Dict) -> ValidationResult:
        """Test symmetry preservation."""
        symmetry_groups = field_config.get('symmetry_groups', [])
        
        if not symmetry_groups:
            return ValidationResult.WARNING
        
        # Check for standard model symmetries
        standard_symmetries = ['SU(3)', 'SU(2)', 'U(1)']
        preserved_count = sum(1 for sym in standard_symmetries if sym in symmetry_groups)
        
        if preserved_count >= 2:
            return ValidationResult.PASS
        elif preserved_count >= 1:
            return ValidationResult.WARNING
        else:
            return ValidationResult.FAIL
    
    def _test_renormalization(self, lagrangian_coeffs: np.ndarray) -> ValidationResult:
        """Test renormalization properties."""
        if len(lagrangian_coeffs) < 20:
            return ValidationResult.WARNING
        
        # Check for UV/IR divergences (simplified)
        # Look for power-law behavior in coefficients
        
        try:
            # Fit power law to coefficient magnitudes
            indices = np.arange(1, len(lagrangian_coeffs) + 1)
            log_coeffs = np.log(np.abs(lagrangian_coeffs) + 1e-10)
            log_indices = np.log(indices)
            
            # Linear fit in log space
            slope = np.polyfit(log_indices, log_coeffs, 1)[0]
            
            # Check if slope indicates renormalizable theory
            if -3 < slope < -0.5:  # Reasonable power law decay
                return ValidationResult.PASS
            else:
                return ValidationResult.WARNING
                
        except Exception:
            return ValidationResult.WARNING
    
    def _test_field_stability(self, lagrangian_coeffs: np.ndarray) -> ValidationResult:
        """Test field configuration stability."""
        # Check for unstable modes
        if len(lagrangian_coeffs) < 10:
            return ValidationResult.WARNING
        
        # Look for tachyonic modes (negative mass² terms)
        mass_terms = lagrangian_coeffs[5:15]  # Approximate mass terms
        
        tachyonic_count = np.sum(mass_terms < -0.1)
        total_count = len(mass_terms)
        
        if tachyonic_count == 0:
            return ValidationResult.PASS
        elif tachyonic_count < total_count / 3:  # Some tachyons might be OK for exotic physics
            return ValidationResult.WARNING
        else:
            return ValidationResult.FAIL
    
    def _test_exotic_properties(self, target_properties: List[Dict]) -> ValidationResult:
        """Test consistency of exotic properties."""
        if not target_properties:
            return ValidationResult.WARNING
        
        exotic_count = 0
        inconsistency_count = 0
        
        for prop in target_properties:
            prop_name = prop.get('name', '').lower()
            prop_value = prop.get('value', 0)
            
            # Check for exotic properties
            if any(keyword in prop_name for keyword in ['negative', 'exotic', 'quantum', 'hyper']):
                exotic_count += 1
                
                # Check for physical inconsistencies
                if 'mass' in prop_name and prop_value < -100:
                    inconsistency_count += 1  # Too negative mass
                elif 'magnetic' in prop_name and abs(prop_value) > 1000:
                    inconsistency_count += 1  # Unreasonably large magnetic moment
        
        if exotic_count == 0:
            return ValidationResult.WARNING  # No exotic properties found
        elif inconsistency_count == 0:
            return ValidationResult.PASS
        elif inconsistency_count < exotic_count / 2:
            return ValidationResult.WARNING
        else:
            return ValidationResult.FAIL
    
    def _compile_field_results(self, report: ValidationReport):
        """Compile overall validation results for quantum field."""
        test_results = report.individual_tests
        
        # Count passes, warnings, and failures
        passes = sum(1 for result in test_results.values() if result == ValidationResult.PASS)
        warnings = sum(1 for result in test_results.values() if result == ValidationResult.WARNING)
        failures = sum(1 for result in test_results.values() if result == ValidationResult.FAIL)
        total_tests = len(test_results)
        
        # Calculate confidence score
        if total_tests > 0:
            report.confidence_score = passes / total_tests
            report.physical_consistency = max(0, (passes - failures) / total_tests)
        
        # Determine overall status
        if failures > total_tests / 3:
            report.overall_status = ValidationResult.FAIL
            report.errors.append("Multiple critical validation tests failed")
        elif warnings > total_tests / 2:
            report.overall_status = ValidationResult.WARNING
            report.warnings.append("Several validation concerns identified")
        else:
            report.overall_status = ValidationResult.PASS
        
        # Add recommendations
        if failures > 0:
            report.recommendations.append("Review field configuration for physical consistency")
        if warnings > 0:
            report.recommendations.append("Consider adjusting parameters to improve stability")

class MaterialValidator(BaseValidator):
    """Validator for material structures."""
    
    def validate(self, material_structure) -> ValidationReport:
        """Validate material structure."""
        report = self._create_base_report()
        
        # Run structural validation tests
        report.individual_tests['geometry'] = self._test_geometry(material_structure)
        report.individual_tests['bonding'] = self._test_bonding(material_structure)
        report.individual_tests['stability'] = self._test_structural_stability(material_structure)
        report.individual_tests['density'] = self._test_density(material_structure)
        report.individual_tests['composition'] = self._test_composition(material_structure)
        
        if self.validation_level in [ValidationLevel.RIGOROUS, ValidationLevel.EXPERIMENTAL]:
            report.individual_tests['thermodynamics'] = self._test_thermodynamics(material_structure)
            report.individual_tests['exotic_elements'] = self._test_exotic_elements(material_structure)
        
        # Compile results
        self._compile_material_results(report, material_structure)
        
        return report
    
    def _test_geometry(self, material) -> ValidationResult:
        """Test geometric consistency."""
        atoms = material.atoms
        lattice = material.lattice
        
        # Check lattice parameters
        if any(param <= 0 for param in [lattice.a, lattice.b, lattice.c]):
            return ValidationResult.FAIL
        
        # Check atomic positions
        for atom in atoms:
            pos = atom.position
            if any(np.isnan(coord) or np.isinf(coord) for coord in pos):
                return ValidationResult.FAIL
        
        # Check for reasonable distances
        positions = np.array([atom.position for atom in atoms])
        if len(positions) > 1:
            distances = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    distances.append(dist)
            
            min_dist = min(distances)
            max_dist = max(distances)
            
            if min_dist < self.constraints.MIN_BOND_LENGTH:
                return ValidationResult.WARNING  # Atoms too close
            if max_dist > 2 * max(lattice.a, lattice.b, lattice.c):
                return ValidationResult.WARNING  # Atoms too far
        
        return ValidationResult.PASS
    
    def _test_bonding(self, material) -> ValidationResult:
        """Test bonding consistency."""
        bonds = material.bonds
        atoms = material.atoms
        
        if not bonds:
            return ValidationResult.WARNING  # No bonds defined
        
        # Check bond lengths and strengths
        for bond in bonds:
            if bond.bond_length < self.constraints.MIN_BOND_LENGTH:
                return ValidationResult.WARNING
            if bond.bond_length > self.constraints.MAX_BOND_LENGTH:
                return ValidationResult.WARNING
            if bond.bond_strength < 0:
                return ValidationResult.WARNING  # Negative bond strength unusual
        
        # Check connectivity
        n_atoms = len(atoms)
        connectivity = np.zeros((n_atoms, n_atoms))
        
        for bond in bonds:
            i, j = bond.atom1_index, bond.atom2_index
            if 0 <= i < n_atoms and 0 <= j < n_atoms:
                connectivity[i, j] = connectivity[j, i] = 1
        
        # Check that structure is connected (at least one path between any two atoms)
        # This is a simplified check
        connected_atoms = set()
        
        def dfs(atom_idx, visited):
            visited.add(atom_idx)
            connected_atoms.add(atom_idx)
            for neighbor in range(n_atoms):
                if connectivity[atom_idx, neighbor] and neighbor not in visited:
                    dfs(neighbor, visited)
        
        if n_atoms > 0:
            dfs(0, set())
            if len(connected_atoms) < n_atoms * 0.8:  # Allow some isolated atoms
                return ValidationResult.WARNING
        
        return ValidationResult.PASS
    
    def _test_structural_stability(self, material) -> ValidationResult:
        """Test structural stability."""
        stability_score = material.stability_score
        
        if stability_score < 0.3:
            return ValidationResult.FAIL
        elif stability_score < 0.7:
            return ValidationResult.WARNING
        else:
            return ValidationResult.PASS
    
    def _test_density(self, material) -> ValidationResult:
        """Test density reasonableness."""
        density = material.density
        
        if density < self.constraints.MIN_DENSITY:
            return ValidationResult.WARNING  # Very low density
        elif density > self.constraints.MAX_DENSITY:
            return ValidationResult.WARNING  # Very high density (but could be exotic)
        else:
            return ValidationResult.PASS
    
    def _test_composition(self, material) -> ValidationResult:
        """Test compositional reasonableness."""
        atoms = material.atoms
        
        # Count elements
        element_counts = {}
        for atom in atoms:
            element = atom.element_symbol
            element_counts[element] = element_counts.get(element, 0) + 1
        
        # Check for reasonable composition
        if len(element_counts) == 0:
            return ValidationResult.FAIL
        
        # Check for exotic elements
        exotic_elements = ['Hm', 'Qe', 'Me']  # Hyper-elements
        exotic_count = sum(element_counts.get(elem, 0) for elem in exotic_elements)
        total_count = sum(element_counts.values())
        
        if exotic_count > total_count * 0.8:  # Too many exotic elements
            return ValidationResult.WARNING
        
        return ValidationResult.PASS
    
    def _test_thermodynamics(self, material) -> ValidationResult:
        """Test thermodynamic consistency."""
        formation_energy = material.formation_energy
        
        # Check formation energy reasonableness
        if formation_energy > self.constraints.MAX_BINDING_ENERGY:
            return ValidationResult.WARNING  # Very high formation energy
        elif formation_energy < self.constraints.MIN_BINDING_ENERGY:
            return ValidationResult.WARNING  # Very low formation energy
        
        return ValidationResult.PASS
    
    def _test_exotic_elements(self, material) -> ValidationResult:
        """Test exotic element consistency."""
        atoms = material.atoms
        exotic_properties = {}
        
        for atom in atoms:
            if atom.exotic_properties:
                exotic_properties.update(atom.exotic_properties)
        
        # Check exotic properties for consistency
        for prop_name, prop_value in exotic_properties.items():
            if 'mass' in prop_name.lower():
                if not (self.constraints.MIN_EFFECTIVE_MASS <= prop_value <= self.constraints.MAX_EFFECTIVE_MASS):
                    return ValidationResult.WARNING
            elif 'magnetic' in prop_name.lower():
                if abs(prop_value) > self.constraints.MAX_MAGNETIC_MOMENT:
                    return ValidationResult.WARNING
        
        return ValidationResult.PASS
    
    def _compile_material_results(self, report: ValidationReport, material):
        """Compile overall validation results for material structure."""
        test_results = report.individual_tests
        
        # Count passes, warnings, and failures
        passes = sum(1 for result in test_results.values() if result == ValidationResult.PASS)
        warnings = sum(1 for result in test_results.values() if result == ValidationResult.WARNING)
        failures = sum(1 for result in test_results.values() if result == ValidationResult.FAIL)
        total_tests = len(test_results)
        
        # Calculate scores
        if total_tests > 0:
            report.confidence_score = passes / total_tests
            report.physical_consistency = max(0, (passes - failures) / total_tests)
        
        # Determine overall status
        if failures > 0:
            report.overall_status = ValidationResult.FAIL
            report.errors.append("Critical structural validation failures detected")
        elif warnings > total_tests / 2:
            report.overall_status = ValidationResult.WARNING
            report.warnings.append("Structural concerns identified")
        else:
            report.overall_status = ValidationResult.PASS
        
        # Add specific recommendations
        if material.stability_score < 0.5:
            report.recommendations.append("Consider structural optimization to improve stability")
        if material.density > 20.0:
            report.recommendations.append("Verify high density is consistent with target properties")

class HyperPropertiesValidator(BaseValidator):
    """Main validator class that orchestrates all validation processes."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.INTERMEDIATE):
        super().__init__(validation_level)
        self.field_validator = QuantumFieldValidator(validation_level)
        self.material_validator = MaterialValidator(validation_level)
    
    def validate_complete_system(self, field_data: Dict[str, Any], 
                                material_structure,
                                assembly_pathway = None) -> ValidationReport:
        """Validate the complete HMAI system output."""
        logger.info("Starting comprehensive system validation")
        
        # Validate quantum field
        field_report = self.field_validator.validate(field_data)
        logger.info(f"Field validation: {field_report.overall_status.value}")
        
        # Validate material structure
        material_report = self.material_validator.validate(material_structure)
        logger.info(f"Material validation: {material_report.overall_status.value}")
        
        # Create combined report
        combined_report = self._combine_reports(field_report, material_report)
        
        # Add system-level validation
        self._validate_system_consistency(combined_report, field_data, material_structure)
        
        # Add assembly pathway validation if provided
        if assembly_pathway is not None:
            self._validate_assembly_pathway(combined_report, assembly_pathway)
        
        logger.info(f"Overall system validation: {combined_report.overall_status.value}")
        logger.info(f"Confidence score: {combined_report.confidence_score:.3f}")
        
        return combined_report
    
    def _combine_reports(self, field_report: ValidationReport, 
                        material_report: ValidationReport) -> ValidationReport:
        """Combine multiple validation reports."""
        combined_report = self._create_base_report()
        
        # Combine individual tests
        combined_report.individual_tests.update({
            f"field_{k}": v for k, v in field_report.individual_tests.items()
        })
        combined_report.individual_tests.update({
            f"material_{k}": v for k, v in material_report.individual_tests.items()
        })
        
        # Combine warnings and errors
        combined_report.warnings.extend(field_report.warnings)
        combined_report.warnings.extend(material_report.warnings)
        combined_report.errors.extend(field_report.errors)
        combined_report.errors.extend(material_report.errors)
        
        # Combine recommendations
        combined_report.recommendations.extend(field_report.recommendations)
        combined_report.recommendations.extend(material_report.recommendations)
        
        # Calculate combined scores
        combined_report.confidence_score = (field_report.confidence_score + material_report.confidence_score) / 2
        combined_report.physical_consistency = (field_report.physical_consistency + material_report.physical_consistency) / 2
        
        # Determine overall status
        if (field_report.overall_status == ValidationResult.FAIL or 
            material_report.overall_status == ValidationResult.FAIL):
            combined_report.overall_status = ValidationResult.FAIL
        elif (field_report.overall_status == ValidationResult.WARNING or 
              material_report.overall_status == ValidationResult.WARNING):
            combined_report.overall_status = ValidationResult.WARNING
        else:
            combined_report.overall_status = ValidationResult.PASS
        
        return combined_report
    
    def _validate_system_consistency(self, report: ValidationReport, 
                                   field_data: Dict[str, Any], 
                                   material_structure):
        """Validate consistency between field and material components."""
        # Check that target properties are consistent
        field_properties = {prop['name']: prop['value'] for prop in field_data.get('target_properties', [])}
        material_properties = material_structure.hyper_properties
        
        consistency_score = 0.0
        property_count = 0
        
        for prop_name in field_properties:
            if prop_name in material_properties:
                field_value = field_properties[prop_name]
                material_value = material_properties[prop_name]
                
                if field_value != 0:
                    relative_error = abs(field_value - material_value) / abs(field_value)
                    consistency_score += max(0, 1 - relative_error)
                    property_count += 1
        
        if property_count > 0:
            avg_consistency = consistency_score / property_count
            if avg_consistency < 0.7:
                report.warnings.append("Inconsistency between field and material properties detected")
                report.recommendations.append("Review property mapping between field and structure")
        
        # Add consistency test result
        if property_count == 0:
            report.individual_tests['system_consistency'] = ValidationResult.WARNING
        elif avg_consistency > 0.8:
            report.individual_tests['system_consistency'] = ValidationResult.PASS
        else:
            report.individual_tests['system_consistency'] = ValidationResult.WARNING
    
    def _validate_assembly_pathway(self, report: ValidationReport, assembly_pathway):
        """Validate assembly pathway feasibility."""
        # Check formation probability
        if assembly_pathway.formation_probability < 1e-6:
            report.warnings.append("Very low formation probability - synthesis may be challenging")
        
        # Check kinetic accessibility
        if assembly_pathway.kinetic_accessibility < 0.1:
            report.warnings.append("Low kinetic accessibility - high activation barriers present")
        
        # Check stability
        if assembly_pathway.overall_stability < 0:
            report.warnings.append("Negative overall stability - material may be metastable")
        
        # Add assembly validation result
        if (assembly_pathway.formation_probability > 1e-3 and 
            assembly_pathway.kinetic_accessibility > 0.3 and 
            assembly_pathway.overall_stability > -0.1):
            report.individual_tests['assembly_feasibility'] = ValidationResult.PASS
        else:
            report.individual_tests['assembly_feasibility'] = ValidationResult.WARNING
    
    def generate_validation_summary(self, report: ValidationReport) -> str:
        """Generate a human-readable validation summary."""
        summary = f"""
HMAI System Validation Summary
==============================

Overall Status: {report.overall_status.value.upper()}
Confidence Score: {report.confidence_score:.2%}
Physical Consistency: {report.physical_consistency:.2%}

Individual Test Results:
"""
        
        for test_name, result in report.individual_tests.items():
            status_symbol = {"pass": "✓", "warning": "⚠", "fail": "✗", "unknown": "?"}.get(result.value, "?")
            summary += f"  {status_symbol} {test_name}: {result.value}\n"
        
        if report.warnings:
            summary += f"\nWarnings ({len(report.warnings)}):\n"
            for warning in report.warnings:
                summary += f"  ⚠ {warning}\n"
        
        if report.errors:
            summary += f"\nErrors ({len(report.errors)}):\n"
            for error in report.errors:
                summary += f"  ✗ {error}\n"
        
        if report.recommendations:
            summary += f"\nRecommendations:\n"
            for rec in report.recommendations:
                summary += f"  → {rec}\n"
        
        return summary
