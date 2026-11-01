"""A Design System wheel needs independent browser parity before qualification."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
CHECK = ROOT / ".github/automation/check-and-build-kellytec-design-system"


def load(relative):
    spec = importlib.util.spec_from_file_location("service_visual_" + Path(relative).stem, CHECK / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(tmp_path):
    wheel = tmp_path / "src/kellytec-design-system/dist/kellytec_design_system-1.0.1-py3-none-any.whl"
    wheel.parent.mkdir(parents=True)
    wheel.write_bytes(b"fixed wheel bytes")
    path = tmp_path / ".automation/kellytec-design-system/snapshot.json"
    path.parent.mkdir(parents=True)
    value = {"snapshot_id": "checked-source"}
    path.write_text(json.dumps(value))
    return wheel, value


@pytest.mark.parametrize("browser_result", ["passed", "dropdown_test_failure", "command_failure", "incomplete_report"])
def test_installed_package_is_qualified_only_after_independent_browser_parity(
    tmp_path, monkeypatch, browser_result,
):
    module = load("scripts/verify_installed_package.py")
    wheel, snapshot = prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "restore_qualification", lambda *args: False)
    calls = []
    records = []

    def command(args, **kwargs):
        calls.append(args)
        if "pytest" in args and browser_result == "dropdown_test_failure":
            assert "tests/kellytec-design-system" in args
            raise RuntimeError("Dropdown reselection browser regression")
        if "-c" in args:
            return "/pinned/chromium"
        if any(str(arg).endswith("check_service_parity.py") for arg in args):
            if browser_result == "command_failure":
                raise RuntimeError("Reference parity differs")
            report = tmp_path / ".automation/design-system-ui/validation.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps({"cases": [
                {"mode": "component", "viewport_width": width,
                 "pixel_equal": True, "computed_styles_equal": True}
                for width in ((390,) if browser_result == "incomplete_report" else (390, 520, 521, 900, 1440))
            ]}))
        return ""

    monkeypatch.setattr(module, "command", command)
    monkeypatch.setattr(module, "record_qualified", lambda *args: records.append(args))
    if browser_result in ("dropdown_test_failure", "command_failure"):
        message = "Dropdown reselection browser regression" if browser_result == "dropdown_test_failure" else "Reference parity differs"
        with pytest.raises(RuntimeError, match=message):
            module.main()
        assert not records
    elif browser_result == "incomplete_report":
        with pytest.raises(ValueError, match="visual comparisons"):
            module.main()
        assert not records
    else:
        module.main()
        assert len(records) == 1
        root, value, files, checks = records[0]
        assert value == snapshot and checks["services-ui-v1"] == "success"
        acceptance = tmp_path / ".automation/design-system-ui/acceptance.json"
        assert wheel in files and acceptance in files
        report = json.loads(acceptance.read_text())
        assert report["snapshot_id"] == snapshot["snapshot_id"]
        assert report["wheel_sha256"] == hashlib.sha256(wheel.read_bytes()).hexdigest()
        assert report["status"] == "passed"


@pytest.mark.parametrize("drift", [None, "checks", "snapshot_id", "wheel_sha256", "status", "wheel_bytes"])
def test_restored_qualification_cannot_bypass_bound_visual_evidence(tmp_path, monkeypatch, drift):
    module = load("scripts/verify_installed_package.py")
    wheel, snapshot = prepare(tmp_path)
    report_path = tmp_path / ".automation/design-system-ui/acceptance.json"
    report_path.parent.mkdir(parents=True)
    wheel_sha256 = hashlib.sha256(wheel.read_bytes()).hexdigest()
    report = {
        "status": "passed", "policy": "services-ui-v1", "visual_comparison": "passed",
        "snapshot_id": snapshot["snapshot_id"], "wheel_sha256": wheel_sha256,
    }
    qualification = {
        "checks": {"services-ui-v1": "success"},
        "artifacts": {
            wheel.relative_to(tmp_path).as_posix(): wheel_sha256,
            report_path.relative_to(tmp_path).as_posix(): "retained-report-digest",
        },
    }
    if drift == "checks":
        qualification["checks"] = {}
    elif drift == "wheel_bytes":
        wheel.write_bytes(b"different wheel bytes")
    elif drift:
        report[drift] = "different-or-failed"
    report_path.write_text(json.dumps(report))
    (tmp_path / ".automation/kellytec-design-system/qualified.json").write_text(json.dumps(qualification))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "restore_qualification", lambda *args: True)

    def forbidden(*args, **kwargs):
        raise AssertionError("Restore must validate retained evidence without rebuilding or requalifying")

    monkeypatch.setattr(module, "command", forbidden)
    monkeypatch.setattr(module, "record_qualified", forbidden)
    if drift:
        with pytest.raises(ValueError, match="Services visual"):
            module.main()
    else:
        module.main()
