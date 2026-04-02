A tiny script that I needed for a task so i will let it live here peacefully.

## What it does

Extracts all embedded images from a PDF file and saves them as individual PNG files. Comes with both a CLI script and a desktop GUI.

## Setup

```bash
pip install -r requirements.txt
```

**Dependencies:** Pillow, PyMuPDF, CustomTkinter

## Usage

### GUI app

```bash
python3 app.py
```

1. Click **Browse** to select a PDF file
2. Optionally change the output folder (defaults to `./extracted_images`)
3. Click **Extract Images**
4. Extracted images appear as thumbnails in the preview area

### CLI script

Edit `extract_images.py` to set your PDF path, then:

```bash
python3 extract_images.py
```

Images are saved as `image_page{page}_{index}.png` in the output folder.
