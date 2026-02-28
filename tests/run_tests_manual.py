import os
import sys
import traceback

os.environ["OPENAI_API_KEY"] = "test-key-123"

from tests.test_config import test_load_config_success, test_config_missing_api_key
from tests.test_api import test_read_main, test_get_config, test_clear_history, test_get_settings

class MockMonkeyPatch:
    def setenv(self, key, val):
        os.environ[key] = val
    def delenv(self, key, raising=False):
        if key in os.environ:
            del os.environ[key]

patch = MockMonkeyPatch()

tests = [
    (test_load_config_success, [patch]),
    (test_config_missing_api_key, [patch]),
    (test_read_main, []),
    (test_get_config, []),
    (test_clear_history, []),
    (test_get_settings, [])
]

passes = 0
for func, args in tests:
    try:
        func(*args)
        print(f"✅ {func.__name__} passed")
        passes += 1
    except Exception as e:
        print(f"❌ {func.__name__} failed")
        traceback.print_exc()

if passes == len(tests):
    print("All tests passed!")
    sys.exit(0)
else:
    print(f"{len(tests) - passes} tests failed.")
    sys.exit(1)
