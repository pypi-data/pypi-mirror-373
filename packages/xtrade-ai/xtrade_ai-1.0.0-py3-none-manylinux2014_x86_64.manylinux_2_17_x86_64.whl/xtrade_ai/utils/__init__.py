"""
XTrade-AI Utility Modules
"""

try:
    from .logger import get_logger, setup_logging
    from .patch import patch_gym_imports, setup_comprehensive_warning_suppression
    from .save_model import ModelLoader, ModelSaver
    from .url_model_loader import URLModelLoader
    from .dependency_container import DependencyContainer, get_container
except ImportError as e:
    # Fallback imports for development/testing
    try:
        from logger import get_logger, setup_logging
        from patch import patch_gym_imports, setup_comprehensive_warning_suppression
        from save_model import ModelLoader, ModelSaver
        from url_model_loader import URLModelLoader
        from dependency_container import DependencyContainer, get_container
    except ImportError:
        # If fallback also fails, create dummy functions
        def get_logger(name):
            import logging
            return logging.getLogger(name)
        
        def setup_logging():
            import logging
            logging.basicConfig(level=logging.INFO)
        
        class ModelSaver:
            pass
        
        class ModelLoader:
            pass
        
        class URLModelLoader:
            pass
        
        class DependencyContainer:
            def __init__(self):
                pass
        
        def get_container():
            return DependencyContainer()
        
        def patch_gym_imports():
            pass
        
        def setup_comprehensive_warning_suppression():
            pass

__all__ = [
    "get_logger",
    "setup_logging",
    "ModelSaver",
    "ModelLoader",
    "URLModelLoader",
    "DependencyContainer",
    "get_container",
    "patch_gym_imports",
    "setup_comprehensive_warning_suppression",
]
