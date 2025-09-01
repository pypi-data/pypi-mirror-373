__version__ = "0.1.6"

def get_provider_info():
    """Function to get provider information."""
    return {
        "package-name": "sciaiot-airflow-providers-tdengine",
        "name": "Airflow TDengine Provider",
        "description": "A provider of Apache Airflow for TDengine.",
        "versions": [__version__],
        "hook-class-names": [
            "sciaiot.airflow.providers.tdengine.hooks.tdengine.TDengineHook"
        ],
        "connection-types": [
            {
                "connection-type": "tdengine",
                "hook-class-name": "sciaiot.airflow.providers.tdengine.hooks.tdengine.TDengineHook"
            }
        ],
    }
