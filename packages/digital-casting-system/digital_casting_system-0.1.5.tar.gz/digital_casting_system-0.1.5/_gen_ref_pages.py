"""Generate API reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files


def generate_api_reference():
  """Generate API reference markdown files and navigation."""

  # Generate the auto navigation structure
  api_nav_content = []

  # Get all module directories from source
  src_path = Path("src/dcs")
  if not src_path.exists():
    print(f"Warning: Source path {src_path} does not exist")
    return

  module_dirs = [
    d for d in src_path.iterdir() if d.is_dir() and not d.name.startswith("__") and not d.name.startswith("_")
  ]

  for module_dir in sorted(module_dirs):
    module_name = module_dir.name
    api_nav_content.append(f"        * {module_name}")

    # Get Python files in this module
    py_files = [f for f in module_dir.glob("*.py") if f.stem not in ["__init__", "__main__"]]

    for py_file in sorted(py_files):
      file_stem = py_file.stem
      api_nav_content.append(f"            * [{file_stem}](api/reference/dcs/{module_name}/{file_stem}.md)")

  # Create the full SUMMARY.md content with embedded navigation
  summary_content = [
    "# Summary",
    "* [Introduction](index.md)",
    "* [Installation](user.md)",
    "* [Contribute](dev.md)",
    "* [Examples](examples/example.md)",
    "* API Reference",
    "    * [Architecture](api/api.md)",
    "    * dcs",
  ]

  # Add the auto-generated navigation
  summary_content.extend(api_nav_content)

  # Add the About section
  summary_content.extend(["* About", "    * [Author](author.md)", "    * [License](license.md)"])

  # Write the complete SUMMARY.md file
  with mkdocs_gen_files.open("SUMMARY.md", "w") as summary_file:
    summary_file.write("\n".join(summary_content))

  # Generate the actual markdown files with cleaner configuration
  for path in sorted(Path("src/dcs").rglob("*.py")):
    module_path = path.relative_to("src/dcs").with_suffix("")
    doc_path = path.relative_to("src/dcs").with_suffix(".md")
    full_doc_path = Path("api/reference/dcs", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
      continue
    elif parts[-1] == "__main__":
      continue

    if not parts:
      continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
      identifier = f"dcs.{'.'.join(parts)}"
      fd.write(f"# {identifier}\n\n")
      fd.write(f"::: {identifier}\n")
      fd.write("    options:\n")
      fd.write("      show_source: false\n")  # This will use your custom template
      fd.write("      show_root_heading: false\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

  print(f"Generated SUMMARY.md with {len(api_nav_content)} API entries")


if __name__ == "__main__":
  generate_api_reference()
