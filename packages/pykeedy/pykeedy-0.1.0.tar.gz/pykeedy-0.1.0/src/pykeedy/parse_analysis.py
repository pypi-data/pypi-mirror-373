import json
import os


def analysis_to_md(
    manifest_path: str = "manifest.json",
    output_markdown_fname: str = "analysis_report.md",
    md_to_imgs_path: str = "./",
    total_width: int = 1800,
) -> None:
    """
    Generate a markdown file from a manifest.json that lists analysis images.

    Args:
        manifest_path: Path to the manifest.json file
        output_markdown_path: Path where the markdown file will be written
        image_path: Path prefix for accessing images in the markdown
        total_width: Total width to distribute among per-manuscript images

    Raises:
        FileNotFoundError: If manifest.json doesn't exist
        ValueError: If required files are missing
        KeyError: If manifest structure is invalid
    """

    # Check for and load manifest.json
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Extract manuscript names and analysis structure
    try:
        manuscripts = manifest["analysis"]["manuscripts"]
        cross_manuscript = manifest["analysis"]["cross_manuscript"]
        per_manuscript = manifest["analysis"]["per_manuscript"]
    except KeyError as e:
        raise KeyError(f"Invalid manifest structure: missing key {e}")

    # Generate all expected PNG filenames
    expected_files = []

    # Add cross-manuscript files
    expected_files.extend(cross_manuscript)

    # Add per-manuscript files (substitute <name> with each manuscript name)
    for analysis_type, pattern_list in per_manuscript.items():
        for pattern in pattern_list:
            for manuscript in manuscripts:
                filename = pattern.replace("<name>", manuscript)
                expected_files.append(filename)

    # Check that all files exist
    missing_files = []
    for filename in expected_files:
        # Remove the image_path prefix if it's already in the filename for checking
        file_to_check = filename
        if not filename.startswith(md_to_imgs_path):
            file_to_check = os.path.join(os.path.dirname(manifest_path), filename)

        if not os.path.exists(file_to_check):
            missing_files.append(filename)

    if missing_files:
        raise ValueError(f"Missing files: {', '.join(missing_files)}")

    # Create linear list of filename patterns for markdown generation
    markdown_patterns = []

    # Add cross-manuscript patterns
    markdown_patterns.extend(cross_manuscript)

    # Add per-manuscript patterns (keeping <name> placeholder)
    for analysis_type, pattern_list in per_manuscript.items():
        markdown_patterns.extend(pattern_list)

    # Generate markdown content
    markdown_lines = []

    breaks = 5

    # Process cross-manuscript images first
    for pattern in cross_manuscript:
        image_src = os.path.join(md_to_imgs_path, pattern).replace("\\", "/")
        markdown_lines.append('<p float="left">')
        markdown_lines.append(f'  <img src="{image_src}" width="{total_width}" />')
        markdown_lines.append("</p>")
    markdown_lines.append("<br></br>\n" * breaks)
    # Process per-manuscript images grouped by type
    num_manuscripts = len(manuscripts)
    individual_width = (
        total_width // num_manuscripts if num_manuscripts > 0 else total_width
    )

    for analysis_type, pattern_list in per_manuscript.items():
        for pattern in pattern_list:
            markdown_lines.append('<p float="left">')

            for manuscript in manuscripts:
                filename = pattern.replace("<name>", manuscript)
                image_src = os.path.join(md_to_imgs_path, filename).replace("\\", "/")
                markdown_lines.append(
                    f'  <img src="{image_src}" width="{individual_width}" />'
                )

            markdown_lines.append("</p>")
            markdown_lines.append("<br></br>\n" * breaks)

    # Write markdown file
    with open(output_markdown_fname, "w") as f:
        f.write("\n".join(markdown_lines))

    print(f"Markdown file generated: {output_markdown_fname}")
