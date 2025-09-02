def is_pdf_file(file_path: str) -> bool:
    """Check if a file is a PDF file"""
    with open(file_path, "rb") as f:
        magic = f.read(5)
        return magic == b"%PDF-"
