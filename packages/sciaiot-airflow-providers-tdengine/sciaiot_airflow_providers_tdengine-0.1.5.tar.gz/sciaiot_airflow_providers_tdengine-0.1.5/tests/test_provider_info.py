
import unittest

from sciaiot.airflow.providers.tdengine import get_provider_info


class TestProviderInfo(unittest.TestCase):
  """
    Test provider info.
  """
  
  def test_info(self):
    """ Run get_provider_info(). """
    info = get_provider_info()
    assert info is not None
    assert info["package-name"] == "sciaiot-airflow-providers-tdengine"
