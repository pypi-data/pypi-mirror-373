#!/usr/bin/env python3
"""
Test runner script for ebook-mcp project.
This script runs all unit tests for the server components.
"""

import sys
import os
import subprocess
import pytest

def run_tests():
    """Run all tests for the ebook-mcp project"""
    
    # Add the src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, src_path)
    
    # Get the tests directory
    tests_dir = os.path.dirname(__file__)
    
    print("Running ebook-mcp unit tests...")
    print("=" * 50)
    
    # Run tests with pytest
    try:
        # Run tests with verbose output and coverage
        result = pytest.main([
            tests_dir,
            '-v',
            '--tb=short',
            '--strict-markers',
            '--disable-warnings'
        ])
        
        if result == 0:
            print("\n" + "=" * 50)
            print("✅ All tests passed!")
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_specific_test(test_file):
    """Run a specific test file"""
    src_path = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, src_path)
    
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    print(f"Running specific test: {test_file}")
    print("=" * 50)
    
    try:
        result = pytest.main([
            test_path,
            '-v',
            '--tb=short'
        ])
        
        if result == 0:
            print("\n" + "=" * 50)
            print("✅ Test passed!")
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ Test failed!")
            return False
            
    except Exception as e:
        print(f"Error running test: {e}")
        return False


def list_tests():
    """List all available test files"""
    tests_dir = os.path.dirname(__file__)
    test_files = []
    
    for file in os.listdir(tests_dir):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file)
    
    print("Available test files:")
    print("=" * 30)
    for test_file in sorted(test_files):
        print(f"  - {test_file}")
    
    return test_files


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_tests()
        elif command == "run":
            if len(sys.argv) > 2:
                test_file = sys.argv[2]
                run_specific_test(test_file)
            else:
                run_tests()
        else:
            print("Usage:")
            print("  python run_tests.py list          - List all test files")
            print("  python run_tests.py run           - Run all tests")
            print("  python run_tests.py run test_file - Run specific test file")
    else:
        run_tests() 