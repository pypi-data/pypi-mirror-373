import pytest
import yaml


@pytest.fixture
def cache_content():
    content = """
        access: eyJ0eXAiOiJKV1XPOCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjEyNTM3OTk1LCJqdGkiOiI1ZjFlYjQ4ZTU2MTY0OTIzYjk5NzNlYWE3MTZmMDJiMyIsInVzZXJfaWQiOiJyb290In0.OlA9G9_ZIyoK8NViEDEoLFQxqwxLjwmzrio7wAgZHrs
        organisation_uuid: 8df668f217494cdfaff89c1a731f31cb
        refresh: eyJ0eXAiOiXPV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYxMjYyNDM5NSwianRpIjoiYjVmOGUyZjgzMjhiNDdhZmFkN2U3MjJlMzQ1OGNhMjAiLCJ1c2VyX2lkIjoicm9vdCJ9.R1yi6i7uSMm9SbARzAsSORCCthlOhe8SvVLXbZFx9_U
        result_folder: /tmp/results
        scenario_folder: /tmp/scenarios
        username: test    
    """
    yield yaml.load(content, Loader=yaml.FullLoader)


@pytest.fixture
def scenario_constant_rain_content():
    content = """
        meta:
            name: "constant rain"
            description: "adds a constant rain event with a duration of 5 minutes at the beginning of the simulation"
        
        scenario:
            simulation:
                threedimodel: "{{ threedimodel_id }}"
                organisation: "{{ organisation_uuid }}"
                name: "{{ simulation_name }}"
                start_datetime: "{{ datetime_now }}"
                duration: 3600
            steps:
                - constantrain:
                    offset: 0
                    duration: 3600
                    value: 0.00002
                    units: 'm/s'
                - action:
                    name: start
                    duration: 300
                    waitfor_timeout: 1800
                - action:
                    name: start
                    waitfor_timeout: 1800
                - waitforstatus:
                    name: 'finished'
                    timeout: 1800    
        """
    yield yaml.load(content, Loader=yaml.FullLoader)
