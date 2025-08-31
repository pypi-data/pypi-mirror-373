"""Run all streaming tests."""

import sys
import subprocess
from pathlib import Path


def run_test(test_file: str) -> bool:
    """Run a single test file and return success status."""
    test_path = Path(__file__).parent / test_file
    
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, str(test_path)], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run {test_file}: {e}")
        return False


def main():
    """Run all streaming tests."""
    print("Streaming Primitives Test Suite")
    print("=" * 60)
    
    # List of test files to run
    tests = [
        "test_basic.py",
        "test_tee.py", 
        "test_buffer.py",
        "test_recorder.py"
    ]
    
    results = {}
    
    # Run each test
    for test in tests:
        results[test] = run_test(test)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test:<20} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(tests)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
