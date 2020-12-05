

def PDFMerger(output_path, input_paths):
    """ Merges all pdfs at `input_paths` and creates a unique pdf at `output_path` """
    from PyPDF2 import PdfFileWriter, PdfFileReader

    pdf_writer = PdfFileWriter()

    for path in input_paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

    with open(output_path, "wb") as fh:
        pdf_writer.write(fh)
