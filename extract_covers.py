#!/usr/bin/env python3
"""
Extract book covers from specific sections of tingle.html
"""

import re
import os
import shutil
from pathlib import Path

# Sections we want to extract
TARGET_SECTIONS = [
    "TINGLERS",
    "LESBIAN TINGLERS",
    "TRANS TINGLERS",
    "BISEXUAL GROUP TINGLERS",
    "GENDER FLUID AND/OR NON-BINARY TINGLERS",
    "NO SEX TINGLERS"
]

def extract_section_content(html, section_name):
    """
    Extract HTML content between a section header and the next h2 tag
    """
    # Try multiple patterns to handle variations like &nbsp; before or between words
    patterns = [
        # Exact match
        rf'<h2[^>]*>{re.escape(section_name)}.*?</h2>(.*?)(?=<h2|$)',
        # With optional &nbsp; at start
        rf'<h2[^>]*>(?:&nbsp;)?\s*{re.escape(section_name)}.*?</h2>(.*?)(?=<h2|$)',
        # With &nbsp; replaced with flexible spacing
        rf'<h2[^>]*>(?:&nbsp;)?\s*{section_name.replace(" ", r"(?:&nbsp;)?\s*")}.*?</h2>(.*?)(?=<h2|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def extract_images_from_section(section_html):
    """
    Extract all tingle_files image paths from a section of HTML
    """
    # Find all img src attributes that point to tingle_files
    pattern = r'<img[^>]+src=["\']?(tingle_files/[^"\'>\s]+)["\']?'
    matches = re.findall(pattern, section_html, re.IGNORECASE)
    return matches

def main():
    print("Reading HTML file...")
    # Read the HTML file
    with open('tingle.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    all_images = []

    # Extract images from each target section
    for section_name in TARGET_SECTIONS:
        print(f"\nProcessing section: {section_name}")
        section_html = extract_section_content(html_content, section_name)

        if section_html:
            images = extract_images_from_section(section_html)
            print(f"  Found {len(images)} images")
            all_images.extend(images)
        else:
            print(f"  WARNING: Section not found!")

    print(f"\nTotal images found: {len(all_images)}")

    # Extract unique image paths
    unique_images = list(set(all_images))
    print(f"Unique images: {len(unique_images)}")

    # Create output directory
    output_dir = Path('selected_covers')
    output_dir.mkdir(exist_ok=True)

    # Copy files
    copied = 0
    not_found = 0
    for img_path in unique_images:
        # Remove any leading slash or URL artifacts
        img_path = img_path.strip()

        source = Path(img_path)

        if source.exists():
            dest = output_dir / source.name
            shutil.copy2(source, dest)
            print(f"Copied: {source.name}")
            copied += 1
        else:
            print(f"Not found: {source}")
            not_found += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total images in target sections: {len(all_images)}")
    print(f"  Unique images: {len(unique_images)}")
    print(f"  Copied: {copied}")
    print(f"  Not found: {not_found}")
    print(f"  Output directory: {output_dir.absolute()}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
