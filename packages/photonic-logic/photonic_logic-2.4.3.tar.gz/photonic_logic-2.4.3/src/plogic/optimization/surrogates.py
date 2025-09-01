"""Enhanced surrogate models with ensemble and CV-based selection for plateau breaking."""
import numpy as np
from typing import Tuple, Optional, Union, Dict, Any
import warnings

# Handle optional imports gracefully
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
    from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import KFold
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available, using fallback surrogate")

from plogic.opt_utils.array_safety import ensure_1d, ensure_2d


class SklearnSurrogateWrapper:
    """Wrapper for sklearn models to ensure array outputs."""
    
    def __init__(self, model):
        """Initialize with sklearn model."""
        self.model = model
    
    def fit(self, X, y, **kwargs):
        """Fit the model."""
        return self.model.fit(X, y, **kwargs)
    
    def predict(self, X, return_std=False, **kwargs):
        """Predict with guaranteed array output.
        
        Args:
            X: Input features
            return_std: Whether to return standard deviation
            **kwargs: Extra kwargs (safely ignored)
            
        Returns:
            predictions or (predictions, std) if return_std=True
        """
        # Accept extra kwargs like 'verbose' safely
        yhat = np.asarray(self.model.predict(X))
        if yhat.ndim == 0:
            yhat = yhat.reshape(1,)
        else:
            yhat = yhat.ravel()
        
        if return_std:
            # If the underlying model has no std, return zeros with same shape
            std = np.zeros_like(yhat, dtype=float)
            return yhat, std
        return yhat


class SimpleSurrogate:
    """Fallback surrogate when sklearn is not available."""
    
    def __init__(self):
        self.X_train = None
        self.y_train = None
        self.y_mean = 0.0
        self.y_std = 1.0
    
    def fit(self, X, y):
        """Fit simple mean/std model."""
        self.X_train = ensure_2d(X)
        self.y_train = ensure_1d(y)
        self.y_mean = float(np.mean(self.y_train))
        self.y_std = float(np.std(self.y_train) + 1e-8)
    
    def predict(self, X, return_std=False):
        """Predict using simple heuristics."""
        X = ensure_2d(X)
        n_pred = X.shape[0]
        
        # Simple prediction: return mean with some uncertainty
        mu = np.full(n_pred, self.y_mean)
        
        if return_std:
            std = np.full(n_pred, self.y_std)
            return mu, std
        return mu


class GaussianProcessSurrogate:
    """Gaussian Process surrogate model with array safety."""
    
    def __init__(self, 
                 length_scale: float = 1.0,
                 nu: float = 2.5,
                 noise_level: float = 1e-5,
                 normalize_y: bool = True):
        """
        Initialize GP surrogate.
        
        Args:
            length_scale: Initial length scale for Matern kernel
            nu: Smoothness parameter for Matern kernel
            noise_level: Noise level for WhiteKernel
            normalize_y: Whether to normalize target values
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for GaussianProcessSurrogate")
        
        # Create kernel
        kernel = (ConstantKernel(1.0, (1e-3, 1e3)) * 
                 Matern(length_scale=length_scale, nu=nu) + 
                 WhiteKernel(noise_level=noise_level))
        
        self.gp = GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=normalize_y,
            alpha=1e-6,
            n_restarts_optimizer=5
        )
        
        self.scaler_X = StandardScaler()
        self.fitted = False
    
    def fit(self, X, y):
        """Fit GP to training data."""
        X = ensure_2d(X)
        y = ensure_1d(y)
        
        # Scale inputs
        X_scaled = self.scaler_X.fit_transform(X)
        
        # Fit GP
        self.gp.fit(X_scaled, y)
        self.fitted = True
    
    def predict(self, X, return_std=False):
        """Make predictions with GP."""
        if not self.fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        X = ensure_2d(X)
        X_scaled = self.scaler_X.transform(X)
        
        if return_std:
            mu, std = self.gp.predict(X_scaled, return_std=True)
            return ensure_1d(mu), ensure_1d(std)
        else:
            mu = self.gp.predict(X_scaled)
            return ensure_1d(mu)


class RandomForestSurrogate:
    """Random Forest surrogate model."""
    
    def __init__(self, n_estimators: int = 300, random_state: int = 42):
        """Initialize RF surrogate."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for RandomForestSurrogate")
        
        self.rf = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler_X = StandardScaler()
        self.fitted = False
    
    def fit(self, X, y):
        """Fit RF to training data."""
        X = ensure_2d(X)
        y = ensure_1d(y)
        
        # Scale inputs
        X_scaled = self.scaler_X.fit_transform(X)
        
        # Fit RF
        self.rf.fit(X_scaled, y)
        self.fitted = True
    
    def predict(self, X, return_std=False):
        """Make predictions with RF."""
        if not self.fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        X = ensure_2d(X)
        X_scaled = self.scaler_X.transform(X)
        
        mu = self.rf.predict(X_scaled)
        mu = ensure_1d(mu)
        
        if return_std:
            # Estimate uncertainty using tree variance
            predictions = np.array([tree.predict(X_scaled) for tree in self.rf.estimators_])
            std = np.std(predictions, axis=0)
            return mu, ensure_1d(std)
        else:
            return mu


class ExtraTreesSurrogate:
    """Extra Trees surrogate model."""
    
    def __init__(self, n_estimators: int = 300, random_state: int = 42):
        """Initialize Extra Trees surrogate."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for ExtraTreesSurrogate")
        
        self.et = ExtraTreesRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler_X = StandardScaler()
        self.fitted = False
    
    def fit(self, X, y):
        """Fit Extra Trees to training data."""
        X = ensure_2d(X)
        y = ensure_1d(y)
        
        # Scale inputs
        X_scaled = self.scaler_X.fit_transform(X)
        
        # Fit Extra Trees
        self.et.fit(X_scaled, y)
        self.fitted = True
    
    def predict(self, X, return_std=False):
        """Make predictions with Extra Trees."""
        if not self.fitted:
            raise RuntimeError("Model must be fitted before prediction")
        
        X = ensure_2d(X)
        X_scaled = self.scaler_X.transform(X)
        
        mu = self.et.predict(X_scaled)
        mu = ensure_1d(mu)
        
        if return_std:
            # Estimate uncertainty using tree variance
            predictions = np.array([tree.predict(X_scaled) for tree in self.et.estimators_])
            std = np.std(predictions, axis=0)
            return mu, ensure_1d(std)
        else:
            return mu


class EnsembleSurrogate:
    """
    Ensemble surrogate that combines multiple models with CV-based selection.
    
    This class automatically selects the best performing model based on
    cross-validation and can switch models during optimization.
    """
    
    def __init__(self, n_splits: int = 5, random_state: int = 42):
        """
        Initialize ensemble surrogate.
        
        Args:
            n_splits: Number of CV folds for model selection
            random_state: Random state for reproducibility
        """
        self.n_splits = n_splits
        self.random_state = random_state
        
        # Initialize candidate models
        self.models = {}
        if SKLEARN_AVAILABLE:
            self.models["gp"] = GaussianProcessSurrogate()
            self.models["rf"] = RandomForestSurrogate(random_state=random_state)
            self.models["et"] = ExtraTreesSurrogate(random_state=random_state)
        else:
            self.models["simple"] = SimpleSurrogate()
        
        self.best_model_name = None
        self.best_model = None
        self.cv_scores = {}
        self.fitted = False
    
    def fit(self, X, y):
        """
        Fit ensemble and select best model via cross-validation.
        
        Args:
            X: Training inputs
            y: Training targets
        """
        X = ensure_2d(X)
        y = ensure_1d(y)
        
        if len(self.models) == 1:
            # Only one model available, use it directly
            self.best_model_name = list(self.models.keys())[0]
            self.best_model = self.models[self.best_model_name]
            self.best_model.fit(X, y)
            self.fitted = True
            return
        
        # Cross-validation model selection
        n_samples = len(y)
        n_folds = min(self.n_splits, max(2, n_samples // 5))
        
        if n_folds < 2:
            # Not enough data for CV, use first available model
            self.best_model_name = list(self.models.keys())[0]
            self.best_model = self.models[self.best_model_name]
            self.best_model.fit(X, y)
            self.fitted = True
            return
        
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=self.random_state)
        
        best_score = float("inf")
        best_name = None
        
        for name, model in self.models.items():
            try:
                scores = []
                
                for train_idx, val_idx in kf.split(X):
                    X_train, X_val = X[train_idx], X[val_idx]
                    y_train, y_val = y[train_idx], y[val_idx]
                    
                    # Fit model on training fold
                    model_copy = self._copy_model(model)
                    model_copy.fit(X_train, y_train)
                    
                    # Predict on validation fold
                    y_pred = model_copy.predict(X_val)
                    
                    # Compute MAE (lower is better)
                    mae = mean_absolute_error(y_val, y_pred)
                    scores.append(mae)
                
                # Average CV score
                avg_score = float(np.mean(scores))
                self.cv_scores[name] = avg_score
                
                if avg_score < best_score:
                    best_score = avg_score
                    best_name = name
                    
            except Exception as e:
                warnings.warn(f"Model {name} failed during CV: {e}")
                self.cv_scores[name] = float("inf")
        
        # Select and fit best model
        if best_name is None:
            # Fallback to first model if all failed
            best_name = list(self.models.keys())[0]
        
        self.best_model_name = best_name
        self.best_model = self.models[best_name]
        self.best_model.fit(X, y)
        self.fitted = True
    
    def predict(self, X, return_std=False):
        """Make predictions with best model."""
        if not self.fitted:
            raise RuntimeError("Ensemble must be fitted before prediction")
        
        return self.best_model.predict(X, return_std=return_std)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about selected model and CV scores."""
        return {
            "best_model": self.best_model_name,
            "cv_scores": self.cv_scores.copy(),
            "available_models": list(self.models.keys())
        }
    
    def _copy_model(self, model):
        """Create a copy of a model for CV."""
        if isinstance(model, GaussianProcessSurrogate):
            return GaussianProcessSurrogate()
        elif isinstance(model, RandomForestSurrogate):
            return RandomForestSurrogate(random_state=self.random_state)
        elif isinstance(model, ExtraTreesSurrogate):
            return ExtraTreesSurrogate(random_state=self.random_state)
        elif isinstance(model, SimpleSurrogate):
            return SimpleSurrogate()
        else:
            # Fallback: try to create new instance
            return type(model)()


def create_surrogate(surrogate_type: str = "ensemble", **kwargs):
    """
    Factory function to create surrogate models.
    
    Args:
        surrogate_type: Type of surrogate ("gp", "rf", "et", "ensemble", "simple", "auto")
        **kwargs: Additional arguments for surrogate
        
    Returns:
        Surrogate model instance
    """
    if surrogate_type == "auto":
        surrogate_type = "ensemble" if SKLEARN_AVAILABLE else "simple"
    
    if surrogate_type == "gp":
        if not SKLEARN_AVAILABLE:
            warnings.warn("sklearn not available, falling back to simple surrogate")
            return SimpleSurrogate()
        return GaussianProcessSurrogate(**kwargs)
    elif surrogate_type == "rf":
        if not SKLEARN_AVAILABLE:
            warnings.warn("sklearn not available, falling back to simple surrogate")
            return SimpleSurrogate()
        return RandomForestSurrogate(**kwargs)
    elif surrogate_type == "et":
        if not SKLEARN_AVAILABLE:
            warnings.warn("sklearn not available, falling back to simple surrogate")
            return SimpleSurrogate()
        return ExtraTreesSurrogate(**kwargs)
    elif surrogate_type == "ensemble":
        return EnsembleSurrogate(**kwargs)
    elif surrogate_type == "simple":
        return SimpleSurrogate()
    else:
        raise ValueError(f"Unknown surrogate type: {surrogate_type}")
