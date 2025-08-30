#!/usr/bin/env python3
"""
Modern MDL Test Suite Runner
Tests the new JavaScript-style MDL language implementation
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"[+] {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def test_mdl_file(mdl_file, description):
    """Test an MDL file by building it"""
    # Test build
    if not run_command(f"mdl build --mdl {mdl_file} -o dist", f"Build: {description}"):
        return False
    
    return True

def test_cli_functionality():
    """Test CLI functionality"""
    print("\n[CLI] Testing CLI Functionality:")
    print("-" * 30)
    
    tests = [
        ("mdl build --help", "CLI build help command"),
        ("mdl new --help", "CLI new help command"),
        ('mdl new test_pack --name "Test Pack"', "CLI new command"),
    ]
    
    results = []
    for cmd, desc in tests:
        results.append(run_command(cmd, desc))
    
    # Clean up test pack
    if os.path.exists("test_pack"):
        shutil.rmtree("test_pack")
    
    return all(results)

def main():
    """Run all modern MDL tests"""
    print("[TEST] Starting Modern MDL Test Suite...")
    print("=" * 60)
    
    # Create test directory
    os.makedirs("dist", exist_ok=True)
    
    # Test results tracking
    total_tests = 0
    passed_tests = 0
    
    # Working MDL examples
    mdl_examples = [
        ("hello_world.mdl", "Hello World"),
        ("variables.mdl", "Variables and Data Types"),
        ("conditionals.mdl", "Conditional Logic"),
        ("simple_control.mdl", "Simple Control Structures"),
        ("loops.mdl", "Loop Constructs"),
        ("namespaces.mdl", "Namespaces and Cross-namespace Calls"),
        ("error_handling.mdl", "Error Handling"),
        ("adventure_pack.mdl", "Complete Adventure Pack"),
        ("pack_format_43_example.mdl", "Pack Format 43 Example"),
        ("pack_format_45_example.mdl", "Pack Format 45 Example"),
        ("pre_82_example.mdl", "Pre-82 Example"),
    ]
    
    # Test MDL files
    print("\n[MDL] Testing Working MDL Files:")
    print("-" * 30)
    for mdl_file, description in mdl_examples:
        if os.path.exists(mdl_file):
            total_tests += 1
            if test_mdl_file(mdl_file, description):
                passed_tests += 1
        else:
            print(f"[!] Skipping {mdl_file} - file not found")
    
    # Test CLI functionality
    total_tests += 1
    if test_cli_functionality():
        passed_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"[SUMMARY] Test Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
