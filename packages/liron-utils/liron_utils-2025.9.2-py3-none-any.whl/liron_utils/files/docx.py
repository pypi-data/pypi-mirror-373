# TODO make/edit Word documents

def load_docx(file):
	import docx

	doc = docx.Document(file)
	return doc
