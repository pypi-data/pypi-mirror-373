"""
Reservoir Computing Optimization Tools
Based on: Various optimization techniques for reservoir computing

Provides automated hyperparameter optimization and reservoir design tools.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable
from .echo_state_network import EchoStateNetwork
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import mean_squared_error
import warnings


class ReservoirOptimizer:
    """
    Automated hyperparameter optimization for reservoir computing
    
    Implements grid search, random search, and evolutionary optimization
    for finding optimal reservoir parameters.
    """
    
    def __init__(
        self,
        optimization_method: str = 'grid_search',
        n_trials: int = 50,
        cv_folds: int = 3,
        random_seed: Optional[int] = None
    ):
        """
        Initialize Reservoir Optimizer
        
        Args:
            optimization_method: 'grid_search', 'random_search', or 'evolutionary'
            n_trials: Number of optimization trials
            cv_folds: Number of cross-validation folds
            random_seed: Random seed for reproducibility
        """
        
        self.optimization_method = optimization_method
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        
        if random_seed is not None:
            np.random.seed(random_seed)
            
        self.best_params = None
        self.best_score = float('inf')
        self.optimization_history = []
        
        print(f"✓ Reservoir Optimizer initialized:")
        print(f"   Method: {optimization_method}")
        print(f"   Trials: {n_trials}")
        print(f"   CV Folds: {cv_folds}")
        
    def optimize(self, 
                 training_data: Tuple[np.ndarray, np.ndarray],
                 param_space: Dict[str, List],
                 scoring_metric: str = 'mse',
                 verbose: bool = True) -> Dict[str, Any]:
        """
        Optimize reservoir parameters
        
        Args:
            training_data: (inputs, targets) tuple
            param_space: Dictionary of parameter ranges
            scoring_metric: Scoring metric ('mse', 'mae', 'r2')
            verbose: Whether to print progress
            
        Returns:
            Optimization results
        """
        
        inputs, targets = training_data
        
        if verbose:
            print(f"🎯 Optimizing reservoir parameters...")
            print(f"   Parameter space: {list(param_space.keys())}")
            print(f"   Data shape: {inputs.shape} -> {targets.shape}")
        
        if self.optimization_method == 'grid_search':
            return self._grid_search_optimize(inputs, targets, param_space, 
                                            scoring_metric, verbose)
        elif self.optimization_method == 'random_search':
            return self._random_search_optimize(inputs, targets, param_space,
                                              scoring_metric, verbose)
        elif self.optimization_method == 'evolutionary':
            return self._evolutionary_optimize(inputs, targets, param_space,
                                             scoring_metric, verbose)
        else:
            raise ValueError(f"Unknown optimization method: {self.optimization_method}")
            
    def _grid_search_optimize(self, inputs: np.ndarray, targets: np.ndarray,
                            param_space: Dict[str, List], scoring_metric: str,
                            verbose: bool) -> Dict[str, Any]:
        """Grid search optimization"""
        
        # Generate parameter grid
        param_grid = list(ParameterGrid(param_space))
        n_combinations = min(len(param_grid), self.n_trials)
        
        if verbose:
            print(f"   Grid search: {n_combinations} parameter combinations")
            
        best_score = float('inf')
        best_params = None
        
        for i, params in enumerate(param_grid[:n_combinations]):
            try:
                score = self._evaluate_parameters(inputs, targets, params, scoring_metric)
                self.optimization_history.append({'params': params, 'score': score})
                
                if score < best_score:
                    best_score = score
                    best_params = params
                    
                if verbose and (i + 1) % max(1, n_combinations // 10) == 0:
                    progress = (i + 1) / n_combinations * 100
                    print(f"   Progress: {progress:5.1f}% | Best {scoring_metric}: {best_score:.6f}")
                    
            except Exception as e:
                if verbose:
                    print(f"   Trial {i+1} failed: {str(e)}")
                continue
                
        self.best_params = best_params
        self.best_score = best_score
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'n_trials': len(self.optimization_history),
            'optimization_history': self.optimization_history
        }
        
    def _random_search_optimize(self, inputs: np.ndarray, targets: np.ndarray,
                              param_space: Dict[str, List], scoring_metric: str,
                              verbose: bool) -> Dict[str, Any]:
        """Random search optimization"""
        
        if verbose:
            print(f"   Random search: {self.n_trials} random trials")
            
        best_score = float('inf')
        best_params = None
        
        for i in range(self.n_trials):
            try:
                # Sample random parameters
                params = {}
                for param_name, param_values in param_space.items():
                    params[param_name] = np.random.choice(param_values)
                    
                score = self._evaluate_parameters(inputs, targets, params, scoring_metric)
                self.optimization_history.append({'params': params, 'score': score})
                
                if score < best_score:
                    best_score = score
                    best_params = params
                    
                if verbose and (i + 1) % max(1, self.n_trials // 10) == 0:
                    progress = (i + 1) / self.n_trials * 100
                    print(f"   Progress: {progress:5.1f}% | Best {scoring_metric}: {best_score:.6f}")
                    
            except Exception as e:
                if verbose:
                    print(f"   Trial {i+1} failed: {str(e)}")
                continue
                
        self.best_params = best_params
        self.best_score = best_score
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'n_trials': len(self.optimization_history),
            'optimization_history': self.optimization_history
        }
        
    def _evolutionary_optimize(self, inputs: np.ndarray, targets: np.ndarray,
                             param_space: Dict[str, List], scoring_metric: str,
                             verbose: bool) -> Dict[str, Any]:
        """Evolutionary optimization (simplified genetic algorithm)"""
        
        population_size = min(20, self.n_trials // 5)
        n_generations = self.n_trials // population_size
        
        if verbose:
            print(f"   Evolutionary search: {n_generations} generations, population {population_size}")
            
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = {}
            for param_name, param_values in param_space.items():
                individual[param_name] = np.random.choice(param_values)
            population.append(individual)
            
        best_score = float('inf')
        best_params = None
        
        for generation in range(n_generations):
            # Evaluate population
            scores = []
            for individual in population:
                try:
                    score = self._evaluate_parameters(inputs, targets, individual, scoring_metric)
                    scores.append(score)
                    self.optimization_history.append({'params': individual, 'score': score})
                    
                    if score < best_score:
                        best_score = score
                        best_params = individual.copy()
                        
                except Exception:
                    scores.append(float('inf'))
                    
            # Selection and reproduction
            if generation < n_generations - 1:
                population = self._evolve_population(population, scores, param_space)
                
            if verbose and (generation + 1) % max(1, n_generations // 5) == 0:
                progress = (generation + 1) / n_generations * 100
                print(f"   Generation {generation+1}/{n_generations} | Best {scoring_metric}: {best_score:.6f}")
                
        self.best_params = best_params
        self.best_score = best_score
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'n_trials': len(self.optimization_history),
            'optimization_history': self.optimization_history
        }
        
    def _evolve_population(self, population: List[Dict], scores: List[float],
                          param_space: Dict[str, List]) -> List[Dict]:
        """Evolve population for next generation"""
        
        # Select parents (tournament selection)
        new_population = []
        
        # Keep best individuals (elitism)
        sorted_indices = np.argsort(scores)
        elite_size = len(population) // 4
        for i in range(elite_size):
            new_population.append(population[sorted_indices[i]].copy())
            
        # Generate offspring
        while len(new_population) < len(population):
            # Tournament selection
            parent1 = self._tournament_select(population, scores)
            parent2 = self._tournament_select(population, scores)
            
            # Crossover
            child = self._crossover(parent1, parent2, param_space)
            
            # Mutation
            child = self._mutate(child, param_space)
            
            new_population.append(child)
            
        return new_population
        
    def _tournament_select(self, population: List[Dict], scores: List[float],
                          tournament_size: int = 3) -> Dict:
        """Tournament selection"""
        
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_scores = [scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmin(tournament_scores)]
        
        return population[winner_idx].copy()
        
    def _crossover(self, parent1: Dict, parent2: Dict, param_space: Dict[str, List]) -> Dict:
        """Uniform crossover"""
        
        child = {}
        for param_name in param_space.keys():
            if np.random.random() < 0.5:
                child[param_name] = parent1[param_name]
            else:
                child[param_name] = parent2[param_name]
                
        return child
        
    def _mutate(self, individual: Dict, param_space: Dict[str, List],
               mutation_rate: float = 0.1) -> Dict:
        """Random mutation"""
        
        mutated = individual.copy()
        
        for param_name, param_values in param_space.items():
            if np.random.random() < mutation_rate:
                mutated[param_name] = np.random.choice(param_values)
                
        return mutated
        
    def _evaluate_parameters(self, inputs: np.ndarray, targets: np.ndarray,
                           params: Dict, scoring_metric: str) -> float:
        """Evaluate parameter set using cross-validation"""
        
        # Create train/validation splits
        n_samples = len(inputs)
        fold_size = n_samples // self.cv_folds
        
        scores = []
        
        for fold in range(self.cv_folds):
            # Create fold splits
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < self.cv_folds - 1 else n_samples
            
            train_indices = list(range(0, val_start)) + list(range(val_end, n_samples))
            val_indices = list(range(val_start, val_end))
            
            if len(train_indices) == 0 or len(val_indices) == 0:
                continue
                
            train_inputs = inputs[train_indices]
            train_targets = targets[train_indices]
            val_inputs = inputs[val_indices]
            val_targets = targets[val_indices]
            
            # Train ESN with parameters
            esn = EchoStateNetwork(**params)
            
            # Handle potential training failures
            try:
                esn.train(train_inputs, train_targets, verbose=False)
                predictions = esn.predict(val_inputs)
                
                # Calculate score
                if scoring_metric == 'mse':
                    score = mean_squared_error(val_targets[100:], predictions)
                elif scoring_metric == 'mae':
                    score = np.mean(np.abs(val_targets[100:] - predictions))
                elif scoring_metric == 'r2':
                    ss_res = np.sum((val_targets[100:] - predictions) ** 2)
                    ss_tot = np.sum((val_targets[100:] - np.mean(val_targets[100:])) ** 2)
                    score = 1 - (ss_res / (ss_tot + 1e-8))  # Lower is better (negative R²)
                else:
                    raise ValueError(f"Unknown scoring metric: {scoring_metric}")
                    
                scores.append(score)
                
            except Exception:
                scores.append(float('inf'))  # Penalty for failed training
                
        return np.mean(scores) if scores else float('inf')
        
    def create_optimized_esn(self) -> EchoStateNetwork:
        """Create ESN with optimized parameters"""
        
        if self.best_params is None:
            raise ValueError("Must run optimization first!")
            
        return EchoStateNetwork(**self.best_params)
        
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization results"""
        
        if not self.optimization_history:
            return {"message": "No optimization performed yet"}
            
        scores = [entry['score'] for entry in self.optimization_history]
        
        return {
            'best_score': self.best_score,
            'best_params': self.best_params,
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'n_trials': len(self.optimization_history),
            'improvement': scores[0] - self.best_score if scores else 0
        }
        
    @staticmethod
    def get_default_param_space() -> Dict[str, List]:
        """Get default parameter space for optimization"""
        
        return {
            'n_reservoir': [100, 200, 500, 1000],
            'spectral_radius': [0.8, 0.9, 0.95, 0.99],
            'sparsity': [0.05, 0.1, 0.15, 0.2],
            'input_scaling': [0.5, 1.0, 1.5],
            'noise_level': [0.001, 0.01, 0.1],
            'leak_rate': [0.1, 0.3, 0.7, 1.0]
        }