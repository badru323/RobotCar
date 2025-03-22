import os 
from PIL import Image

input_folder = "ELEC390_Grp49_Dataset/Grp12Dataset/Roboflow_dump/train" # Update this path
output_folder = "ELEC390_Grp49_Dataset/Dataset320x320/Annotations"

#os.makedirs(output_folder, exist_ok = True)

xml_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(".xml")])

for idx, filename in enumerate(xml_files, start = 439):
    input_path = os.path.join(input_folder, filename)
    try:
        
        # create the proper file names
        new_filename = f"team49_{idx:03}.xml"
        output_path = os.path.join(output_folder, new_filename)
            
        os.rename(input_path, output_path)
        print(f"Processed {filename} -> {new_filename}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("All XML files have been renamed and moved.")
