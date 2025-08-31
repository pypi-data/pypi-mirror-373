"""
Base form classes for Raystack framework.
"""

class Form:
    """
    Base form class for handling form data.
    """
    
    def __init__(self, data=None, files=None):
        self.data = data or {}
        self.files = files or {}
        self.errors = {}
    
    def is_valid(self):
        """
        Check if the form is valid.
        Override this method in subclasses.
        """
        return len(self.errors) == 0
    
    def clean(self):
        """
        Clean and validate form data.
        Override this method in subclasses.
        """
        pass
