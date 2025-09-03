def clean_text(text):
    """
    Clean the input text by removing unnecessary whitespace and formatting.
    
    Args:
        text (str): The text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    return ' '.join(text.split())

def validate_file(file_path):
    """
    Validate the existence and readability of a file.
    
    Args:
        file_path (str): The path to the file to validate.
        
    Returns:
        bool: True if the file is valid, False otherwise.
    """
    import os
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def get_file_timestamp(file_path):
    """
    Get the last modified timestamp of a file.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        float: The last modified timestamp.
    """
    import os
    return os.path.getmtime(file_path) if validate_file(file_path) else None