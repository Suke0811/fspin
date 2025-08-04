from .rate_control import RateControl as rate
from .decorators import spin as spin_decorator  # Original decorator
from .spin_context import spin as spin_context_manager  # New context manager
from .loop_context import loop  # Keep for backward compatibility
from .unified import spin  # Unified entry point that intelligently selects between decorator and context manager
