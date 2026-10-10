"""Checks that can run in the public repository without private Reins access."""

import asyncio
import re
import subprocess
from pathlib import Path

import yaml

from examples.customer_after import handle_ticket as after
from examples.customer_before import handle_ticket as before

ROOT = Path(__file__).resolve().parents[1]


def test_before_after_preserve_prompt_and_business_output():
    prompts = []

    async def provider(prompt):
        prompts.append(prompt)
        return {
            "output": {"reply": "Draft reply"},
            "cost_usd": "0.001",
            "usage": {"input_tokens": 10, "output_tokens": 2},
        }

    class Workflow:
        def __init__(self):
            self.calls = []

        def progress(self, stage, done, total):
            self.calls.append((stage, done, total))

        async def acall(self, execute, **kwargs):
            result, cost = await execute()
            self.calls.append((kwargs, cost))
            return result

    workflow = Workflow()
    plain = asyncio.run(before("ticket", "policy", provider))
    wrapped = asyncio.run(
        after("ticket", "policy", provider, workflow, max_cost="0.01")
    )
    assert plain == wrapped
    assert prompts[0] == prompts[1]
    assert workflow.calls[1][0]["max_cost"] == "0.01"
    assert workflow.calls[1][1] == "0.001"


def run_installer(*args):
    return subprocess.run(
        ["bash", str(ROOT / "scripts/install-skill.sh"), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_install_skill_both_idempotent_and_uninstall(tmp_path):
    args = ("--target", str(tmp_path), "--assistant", "both")
    preview = run_installer(*args, "--dry-run")
    assert preview.returncode == 0 and "Would install" in preview.stdout
    assert not (tmp_path / ".agents").exists()
    first = run_installer(*args)
    assert first.returncode == 0, first.stderr
    for path in (
        tmp_path / ".agents/skills/reins-integrate/SKILL.md",
        tmp_path / ".claude/skills/reins-integrate/SKILL.md",
    ):
        assert path.exists()
        assert (
            path.read_bytes()
            == (ROOT / "customer-install-pack/skill/reins-integrate/SKILL.md").read_bytes()
        )
    again = run_installer(*args)
    assert again.returncode == 0 and "Already installed" in again.stdout
    changed = tmp_path / ".agents/skills/reins-integrate/SKILL.md"
    changed.write_text("modified")
    refused = run_installer(*args)
    assert refused.returncode == 3
    assert changed.read_text() == "modified"
    restored = run_installer(*args, "--force")
    assert restored.returncode == 0
    removed = run_installer(*args, "--uninstall")
    assert removed.returncode == 0
    assert not changed.exists()


def test_installer_refuses_symlinked_skill_paths_without_touching_external_files(
    tmp_path,
):
    customer = tmp_path / "customer"
    external = tmp_path / "external"
    customer.mkdir()
    external.mkdir()
    existing = external / "reins-integrate"
    existing.mkdir()
    marker = existing / "customer-notes.txt"
    marker.write_text("preserve me")
    (customer / ".agents").mkdir()
    (customer / ".agents/skills").symlink_to(external, target_is_directory=True)

    args = ("--target", str(customer), "--assistant", "both")
    for action in ((), ("--dry-run",), ("--force",), ("--uninstall", "--force")):
        result = run_installer(*args, *action)
        assert result.returncode == 3
        assert "symlinked skill path" in result.stderr
        assert marker.read_text() == "preserve me"
        assert not (customer / ".claude").exists()


def test_skill_frontmatter_and_docs_links():
    package = ROOT / "customer-install-pack/skill/reins-integrate"
    legacy = ROOT / "skills/reins-integrate"
    assert sorted(path.relative_to(package) for path in package.rglob("*")) == sorted(
        path.relative_to(legacy) for path in legacy.rglob("*")
    )
    for path in package.rglob("*"):
        if path.is_file():
            assert (
                path.read_bytes() == (legacy / path.relative_to(package)).read_bytes()
            )
    skill = (package / "SKILL.md").read_text()
    assert skill.startswith("---\n")
    frontmatter = yaml.safe_load(skill.split("---", 2)[1])
    assert frontmatter["name"] == "reins-integrate"
    assert "customer" in frontmatter["description"].lower()
    assert "references/integration.md" in skill
    for language in ("en", "zh-CN"):
        for name in ("quickstart", "integration"):
            assert (ROOT / f"docs/{name}.{language}.md").exists()
        assert not (ROOT / f"docs/pilot.{language}.md").exists()


def test_local_markdown_links_resolve():
    files = [
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "customer-install-pack/private-repository.md",
        *ROOT.glob("docs/*.md"),
    ]
    for document in files:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if target.startswith(("https://", "http://", "#")):
                continue
            path = target.split("#", 1)[0]
            assert (document.parent / path).exists(), (document, target)
