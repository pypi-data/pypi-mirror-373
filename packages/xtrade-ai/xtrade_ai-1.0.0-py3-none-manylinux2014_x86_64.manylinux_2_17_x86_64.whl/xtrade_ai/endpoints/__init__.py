"""
XTrade-AI Modular API Endpoints

This package contains all API endpoints organized by functionality.
"""

from .health import router as health_router
from .models import router as models_router
from .predictions import router as predictions_router
from .training import router as training_router
from .fine_tuning import router as fine_tuning_router
from .backtest import router as backtest_router
from .market_data import router as market_data_router

__all__ = [
    'health_router',
    'models_router',
    'predictions_router',
    'training_router',
    'fine_tuning_router',
    'backtest_router',
    'market_data_router'
]