import pytest
import os

def run_all_tests():
    # Run all tests in the test_llms directory
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    pytest.main([test_dir])

if __name__ == "__main__":
    run_all_tests()
    