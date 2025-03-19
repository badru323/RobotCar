import os
import xml.etree.ElementTree as ET

def remove_polygon(xml_file, output_file):
    """
    Remove <polygon> elements from a Pascal VOC XML file.
    The rectangular bounding boxes (<bndbox>) remain untouched.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return

    modified = False
    # Loop over each <object> in the XML file
    for obj in root.findall('object'):
        polygon = obj.find('polygon')
        if polygon is not None:
            obj.remove(polygon)
            modified = True
            print(f"Removed <polygon> element in object '{obj.find('name').text}' from {xml_file}")

    # Write out the updated XML if modified, otherwise copy original
    if modified:
        file_name = os.path.basename(xml_file)
        tree.write(output_file)
        print(f"Updated XML saved to {output_file}")
    else:
        # Optionally, copy file without changes
        tree.write(output_file)
        print(f"No <polygon> found in {xml_file}. File copied to {output_file}")

def process_directory(input_dir, output_dir):
    """
    Process all XML files in the input directory and save updated files in the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.xml'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            remove_polygon(input_file, output_file)

if __name__ == "__main__":
    # Change these paths to match your directories
    input_directory = "ELEC390_Grp49_Dataset/Grp12Dataset/annotations"   # e.g., "annotations_input"
    output_directory = "ELEC390_Grp49_Dataset/Grp12Dataset/Annotations_rect" # e.g., "annotations_output"
    process_directory(input_directory, output_directory)

