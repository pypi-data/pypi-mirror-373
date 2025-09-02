import pytest
from wbcore.test import GenerateTest, default_config

config = {}
for key, value in default_config.items():
    config[key] = list(filter(lambda x: x.__module__.startswith("wbreport"), value))


@pytest.mark.django_db
@GenerateTest(config)
class TestProject:
    pass
