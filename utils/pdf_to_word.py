import concurrent.futures
from pdf2docx import Converter

def convert_pdf(pdf_file, docx_file):
    convertor = Converter(pdf_file)
    convertor.convert(docx_file)
    convertor.close()

def pdf_to_word(pdf_file, docx_file):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.submit(
            convert_pdf,
            pdf_file,
            docx_file
        )