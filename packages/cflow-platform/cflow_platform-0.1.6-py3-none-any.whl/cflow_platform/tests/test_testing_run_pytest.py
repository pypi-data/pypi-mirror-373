from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from cflow_platform.handlers.testing_handlers import _parse_pytest_output
from cflow_platform.core.test_runner import run_tests


def test_parse_pytest_output_extracts_summary_and_failures() -> None:
    sample = (
        "============================= test session starts ==============================\n"
        "platform darwin -- Python 3.11.13, pytest-8.4.1\n"
        "collected 1 item\n\n"
        "=================================== FAILURES ===================================\n"
        "___________________________ test_something_fails _____________________________\n"
        "Traceback (most recent call last):\n"
        "  File 'test_example.py', line 3, in test_something_fails\n"
        "    assert 1 == 2\n"
        "AssertionError: assert 1 == 2\n\n"
        "=========================== short test summary info ===========================\n"
        "FAILED test_example.py::test_something_fails - AssertionError: assert 1 == 2\n"
        "============================== 1 failed in 0.01s =============================\n"
    )
    summary = _parse_pytest_output(sample)
    assert "failures" in summary
    assert isinstance(summary["failures"], list)
    assert summary["failures"], "expected at least one failure parsed"
    assert "summary_line" in summary
    assert "failed" in summary["summary_line"].lower()


def test_run_pytest_no_tests_path_returns_nonzero() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        res = run_tests(paths=[tmp], in_process=False)
        assert res["status"] == "failure"
        assert res["summary"]["exit_code"] != 0
        assert "no tests ran" in (res.get("stdout", "") + res.get("stderr", "")).lower()


def test_run_pytest_with_passing_test_succeeds() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_file = tmp_path / "test_ok.py"
        test_file.write_text(
            "def test_ok():\n"
            "    assert True\n"
        )
        res = run_tests(paths=[str(tmp_path)], in_process=False)
        assert res["status"] == "success"
        assert res["summary"]["exit_code"] == 0

