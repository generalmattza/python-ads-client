from tests.conftest import PYADS_TESTSERVER_VARIABLE_NAMES

TEST_VAR_NAMES = PYADS_TESTSERVER_VARIABLE_NAMES
TEST_VARIABLES = [(var_name, n) for var_name, n in zip(TEST_VAR_NAMES, range(12))]


def test_ads_target_read_by_name(testserver_advanced, testserver_target):
    """Test single reading by name using the ADS client class."""

    [testserver_target.read_by_name(var_name) for var_name in TEST_VAR_NAMES]


def test_ads_target_write_by_name(testserver_advanced, testserver_target):
    """Test single writing by name using the ADS client class."""

    [testserver_target.write_by_name(var_name, 0) for var_name in TEST_VAR_NAMES]


def test_ads_target_batch_write_by_name(testserver_advanced, testserver_target):
    """Test batch writing by name using the ADS client class."""

    testserver_target.batch_write_by_name(TEST_VARIABLES)


def test_ads_target_batch_read_by_name(testserver_advanced, testserver_target):
    """Test batch reading by name using the ADS client class."""

    testserver_target.batch_read_by_name(TEST_VAR_NAMES)


def test_ads_target_write_by_name_verify(testserver_advanced, testserver_target):
    """Test writing by name with verification using the ADS client class."""

    [
        testserver_target.write_by_name(var_name, 1, verify=True)
        for var_name in TEST_VAR_NAMES
    ]


def test_ads_target_batch_write_by_name_verify(testserver_advanced, testserver_target):
    """Test batch writing by name with verification using the ADS client class."""

    testserver_target.batch_write_by_name(TEST_VARIABLES, verify=True)


def test_ads_target_read_device_info(testserver_advanced, testserver_target):
    """Test reading device info using the ADS client class."""

    testserver_target.read_device_info()
