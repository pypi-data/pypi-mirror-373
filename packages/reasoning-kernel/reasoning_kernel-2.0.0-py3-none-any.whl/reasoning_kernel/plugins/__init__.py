"""Plugin package initialization - Simplified SK-native structure."""

# Import working plugins with graceful fallbacks
try:
    from .msa_reasoning_simple import MSAReasoningPlugin
except ImportError:
    MSAReasoningPlugin = None

try:
    from .simple_test import SimpleTestPlugin
except ImportError:
    SimpleTestPlugin = None

# Try complex plugins with graceful fallbacks
try:
    from .knowledge import KnowledgePlugin, create_knowledge_plugin
except ImportError:
    KnowledgePlugin = None
    create_knowledge_plugin = None

try:
    from .world_model import WorldModelPlugin, create_world_model_plugin
except ImportError:
    WorldModelPlugin = None
    create_world_model_plugin = None

# Export available plugins
__all__ = []

if MSAReasoningPlugin:
    __all__.append("MSAReasoningPlugin")

if SimpleTestPlugin:
    __all__.append("SimpleTestPlugin")

if KnowledgePlugin:
    __all__.extend(["KnowledgePlugin", "create_knowledge_plugin"])

if WorldModelPlugin:
    __all__.extend(["WorldModelPlugin", "create_world_model_plugin"])
