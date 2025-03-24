import os
import xml.etree.ElementTree as ET
import re

# Set the path to the folder containing the annotation XML files
annotation_dir = "ELEC390_Grp49_Dataset/Team31/good_dataset/Annotations/"  # Update this path as needed

# Get a sorted list of XML files
xml_files = sorted([f for f in os.listdir(annotation_dir) if f.endswith(".xml")])

# Iterate over the sorted XML files and use an index for renaming
for idx, xml_file in enumerate(xml_files, start=985):
    xml_path = os.path.join(annotation_dir, xml_file)

    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find the <filename> tag
    filename_tag = root.find("filename")
    if filename_tag is not None:
        old_filename = filename_tag.text  # e.g., "team12_179.jpg"

        # Debugging: Print the old filename
        print(f"Old filename: {old_filename}")

        # Format the new filename as team49_idx (e.g., team49_001.jpg)
        new_filename = f"team49_{idx:04d}.jpg"  # E.g., "team49_001.jpg"
        filename_tag.text = new_filename  # Update XML

    # Find the <path> tag and update it
    path_tag = root.find("path")
    if path_tag is not None:
        path_tag.text = new_filename  # Ensure <path> is updated to match new filename

    # Save the updated XML file
    tree.write(xml_path)
    print(f"Updated {xml_file}: {old_filename} -> {new_filename}")
