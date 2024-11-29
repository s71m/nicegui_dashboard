import os
from pathlib import Path
from typing import Dict
from loguru import logger

from utils.common.registry import Registry
from web.components.pageinfo import PageInfo

CURRENT_DIR = Path(__file__).parent.parent
PAGES = "pages"


class PageManager:
    def __init__(self):
        self.pages_dir = CURRENT_DIR / PAGES
        # Registry.clear()  # Clear registry on init

    def _create_page_info(self, route: str, modulepath: str) -> PageInfo:
        """Create PageInfo instance"""
        classname = modulepath.split('.')[-1].title().replace('_', '')
        display = modulepath.split('.')[-1].replace('_', ' ').title().replace(' Page', '')

        return PageInfo(
            route=route,
            modulepath=modulepath,
            classname=classname,
            display=display
        )

    def _scan_pages(self) -> Dict[str, PageInfo]:
        """
        Walks through a directory tree, finds Python files, and generates a dictionary of page routes and PageInfo objects.

        Returns:
            dict: A dictionary with page routes as keys and PageInfo instances as values in the following format:
            {
                '/': PageInfo(route='/', modulepath='web.pages.home_page', classname='HomePage', display='Home PageTemplate'),
                '/contact': PageInfo(route='/contact', modulepath='web.pages.contact_page', classname='ContactPage', display='Contact PageTemplate'),
                '/ex/custom': PageInfo(route='/ex/custom', modulepath='web.pages.ex.custom_page', classname='CustomPage', display='Custom PageTemplate')
            }
        """
        pages = {}
        priority_folders = ['binance', 'tinkoff']

        for root, dirs, files in os.walk(self.pages_dir):
            relative_path = Path(root).relative_to(self.pages_dir)

            for file in files:
                if not file.endswith('.py'):
                    continue

                file_path = Path(root) / file
                modulename = file_path.stem
                modulepath = str(file_path.relative_to(CURRENT_DIR.parent)).replace(os.sep, '.').replace('.py', '')

                base_name = modulename.replace('_page', '')
                if str(relative_path) == '.':
                    route = f"/{base_name}"
                else:
                    route = f"/{relative_path}/{base_name}"

                pages[route] = self._create_page_info(route, modulepath)

        # Sort pages
        return dict(
            sorted(pages.items(), key=lambda x: (
                x[1].folder not in priority_folders,
                x[1].folder == 'pages_root',
                x[1].folder,
                x[0]
            ))
        )

    def get_pages(self):
        """Retrieve pages from the Registry, initializing them if necessary."""
        pages = Registry.get_pages()
        if not pages:  # Check if pages is empty
            # logger.debug("Scan pages")
            Registry.set_pages(self._scan_pages())
            pages = Registry.get_pages()

        return pages

pagemanager = PageManager()