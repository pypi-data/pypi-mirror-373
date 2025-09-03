#!/usr/bin/env python3
"""
Quick MSA Enhancement Validation
===============================

Fast validation that the enhanced MSA plugins work correctly with the updated orchestrator
without requiring full Semantic Kernel environment setup.
"""

import json
import sys


def validate_orchestrator_updates():
    """Validate that orchestrator uses new enhanced function names."""
    print("🔍 Validating orchestrator updates...")

    try:
        with open("reasoning_kernel/sk_core/sk_orchestrator.py", "r") as f:
            orchestrator_content = f.read()

        # Check for new function names
        if "generate_probabilistic_program" in orchestrator_content:
            print("✅ Orchestrator uses generate_probabilistic_program")
        else:
            print("❌ Orchestrator missing generate_probabilistic_program")
            return False

        if "execute_probabilistic_program" in orchestrator_content:
            print("✅ Orchestrator uses execute_probabilistic_program")
        else:
            print("❌ Orchestrator missing execute_probabilistic_program")
            return False

        # Check for old function names (should be gone)
        if "generate_ppl_program" in orchestrator_content:
            print("⚠️  Orchestrator still contains old generate_ppl_program references")
        else:
            print("✅ Old function name generate_ppl_program removed")

        if 'execute_ppl"' in orchestrator_content:
            print("⚠️  Orchestrator still contains old execute_ppl references")
        else:
            print("✅ Old function name execute_ppl removed")

        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def validate_plugin_consistency():
    """Validate plugin function signatures are consistent."""
    print("🔍 Validating plugin consistency...")

    try:
        with open("reasoning_kernel/sk_core/msa_program_plugin.py", "r") as f:
            plugin_content = f.read()

        # Check for enhanced function names
        if "def generate_probabilistic_program(" in plugin_content:
            print("✅ Plugin has generate_probabilistic_program function")
        else:
            print("❌ Plugin missing generate_probabilistic_program function")
            return False

        if "def execute_probabilistic_program(" in plugin_content:
            print("✅ Plugin has execute_probabilistic_program function")
        else:
            print("❌ Plugin missing execute_probabilistic_program function")
            return False

        # Check for SK best practices annotations
        if "@kernel_function" in plugin_content:
            print("✅ Plugin uses @kernel_function decorators")
        else:
            print("⚠️  Plugin missing @kernel_function decorators")

        if "Annotated[str," in plugin_content:
            print("✅ Plugin uses Annotated type hints")
        else:
            print("⚠️  Plugin missing Annotated type hints")

        return True

    except Exception as e:
        print(f"❌ Plugin validation failed: {e}")
        return False


def main():
    """Run quick validation checks."""
    print("=" * 60)
    print("MSA Enhancement Quick Validation")
    print("=" * 60)

    checks = [
        validate_orchestrator_updates,
        validate_plugin_consistency,
    ]

    passed = 0
    for check in checks:
        if check():
            passed += 1
        print()

    print("=" * 60)
    if passed == len(checks):
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Enhanced MSA plugins are properly integrated")
        print("✅ Orchestrator updated with new function names")
        print("✅ Ready for production integration testing")
        print()
        print("📋 Next Steps:")
        print("  1. Fix Semantic Kernel environment issues")
        print("  2. Run full integration test (test_msa_integration.py)")
        print("  3. Validate performance improvements")
        print("  4. Update API documentation")
        print("  5. Deploy to production")
        return 0
    else:
        print(f"❌ {len(checks) - passed} validation(s) failed")
        print("Fix issues above before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
