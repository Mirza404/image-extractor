import fitz
import io
import os
from PIL import Image

def extract_images_from_pdf(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_document = fitz.open(pdf_path)
    image_count = 0
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            image = Image.open(io.BytesIO(image_bytes))
            
            image_filename = os.path.join(output_folder, f"image_page{page_num+1}_{image_index+1}.png")
            image.save(image_filename, format="PNG")
            
            print(f"Saved: {image_filename}")
            image_count += 1
            
    print(f"Total {image_count} images extracted.")

# Usage
pdf_file = "namjestaj.pdf" # Replace with your PDF file name
output_dir = "extracted_images"

extract_images_from_pdf(pdf_file, output_dir)
