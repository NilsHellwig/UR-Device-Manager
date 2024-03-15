import os
BASE_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://0.0.0.0:8000') 
DUMMY_DATA_PATH = "test_data/import_dummy.json"
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', "vollgeheim")
TEST_STANDARD_USER_PASSWORD = os.getenv('TEST_STANDARD_USER_PASSWORD', "test123")
