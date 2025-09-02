import pytest
from wbcore.test import GenerateTest, default_config

config = {}
for key, value in default_config.items():
    config[key] = list(filter(lambda x: x.__module__.startswith("wbintegrator_office365"), value))


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass
