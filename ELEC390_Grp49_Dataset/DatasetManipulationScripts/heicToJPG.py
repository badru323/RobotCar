import os
import pillow_heif
from pillow_heif import open_heif
from PIL import Image

pillow_heif.register_heif_opener()

input_folder = "C:/Users/User/OneDrive - Queen's University/Pictures/ELEC390_Grp49_Dataset"  # Change this to your folder path
output_folder = "Downloads/Group_Dataset/Images"  # Change this to where you want to save JPGs

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".heic"):
        heic_path = os.path.join(input_folder, filename)
        jpg_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")

        heif_image = open_heif(heic_path)
        # image = Image.frombytes(
        #     heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride
        #)
        image = heif_image.to_pillow()
        image.save(jpg_path, "JPEG")
        print(f"Converted {filename} to JPG")

print("Conversion complete!")
