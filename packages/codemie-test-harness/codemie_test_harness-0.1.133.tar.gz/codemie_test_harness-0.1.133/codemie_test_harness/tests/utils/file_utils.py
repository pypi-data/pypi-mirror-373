def save_file(response, target_file_path):
    """
    Saves the file from the API response to the specified path.

    Args:
        response: The response object containing the file data.
        target_file_path: The path where the file will be saved.

    Returns:
        file: The saved file.
    """
    try:
        # Open the target file in write-binary mode
        with open(target_file_path, "wb") as target_file:
            target_file.write(response)
    except Exception as e:
        raise RuntimeError("Failed to write the file!") from e

    return target_file_path
