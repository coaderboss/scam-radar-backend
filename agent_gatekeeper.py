def validate_input(url: str | None, message: str | None):
    if not url and not message:
        raise ValueError("Input cannot be completely empty.")
    
    if url:
        if "." not in url or len(url) < 4:
            raise ValueError("Garbage Input Detected: Not a valid URL format.")
    
    return True