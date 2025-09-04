"""
Token management and tracking for Archer
Implements limits and tracking inspired by OpenCode
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

# Constants
OUTPUT_TOKEN_MAX = 32_000  # Maximum output tokens per response
CONTEXT_WARNING_THRESHOLD = 0.9  # Warn when context is 90% full

# File operation limits
FILE_LIMITS = {
    'glob': 100,      # Max files returned by glob operations
    'ls': 100,        # Max files returned by ls operations
    'read': 2000,     # Default max lines per file read
}


@dataclass
class TokenUsage:
    """Track token usage for a single API call"""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class ModelLimits:
    """Model-specific token limits"""
    context: int
    output: int
    
    @classmethod
    def for_model(cls, model_name: str) -> 'ModelLimits':
        """Get limits for a specific model"""
        # Claude 3.5 Sonnet limits
        if "sonnet" in model_name.lower():
            return cls(context=200_000, output=min(8192, OUTPUT_TOKEN_MAX))
        # Claude 3 Opus limits
        elif "opus" in model_name.lower():
            return cls(context=200_000, output=min(4096, OUTPUT_TOKEN_MAX))
        # Claude 3 Haiku limits
        elif "haiku" in model_name.lower():
            return cls(context=200_000, output=min(4096, OUTPUT_TOKEN_MAX))
        # Default conservative limits
        else:
            return cls(context=100_000, output=min(4096, OUTPUT_TOKEN_MAX))


class TokenManager:
    """Manage token usage and enforce limits"""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name
        self.limits = ModelLimits.for_model(model_name)
        self.usage_history: List[TokenUsage] = []
        self.session_start = time.time()
        self.total_input = 0
        self.total_output = 0
        self.total_cached = 0
        
    def add_usage(self, usage: TokenUsage) -> None:
        """Add a token usage record"""
        self.usage_history.append(usage)
        self.total_input += usage.input_tokens
        self.total_output += usage.output_tokens
        self.total_cached += usage.cached_tokens
        
    def get_current_context_usage(self) -> float:
        """Get current context usage as a percentage"""
        if not self.usage_history:
            return 0.0
        
        # Get the most recent usage
        latest = self.usage_history[-1]
        total_context = latest.input_tokens + latest.cached_tokens
        
        return total_context / self.limits.context if self.limits.context > 0 else 0.0
    
    def should_summarize(self) -> bool:
        """Check if conversation should be summarized"""
        usage = self.get_current_context_usage()
        return usage >= CONTEXT_WARNING_THRESHOLD
    
    def get_remaining_context(self) -> int:
        """Get remaining context tokens"""
        if not self.usage_history:
            return self.limits.context
        
        latest = self.usage_history[-1]
        used = latest.input_tokens + latest.cached_tokens
        return max(0, self.limits.context - used - self.limits.output)
    
    def format_usage_display(self, usage: Optional[TokenUsage] = None) -> str:
        """Format token usage for display"""
        if usage is None and self.usage_history:
            usage = self.usage_history[-1]
        
        if not usage:
            return ""
        
        # Calculate percentages
        context_pct = self.get_current_context_usage() * 100
        
        # Format the display
        parts = []
        parts.append(f"📊 Tokens: in={usage.input_tokens:,}")
        parts.append(f"out={usage.output_tokens:,}")
        
        if usage.cached_tokens > 0:
            parts.append(f"cached={usage.cached_tokens:,}")
        
        parts.append(f"context={context_pct:.1f}%")
        
        # Add warning if approaching limit
        if context_pct >= 90:
            parts.append("⚠️ Near limit")
        elif context_pct >= 75:
            parts.append("⚡ High usage")
        
        return " | ".join(parts)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        duration = time.time() - self.session_start
        
        return {
            'duration_seconds': duration,
            'total_requests': len(self.usage_history),
            'total_input_tokens': self.total_input,
            'total_output_tokens': self.total_output,
            'total_cached_tokens': self.total_cached,
            'total_tokens': self.total_input + self.total_output,
            'average_input_per_request': self.total_input / len(self.usage_history) if self.usage_history else 0,
            'average_output_per_request': self.total_output / len(self.usage_history) if self.usage_history else 0,
            'context_usage_percent': self.get_current_context_usage() * 100,
            'model': self.model_name,
            'limits': {
                'context': self.limits.context,
                'output': self.limits.output
            }
        }
    
    def estimate_cost(self) -> Dict[str, float]:
        """Estimate API costs based on token usage"""
        # Claude 3.5 Sonnet pricing (as of 2024)
        # These are approximate and should be updated
        PRICING = {
            'sonnet': {'input': 3.00 / 1_000_000, 'output': 15.00 / 1_000_000},
            'opus': {'input': 15.00 / 1_000_000, 'output': 75.00 / 1_000_000},
            'haiku': {'input': 0.25 / 1_000_000, 'output': 1.25 / 1_000_000},
        }
        
        # Determine model family
        model_key = 'sonnet'
        for key in PRICING:
            if key in self.model_name.lower():
                model_key = key
                break
        
        rates = PRICING[model_key]
        input_cost = self.total_input * rates['input']
        output_cost = self.total_output * rates['output']
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'currency': 'USD'
        }


class ConversationSummarizer:
    """Handle conversation summarization when context is too large"""
    
    @staticmethod
    def should_summarize(messages: List[Dict[str, Any]], token_manager: TokenManager) -> bool:
        """Check if conversation should be summarized"""
        return token_manager.should_summarize()
    
    @staticmethod
    def create_summary_request(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary request for the conversation"""
        # Find the last summary point
        last_summary_idx = -1
        for i, msg in enumerate(messages):
            if msg.get('role') == 'assistant' and msg.get('metadata', {}).get('is_summary'):
                last_summary_idx = i
        
        # Get messages to summarize
        messages_to_summarize = messages[last_summary_idx + 1:] if last_summary_idx >= 0 else messages
        
        return {
            'role': 'user',
            'content': [{
                'type': 'text',
                'text': (
                    "Please provide a detailed but concise summary of our conversation so far. "
                    "Focus on:\n"
                    "- What has been accomplished\n"
                    "- Current work in progress\n"
                    "- Files that have been modified\n"
                    "- Important context and decisions\n"
                    "- Next steps to take\n\n"
                    "This summary will be used to continue our conversation with reduced context."
                )
            }]
        }
    
    @staticmethod
    def compress_conversation(messages: List[Dict[str, Any]], summary: str) -> List[Dict[str, Any]]:
        """Compress conversation history using the summary"""
        # Keep system messages
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        
        # Create summary message
        summary_message = {
            'role': 'assistant',
            'content': [{
                'type': 'text',
                'text': f"[Previous Conversation Summary]\n\n{summary}"
            }],
            'metadata': {'is_summary': True, 'timestamp': datetime.now().isoformat()}
        }
        
        # Find recent messages to keep (last 2-3 exchanges)
        recent_cutoff = max(0, len(messages) - 6)  # Keep last 3 user + 3 assistant messages
        recent_messages = messages[recent_cutoff:]
        
        # Combine: system + summary + recent
        return system_messages + [summary_message] + recent_messages