#!/usr/bin/env python3
"""
Quick MSA Plugin Import Test
============================
"""

import sys
from pathlib import Path

# Add the reasoning_kernel package to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    print("🧪 Testing MSA Plugin Imports")
    print("=" * 40)

    try:
        from reasoning_kernel.plugins.msa_reasoning_simple import MSAReasoningPlugin

        plugin = MSAReasoningPlugin()
        print(f"✅ Simple plugin imported and instantiated")
        print(f"   Class: {type(plugin).__name__}")
        print(f"   Methods: {[m for m in dir(plugin) if not m.startswith('_') and callable(getattr(plugin, m))]}")
    except Exception as e:
        print(f"❌ Simple plugin failed: {e}")

    try:
        from reasoning_kernel.plugins.msa_reasoning_enhanced import EnhancedMSAReasoningPlugin

        plugin = EnhancedMSAReasoningPlugin()
        print(f"✅ Enhanced plugin imported and instantiated")
        print(f"   Class: {type(plugin).__name__}")
        print(f"   Methods: {[m for m in dir(plugin) if not m.startswith('_') and callable(getattr(plugin, m))]}")
    except Exception as e:
        print(f"❌ Enhanced plugin failed: {e}")

    print("\n🎉 Import test complete!")


if __name__ == "__main__":
    test_imports()
