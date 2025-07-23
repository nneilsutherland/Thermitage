import exifread

def print_exif_tags(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)

    print(f"\n[INFO] EXIF tags found in {image_path}:")
    for tag in tags:
        print(f"{tag} : {tags[tag]}")

# Test it:
print_exif_tags('/Users/neilsutherland/Library/CloudStorage/OneDrive-TheUniversityofNottingham/Projects/VSC_VisualStudioCode/Thermitage/data/RAD_RadCamCal_UK/Vignetting/RadTIFF/14-25-28-269-radiometric.tiff')
