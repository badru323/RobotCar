import os 
from PIL import Image

input_folder = "ELEC390_Grp49_Dataset/Dataset320x320/Roboflow_dump/train" # Update this path
output_folder = "ELEC390_Grp49_Dataset/Dataset320x320/Images"

os.makedirs(output_folder, exist_ok = True)

jpg_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(".jpg")])

for idx, filename in enumerate(jpg_files, start = 1):
    input_path = os.path.join(input_folder, filename)
    try:
        with Image.open(input_path) as img:
            # resize the image to 640x640 pixels
            # resized_img = img.resize((640,640), resample=Image.Resampling.LANCZOS)
            # create the proper file names
            new_filename = f"team49_{idx:03}.jpg"
            output_path = os.path.join(output_folder, new_filename)
            # Save the resized image as JPG
            img.convert("RGB").save(output_path, "JPEG")
            print(f"Processed {filename} -> {new_filename}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("All images have been resized and renamed.")
