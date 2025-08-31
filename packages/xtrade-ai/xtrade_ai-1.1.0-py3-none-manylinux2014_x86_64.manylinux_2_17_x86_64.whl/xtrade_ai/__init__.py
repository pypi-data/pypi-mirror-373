"""
XTrade-AI Framework

A comprehensive reinforcement learning framework for algorithmic trading
with enhanced error handling, memory management, and thread safety.
"""

__version__ = "1.0.0"
__author__ = "Anas Amu"
__email__ = "anasamu7@gmail.com"
__github__ = "https://github.com/anasamu/xtrade-ai-framework"

import sys
import warnings
from typing import Any, Dict, List, Optional, Union

# Suppress warnings during import
warnings.filterwarnings("ignore", category=UserWarning, module=".*")


def _safe_import(module_name: str, class_name: str = None, fallback=None):
    """
    Safely import modules with comprehensive error handling.

    Args:
        module_name: Name of the module to import
        class_name: Name of the class to import (optional)
        fallback: Fallback value if import fails

    Returns:
        Imported module/class or fallback value
    """
    try:
        if class_name:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        print(
            f"Warning: Failed to import {module_name}{'.' + class_name if class_name else ''}: {e}"
        )
        return fallback
    except Exception as e:
        print(
            f"Error: Unexpected error importing {module_name}{'.' + class_name if class_name else ''}: {e}"
        )
        return fallback


# Import main framework class with enhanced error handling
XTradeAIFramework = _safe_import("xtrade_ai.xtrade_ai_framework", "XTradeAIFramework")

# Import configuration with validation
XTradeAIConfig = _safe_import("xtrade_ai.config", "XTradeAIConfig")

# Import data structures with comprehensive error handling
try:
    from .data_structures import (
        ActionType,
        CloseOrderDecision,
        MarketState,
        Order,
        Portfolio,
        Position,
        RiskAssessment,
        Trade,
        TradingDecision,
    )
except ImportError as e:
    print(f"Warning: Failed to import data structures: {e}")
    TradingDecision = None
    ActionType = None
    RiskAssessment = None
    MarketState = None
    Position = None
    Order = None
    Trade = None
    Portfolio = None
    CloseOrderDecision = None

# Import utility functions with fallback
try:
    from .utils.dependency_container import DependencyContainer, get_container
    from .utils.error_handler import (
        ErrorCategory,
        ErrorHandler,
        get_error_handler,
        handle_error,
    )
    from .utils.import_manager import get_import_manager, import_class, safe_import
    from .utils.logger import get_logger
    from .utils.memory_manager import auto_cleanup, force_cleanup, get_memory_manager
    from .utils.thread_manager import get_thread_manager, submit_task, wait_for_all
except ImportError as e:
    print(f"Warning: Failed to import utility modules: {e}")
    get_logger = None
    get_memory_manager = None
    auto_cleanup = None
    force_cleanup = None
    get_thread_manager = None
    submit_task = None
    wait_for_all = None
    safe_import = None
    import_class = None
    get_import_manager = None
    handle_error = None
    ErrorHandler = None
    get_error_handler = None
    ErrorCategory = None
    DependencyContainer = None
    get_container = None

# Import all modules with comprehensive error handling xtrade_ai
try:
    from .modules.action_selector import ActionSelector
    from .modules.baseline3_integration import Baseline3Integration
    from .modules.calibration import EnsembleCalibrator, TemperatureScaler
    from .modules.close_order_decision import CloseOrderDecisionMaker
    from .modules.integrated_analysis import IntegratedAnalysis
    from .modules.market_simulation import MarketSimulation
    from .modules.meta_learning import MetaLearningModule
    from .modules.monitoring import MonitoringModule
    from .modules.optimization import OptimizationModule
    from .modules.policy_validator import PolicyValidator
    from .modules.reward_shaping import RewardShaper
    from .modules.risk_management import RiskManagementModule
    from .modules.technical_analysis import TechnicalAnalysisModule
    from .modules.technical_indicator import AdaptiveIndicatorModule
    from .modules.xgboost_module import XGBoostModule
except ImportError as e:
    print(f"Warning: Failed to import trading modules: {e}")
    Baseline3Integration = None
    CloseOrderDecisionMaker = None
    RiskManagementModule = None
    AdaptiveIndicatorModule = None
    TechnicalAnalysisModule = None
    XGBoostModule = None
    RewardShaper = None
    ActionSelector = None
    MonitoringModule = None
    TemperatureScaler = None
    EnsembleCalibrator = None
    MarketSimulation = None
    IntegratedAnalysis = None
    MetaLearningModule = None
    OptimizationModule = None
    PolicyValidator = None

# Import additional components
try:
    from .attention_mechanism import TransformerBlock
    from .base_environment import BaseEnvironment
    from .data_preprocessor import DataPreprocessor
    from .policy_networks import AttentionPolicyNetwork
except ImportError as e:
    print(f"Warning: Failed to import additional components: {e}")
    BaseEnvironment = None
    DataPreprocessor = None
    AttentionPolicyNetwork = None
    TransformerBlock = None

# Comprehensive __all__ list for better package exposure
__all__ = [
    # Main framework
    "XTradeAIFramework",
    "XTradeAIConfig",
    # Data structures
    "TradingDecision",
    "ActionType",
    "RiskAssessment",
    "MarketState",
    "Position",
    "Order",
    "Trade",
    "Portfolio",
    "CloseOrderDecision",
    # Utilities
    "get_logger",
    "get_memory_manager",
    "auto_cleanup",
    "force_cleanup",
    "get_thread_manager",
    "submit_task",
    "wait_for_all",
    "safe_import",
    "import_class",
    "get_import_manager",
    "handle_error",
    "ErrorHandler",
    "get_error_handler",
    "ErrorCategory",
    "DependencyContainer",
    "get_container",
    # Trading modules
    "Baseline3Integration",
    "CloseOrderDecisionMaker",
    "RiskManagementModule",
    "AdaptiveIndicatorModule",
    "TechnicalAnalysisModule",
    "XGBoostModule",
    "RewardShaper",
    "ActionSelector",
    "MonitoringModule",
    "TemperatureScaler",
    "EnsembleCalibrator",
    "MarketSimulation",
    "IntegratedAnalysis",
    "MetaLearningModule",
    "OptimizationModule",
    "PolicyValidator",
    # Additional components
    "BaseEnvironment",
    "DataPreprocessor",
    "AttentionPolicyNetwork",
    "TransformerBlock",
]


# Version info for compatibility
def get_version() -> str:
    """Get the current version of XTrade-AI Framework."""
    return __version__


def get_info() -> Dict[str, str]:
    """Get framework information."""
    return {
        "name": "XTrade-AI Framework",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "github": __github__,
        "description": "A comprehensive reinforcement learning framework for algorithmic trading",
    }


def get_dependencies_status() -> Dict[str, bool]:
    """
    Check the status of all dependencies.

    Returns:
        Dictionary mapping dependency names to their availability status
    """
    dependencies = {
        "torch": _safe_import("torch") is not None,
        "stable_baselines3": _safe_import("stable_baselines3") is not None,
        "gymnasium": _safe_import("gymnasium") is not None,
        "pandas": _safe_import("pandas") is not None,
        "numpy": _safe_import("numpy") is not None,
        "sklearn": _safe_import("sklearn") is not None,
        "xgboost": _safe_import("xgboost") is not None,
        "pandas_ta": _safe_import("pandas_ta") is not None,
        "matplotlib": _safe_import("matplotlib") is not None,
    }
    return dependencies


def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for the framework.

    Returns:
        Dictionary with health check results
    """
    health_status = {
        "framework_version": __version__,
        "python_version": sys.version,
        "critical_components": {},
        "dependencies": get_dependencies_status(),
        "overall_status": "healthy",
    }

    # Check critical components
    critical_components = [
        ("XTradeAIFramework", XTradeAIFramework),
        ("XTradeAIConfig", XTradeAIConfig),
        ("get_logger", get_logger),
        ("BaseEnvironment", BaseEnvironment),
        ("DataPreprocessor", DataPreprocessor),
    ]

    missing_components = []
    for name, component in critical_components:
        if component is None:
            missing_components.append(name)
            health_status["critical_components"][name] = False
        else:
            health_status["critical_components"][name] = True

    # Check dependencies
    missing_deps = [
        dep for dep, available in health_status["dependencies"].items() if not available
    ]

    if missing_components:
        health_status["overall_status"] = "critical_components_missing"
        print(f"❌ Critical components missing: {missing_components}")
    elif missing_deps:
        health_status["overall_status"] = "dependencies_missing"
        print(f"⚠️  Dependencies missing: {missing_deps}")
    else:
        print("✅ XTrade-AI Framework is healthy and ready to use!")

    return health_status


def quick_start_example() -> str:
    """
    Provide a quick start example for users.

    Returns:
        String with quick start example
    """
    return """
Quick Start Example:

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

# Create configuration
config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"
config.trading.initial_balance = 10000.0

# Initialize framework
framework = XTradeAIFramework(config)

# Train the framework
# framework.train(training_data, epochs=100)

# Make predictions
# prediction = framework.predict(market_data)
# print(f"Action: {prediction['action']}, Confidence: {prediction['confidence']}")
```

For more examples, see the documentation at: https://xtrade-ai-framework.readthedocs.io/en/latest/
"""


# API imports
try:
    from .api import start_api_server
except ImportError:
    start_api_server = None

# Auto health check on import (only in development mode)
if __name__ != "__main__":
    # Only run health check if explicitly requested or in development
    import os

    if os.getenv("XTRADE_AI_HEALTH_CHECK", "false").lower() == "true":
        health_check()
