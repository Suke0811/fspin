import logging
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fspin.RateControl import spin


def test_exception_logging_and_warning(caplog, capsys):
    call_count = 0

    def condition():
        nonlocal call_count
        call_count += 1
        # run only once
        return call_count <= 1

    @spin(freq=1000, condition_fn=condition, report=False, thread=False)
    def faulty():
        raise ValueError("boom")

    with caplog.at_level(logging.ERROR):
        with pytest.warns(RuntimeWarning) as record:
            faulty()
        stderr = capsys.readouterr().err

    # Ensure warning contains function name
    assert any("faulty" in str(w.message) for w in record), record
    # Ensure log contains error with function name
    assert any("faulty" in r.getMessage() for r in caplog.records), caplog.text
    # Stderr should contain the traceback
    assert "Traceback" in stderr
    assert "ValueError: boom" in stderr
