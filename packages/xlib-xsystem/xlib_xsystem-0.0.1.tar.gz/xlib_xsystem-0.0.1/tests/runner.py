#!/usr/bin/env python3
"""
Main test runner for xSystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import sys
import subprocess
from pathlib import Path


def run_all_tests():
    """Run all tests (core, unit, integration) in sequence."""
    
    test_categories = ['core', 'unit', 'integration']
    results = {}
    
    for category in test_categories:
        print(f"\n{'='*50}")
        print(f"Running {category.upper()} tests...")
        print(f"{'='*50}")
        
        runner_path = Path(__file__).parent / category / "runner.py"
        if runner_path.exists():
            try:
                result = subprocess.run([sys.executable, str(runner_path)], 
                                      capture_output=False)
                results[category] = result.returncode
                if result.returncode == 0:
                    print(f"✅ {category.upper()} tests PASSED")
                else:
                    print(f"❌ {category.upper()} tests FAILED")
            except Exception as e:
                print(f"❌ Error running {category} tests: {e}")
                results[category] = 1
        else:
            print(f"⚠️  No runner found for {category} tests")
            results[category] = 0
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    all_passed = True
    for category, result in results.items():
        status = "PASSED" if result == 0 else "FAILED"
        print(f"{category.upper()}: {status}")
        if result != 0:
            all_passed = False
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


def run_specific_category(category: str):
    """Run tests for a specific category."""
    
    runner_path = Path(__file__).parent / category / "runner.py"
    
    if not runner_path.exists():
        print(f"❌ No runner found for category: {category}")
        print(f"Available categories: core, unit, integration")
        return 1
    
    try:
        result = subprocess.run([sys.executable, str(runner_path)], 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running {category} tests: {e}")
        return 1


def run_unit_category(unit_category: str):
    """Run specific unit test category."""
    
    unit_runner = Path(__file__).parent / "unit" / "runner.py"
    
    if not unit_runner.exists():
        print(f"❌ Unit test runner not found")
        return 1
    
    try:
        result = subprocess.run([sys.executable, str(unit_runner), unit_category], 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running unit category {unit_category}: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit" and len(sys.argv) > 2:
            # Run specific unit category
            exit_code = run_unit_category(sys.argv[2])
        else:
            # Run specific category
            exit_code = run_specific_category(sys.argv[1])
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
