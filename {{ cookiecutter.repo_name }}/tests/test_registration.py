import importlib

import pytest


pytest.importorskip("tiansuo")
{% if cookiecutter.include_probe == "yes" %}
pytest.importorskip("probeinterface")
{% endif %}

from tiansuo.processor import PROCESS_STAGES
from tiansuo.processor.registry import get_processor_registration_name, get_registered_probe, get_registered_processors


def _import_plugin_package():
    return importlib.import_module("{{ cookiecutter.python_package }}")


{% if cookiecutter.include_processor == "yes" %}
def test_processor_is_registered_after_import():
    _import_plugin_package()

    registered_names = [
        get_processor_registration_name(processor_cls)
        for processor_cls in get_registered_processors(PROCESS_STAGES.PREPROCESS)
    ]

    assert "ExamplePluginProcessor" in registered_names
{% endif %}


{% if cookiecutter.include_probe == "yes" %}
def test_probe_is_registered_after_import():
    _import_plugin_package()
    assert get_registered_probe("example_linear_probe") is not None
{% endif %}


{% if cookiecutter.include_processor == "no" and cookiecutter.include_probe == "no" %}
def test_package_can_be_imported():
    module = _import_plugin_package()
    assert module.__name__ == "{{ cookiecutter.python_package }}"
{% endif %}