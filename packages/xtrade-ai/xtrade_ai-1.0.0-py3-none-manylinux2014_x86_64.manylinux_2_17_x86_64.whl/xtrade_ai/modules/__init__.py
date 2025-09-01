# Modules package for XTrade-AI

# Import all available modules with error handling
try:
    from .meta_learning import MetaLearningModule
except ImportError:
    MetaLearningModule = None

try:
    from .baseline3_integration import Baseline3Integration
except ImportError:
    Baseline3Integration = None

try:
    from .close_order_decision import CloseOrderDecisionMaker
except ImportError:
    CloseOrderDecisionMaker = None

try:
    from .risk_management import RiskManagementModule
except ImportError:
    RiskManagementModule = None

try:
    from .technical_indicator import AdaptiveIndicatorModule
except ImportError:
    AdaptiveIndicatorModule = None

try:
    from .technical_analysis import TechnicalAnalysisModule
except ImportError:
    TechnicalAnalysisModule = None

try:
    from .xgboost_module import XGBoostModule
except ImportError:
    XGBoostModule = None

try:
    from .reward_shaping import RewardShaper
except ImportError:
    RewardShaper = None

try:
    from .action_selector import ActionSelector
except ImportError:
    ActionSelector = None

try:
    from .monitoring import MonitoringModule
except ImportError:
    MonitoringModule = None

try:
    from .calibration import EnsembleCalibrator, TemperatureScaler
except ImportError:
    TemperatureScaler = None
    EnsembleCalibrator = None

try:
    from .market_simulation import MarketSimulation
except ImportError:
    MarketSimulation = None

try:
    from .integrated_analysis import IntegratedAnalysis
except ImportError:
    IntegratedAnalysis = None

try:
    from .optimization import OptimizationModule
except ImportError:
    OptimizationModule = None

try:
    from .policy_validator import PolicyValidator
except ImportError:
    PolicyValidator = None

try:
    from .data_source_manager import DataSourceManager
except ImportError:
    DataSourceManager = None

# Define __all__ for proper package exposure
__all__ = [
    "MetaLearningModule",
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
    "OptimizationModule",
    "PolicyValidator",
    "DataSourceManager",
]
