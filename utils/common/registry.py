class Registry:
    """Singleton registry for application pages"""
    _pages = {}

    @classmethod
    def clear(cls):
        """Clear the registry"""
        cls._pages = {}

    @classmethod
    def set_pages(cls, pages):
        cls._pages = pages

    @classmethod
    def get_pages(cls):
        return cls._pages