from pathlib import Path


PROJECT_ROOT = Path.cwd()


def maybe_remove(rel_path: str, enabled: bool) -> None:
    path = PROJECT_ROOT / rel_path
    if enabled or not path.exists():
        return
    path.unlink()


def main() -> None:
    include_processor = "{{ cookiecutter.include_processor }}" == "yes"
    include_probe = "{{ cookiecutter.include_probe }}" == "yes"

    maybe_remove("{{ cookiecutter.python_package }}/processor.py", include_processor)
    maybe_remove("{{ cookiecutter.python_package }}/probe.py", include_probe)


if __name__ == "__main__":
    main()