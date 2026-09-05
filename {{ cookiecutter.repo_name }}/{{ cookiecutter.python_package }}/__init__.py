"""Linxi plugin package template.

Importing this package triggers registration of bundled processors and probes.
"""

{% if cookiecutter.include_processor == "yes" %}
from .processor import ExamplePluginProcessor
{% endif %}
{% if cookiecutter.include_probe == "yes" %}
from .probe import build_example_linear_probe
{% endif %}

__all__ = [
{% if cookiecutter.include_processor == "yes" %}
    "ExamplePluginProcessor",
{% endif %}
{% if cookiecutter.include_probe == "yes" %}
    "build_example_linear_probe",
{% endif %}
]