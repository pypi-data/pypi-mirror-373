import os

def get_output_path(input_path, output_path=None, default_ext=None):
    if output_path:
        return output_path
    
    base, _ = os.path.splitext(input_path)
    return base + default_ext
