class InputFileException(Exception):
    """
    Exception raised for errors in the input map files.
    
    This exception is used when there are issues with reading or processing
    map input files, such as unsupported file formats or corrupted data.
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a custom message.

        Args:
            message: Detailed description of the error
        """
        self.message = message
        super().__init__(self.message)
