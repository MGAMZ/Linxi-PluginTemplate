#!/usr/bin/env python3
"""Check the ASCII render guards of this Cookiecutter template.

File-type detectors decide text vs binary from a file's leading bytes only: cookiecutter reads the first 512 bytes, binaryornot the first 1024. A Chinese-dense leading block cut mid-character at one of these boundaries makes the whole file judged binary, so it is copied into generated projects without any template rendering and without warning. The mitigation is an ASCII guard: every rendered text file whose body contains non-ASCII characters starts with a pure-ASCII comment block longer than 1024 bytes, so both detectors always see clean text.

This script runs two checks: it classifies the leading block of each of the nine rendered text files against both byte windows, then generates the project once with the pinned cookiecutter into a fresh temp directory and reports any unrendered Jinja markers (`{{`, `{%`) left in the generated files. The second check fails the whole run when the interpreter's cookiecutter version is not the pinned 2.7.1. Run it with an interpreter that has cookiecutter 2.7.1 installed:

    python scripts/check_render_guards.py

Exit code 0 means both checks passed, 1 means at least one failed.
"""

import shutil
import sys
import tempfile
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PINNED_COOKIECUTTER = "2.7.1"
# Leading-byte windows of the file-type detectors: cookiecutter slices 512 bytes, binaryornot slices 1024.
GUARD_WINDOWS = (512, 1024)
# The nine rendered text files, fixed list (see CONTRIBUTING.md).
RENDERED_TEXT_FILES = (
    "{{ cookiecutter.repo_name }}/.gitignore",
    "{{ cookiecutter.repo_name }}/NEXTSTEPS.md",
    "{{ cookiecutter.repo_name }}/README.md",
    "{{ cookiecutter.repo_name }}/pyproject.toml",
    "{{ cookiecutter.repo_name }}/tests/test_registration.py",
    "{{ cookiecutter.repo_name }}/{{ cookiecutter.python_package }}/__init__.py",
    "{{ cookiecutter.repo_name }}/{{ cookiecutter.python_package }}/probe.py",
    "{{ cookiecutter.repo_name }}/{{ cookiecutter.python_package }}/processor.py",
    "hooks/post_gen_project.py",
)
JINJA_RESIDUE_MARKERS = (b"{{", b"{%")


@dataclass(frozen=True, slots=True)
class GuardRow:
    rel_path: str
    size: int | None
    first_non_ascii: int | None
    text_at: dict[int, bool]
    passed: bool
    note: str


def first_non_ascii_offset(data: bytes) -> int | None:
    for index, byte in enumerate(data):
        if byte >= 0x80:
            return index
    return None


def head_decodes_as_text(data: bytes, window: int) -> bool:
    head = data[:window]
    if b"\x00" in head:
        return False
    try:
        head.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def classify_rendered_file(rel_path: str) -> GuardRow:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        return GuardRow(rel_path, None, None, {}, False, "file missing")
    data = path.read_bytes()
    first_non_ascii = first_non_ascii_offset(data)
    text_at = {window: head_decodes_as_text(data, window) for window in GUARD_WINDOWS}
    guarded = first_non_ascii is None or first_non_ascii >= GUARD_WINDOWS[-1]
    passed = guarded and all(text_at.values())
    if not all(text_at.values()):
        failed = [str(w) for w, ok in text_at.items() if not ok]
        note = f"head undecodable at window {','.join(failed)} (detector would judge binary)"
    elif not guarded:
        assert first_non_ascii is not None
        note = f"non-ASCII at byte {first_non_ascii} < {GUARD_WINDOWS[-1]}: guard block missing or too short"
    elif first_non_ascii is None:
        note = "pure ASCII"
    else:
        note = f"ASCII guard spans byte {first_non_ascii}"
    return GuardRow(rel_path, len(data), first_non_ascii, text_at, passed, note)


def check_guard_classification() -> tuple[bool, list[str]]:
    header = f"{'file':<62} {'bytes':>6} {'nonascii':>8} {'t512':>5} {'t1024':>5}  verdict  note"
    lines = [header, "-" * len(header)]
    all_passed = True
    for rel_path in RENDERED_TEXT_FILES:
        row = classify_rendered_file(rel_path)
        all_passed = all_passed and row.passed
        size = "-" if row.size is None else str(row.size)
        offset = "-" if row.first_non_ascii is None else str(row.first_non_ascii)
        t512 = "-" if not row.text_at else ("text" if row.text_at[512] else "BIN")
        t1024 = "-" if not row.text_at else ("text" if row.text_at[1024] else "BIN")
        verdict = "PASS" if row.passed else "FAIL"
        lines.append(f"{row.rel_path:<62} {size:>6} {offset:>8} {t512:>5} {t1024:>5}  {verdict:<7} {row.note}")
    return all_passed, lines


def check_scaffold_drill() -> tuple[bool, list[str]]:
    lines: list[str] = []
    try:
        installed = pkg_version("cookiecutter")
    except PackageNotFoundError:
        return False, ["cookiecutter is not installed in this interpreter"]
    lines.append(f"executing interpreter: {sys.executable}")
    lines.append(f"cookiecutter version: {installed} (pinned: {PINNED_COOKIECUTTER})")
    if installed != PINNED_COOKIECUTTER:
        return False, [*lines, "FAIL: version mismatch, rerun inside the pinned environment"]
    try:
        binaryornot_version = pkg_version("binaryornot")
    except PackageNotFoundError:
        binaryornot_version = "not installed"
    lines.append(f"binaryornot version: {binaryornot_version}")

    from cookiecutter.main import cookiecutter

    tmp_root = tempfile.mkdtemp(prefix="linxi-t1-selfcheck-")
    try:
        project_dir = Path(cookiecutter(str(REPO_ROOT), no_input=True, output_dir=tmp_root, config_file=None))
        generated = sorted(p for p in project_dir.rglob("*") if p.is_file())
        if not generated:
            return False, [*lines, "FAIL: scaffold produced no files"]
        lines.append(f"scaffold target: {tmp_root} ({len(generated)} generated files)")
        lines.append(f"{'generated file':<40} {'{{':>4} {'{%':>4}  verdict")
        all_clean = True
        for path in generated:
            data = path.read_bytes()
            counts = [data.count(marker) for marker in JINJA_RESIDUE_MARKERS]
            clean = all(count == 0 for count in counts)
            all_clean = all_clean and clean
            rel = path.relative_to(project_dir).as_posix()
            verdict = "CLEAN" if clean else "RESIDUE"
            lines.append(f"{rel:<40} {counts[0]:>4} {counts[1]:>4}  {verdict}")
        return all_clean, lines
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        if Path(tmp_root).exists():
            lines.append(f"WARN: temp dir survived cleanup: {tmp_root}")
        else:
            lines.append("temp scaffold dir removed")


def main() -> int:
    check1_passed, check1_lines = check_guard_classification()
    check2_passed, check2_lines = check_scaffold_drill()
    print("CHECK 1 rendered-text guard classification: " + ("PASS" if check1_passed else "FAIL"))
    print("\n".join(check1_lines))
    print("CHECK 2 pinned-version scaffold drill + jinja residue search: " + ("PASS" if check2_passed else "FAIL"))
    print("\n".join(check2_lines))
    print("SELF-CHECK RESULT: " + ("PASS" if check1_passed and check2_passed else "FAIL"))
    return 0 if check1_passed and check2_passed else 1


if __name__ == "__main__":
    sys.exit(main())
