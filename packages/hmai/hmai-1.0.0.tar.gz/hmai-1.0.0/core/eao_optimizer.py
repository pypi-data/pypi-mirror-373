"""
Entropic Assembly Optimizer (EAO)

This module implements the Entropic Assembly Optimizer that uses entropy-based
stability principles to simulate how novel atoms self-assemble into usable
bulk materials. It ensures that the designed hyper-materials can actually
form stable structures under realistic conditions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import logging
from enum import Enum
from scipy.optimize import minimize, differential_evolution
from scipy.special import logsumexp
from scipy.stats import boltzmann
import networkx as nx
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

logger = logging.getLogger(__name__)

class AssemblyConditions(Enum):
    """Different conditions for material assembly."""
    VACUUM = "vacuum"
    ATMOSPHERIC = "atmospheric"
    HIGH_PRESSURE = "high_pressure"
    LOW_TEMPERATURE = "low_temperature"
    HIGH_TEMPERATURE = "high_temperature"
    MAGNETIC_FIELD = "magnetic_field"
    ELECTRIC_FIELD = "electric_field"

@dataclass
class EnvironmentalParameters:
    """Parameters defining the assembly environment."""
    temperature: float = 300.0  # Kelvin
    pressure: float = 1.0  # atm
    magnetic_field: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Tesla
    electric_field: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # V/m
    atmosphere_composition: Dict[str, float] = field(default_factory=lambda: {'N2': 0.78, 'O2': 0.21, 'Ar': 0.01})
    solution_ph: Optional[float] = None
    ionic_strength: float = 0.0

@dataclass
class AssemblyState:
    """Represents a state in the assembly process."""
    configuration: np.ndarray  # Positions of all atoms/molecules
    energy: float
    entropy: float
    free_energy: float
    stability_metrics: Dict[str, float]
    time_step: int = 0

@dataclass
class AssemblyPathway:
    """Represents a complete assembly pathway."""
    states: List[AssemblyState]
    transition_barriers: List[float]
    overall_stability: float
    formation_probability: float
    kinetic_accessibility: float

class EntropyCalculator:
    """Calculates various entropy contributions to the system."""
    
    def __init__(self, k_b: float = 8.617e-5):  # Boltzmann constant in eV/K
        self.k_b = k_b
        
    def configurational_entropy(self, positions: np.ndarray, 
                              lattice_params: Tuple[float, float, float]) -> float:
        """Calculate configurational entropy based on atomic positions."""
        n_atoms = len(positions)
        if n_atoms < 2:
            return 0.0
        
        # Calculate pair correlation function
        distances = self._calculate_pairwise_distances(positions)
        
        # Estimate configurational entropy using pair correlations
        # S_config = -k_B * sum(p_i * ln(p_i)) where p_i are occupancy probabilities
        
        # Discretize space and calculate occupancy probabilities
        bin_edges = np.linspace(0, max(lattice_params), 20)
        hist, _ = np.histogram(distances.flatten(), bins=bin_edges, density=True)
        
        # Remove zeros and normalize
        hist = hist[hist > 0]
        hist = hist / np.sum(hist)
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log(hist))
        return entropy
    
    def vibrational_entropy(self, positions: np.ndarray, 
                          mass_matrix: np.ndarray,
                          temperature: float) -> float:
        """Calculate vibrational entropy using harmonic approximation."""
        n_atoms = len(positions)
        
        # Simplified harmonic approximation
        # Calculate average frequency from nearest neighbor distances
        distances = self._calculate_pairwise_distances(positions)
        avg_distance = np.mean(distances[distances > 0])
        
        # Estimate vibrational frequency (simplified)
        omega = 1.0 / avg_distance  # Rough approximation
        
        # Quantum harmonic oscillator entropy
        x = omega / (2 * self.k_b * temperature)
        if x < 1e-10:  # High temperature limit
            entropy = self.k_b * (1 - np.log(x))
        else:
            entropy = self.k_b * (x / (np.exp(x) - 1) - np.log(1 - np.exp(-x)))
        
        return entropy * 3 * n_atoms  # 3N vibrational modes
    
    def mixing_entropy(self, composition: Dict[str, int]) -> float:
        """Calculate entropy of mixing for multi-component system."""
        total_atoms = sum(composition.values())
        if total_atoms <= 1:
            return 0.0
        
        entropy = 0.0
        for count in composition.values():
            if count > 0:
                fraction = count / total_atoms
                entropy -= fraction * np.log(fraction)
        
        return self.k_b * total_atoms * entropy
    
    def magnetic_entropy(self, magnetic_moments: np.ndarray, 
                        magnetic_field: Tuple[float, float, float],
                        temperature: float) -> float:
        """Calculate magnetic entropy contribution."""
        if len(magnetic_moments) == 0:
            return 0.0
        
        # Simplified Ising-like model
        field_magnitude = np.linalg.norm(magnetic_field)
        if field_magnitude < 1e-10:
            # Zero field case - maximum disorder
            return self.k_b * len(magnetic_moments) * np.log(2)
        
        # With field - reduced entropy
        beta = 1.0 / (self.k_b * temperature)
        energy_scale = field_magnitude * np.mean(np.linalg.norm(magnetic_moments, axis=1))
        
        # Partition function for spin-1/2 in magnetic field
        z = 2 * np.cosh(beta * energy_scale)
        entropy = self.k_b * (np.log(z) - beta * energy_scale * np.tanh(beta * energy_scale))
        
        return entropy * len(magnetic_moments)
    
    def _calculate_pairwise_distances(self, positions: np.ndarray) -> np.ndarray:
        """Calculate pairwise distances between positions."""
        n_atoms = len(positions)
        distances = np.zeros((n_atoms, n_atoms))
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                dist = np.linalg.norm(positions[i] - positions[j])
                distances[i, j] = distances[j, i] = dist
        
        return distances

class EnergyCalculator:
    """Calculates energy contributions for the assembly process."""
    
    def __init__(self):
        self.force_field_params = self._initialize_force_field()
    
    def _initialize_force_field(self) -> Dict[str, Dict]:
        """Initialize force field parameters for different interactions."""
        return {
            'lennard_jones': {
                'C-C': {'epsilon': 0.07, 'sigma': 3.4},
                'O-O': {'epsilon': 0.15, 'sigma': 3.12},
                'C-O': {'epsilon': 0.10, 'sigma': 3.26},
                'default': {'epsilon': 0.05, 'sigma': 3.0}
            },
            'coulomb': {
                'screening_length': 10.0,  # Angstroms
                'dielectric_constant': 1.0
            },
            'magnetic': {
                'exchange_coupling': 1.0,  # meV
                'anisotropy': 0.1  # meV
            }
        }
    
    def total_energy(self, positions: np.ndarray, 
                    elements: List[str],
                    charges: np.ndarray,
                    magnetic_moments: np.ndarray,
                    environment: EnvironmentalParameters) -> float:
        """Calculate total energy of the system."""
        energy = 0.0
        
        # Van der Waals interactions
        energy += self.van_der_waals_energy(positions, elements)
        
        # Coulomb interactions
        if np.any(charges != 0):
            energy += self.coulomb_energy(positions, charges, environment)
        
        # Magnetic interactions
        if len(magnetic_moments) > 0:
            energy += self.magnetic_energy(positions, magnetic_moments, environment)
        
        # External field interactions
        energy += self.external_field_energy(positions, charges, magnetic_moments, environment)
        
        return energy
    
    def van_der_waals_energy(self, positions: np.ndarray, elements: List[str]) -> float:
        """Calculate van der Waals energy using Lennard-Jones potential."""
        energy = 0.0
        n_atoms = len(positions)
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                r = np.linalg.norm(positions[i] - positions[j])
                if r < 1e-6:  # Avoid division by zero
                    continue
                
                # Get LJ parameters
                pair_key = f"{elements[i]}-{elements[j]}"
                if pair_key not in self.force_field_params['lennard_jones']:
                    pair_key = f"{elements[j]}-{elements[i]}"
                
                if pair_key in self.force_field_params['lennard_jones']:
                    params = self.force_field_params['lennard_jones'][pair_key]
                else:
                    params = self.force_field_params['lennard_jones']['default']
                
                epsilon = params['epsilon']
                sigma = params['sigma']
                
                # Lennard-Jones potential: 4*epsilon*[(sigma/r)^12 - (sigma/r)^6]
                r_ratio = sigma / r
                energy += 4 * epsilon * (r_ratio**12 - r_ratio**6)
        
        return energy
    
    def coulomb_energy(self, positions: np.ndarray, charges: np.ndarray, 
                      environment: EnvironmentalParameters) -> float:
        """Calculate Coulomb interaction energy."""
        energy = 0.0
        n_atoms = len(positions)
        
        # Constants
        ke = 14.3997  # eV·Å / e²
        dielectric = self.force_field_params['coulomb']['dielectric_constant']
        screening = self.force_field_params['coulomb']['screening_length']
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                r = np.linalg.norm(positions[i] - positions[j])
                if r < 1e-6:
                    continue
                
                # Screened Coulomb potential
                coulomb_energy = (ke * charges[i] * charges[j] / (dielectric * r)) * np.exp(-r / screening)
                energy += coulomb_energy
        
        return energy
    
    def magnetic_energy(self, positions: np.ndarray, magnetic_moments: np.ndarray,
                       environment: EnvironmentalParameters) -> float:
        """Calculate magnetic interaction energy."""
        energy = 0.0
        n_atoms = len(positions)
        
        if n_atoms < 2 or len(magnetic_moments) == 0:
            return energy
        
        exchange_coupling = self.force_field_params['magnetic']['exchange_coupling']
        
        for i in range(n_atoms):
            for j in range(i + 1, n_atoms):
                r = np.linalg.norm(positions[i] - positions[j])
                if r < 1e-6:
                    continue
                
                # Exchange interaction (simplified Heisenberg model)
                # E = -J * S_i · S_j * exp(-r/r_0)
                dot_product = np.dot(magnetic_moments[i], magnetic_moments[j])
                exchange_energy = -exchange_coupling * dot_product * np.exp(-r / 5.0)
                energy += exchange_energy
        
        return energy
    
    def external_field_energy(self, positions: np.ndarray, charges: np.ndarray,
                             magnetic_moments: np.ndarray, 
                             environment: EnvironmentalParameters) -> float:
        """Calculate energy due to external fields."""
        energy = 0.0
        
        # Electric field interaction
        E_field = np.array(environment.electric_field)
        if np.linalg.norm(E_field) > 1e-10:
            for i, charge in enumerate(charges):
                # E = -q · E · r (assuming linear potential)
                energy += -charge * np.dot(E_field, positions[i])
        
        # Magnetic field interaction (Zeeman effect)
        B_field = np.array(environment.magnetic_field)
        if np.linalg.norm(B_field) > 1e-10 and len(magnetic_moments) > 0:
            mu_b = 5.788e-5  # Bohr magneton in eV/T
            for moment in magnetic_moments:
                # E = -μ · B
                energy += -mu_b * np.dot(moment, B_field)
        
        return energy

class MonteCarloSampler:
    """Monte Carlo sampler for exploring assembly pathways."""
    
    def __init__(self, energy_calculator: EnergyCalculator, 
                 entropy_calculator: EntropyCalculator):
        self.energy_calc = energy_calculator
        self.entropy_calc = entropy_calculator
        self.move_history = []
    
    def metropolis_hastings_step(self, current_state: AssemblyState,
                                elements: List[str],
                                charges: np.ndarray,
                                magnetic_moments: np.ndarray,
                                environment: EnvironmentalParameters,
                                step_size: float = 0.1) -> AssemblyState:
        """Perform one Metropolis-Hastings step."""
        # Propose new configuration
        new_positions = current_state.configuration.copy()
        
        # Random displacement of a random atom
        atom_idx = np.random.randint(len(new_positions))
        displacement = np.random.normal(0, step_size, 3)
        new_positions[atom_idx] += displacement
        
        # Calculate energies
        old_energy = self.energy_calc.total_energy(
            current_state.configuration, elements, charges, magnetic_moments, environment
        )
        new_energy = self.energy_calc.total_energy(
            new_positions, elements, charges, magnetic_moments, environment
        )
        
        # Calculate entropies (simplified - only configurational for efficiency)
        old_entropy = self.entropy_calc.configurational_entropy(
            current_state.configuration, (10, 10, 10)
        )
        new_entropy = self.entropy_calc.configurational_entropy(
            new_positions, (10, 10, 10)
        )
        
        # Free energies
        T = environment.temperature
        old_free_energy = old_energy - T * old_entropy
        new_free_energy = new_energy - T * new_entropy
        
        # Metropolis criterion
        delta_f = new_free_energy - old_free_energy
        accept_prob = min(1.0, np.exp(-delta_f / (8.617e-5 * T)))
        
        if np.random.rand() < accept_prob:
            # Accept move
            new_state = AssemblyState(
                configuration=new_positions,
                energy=new_energy,
                entropy=new_entropy,
                free_energy=new_free_energy,
                stability_metrics=self._calculate_stability_metrics(new_positions),
                time_step=current_state.time_step + 1
            )
            self.move_history.append(('accept', delta_f, accept_prob))
            return new_state
        else:
            # Reject move - return current state
            current_state.time_step += 1
            self.move_history.append(('reject', delta_f, accept_prob))
            return current_state
    
    def _calculate_stability_metrics(self, positions: np.ndarray) -> Dict[str, float]:
        """Calculate various stability metrics for the configuration."""
        metrics = {}
        
        # Radial distribution function peak sharpness
        if len(positions) > 1:
            distances = []
            n_atoms = len(positions)
            for i in range(n_atoms):
                for j in range(i + 1, n_atoms):
                    distances.append(np.linalg.norm(positions[i] - positions[j]))
            
            if distances:
                distances = np.array(distances)
                hist, bins = np.histogram(distances, bins=20, density=True)
                
                # Peak sharpness (higher = more ordered)
                metrics['rdf_sharpness'] = np.max(hist) / np.mean(hist) if np.mean(hist) > 0 else 0
                
                # Coordination uniformity
                coord_numbers = []
                cutoff = np.mean(distances) + np.std(distances)
                for i in range(n_atoms):
                    coord_num = 0
                    for j in range(n_atoms):
                        if i != j:
                            dist = np.linalg.norm(positions[i] - positions[j])
                            if dist < cutoff:
                                coord_num += 1
                    coord_numbers.append(coord_num)
                
                metrics['coordination_uniformity'] = 1.0 / (1.0 + np.std(coord_numbers))
        
        return metrics
    
    def parallel_sampling(self, initial_states: List[AssemblyState],
                         elements: List[str],
                         charges: np.ndarray,
                         magnetic_moments: np.ndarray,
                         environment: EnvironmentalParameters,
                         n_steps: int = 1000,
                         n_processes: Optional[int] = None) -> List[List[AssemblyState]]:
        """Run parallel Monte Carlo sampling from multiple initial states."""
        if n_processes is None:
            n_processes = min(mp.cpu_count(), len(initial_states))
        
        def sample_trajectory(initial_state):
            trajectory = [initial_state]
            current_state = initial_state
            
            for _ in range(n_steps):
                current_state = self.metropolis_hastings_step(
                    current_state, elements, charges, magnetic_moments, environment
                )
                trajectory.append(current_state)
            
            return trajectory
        
        with ProcessPoolExecutor(max_workers=n_processes) as executor:
            trajectories = list(executor.map(sample_trajectory, initial_states))
        
        return trajectories

class EntropicAssemblyOptimizer:
    """
    Main EAO class that orchestrates the entropic assembly optimization.
    
    This optimizer uses entropy-based stability principles to find the most
    stable and accessible assembly pathways for hyper-materials.
    """
    
    def __init__(self):
        self.energy_calc = EnergyCalculator()
        self.entropy_calc = EntropyCalculator()
        self.mc_sampler = MonteCarloSampler(self.energy_calc, self.entropy_calc)
        self.optimization_history = []
        
    def optimize_assembly(self, material_structure,
                         environment: EnvironmentalParameters,
                         n_initial_configs: int = 10,
                         n_mc_steps: int = 10000,
                         convergence_threshold: float = 1e-6) -> AssemblyPathway:
        """
        Optimize the assembly pathway for a given material structure.
        
        Args:
            material_structure: MaterialStructure from MQB compiler
            environment: Environmental conditions for assembly
            n_initial_configs: Number of initial configurations to try
            n_mc_steps: Number of Monte Carlo steps per trajectory
            convergence_threshold: Convergence criterion for optimization
            
        Returns:
            AssemblyPathway with optimized assembly route
        """
        logger.info(f"Starting assembly optimization with {n_initial_configs} initial configs")
        
        # Extract data from material structure
        positions = np.array([atom.position for atom in material_structure.atoms])
        elements = [atom.element_symbol for atom in material_structure.atoms]
        charges = np.array([atom.charge for atom in material_structure.atoms])
        magnetic_moments = np.array([atom.magnetic_moment for atom in material_structure.atoms])
        
        # Generate initial configurations
        initial_states = self._generate_initial_configurations(
            positions, elements, charges, magnetic_moments, environment, n_initial_configs
        )
        
        # Run parallel Monte Carlo sampling
        logger.info("Running Monte Carlo sampling...")
        trajectories = self.mc_sampler.parallel_sampling(
            initial_states, elements, charges, magnetic_moments, environment, n_mc_steps
        )
        
        # Analyze trajectories and find optimal pathway
        logger.info("Analyzing trajectories...")
        optimal_pathway = self._analyze_trajectories(trajectories, environment)
        
        # Validate the pathway
        pathway_valid = self._validate_pathway(optimal_pathway, environment)
        logger.info(f"Pathway validation: {'PASSED' if pathway_valid else 'FAILED'}")
        
        return optimal_pathway
    
    def _generate_initial_configurations(self, positions: np.ndarray,
                                       elements: List[str],
                                       charges: np.ndarray,
                                       magnetic_moments: np.ndarray,
                                       environment: EnvironmentalParameters,
                                       n_configs: int) -> List[AssemblyState]:
        """Generate diverse initial configurations for optimization."""
        initial_states = []
        
        for i in range(n_configs):
            # Create variations of the initial structure
            if i == 0:
                # First config is the original structure
                init_positions = positions.copy()
            else:
                # Add random perturbations
                perturbation_scale = 0.5 * (i / n_configs)  # Increasing perturbation
                init_positions = positions + np.random.normal(0, perturbation_scale, positions.shape)
            
            # Calculate initial properties
            energy = self.energy_calc.total_energy(
                init_positions, elements, charges, magnetic_moments, environment
            )
            
            # Calculate entropy contributions
            config_entropy = self.entropy_calc.configurational_entropy(init_positions, (10, 10, 10))
            vib_entropy = self.entropy_calc.vibrational_entropy(
                init_positions, np.ones(len(elements)), environment.temperature
            )
            mag_entropy = self.entropy_calc.magnetic_entropy(
                magnetic_moments, environment.magnetic_field, environment.temperature
            )
            
            total_entropy = config_entropy + vib_entropy + mag_entropy
            free_energy = energy - environment.temperature * total_entropy
            
            # Create initial state
            initial_state = AssemblyState(
                configuration=init_positions,
                energy=energy,
                entropy=total_entropy,
                free_energy=free_energy,
                stability_metrics=self.mc_sampler._calculate_stability_metrics(init_positions),
                time_step=0
            )
            
            initial_states.append(initial_state)
        
        return initial_states
    
    def _analyze_trajectories(self, trajectories: List[List[AssemblyState]], 
                            environment: EnvironmentalParameters) -> AssemblyPathway:
        """Analyze Monte Carlo trajectories to find optimal assembly pathway."""
        best_states = []
        all_free_energies = []
        
        # Find the best state from each trajectory
        for trajectory in trajectories:
            if trajectory:
                best_state = min(trajectory, key=lambda state: state.free_energy)
                best_states.append(best_state)
                all_free_energies.extend([state.free_energy for state in trajectory])
        
        if not best_states:
            raise ValueError("No valid trajectories found")
        
        # Find the globally optimal state
        global_best = min(best_states, key=lambda state: state.free_energy)
        
        # Construct assembly pathway (simplified - using best trajectory)
        best_trajectory_idx = best_states.index(global_best)
        best_trajectory = trajectories[best_trajectory_idx]
        
        # Calculate transition barriers (simplified)
        transition_barriers = []
        for i in range(1, len(best_trajectory)):
            barrier = max(0, best_trajectory[i].free_energy - best_trajectory[i-1].free_energy)
            transition_barriers.append(barrier)
        
        # Calculate overall stability
        final_free_energy = global_best.free_energy
        initial_free_energy = best_trajectory[0].free_energy
        overall_stability = initial_free_energy - final_free_energy
        
        # Calculate formation probability (Boltzmann factor)
        kT = 8.617e-5 * environment.temperature  # eV
        formation_probability = np.exp(-max(transition_barriers) / kT) if transition_barriers else 1.0
        
        # Calculate kinetic accessibility (based on average barrier height)
        avg_barrier = np.mean(transition_barriers) if transition_barriers else 0.0
        kinetic_accessibility = np.exp(-avg_barrier / kT)
        
        pathway = AssemblyPathway(
            states=best_trajectory,
            transition_barriers=transition_barriers,
            overall_stability=overall_stability,
            formation_probability=formation_probability,
            kinetic_accessibility=kinetic_accessibility
        )
        
        logger.info(f"Optimal pathway found with {len(best_trajectory)} states")
        logger.info(f"Overall stability: {overall_stability:.3f} eV")
        logger.info(f"Formation probability: {formation_probability:.3f}")
        
        return pathway
    
    def _validate_pathway(self, pathway: AssemblyPathway, 
                         environment: EnvironmentalParameters) -> bool:
        """Validate the assembly pathway for physical consistency."""
        if not pathway.states:
            return False
        
        # Check energy conservation (allowing for thermal fluctuations)
        kT = 8.617e-5 * environment.temperature
        max_energy_jump = 5 * kT  # Allow jumps up to 5kT
        
        for i in range(1, len(pathway.states)):
            energy_diff = pathway.states[i].energy - pathway.states[i-1].energy
            if energy_diff > max_energy_jump:
                logger.warning(f"Large energy jump detected: {energy_diff:.3f} eV")
                return False
        
        # Check stability metrics
        final_state = pathway.states[-1]
        if final_state.stability_metrics.get('coordination_uniformity', 0) < 0.3:
            logger.warning("Low coordination uniformity in final state")
            return False
        
        # Check formation probability
        if pathway.formation_probability < 1e-10:
            logger.warning("Formation probability too low")
            return False
        
        return True
    
    def predict_bulk_properties(self, pathway: AssemblyPathway, 
                              environment: EnvironmentalParameters) -> Dict[str, float]:
        """Predict bulk material properties from assembly pathway."""
        final_state = pathway.states[-1]
        
        properties = {}
        
        # Mechanical properties (simplified estimates)
        avg_coordination = final_state.stability_metrics.get('coordination_uniformity', 0.5)
        properties['bulk_modulus'] = 100 * avg_coordination  # GPa, rough estimate
        properties['shear_modulus'] = 50 * avg_coordination   # GPa, rough estimate
        
        # Thermal properties
        properties['melting_point'] = 300 + final_state.stability_metrics.get('rdf_sharpness', 1) * 500  # K
        properties['thermal_conductivity'] = 10 * avg_coordination  # W/m·K
        
        # Electrical properties (simplified)
        if any('Qe' in str(state.configuration) for state in pathway.states[-10:]):
            properties['electrical_resistivity'] = 1e-6  # Very low for quantum coherent materials
        else:
            properties['electrical_resistivity'] = 1e-3  # Ω·m
        
        # Formation energy per atom
        properties['formation_energy_per_atom'] = final_state.free_energy / len(final_state.configuration)
        
        # Stability under conditions
        properties['thermodynamic_stability'] = pathway.overall_stability
        properties['kinetic_stability'] = pathway.kinetic_accessibility
        
        logger.info("Predicted bulk properties:")
        for prop, value in properties.items():
            logger.info(f"  {prop}: {value:.3e}")
        
        return properties
    
    def optimize_synthesis_conditions(self, pathway: AssemblyPathway,
                                    target_properties: Dict[str, float],
                                    condition_ranges: Dict[str, Tuple[float, float]]) -> EnvironmentalParameters:
        """Optimize synthesis conditions for desired properties."""
        logger.info("Optimizing synthesis conditions...")
        
        def objective_function(params):
            """Objective function for condition optimization."""
            # Unpack parameters
            temp, pressure = params[:2]
            
            # Create environment with new conditions
            test_env = EnvironmentalParameters(
                temperature=temp,
                pressure=pressure,
                magnetic_field=(0, 0, 0),  # Keep simple for now
                electric_field=(0, 0, 0)
            )
            
            # Predict properties under these conditions
            predicted_props = self.predict_bulk_properties(pathway, test_env)
            
            # Calculate objective (minimize difference from targets)
            objective = 0.0
            for prop_name, target_value in target_properties.items():
                if prop_name in predicted_props:
                    diff = (predicted_props[prop_name] - target_value) ** 2
                    objective += diff / (target_value ** 2 + 1e-10)  # Normalized difference
            
            return objective
        
        # Set up optimization bounds
        bounds = [
            condition_ranges.get('temperature', (200, 1000)),
            condition_ranges.get('pressure', (0.1, 100))
        ]
        
        # Initial guess
        initial_params = [300, 1.0]  # Room temperature, atmospheric pressure
        
        # Optimize using differential evolution (global optimizer)
        result = differential_evolution(
            objective_function, 
            bounds, 
            seed=42,
            maxiter=100
        )
        
        if result.success:
            optimal_temp, optimal_pressure = result.x
            
            optimized_env = EnvironmentalParameters(
                temperature=optimal_temp,
                pressure=optimal_pressure,
                magnetic_field=(0, 0, 0),
                electric_field=(0, 0, 0)
            )
            
            logger.info(f"Optimal conditions found:")
            logger.info(f"  Temperature: {optimal_temp:.1f} K")
            logger.info(f"  Pressure: {optimal_pressure:.2f} atm")
            
            return optimized_env
        else:
            logger.warning("Condition optimization failed, returning defaults")
            return EnvironmentalParameters()
    
    def generate_synthesis_protocol(self, pathway: AssemblyPathway,
                                  optimal_conditions: EnvironmentalParameters) -> Dict[str, Any]:
        """Generate a detailed synthesis protocol."""
        protocol = {
            'title': 'HMAI Hyper-Material Synthesis Protocol',
            'conditions': {
                'temperature': f"{optimal_conditions.temperature:.1f} K",
                'pressure': f"{optimal_conditions.pressure:.2f} atm",
                'atmosphere': optimal_conditions.atmosphere_composition
            },
            'steps': [],
            'timeline': f"{len(pathway.states)} steps",
            'expected_yield': f"{pathway.formation_probability * 100:.1f}%",
            'critical_parameters': {
                'max_transition_barrier': f"{max(pathway.transition_barriers):.3f} eV" if pathway.transition_barriers else "N/A",
                'stability_score': f"{pathway.overall_stability:.3f}"
            }
        }
        
        # Generate step-by-step instructions
        for i, state in enumerate(pathway.states[::len(pathway.states)//5]):  # Sample 5 key steps
            step = {
                'step_number': i + 1,
                'description': f"Assembly stage {i + 1}",
                'energy': f"{state.energy:.3f} eV",
                'stability_metrics': state.stability_metrics,
                'monitoring_parameters': [
                    "Temperature",
                    "Pressure", 
                    "Formation rate",
                    "Structural order"
                ]
            }
            protocol['steps'].append(step)
        
        return protocol
