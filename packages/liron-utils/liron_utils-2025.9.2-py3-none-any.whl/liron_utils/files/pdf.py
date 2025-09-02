def merge_pdf(out, files):
	from PyPDF2 import PdfFileMerger

	h = PdfFileMerger()
	[h.append(file) for file in files]
	h.write(out)
	h.close()
