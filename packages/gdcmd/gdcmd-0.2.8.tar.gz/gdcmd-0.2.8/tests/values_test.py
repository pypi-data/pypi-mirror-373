from gdcmd.helm.validate import validate_strings
from gdcmd.helm.values import ValuesYaml, Sync, App


def test_combined_values():
    values = ValuesYaml()
    new_port = ValuesYaml(sync=Sync(app=App(licenceBase64="abc123")))

    yaml = values.merge(new_port).to_str()
    assert "abc123" in yaml


def test_serialization_to_from_dict():
    values = ValuesYaml().to_dict()
    ValuesYaml.from_dict(values)


def test_validation_work_on_wrong_yaml():
    values = ValuesYaml().to_dict()
    values["sync"]["app"]["hostPortHttps"] = 1000

    try:
        ValuesYaml.from_dict(values)
    except Exception as e:
        assert "common.requireHttps" in str(e)


def test_validation():
    validate_strings([""])

    validate_strings(["""
    deploy:
        db: true
    """])

    try:
        validate_strings(["""
        sync:
            app:
                hostPortHttps: 1000
        """])
        assert False
    except Exception as e:
        assert "common.requireHttps" in str(e)
