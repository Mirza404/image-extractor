import customtkinter as ctk
import fitz
import io
import os
import threading
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox


class ImageExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Image Extractor")
        self.geometry("720x520")
        self.minsize(600, 450)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.pdf_path = ctk.StringVar()
        self.output_path = ctk.StringVar(value=os.path.join(os.getcwd(), "extracted_images"))
        self.thumbnails = []

        self._build_ui()

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(main, text="PDF Image Extractor", font=("", 22, "bold")).pack(pady=(0, 16))

        # PDF file picker
        pdf_frame = ctk.CTkFrame(main)
        pdf_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(pdf_frame, text="PDF File:", width=90, anchor="w").pack(side="left", padx=(12, 4), pady=10)
        ctk.CTkEntry(pdf_frame, textvariable=self.pdf_path, placeholder_text="Select a PDF file...").pack(
            side="left", fill="x", expand=True, pady=10
        )
        ctk.CTkButton(pdf_frame, text="Browse", width=80, command=self._browse_pdf).pack(
            side="right", padx=(8, 12), pady=10
        )

        # Output folder picker
        out_frame = ctk.CTkFrame(main)
        out_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(out_frame, text="Output:", width=90, anchor="w").pack(side="left", padx=(12, 4), pady=10)
        ctk.CTkEntry(out_frame, textvariable=self.output_path, placeholder_text="Output folder...").pack(
            side="left", fill="x", expand=True, pady=10
        )
        ctk.CTkButton(out_frame, text="Browse", width=80, command=self._browse_output).pack(
            side="right", padx=(8, 12), pady=10
        )

        # Extract button + progress
        action_frame = ctk.CTkFrame(main, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 8))
        self.extract_btn = ctk.CTkButton(
            action_frame, text="Extract Images", height=38, font=("", 14, "bold"), command=self._start_extract
        )
        self.extract_btn.pack(side="left")
        self.status_label = ctk.CTkLabel(action_frame, text="", font=("", 12))
        self.status_label.pack(side="left", padx=12)

        self.progress = ctk.CTkProgressBar(main)
        self.progress.pack(fill="x", pady=(0, 12))
        self.progress.set(0)

        # Preview area
        ctk.CTkLabel(main, text="Preview", font=("", 13, "bold"), anchor="w").pack(fill="x")
        self.preview_frame = ctk.CTkScrollableFrame(main, height=200)
        self.preview_frame.pack(fill="both", expand=True, pady=(4, 0))

    def _browse_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if path:
            self.pdf_path.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)

    def _start_extract(self):
        pdf = self.pdf_path.get().strip()
        output = self.output_path.get().strip()
        if not pdf:
            messagebox.showwarning("No file", "Please select a PDF file.")
            return
        if not os.path.isfile(pdf):
            messagebox.showerror("Not found", f"File not found:\n{pdf}")
            return
        self.extract_btn.configure(state="disabled")
        self.progress.set(0)
        self._clear_preview()
        threading.Thread(target=self._extract, args=(pdf, output), daemon=True).start()

    def _extract(self, pdf_path, output_folder):
        try:
            os.makedirs(output_folder, exist_ok=True)
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            image_count = 0
            extracted = []

            for page_num in range(total_pages):
                page = doc[page_num]
                images = page.get_images(full=True)
                for idx, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    pil_img = Image.open(io.BytesIO(image_bytes))
                    filename = f"image_page{page_num + 1}_{idx + 1}.png"
                    filepath = os.path.join(output_folder, filename)
                    pil_img.save(filepath, format="PNG")

                    image_count += 1
                    extracted.append((filepath, pil_img.copy()))

                progress = (page_num + 1) / total_pages
                self.after(0, self._update_progress, progress, f"Page {page_num + 1}/{total_pages}")

            doc.close()
            self.after(0, self._extraction_done, image_count, extracted)
        except Exception as e:
            self.after(0, self._extraction_error, str(e))

    def _update_progress(self, value, text):
        self.progress.set(value)
        self.status_label.configure(text=text)

    def _extraction_done(self, count, extracted):
        self.progress.set(1)
        self.status_label.configure(text=f"Done! {count} image{'s' if count != 1 else ''} extracted.")
        self.extract_btn.configure(state="normal")
        self._show_previews(extracted)

    def _extraction_error(self, error):
        self.status_label.configure(text="Error!")
        self.extract_btn.configure(state="normal")
        messagebox.showerror("Error", f"Extraction failed:\n{error}")

    def _clear_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()

    def _show_previews(self, extracted):
        self._clear_preview()
        cols = 5
        for i, (filepath, pil_img) in enumerate(extracted):
            pil_img.thumbnail((120, 120))
            tk_img = ImageTk.PhotoImage(pil_img)
            self.thumbnails.append(tk_img)

            cell = ctk.CTkFrame(self.preview_frame)
            cell.grid(row=i // cols, column=i % cols, padx=6, pady=6)

            label = ctk.CTkLabel(cell, image=tk_img, text="")
            label.pack(padx=4, pady=(4, 0))

            name = os.path.basename(filepath)
            ctk.CTkLabel(cell, text=name, font=("", 10), wraplength=110).pack(pady=(0, 4))


if __name__ == "__main__":
    app = ImageExtractorApp()
    app.mainloop()
