from dataclasses import dataclass


@dataclass
class PageInfo:
    """Data class to hold page metadata"""
    route: str
    modulepath: str
    classname: str
    display: str

    @property
    def folder(self) -> str:
        """Get the folder name from the route"""
        parts = self.route.strip('/').split('/')
        return 'pages_root' if len(parts) == 1 else parts[0]
