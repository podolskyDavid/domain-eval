from docling.document_converter import DocumentConverter

converter = DocumentConverter()

def parse_pitch_deck(source_path: str) -> str:
    """
    Convert a pitch deck document to markdown format.
    
    Args:
        source_path (str): Local file path or URL to the document
        
    Returns:
        str: The document content in markdown format
    """

    result = converter.convert(source_path)
    return result.document.export_to_markdown()

if __name__ == "__main__":
    # Example usage
    source = "app/data/test1.pdf"
    markdown_content = parse_pitch_deck(source)
    print(markdown_content)