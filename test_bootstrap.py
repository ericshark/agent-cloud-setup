"""Isolated regression checks; never use real agent homes."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="cloud-setup-test-") as tmp:
    base = Path(tmp)
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/ericshark/agent-cloud-setup.git", str(base/"clone")], check=True)
    for name in ("bootstrap.sh", "verify.sh", "cloud-install.sh"):
        shutil.copy2(ROOT/name, base/"clone"/name)
    repo = base/"clone"
    caller, home, profile, project = [base/n for n in ("caller", "runtime", "profile", "project")]
    for path in (caller, home, profile, project):
        path.mkdir()
    sentinel = project/"AGENTS.md"
    sentinel.write_text("project unchanged")
    env = dict(os.environ, HOME=str(caller), CODEX_HOME=str(base/"wrong"),
               AGENT_SETUP_HOME=str(home), AGENT_SETUP_CODEX_HOME=str(profile))
    def run(script="bootstrap.sh", ok=True, extra=None):
        result = subprocess.run(["bash", str(repo/script)], cwd=project,
                                env=env if extra is None else extra,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert (result.returncode == 0) == ok, result.stdout
        return result
    profile.joinpath("AGENTS.md").write_text("previous")
    unrelated = home/".agents/skills/unrelated/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("preserve")
    run()
    before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in home.rglob("*") if p.is_file()}
    run()
    assert before == {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in home.rglob("*") if p.is_file()}
    assert not list(caller.iterdir())
    assert not (base/"wrong").exists()
    assert sentinel.read_text() == "project unchanged"
    assert unrelated.read_text() == "preserve"
    assert next((home/".agent-cloud-setup/backups").glob("*/codex/AGENTS.md")).read_text() == "previous"
    skills = list((repo/".agents/skills").iterdir())
    assert len(skills) == 11
    for source in (repo/".agents/skills").rglob("*"):
        if source.is_file():
            for dest in (home/".agents/skills", home/".claude/skills"):
                installed = dest/source.relative_to(repo/".agents/skills")
                assert installed.read_bytes() == source.read_bytes()
                assert installed.stat().st_uid == os.getuid()
                assert installed.stat().st_mode & 0o777 == source.stat().st_mode & 0o777
    (home/".agents/skills/performance/SKILL.md").unlink()
    run("verify.sh", ok=False)
    run()
    blocked = base/"blocked"
    blocked.write_text("not a directory")
    run(ok=False, extra=dict(env, AGENT_SETUP_HOME=str(blocked)))
    run(ok=False, extra=dict(env, AGENT_SETUP_HOME="relative"))
    default_home = base/"default"
    default_env = dict(os.environ, HOME=str(default_home))
    for name in ("CODEX_HOME", "AGENT_SETUP_HOME", "AGENT_SETUP_CODEX_HOME"):
        default_env.pop(name, None)
    run(extra=default_env)
    explicit_env = dict(default_env, HOME=str(base/"explicit"), CODEX_HOME=str(base/"custom"))
    run(extra=explicit_env)
    assert (base/"custom/AGENTS.md").is_file()
    # A local unavailable remote exercises the same fail-fast clone command without
    # depending on whether a particular external network failure can be induced.
    failed = subprocess.run(["git", "clone", str(base/"missing-remote"), str(base/"failed-clone")],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert failed.returncode != 0 and not (base/"failed-clone").exists()
    print("PASS: public clone; default/explicit/independent homes; 11 skills and all bytes; modes/owners; repeat idempotency; backups; project preservation; missing files; invalid paths; install and clone failures")
