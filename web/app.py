import os

from nicegui import ui, app
import importlib

from web.components.pagemanager import pagemanager


from loguru import logger

from web.header import create_menu

print(os.getenv('PYTHONPATH'))

app.add_static_files('/static', 'web/static')

@ui.page('/{folder}/{module}')
def dynamic_page(folder: str, module: str):
    """
    Dynamic page that loads and instantiates a class based on URL parameters.
    Example URL: /examples/example or /cards/cards_polars
    """


    # Construct the route path
    route = f'/{folder}/{module}'

    # Get page info from Registry
    pages = pagemanager.get_pages()
    page_info = pages.get(route)

    if page_info is not None:
        try:
            # Import the module using the module path from Registry
            module = importlib.import_module(page_info.modulepath)

            # Get the class using the classname from Registry
            if hasattr(module, page_info.classname):
                ModuleClass = getattr(module, page_info.classname)
                # Instantiate the class
                ModuleClass(page_info)
            else:
                ui.label(f"Class {page_info.classname} not found in module").classes('text-red-500')
        except Exception as e:
            logger.error(f"Error instantiating {module}\n {page_info}: \n{str(e)}")
            ui.label(f"Error instantiating {module}\n {page_info}: \n{str(e)}").classes('text-red-500')
    else:
        ui.label(f"Page not found: {route}").classes('text-red-500')


# Main page with navigation
@ui.page('/')
def main_page():
    ui.add_head_html('''
        <link rel="stylesheet" href="/static/header.css">
    ''')
    with ui.header():
        with ui.row().classes('items-center'):
            ui.label("/").classes('text-white text-xl font-bold').style('width: 350px;')
            ui.html(create_menu())
    with ui.card().classes('p-4'):
        ui.label('Welcome')

ui.run(dark=True, reload=False)