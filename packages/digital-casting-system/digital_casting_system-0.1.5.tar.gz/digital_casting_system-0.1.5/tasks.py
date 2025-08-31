import json
import os
import re
import tempfile
from pathlib import Path

from invoke import task

from _gen_ref_pages import generate_api_reference


@task
def format(ctx, fix: bool = False):
  """Format the code using ruff."""
  filepath = Path("./src") / "dcs"
  matches = list(filepath.rglob("*.py"))
  files = " ".join(str(f) for f in matches)
  cmd = f"ruff format {files}"
  if fix:
    cmd += " --fix"
  ctx.run(cmd, pty=True)


@task
def test(ctx, verbose: bool = False):
  """Run tests with pytest (0.3 seconds)."""
  cmd = "python -m pytest"
  if verbose:
    cmd += " -v"
  print("Running tests...")
  ctx.run(cmd, pty=True)


@task
def docs(ctx, serve: bool = False):
  """Build documentation with auto-generated API reference."""
  print("Building documentation with auto-generated API reference...")

  if serve:
    print("Serving documentation at http://127.0.0.1:8000")
    ctx.run("mkdocs serve", pty=True)
  else:
    generate_api_reference()
    ctx.run("mkdocs build", pty=True)
    print("Documentation built successfully!")


@task
def docs_clean(ctx):
  """Clean generated documentation files."""
  print("Cleaning generated documentation...")
  ctx.run("rm -rf docs/api/reference/", pty=True)
  ctx.run("rm -rf dist/", pty=True)
  print("Documentation cleaned!")


@task
def build(ctx):
  """Build the package for distribution."""
  print("Building package...")

  # Clean first
  build_clean(ctx)

  # Build with hatchling (no isolation to avoid network issues)
  ctx.run("python -m build --no-isolation", pty=True)
  print("Package built successfully!")


@task
def build_clean(ctx):
  """Clean build artifacts."""
  print("Cleaning build artifacts...")
  ctx.run("rm -rf build/", pty=True)
  ctx.run("rm -rf dist/", pty=True)
  ctx.run("rm -rf *.egg-info/", pty=True)
  ctx.run("find . -name '*.pyc' -delete 2>/dev/null || true", pty=True)
  ctx.run("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true", pty=True)
  print("Build artifacts cleaned!")


@task
def github_release(ctx):
  """Create GitHub release using API - automatically detects tag and repo"""
  # Get the latest tag automatically
  result = ctx.run("git describe --tags --abbrev=0", hide=True)
  tag = result.stdout.strip()

  # Get repo name from git remote
  result = ctx.run("git remote get-url origin", hide=True)
  remote_url = result.stdout.strip()

  if "github.com" in remote_url:
    repo = remote_url.split("github.com")[-1].strip(":/").replace(".git", "")
    if repo.startswith("/"):
      repo = repo[1:]
  else:
    raise ValueError(f"Not a GitHub repository: {remote_url}")

  print(f"Creating GitHub release for {repo} tag: {tag}")

  release_data = {
    "tag_name": tag,
    "name": f"Release {tag}",
    "generate_release_notes": True,
    "draft": False,
    "prerelease": False,
  }

  json_data = json.dumps(release_data).replace('"', '\\"')

  ctx.run(
    f'curl -X POST -H "Authorization: token $GITHUB_TOKEN" '
    f'-H "Accept: application/vnd.github+json" '
    f'-d "{json_data}" '
    f"https://api.github.com/repos/{repo}/releases",
    pty=True,
  )


def _changelog_section_for_version(changelog_path: Path, version: str) -> str:
  """Return the changelog section for the given version (without leading 'v').
  If not found, return an empty string."""
  if not changelog_path.exists():
    return ""
  text = changelog_path.read_text(encoding="utf-8")
  ver = version.lstrip("v")
  # match header line like: ## [0.1.3] - 2025-08-30  (or ## 0.1.3 - ...)
  header_re = re.compile(rf"^##\s*\[?{re.escape(ver)}\]?(?:\s*-\s*.*)?\s*$", re.MULTILINE)
  m = header_re.search(text)
  if not m:
    return ""
  start = m.start()
  # find next "## " header after start
  next_header_re = re.compile(r"^##\s+", re.MULTILINE)
  next_m = next_header_re.search(text, m.end())
  end = next_m.start() if next_m else len(text)
  return text[start:end].strip()


@task
def gh_release(ctx):
  """Create GitHub release using GitHub CLI - automatically detects tag"""
  result = ctx.run("git describe --tags --abbrev=0", hide=True)
  tag = result.stdout.strip()

  print(f"Creating GitHub release for tag: {tag}")

  changelog_path = Path("CHANGELOG.md")
  changelog_body = _changelog_section_for_version(changelog_path, tag)

  ctx.run("git push origin --tags", pty=True)
  if changelog_body:
    # write a temp notes file and pass --notes-file so only the version section is used
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".md") as tf:
      tf.write(changelog_body)
      notes_file = tf.name
    try:
      ctx.run(f"gh release create {tag} --title '{tag}' --notes-file {notes_file}", pty=True)
    finally:
      try:
        os.remove(notes_file)
      except OSError:
        pass
  else:
    print(f"Warning: no changelog section found for version '{tag}'. Falling back to generated notes.")
    ctx.run(f"gh release create {tag} --title '{tag}' --generate-notes", pty=True)


@task
def build_release(ctx, part: str = "patch", publish: bool = False):
  """Build a release with automatic version bumping and tagging.

  Args:
      part: Version part to bump (patch, minor, major). Default: patch
  """
  print(f"Building release with {part} version bump...")
  build_clean(ctx)
  ctx.run(f"bump-my-version bump {part}", pty=True)
  print("Building package...")
  ctx.run("python -m build --no-isolation", pty=True)
  print(f"Release built successfully with {part} version bump!")

  if publish:
    import glob

    wheel_files = glob.glob("dist/*.whl")
    tarball_files = glob.glob("dist/*.tar.gz")
    package_files = wheel_files + tarball_files

    if package_files:
      files_str = " ".join(package_files)
      ctx.run(f"twine upload {files_str}", pty=True)
    else:
      print("No package files found to upload")
