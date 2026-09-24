import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server  # noqa: E402  (imports the FastMCP tool functions)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MAKE_DEMO = PROJECT_ROOT / "demo" / "make_demo.sh"
PROBE = PROJECT_ROOT / "sleuth" / "bisect_probe.py"

FAILING_TEST = "tests/test_pricing.py::test_bulk_discount_tier"


@pytest.fixture(scope="module")
def demo_repo(tmp_path_factory):
    target = tmp_path_factory.mktemp("demo") / "demo"
    subprocess.run(["bash", str(MAKE_DEMO), str(target)],
                   check=True, capture_output=True, text=True, timeout=60)
    commits = subprocess.run(
        ["git", "rev-list", "--reverse", "HEAD"], cwd=target,
        capture_output=True, text=True, check=True, timeout=30,
    ).stdout.strip().splitlines()
    assert len(commits) == 8
    return {"path": str(target), "bug_commit": commits[3]}


def test_run_tests_reports_single_failure(demo_repo):
    summary = server.run_tests(demo_repo["path"])
    assert summary["failed"] == 1
    assert summary["failing_tests"] == [FAILING_TEST]
    assert summary["passed"] == 9


def test_reproduce_is_deterministic(demo_repo):
    result = server.reproduce(demo_repo["path"], FAILING_TEST, runs=3)
    assert result["deterministic"] is True
    assert result["failed_every_run"] is True


def test_bisect_finds_culprit_commit(demo_repo):
    import shlex
    cmd = "%s -B %s %s" % (
        shlex.quote(sys.executable), shlex.quote(str(PROBE)),
        shlex.quote(demo_repo["path"]))
    result = server.bisect(demo_repo["path"], cmd)
    assert result["ok"] is True
    assert result["culprit"] == demo_repo["bug_commit"]
    assert "simplify discount tier" in result["message"]
    # working tree must be back on main after bisect
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=demo_repo["path"],
        capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    assert branch == "main"


def test_inspect_commit_returns_diff(demo_repo):
    info = server.inspect_commit(demo_repo["path"], demo_repo["bug_commit"])
    assert info["ok"] is True
    assert "qty > 10" in info["diff"]
    assert "simplify discount tier" in info["subject"]


def _make_fix_diff(demo_repo):
    import difflib
    p = Path(demo_repo["path"]) / "pricing.py"
    old = p.read_text(encoding="utf-8").splitlines(keepends=True)
    new = [l.replace("if qty > 10:  # BUG: off-by-one, should be >= 10",
                     "if qty >= 10:")
           for l in old]
    assert new != old
    return "".join(difflib.unified_diff(old, new, "a/pricing.py", "b/pricing.py"))


def test_apply_patch_refuses_without_approval(demo_repo):
    prop = server.propose_patch(
        demo_repo["path"], FAILING_TEST, demo_repo["bug_commit"],
        _make_fix_diff(demo_repo),
        "The tier boundary is off by one: qty == 10 must earn the 10% tier. "
        "Restore >= so the boundary matches the documented tiers.")
    assert prop["ok"] is True
    refused = server.apply_patch(demo_repo["path"], prop["proposal_id"], approved=False)
    assert refused["applied"] is False
    assert "approval" in refused["reason"]
    # tree untouched: the test still fails
    summary = server.run_tests(demo_repo["path"])
    assert summary["failed"] == 1


def test_apply_patch_with_approval_fixes_tests(demo_repo):
    prop = server.propose_patch(
        demo_repo["path"], FAILING_TEST, demo_repo["bug_commit"],
        _make_fix_diff(demo_repo),
        "Same fix as the refused proposal, now with explicit human approval.")
    done = server.apply_patch(demo_repo["path"], prop["proposal_id"], approved=True)
    assert done["applied"] is True
    assert done["verification"]["failed"] == 0
    assert done["verification"]["passed"] == 10


def test_log_evidence_appends():
    before = server.log_evidence("self_test", {"ping": 1})
    after = server.log_evidence("self_test", {"ping": 2})
    assert after["entries"] == before["entries"] + 1
