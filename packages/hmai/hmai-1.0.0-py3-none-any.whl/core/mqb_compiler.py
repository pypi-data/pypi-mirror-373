"""
Materials-to-Quantum Bridge (MQB) Compiler

This module implements the MQB compiler that translates generative quantum field
theory outputs into atomic and molecular lattice structures. It serves as the
critical bridge between theoretical quantum field configurations and practical
material blueprints.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
import logging
from enum import Enum
import json
import networkx as nx
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

logger = logging.getLogger(__name__)

class LatticeType(Enum):
    """Supported lattice types for material structures."""
    CUBIC = "cubic"
    HEXAGONAL = "hexagonal"
    TETRAGONAL = "tetragonal"
    ORTHORHOMBIC = "orthorhombic"
    MONOCLINIC = "monoclinic"
    TRICLINIC = "triclinic"
    CUSTOM = "custom"

@dataclass
class AtomicSpecification:
    """Specification for an atom in the material structure."""
    element_symbol: str
    position: Tuple[float, float, float]
    charge: float = 0.0
    magnetic_moment: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    exotic_properties: Dict[str, float] = field(default_factory=dict)

@dataclass
class BondSpecification:
    """Specification for bonds between atoms."""
    atom1_index: int
    atom2_index: int
    bond_type: str = "covalent"
    bond_strength: float = 1.0
    bond_length: float = 1.0
    exotic_interactions: Dict[str, float] = field(default_factory=dict)

@dataclass
class LatticeParameters:
    """Parameters defining the crystal lattice."""
    a: float  # Lattice parameter a
    b: float  # Lattice parameter b
    c: float  # Lattice parameter c
    alpha: float = 90.0  # Angle alpha (degrees)
    beta: float = 90.0   # Angle beta (degrees)
    gamma: float = 90.0  # Angle gamma (degrees)
    space_group: str = "P1"
    lattice_type: LatticeType = LatticeType.CUBIC

@dataclass
class MaterialStructure:
    """Complete specification of a material structure."""
    atoms: List[AtomicSpecification]
    bonds: List[BondSpecification]
    lattice: LatticeParameters
    unit_cell_volume: float
    density: float
    formation_energy: float = 0.0
    stability_score: float = 0.0
    hyper_properties: Dict[str, float] = field(default_factory=dict)

class QuantumFieldToAtomicMapper:
    """Maps quantum field parameters to atomic configurations."""
    
    def __init__(self):
        self.element_library = self._initialize_element_library()
        self.field_to_element_map = self._create_field_element_mapping()
    
    def _initialize_element_library(self) -> Dict[str, Dict]:
        """Initialize library of known and hypothetical elements."""
        # Standard elements
        standard_elements = {
            'H': {'atomic_number': 1, 'mass': 1.008, 'radius': 0.31, 'electronegativity': 2.20},
            'He': {'atomic_number': 2, 'mass': 4.003, 'radius': 0.28, 'electronegativity': 0.0},
            'Li': {'atomic_number': 3, 'mass': 6.941, 'radius': 1.28, 'electronegativity': 0.98},
            'C': {'atomic_number': 6, 'mass': 12.011, 'radius': 0.70, 'electronegativity': 2.55},
            'O': {'atomic_number': 8, 'mass': 15.999, 'radius': 0.66, 'electronegativity': 3.44},
            'Si': {'atomic_number': 14, 'mass': 28.085, 'radius': 1.11, 'electronegativity': 1.90},
            'Fe': {'atomic_number': 26, 'mass': 55.845, 'radius': 1.26, 'electronegativity': 1.83},
        }
        
        # Hypothetical hyper-elements (for exotic properties)
        hyper_elements = {
            'Hm': {'atomic_number': -1, 'mass': -1.0, 'radius': 0.50, 'electronegativity': 0.0},  # Negative mass
            'Qe': {'atomic_number': 119, 'mass': 300.0, 'radius': 2.00, 'electronegativity': 5.0},  # Quantum exotic
            'Me': {'atomic_number': 120, 'mass': 310.0, 'radius': 1.80, 'electronegativity': 0.1},  # Magnetic exotic
        }
        
        return {**standard_elements, **hyper_elements}
    
    def _create_field_element_mapping(self) -> Dict[str, str]:
        """Create mapping from field characteristics to elements."""
        return {
            'negative_mass': 'Hm',
            'exotic_magnetic': 'Me',
            'quantum_coherent': 'Qe',
            'standard_light': 'Li',
            'standard_heavy': 'Fe',
            'semiconducting': 'Si',
            'insulating': 'O',
            'metallic': 'Fe'
        }
    
    def map_field_to_elements(self, lagrangian_coeffs: np.ndarray) -> List[str]:
        """Map quantum field coefficients to appropriate elements."""
        elements = []
        
        # Analyze coefficient patterns to determine element types
        coeff_abs = np.abs(lagrangian_coeffs)
        coeff_signs = np.sign(lagrangian_coeffs)
        
        # Negative coefficients might indicate exotic elements
        negative_ratio = np.sum(coeff_signs < 0) / len(coeff_signs)
        if negative_ratio > 0.3:
            elements.append('Hm')  # Negative mass element
        
        # Large coefficients might indicate heavy elements
        large_coeff_ratio = np.sum(coeff_abs > 1.0) / len(coeff_abs)
        if large_coeff_ratio > 0.5:
            elements.append('Fe')
        else:
            elements.append('Li')
        
        # Oscillatory patterns might indicate quantum coherent elements
        if self._detect_oscillatory_pattern(lagrangian_coeffs):
            elements.append('Qe')
        
        # Ensure we have at least carbon for structural stability
        if 'C' not in elements and len(elements) < 3:
            elements.append('C')
        
        return list(set(elements))  # Remove duplicates
    
    def _detect_oscillatory_pattern(self, coeffs: np.ndarray) -> bool:
        """Detect oscillatory patterns in coefficients."""
        if len(coeffs) < 10:
            return False
        
        # Simple FFT-based pattern detection
        fft = np.fft.fft(coeffs[:20])  # Use first 20 coefficients
        dominant_freq = np.argmax(np.abs(fft[1:10])) + 1
        return np.abs(fft[dominant_freq]) > 0.5 * np.max(np.abs(fft))

class LatticeConstructor:
    """Constructs crystal lattices from atomic specifications."""
    
    def __init__(self):
        self.lattice_templates = self._initialize_lattice_templates()
    
    def _initialize_lattice_templates(self) -> Dict[LatticeType, Dict]:
        """Initialize templates for different lattice types."""
        return {
            LatticeType.CUBIC: {
                'positions': [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)],
                'coordination': 8,
                'symmetry': 'Oh'
            },
            LatticeType.HEXAGONAL: {
                'positions': [(0, 0, 0), (1/3, 2/3, 0.5)],
                'coordination': 6,
                'symmetry': 'D6h'
            },
            LatticeType.CUSTOM: {
                'positions': [],
                'coordination': 'variable',
                'symmetry': 'C1'
            }
        }
    
    def construct_lattice(self, elements: List[str], target_properties: Dict[str, float]) -> LatticeParameters:
        """Construct optimal lattice for given elements and properties."""
        # Determine lattice type based on elements and properties
        lattice_type = self._select_lattice_type(elements, target_properties)
        
        # Calculate lattice parameters
        lattice_params = self._calculate_lattice_parameters(elements, lattice_type, target_properties)
        
        return lattice_params
    
    def _select_lattice_type(self, elements: List[str], properties: Dict[str, float]) -> LatticeType:
        """Select appropriate lattice type based on elements and target properties."""
        # Heuristic selection based on properties
        if 'negative_mass' in properties:
            return LatticeType.CUSTOM  # Exotic properties need custom lattices
        elif 'magnetic_moment' in properties:
            return LatticeType.HEXAGONAL  # Magnetic materials often prefer hexagonal
        elif len(elements) <= 2:
            return LatticeType.CUBIC  # Simple binary systems
        else:
            return LatticeType.TETRAGONAL  # Complex systems
    
    def _calculate_lattice_parameters(self, elements: List[str], 
                                    lattice_type: LatticeType, 
                                    properties: Dict[str, float]) -> LatticeParameters:
        """Calculate lattice parameters for the given configuration."""
        # Base lattice parameter estimation from atomic radii
        base_param = self._estimate_base_parameter(elements)
        
        # Adjust based on target properties
        scaling_factors = self._calculate_scaling_factors(properties)
        
        a = base_param * scaling_factors.get('a_scale', 1.0)
        b = base_param * scaling_factors.get('b_scale', 1.0)
        c = base_param * scaling_factors.get('c_scale', 1.0)
        
        # Set angles based on lattice type
        angles = self._get_lattice_angles(lattice_type)
        
        return LatticeParameters(
            a=a, b=b, c=c,
            alpha=angles['alpha'],
            beta=angles['beta'],
            gamma=angles['gamma'],
            lattice_type=lattice_type
        )
    
    def _estimate_base_parameter(self, elements: List[str]) -> float:
        """Estimate base lattice parameter from atomic radii."""
        # This is a simplified estimation
        base_radius = 2.0  # Angstroms, default
        return 2.0 * base_radius  # Approximate nearest neighbor distance
    
    def _calculate_scaling_factors(self, properties: Dict[str, float]) -> Dict[str, float]:
        """Calculate scaling factors based on target properties."""
        factors = {'a_scale': 1.0, 'b_scale': 1.0, 'c_scale': 1.0}
        
        # Example adjustments (simplified)
        if 'density' in properties:
            density_factor = max(0.5, min(2.0, properties['density'] / 5.0))  # Assume target ~5 g/cm³
            factors['a_scale'] *= density_factor ** (-1/3)
            factors['b_scale'] *= density_factor ** (-1/3)
            factors['c_scale'] *= density_factor ** (-1/3)
        
        return factors
    
    def _get_lattice_angles(self, lattice_type: LatticeType) -> Dict[str, float]:
        """Get lattice angles for different lattice types."""
        angle_map = {
            LatticeType.CUBIC: {'alpha': 90.0, 'beta': 90.0, 'gamma': 90.0},
            LatticeType.HEXAGONAL: {'alpha': 90.0, 'beta': 90.0, 'gamma': 120.0},
            LatticeType.TETRAGONAL: {'alpha': 90.0, 'beta': 90.0, 'gamma': 90.0},
            LatticeType.CUSTOM: {'alpha': 95.0, 'beta': 85.0, 'gamma': 100.0}
        }
        return angle_map.get(lattice_type, {'alpha': 90.0, 'beta': 90.0, 'gamma': 90.0})

class MaterialsQuantumBridge:
    """
    Main MQB Compiler that translates quantum field theories to material structures.
    
    This is the core component that bridges the gap between generative quantum
    field theory outputs and practical atomic/molecular blueprints.
    """
    
    def __init__(self):
        self.field_mapper = QuantumFieldToAtomicMapper()
        self.lattice_constructor = LatticeConstructor()
        self.optimization_history = []
    
    def compile_field_to_material(self, field_data: Dict[str, Any]) -> MaterialStructure:
        """
        Compile quantum field data into material structure.
        
        Args:
            field_data: Output from GQFT engine containing Lagrangian and properties
            
        Returns:
            MaterialStructure object with complete atomic specification
        """
        logger.info("Starting field-to-material compilation")
        
        # Extract field parameters
        lagrangian_coeffs = field_data['lagrangian_coefficients']
        target_properties = {prop['name']: prop['value'] for prop in field_data['target_properties']}
        
        # Map field to elements
        elements = self.field_mapper.map_field_to_elements(lagrangian_coeffs)
        logger.info(f"Mapped field to elements: {elements}")
        
        # Construct lattice
        lattice = self.lattice_constructor.construct_lattice(elements, target_properties)
        
        # Generate atomic positions
        atoms = self._generate_atomic_positions(elements, lattice, target_properties)
        
        # Generate bonds
        bonds = self._generate_bonds(atoms, lattice)
        
        # Calculate properties
        structure_properties = self._calculate_structure_properties(atoms, bonds, lattice)
        
        # Create material structure
        material = MaterialStructure(
            atoms=atoms,
            bonds=bonds,
            lattice=lattice,
            unit_cell_volume=structure_properties['volume'],
            density=structure_properties['density'],
            formation_energy=structure_properties['formation_energy'],
            stability_score=structure_properties['stability'],
            hyper_properties=target_properties
        )
        
        logger.info(f"Compiled material with {len(atoms)} atoms and {len(bonds)} bonds")
        return material
    
    def _generate_atomic_positions(self, elements: List[str], 
                                 lattice: LatticeParameters,
                                 properties: Dict[str, float]) -> List[AtomicSpecification]:
        """Generate atomic positions in the unit cell."""
        atoms = []
        
        # Get lattice template positions
        template = self.lattice_constructor.lattice_templates[lattice.lattice_type]
        base_positions = template['positions']
        
        # Create atoms at template positions
        for i, pos in enumerate(base_positions):
            if i < len(elements):
                element = elements[i]
            else:
                element = elements[i % len(elements)]  # Cycle through elements
            
            # Convert fractional to Cartesian coordinates
            cartesian_pos = self._fractional_to_cartesian(pos, lattice)
            
            # Add exotic properties if applicable
            exotic_props = self._assign_exotic_properties(element, properties)
            
            atom = AtomicSpecification(
                element_symbol=element,
                position=cartesian_pos,
                charge=0.0,  # Neutral by default
                magnetic_moment=(0.0, 0.0, 0.0),  # Will be set based on properties
                exotic_properties=exotic_props
            )
            atoms.append(atom)
        
        # Add more atoms if needed for target composition
        while len(atoms) < max(4, len(elements) * 2):
            element = elements[len(atoms) % len(elements)]
            # Random position within unit cell
            pos = (np.random.rand(), np.random.rand(), np.random.rand())
            cartesian_pos = self._fractional_to_cartesian(pos, lattice)
            
            atom = AtomicSpecification(
                element_symbol=element,
                position=cartesian_pos,
                exotic_properties=self._assign_exotic_properties(element, properties)
            )
            atoms.append(atom)
        
        return atoms
    
    def _fractional_to_cartesian(self, frac_pos: Tuple[float, float, float], 
                                lattice: LatticeParameters) -> Tuple[float, float, float]:
        """Convert fractional coordinates to Cartesian."""
        x, y, z = frac_pos
        
        # Simplified conversion (assumes orthogonal axes for now)
        cart_x = x * lattice.a
        cart_y = y * lattice.b
        cart_z = z * lattice.c
        
        return (cart_x, cart_y, cart_z)
    
    def _assign_exotic_properties(self, element: str, target_properties: Dict[str, float]) -> Dict[str, float]:
        """Assign exotic properties to atoms based on element and targets."""
        exotic_props = {}
        
        # Hyper-element specific properties
        if element == 'Hm':  # Negative mass element
            exotic_props['effective_mass'] = -1.0
            exotic_props['gravitational_coupling'] = -1.0
        elif element == 'Qe':  # Quantum exotic element
            exotic_props['quantum_coherence'] = 0.95
            exotic_props['entanglement_range'] = 10.0
        elif element == 'Me':  # Magnetic exotic element
            exotic_props['magnetic_susceptibility'] = 100.0
            exotic_props['curie_temperature'] = 500.0
        
        # Apply target properties
        for prop_name, prop_value in target_properties.items():
            if 'magnetic' in prop_name.lower():
                exotic_props['magnetic_moment'] = prop_value
            elif 'mass' in prop_name.lower():
                exotic_props['effective_mass'] = prop_value
        
        return exotic_props
    
    def _generate_bonds(self, atoms: List[AtomicSpecification], 
                       lattice: LatticeParameters) -> List[BondSpecification]:
        """Generate bonds between atoms based on distances and chemistry."""
        bonds = []
        
        # Calculate distance matrix
        positions = np.array([atom.position for atom in atoms])
        distances = cdist(positions, positions)
        
        # Define bonding criteria (simplified)
        max_bond_distance = max(lattice.a, lattice.b, lattice.c) * 0.6
        
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                distance = distances[i, j]
                
                if distance < max_bond_distance and distance > 0.1:  # Not too close
                    bond_type = self._determine_bond_type(atoms[i], atoms[j], distance)
                    bond_strength = self._calculate_bond_strength(atoms[i], atoms[j], distance)
                    
                    bond = BondSpecification(
                        atom1_index=i,
                        atom2_index=j,
                        bond_type=bond_type,
                        bond_strength=bond_strength,
                        bond_length=distance
                    )
                    bonds.append(bond)
        
        return bonds
    
    def _determine_bond_type(self, atom1: AtomicSpecification, 
                           atom2: AtomicSpecification, distance: float) -> str:
        """Determine bond type based on atoms and distance."""
        # Simplified bond type determination
        if 'Hm' in [atom1.element_symbol, atom2.element_symbol]:
            return 'exotic_gravitational'
        elif 'Qe' in [atom1.element_symbol, atom2.element_symbol]:
            return 'quantum_coherent'
        elif distance < 2.0:
            return 'covalent'
        else:
            return 'van_der_waals'
    
    def _calculate_bond_strength(self, atom1: AtomicSpecification, 
                               atom2: AtomicSpecification, distance: float) -> float:
        """Calculate bond strength based on atoms and distance."""
        # Simplified Morse potential-like calculation
        base_strength = 1.0
        distance_factor = np.exp(-distance / 2.0)
        
        # Exotic bonding for hyper-elements
        if atom1.element_symbol in ['Hm', 'Qe', 'Me'] or atom2.element_symbol in ['Hm', 'Qe', 'Me']:
            base_strength *= 2.0  # Stronger exotic interactions
        
        return base_strength * distance_factor
    
    def _calculate_structure_properties(self, atoms: List[AtomicSpecification],
                                      bonds: List[BondSpecification],
                                      lattice: LatticeParameters) -> Dict[str, float]:
        """Calculate structural properties of the material."""
        # Calculate unit cell volume
        volume = lattice.a * lattice.b * lattice.c
        if lattice.lattice_type != LatticeType.CUBIC:
            # Apply angle corrections (simplified)
            volume *= np.sin(np.radians(lattice.gamma))
        
        # Estimate density (simplified)
        total_mass = sum(self._get_atomic_mass(atom.element_symbol) for atom in atoms)
        density = total_mass / (volume * 1.66054e-24)  # Convert to g/cm³
        
        # Estimate formation energy (very simplified)
        bond_energy = sum(bond.bond_strength for bond in bonds)
        formation_energy = -bond_energy / len(atoms)  # Per atom
        
        # Stability score based on coordination and bonding
        avg_coordination = len(bonds) * 2 / len(atoms)  # Average coordination number
        stability = min(1.0, avg_coordination / 6.0)  # Normalize to [0, 1]
        
        return {
            'volume': volume,
            'density': density,
            'formation_energy': formation_energy,
            'stability': stability
        }
    
    def _get_atomic_mass(self, element_symbol: str) -> float:
        """Get atomic mass for an element."""
        element_data = self.field_mapper.element_library.get(element_symbol, {})
        return element_data.get('mass', 12.0)  # Default to carbon mass
    
    def optimize_structure(self, material: MaterialStructure, 
                         optimization_targets: Dict[str, float]) -> MaterialStructure:
        """Optimize material structure for target properties."""
        logger.info("Starting structure optimization")
        
        def objective_function(params):
            # Params: [lattice_a, lattice_b, lattice_c, ...]
            # Simplified optimization - adjust lattice parameters
            test_lattice = LatticeParameters(
                a=max(1.0, params[0]),
                b=max(1.0, params[1]),
                c=max(1.0, params[2]),
                alpha=material.lattice.alpha,
                beta=material.lattice.beta,
                gamma=material.lattice.gamma,
                lattice_type=material.lattice.lattice_type
            )
            
            # Recalculate properties
            props = self._calculate_structure_properties(material.atoms, material.bonds, test_lattice)
            
            # Calculate objective (minimize difference from targets)
            objective = 0.0
            for target_name, target_value in optimization_targets.items():
                if target_name in props:
                    objective += (props[target_name] - target_value) ** 2
            
            return objective
        
        # Initial parameters
        initial_params = [material.lattice.a, material.lattice.b, material.lattice.c]
        
        # Optimize
        result = minimize(objective_function, initial_params, method='SLSQP',
                         bounds=[(1.0, 20.0), (1.0, 20.0), (1.0, 20.0)])
        
        if result.success:
            # Update material with optimized parameters
            optimized_lattice = LatticeParameters(
                a=result.x[0], b=result.x[1], c=result.x[2],
                alpha=material.lattice.alpha,
                beta=material.lattice.beta,
                gamma=material.lattice.gamma,
                lattice_type=material.lattice.lattice_type
            )
            
            # Recalculate all properties
            updated_props = self._calculate_structure_properties(
                material.atoms, material.bonds, optimized_lattice
            )
            
            # Create optimized material
            optimized_material = MaterialStructure(
                atoms=material.atoms,
                bonds=material.bonds,
                lattice=optimized_lattice,
                unit_cell_volume=updated_props['volume'],
                density=updated_props['density'],
                formation_energy=updated_props['formation_energy'],
                stability_score=updated_props['stability'],
                hyper_properties=material.hyper_properties
            )
            
            logger.info("Structure optimization completed successfully")
            return optimized_material
        else:
            logger.warning("Structure optimization failed, returning original")
            return material
    
    def export_structure(self, material: MaterialStructure, format: str = 'cif') -> str:
        """Export material structure in specified format."""
        if format.lower() == 'cif':
            return self._export_to_cif(material)
        elif format.lower() == 'json':
            return self._export_to_json(material)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_cif(self, material: MaterialStructure) -> str:
        """Export structure to CIF format."""
        cif_content = f"""# Hyper-Material AI Generated Structure
# Generated by HMAI MQB Compiler

data_HMAI_material

_cell_length_a    {material.lattice.a:.6f}
_cell_length_b    {material.lattice.b:.6f}
_cell_length_c    {material.lattice.c:.6f}
_cell_angle_alpha {material.lattice.alpha:.2f}
_cell_angle_beta  {material.lattice.beta:.2f}
_cell_angle_gamma {material.lattice.gamma:.2f}
_cell_volume      {material.unit_cell_volume:.6f}

_space_group_name_H-M_alt '{material.lattice.space_group}'
_space_group_IT_number    1

loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
"""
        
        for i, atom in enumerate(material.atoms):
            # Convert Cartesian to fractional coordinates
            frac_x = atom.position[0] / material.lattice.a
            frac_y = atom.position[1] / material.lattice.b
            frac_z = atom.position[2] / material.lattice.c
            
            cif_content += f"{atom.element_symbol}{i+1} {atom.element_symbol} {frac_x:.6f} {frac_y:.6f} {frac_z:.6f}\n"
        
        return cif_content
    
    def _export_to_json(self, material: MaterialStructure) -> str:
        """Export structure to JSON format."""
        structure_dict = {
            'atoms': [
                {
                    'element': atom.element_symbol,
                    'position': atom.position,
                    'charge': atom.charge,
                    'magnetic_moment': atom.magnetic_moment,
                    'exotic_properties': atom.exotic_properties
                }
                for atom in material.atoms
            ],
            'bonds': [
                {
                    'atom1': bond.atom1_index,
                    'atom2': bond.atom2_index,
                    'type': bond.bond_type,
                    'strength': bond.bond_strength,
                    'length': bond.bond_length,
                    'exotic_interactions': bond.exotic_interactions
                }
                for bond in material.bonds
            ],
            'lattice': {
                'a': material.lattice.a,
                'b': material.lattice.b,
                'c': material.lattice.c,
                'alpha': material.lattice.alpha,
                'beta': material.lattice.beta,
                'gamma': material.lattice.gamma,
                'type': material.lattice.lattice_type.value,
                'space_group': material.lattice.space_group
            },
            'properties': {
                'volume': material.unit_cell_volume,
                'density': material.density,
                'formation_energy': material.formation_energy,
                'stability_score': material.stability_score,
                'hyper_properties': material.hyper_properties
            }
        }
        
        return json.dumps(structure_dict, indent=2)
