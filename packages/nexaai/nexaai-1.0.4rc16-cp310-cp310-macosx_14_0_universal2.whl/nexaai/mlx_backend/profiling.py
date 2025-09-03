from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import IntEnum

# --------------------------------------------------------------------------------------
# Stop reason constants matching profile.h
# --------------------------------------------------------------------------------------

class StopReason(IntEnum):
    """Stop reason constants matching profile.h"""
    ML_STOP_REASON_UNKNOWN = 0
    ML_STOP_REASON_EOS = 1
    ML_STOP_REASON_LENGTH = 2
    ML_STOP_REASON_USER = 3
    ML_STOP_REASON_STOP_SEQUENCE = 4
    ML_STOP_REASON_COMPLETED = 5

# --------------------------------------------------------------------------------------
# Profiling data structure
# --------------------------------------------------------------------------------------

@dataclass
class ProfilingData:
    """Profiling data for performance metrics."""
    ttft_us: int = 0             # Time to first token (us)
    total_time_us: int = 0       # Total generation time (us) 
    prompt_time_us: int = 0      # Prompt processing time (us)
    decode_time_us: int = 0      # Token generation time (us)
    tokens_per_second: float = 0.0  # Decoding speed (tokens/sec)
    total_tokens: int = 0        # Total tokens generated
    prompt_tokens: int = 0       # Number of prompt tokens
    generated_tokens: int = 0    # Number of generated tokens
    stop_reason: int = StopReason.ML_STOP_REASON_UNKNOWN  # Stop reason (numeric)
    
    def reset(self):
        """Reset all profiling data."""
        self.ttft_us = 0
        self.total_time_us = 0
        self.prompt_time_us = 0
        self.decode_time_us = 0
        self.tokens_per_second = 0.0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.generated_tokens = 0
        self.stop_reason = StopReason.ML_STOP_REASON_UNKNOWN

# --------------------------------------------------------------------------------------
# Profiling context (similar to ml_ProfilingContext in profile.h)
# --------------------------------------------------------------------------------------

@dataclass
class ProfilingContext:
    """Profiling context for tracking timing and state."""
    start_time: Optional[float] = None
    prompt_start_time: Optional[float] = None
    prompt_end_time: Optional[float] = None
    decode_start_time: Optional[float] = None
    decode_end_time: Optional[float] = None
    first_token_time: Optional[float] = None
    end_time: Optional[float] = None
    
    ttft_recorded: bool = False
    stop_reason: int = StopReason.ML_STOP_REASON_UNKNOWN
    prompt_tokens: int = 0
    generated_tokens: int = 0
    
    def reset(self):
        """Reset profiling context."""
        self.start_time = None
        self.prompt_start_time = None
        self.prompt_end_time = None
        self.decode_start_time = None
        self.decode_end_time = None
        self.first_token_time = None
        self.end_time = None
        self.ttft_recorded = False
        self.stop_reason = StopReason.ML_STOP_REASON_UNKNOWN
        self.prompt_tokens = 0
        self.generated_tokens = 0

# --------------------------------------------------------------------------------------
# Profiling functions (similar to profile.h functions)
# --------------------------------------------------------------------------------------

def profiling_reset(ctx: ProfilingContext) -> None:
    """Reset profiling context (ml_profiling_reset)."""
    ctx.reset()

def profiling_start(ctx: ProfilingContext) -> None:
    """Start profiling (ml_profiling_start)."""
    ctx.start_time = time.perf_counter()
    ctx.prompt_start_time = ctx.start_time

def profiling_prompt_start(ctx: ProfilingContext) -> None:
    """Start prompt processing timing (ml_profiling_prompt_start)."""
    ctx.prompt_start_time = time.perf_counter()

def profiling_prompt_end(ctx: ProfilingContext) -> None:
    """End prompt processing timing (ml_profiling_prompt_end)."""
    ctx.prompt_end_time = time.perf_counter()

def profiling_decode_start(ctx: ProfilingContext) -> None:
    """Start decode timing (ml_profiling_decode_start)."""
    ctx.decode_start_time = time.perf_counter()

def profiling_decode_end(ctx: ProfilingContext) -> None:
    """End decode timing (ml_profiling_decode_end)."""
    ctx.decode_end_time = time.perf_counter()

def profiling_record_ttft(ctx: ProfilingContext) -> None:
    """Record time to first token (ml_profiling_record_ttft)."""
    if not ctx.ttft_recorded and ctx.start_time is not None:
        ctx.first_token_time = time.perf_counter()
        ctx.ttft_recorded = True

def profiling_update_prompt_tokens(ctx: ProfilingContext, prompt_tokens: int) -> None:
    """Update prompt token count (ml_profiling_update_prompt_tokens)."""
    ctx.prompt_tokens = prompt_tokens

def profiling_update_generated_tokens(ctx: ProfilingContext, generated_tokens: int) -> None:
    """Update generated token count (ml_profiling_update_generated_tokens)."""
    ctx.generated_tokens = generated_tokens

def profiling_stop_reason(ctx: ProfilingContext, stop_reason: int) -> None:
    """Set stop reason (ml_profiling_stop_reason)."""
    ctx.stop_reason = stop_reason

def profiling_end(ctx: ProfilingContext) -> None:
    """End profiling (ml_profiling_end)."""
    ctx.end_time = time.perf_counter()

def profiling_gen_data(ctx: ProfilingContext) -> ProfilingData:
    """Generate profiling data from context (ml_profiling_gen_data)."""
    data = ProfilingData()
    
    if ctx.start_time is None or ctx.end_time is None:
        return data
    
    # Calculate total time
    data.total_time_us = int((ctx.end_time - ctx.start_time) * 1_000_000)
    
    # Calculate prompt time
    if ctx.prompt_start_time is not None and ctx.prompt_end_time is not None:
        data.prompt_time_us = int((ctx.prompt_end_time - ctx.prompt_start_time) * 1_000_000)
    
    # Calculate decode time
    if ctx.decode_start_time is not None and ctx.decode_end_time is not None:
        data.decode_time_us = int((ctx.decode_end_time - ctx.decode_start_time) * 1_000_000)
    
    # Calculate TTFT
    if ctx.first_token_time is not None and ctx.start_time is not None:
        data.ttft_us = int((ctx.first_token_time - ctx.start_time) * 1_000_000)
    
    # Set token counts
    data.prompt_tokens = ctx.prompt_tokens
    data.generated_tokens = ctx.generated_tokens
    data.total_tokens = ctx.prompt_tokens + ctx.generated_tokens
    
    # Calculate tokens per second
    if data.decode_time_us > 0:
        data.tokens_per_second = (data.generated_tokens * 1_000_000.0) / data.decode_time_us
    
    # Set stop reason
    data.stop_reason = ctx.stop_reason
    
    return data

def stop_reason_to_string(reason: int) -> str:
    """Convert stop reason to string (stop_reason_to_string)."""
    try:
        return StopReason(reason).name
    except ValueError:
        return f"UNKNOWN({reason})"

# --------------------------------------------------------------------------------------
# Profiling mixin for model classes
# --------------------------------------------------------------------------------------

class ProfilingMixin:
    """Mixin class to add profiling capabilities to model classes."""
    
    def __init__(self):
        """Initialize profiling mixin."""
        self._profiling_context = ProfilingContext()
        self._profiling_data = ProfilingData()
    
    def _start_profiling(self) -> None:
        """Start profiling for an operation."""
        profiling_reset(self._profiling_context)
        profiling_start(self._profiling_context)
    
    def _prompt_start(self) -> None:
        """Start prompt processing timing."""
        profiling_prompt_start(self._profiling_context)
    
    def _prompt_end(self) -> None:
        """End prompt processing timing."""
        profiling_prompt_end(self._profiling_context)
    
    def _decode_start(self) -> None:
        """Start decode timing."""
        profiling_decode_start(self._profiling_context)
    
    def _decode_end(self) -> None:
        """End decode timing."""
        profiling_decode_end(self._profiling_context)
    
    def _record_ttft(self) -> None:
        """Record time to first token."""
        profiling_record_ttft(self._profiling_context)
    
    def _update_prompt_tokens(self, prompt_tokens: int) -> None:
        """Update prompt token count."""
        profiling_update_prompt_tokens(self._profiling_context, prompt_tokens)
    
    def _update_generated_tokens(self, generated_tokens: int) -> None:
        """Update generated token count."""
        profiling_update_generated_tokens(self._profiling_context, generated_tokens)
    
    def _set_stop_reason(self, stop_reason: int) -> None:
        """Set stop reason."""
        profiling_stop_reason(self._profiling_context, stop_reason)
    
    def _end_profiling(self) -> ProfilingData:
        """End profiling and return data."""
        profiling_end(self._profiling_context)
        self._profiling_data = profiling_gen_data(self._profiling_context)
        return self._profiling_data
    
    def get_profiling_data(self) -> ProfilingData:
        """Get profiling data for the last operation."""
        return self._profiling_data
    
    def reset_profiling(self) -> None:
        """Reset profiling data."""
        self._profiling_data.reset()