from PyPDF2 import PdfFileReader, PdfFileWriter #pip install PyPDF2
import os, sys, tkinter as tk
from tkinter import ttk, filedialog
"""Extract some pages from a PDF"""

SUFFIX = "_extract"
HELP_TEXT = f"""The resulting file will be suffixed with "{SUFFIX}".
The selection of pages is done in the form "2:5, 7, 12, 15:13", meaning pages 2 to 5, 7, 12, and 15 to 13"""

def intervalText_to_list(text, uniqueAndsorted = False): #Transforms a text like "2:4, 6, 7:5" in a list [2, 3, 4, 6, 7, 6, 5]
    pages_groups = text.split(",")
    pages = []
    for p in pages_groups:
        if p.strip():
            try:
                pages_int = p.split(":")
                if len(pages_int) == 1:
                    pages += [int(pages_int[0])]
                elif len(pages_int) == 2:
                    mini, maxi = [int(i) for i in pages_int]
                    sign = 1 if mini<maxi else -1 #if mini>maxi, range is in reverse order
                    pages += list(range(mini, maxi+sign, sign))
                else:
                    raise BaseException
            except:
                raise BaseException(f"ERROR: Can't interprete {p}")
    if uniqueAndsorted: #Sort and remove duplicates
        return set(pages)
    return pages

def add_file_suffix(path, suffix):
    root, ext = os.path.splitext(path)
    return root + suffix + ext

def extract_PDF_pages(pdf_path, pages_list):
    source_pdf = PdfFileReader(open(pdf_path, 'rb'))
    pdf_writer = PdfFileWriter()
    for p in pages_list:
        pdf_writer.addPage(source_pdf.getPage(p-1))
    target_pdf_path = add_file_suffix(pdf_path, SUFFIX)
    #TBD: check if already exists
    with open(target_pdf_path, mode="wb") as output_pdf:
        pdf_writer.write(output_pdf)

class window(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pdf_path = None
        self.pages_text = ""

        self.pages_var = tk.StringVar()
        self.pages_var.trace_add("write", self.selection_modified) #TBD

        self.master.title("Extract pages from PDF")
        #help_label = ttk.Label(text=HELP_TEXT).pack()

        fm_file = ttk.Frame()
        ttk.Button(fm_file, text="Choose PDF", command=self.choose_file).pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.file_label = ttk.Label(fm_file, text="")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        fm_file.pack(side=tk.TOP, fill=tk.X)

        fm_page = ttk.Frame()
        ttk.Label(fm_page, text="Enter pages").pack(side=tk.LEFT)
        ttk.Entry(fm_page, textvariable=self.pages_var).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.extract_button = ttk.Button(fm_page, text="Extract pages", command=self.extract_pages)
        self.extract_button.pack(side=tk.LEFT, anchor=tk.E)
        self.extract_button.state(['disabled'])
        fm_page.pack(side=tk.TOP, fill=tk.X)

        self.status_label = ttk.Label(text="")
        self.status_label.pack(side=tk.TOP, fill=tk.X)

    def choose_file(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        self.file_label['text'] = os.path.basename(self.pdf_path)
        self.check_inputs()
        self.status_label['text'] = ""

    def extract_pages(self):
        try:
            pages = intervalText_to_list(self.pages_text)
        except BaseException as e:
            b = sys.exc_info()
            exctype, value = sys.exc_info()[:2]
            self.status_label['text'] = value
            self.extract_button.state(['disabled'])
        else:
            extract_PDF_pages(self.pdf_path, pages)
            target_name = add_file_suffix(os.path.basename(self.pdf_path), SUFFIX)
            self.status_label['text'] = f"Done. Check the new file {target_name}."

    def selection_modified(self, a, b, c):
        self.pages_text = self.pages_var.get()
        self.check_inputs()
        self.status_label['text'] = ""
        pass

    def check_inputs(self):
        if self.pages_text != "" and self.pdf_path:
            self.extract_button.state(['!disabled'])
        else:
            self.extract_button.state(['disabled'])

def main():
    window().mainloop()

if __name__ == '__main__':
    main()