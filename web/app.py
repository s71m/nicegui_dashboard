
from nicegui import ui, app
from fastapi import Request
import importlib

from web.components.pagemanager import pagemanager


from loguru import logger

from web.header import create_menu


app.add_static_files('/static', 'web/static')


@ui.page('/{path:path}')
async def dynamic_module_page(request: Request):
    """
    Dynamic page that loads and instantiates a class based on URL parameters.
    Can handle both /example and /folder/module patterns
    """

    path = request.url.path.strip('/')
    route = f'/{path}'

    pages = pagemanager.get_pages()
    page_info = pages.get(route)

    if page_info is not None:
        try:
            module = importlib.import_module(page_info.modulepath)
            if hasattr(module, page_info.classname):
                ModuleClass = getattr(module, page_info.classname)

                ModuleClass(pageinfo=page_info, request=request)
            else:
                ui.label(f"Class {page_info.classname} not found in module").classes('text-red-500')
        except Exception as e:
            logger.error(f"Error instantiating {module}\n {page_info}: \n{str(e)}")
            ui.label(f"Error instantiating {module}\n {page_info}: \n{str(e)}").classes('text-red-500')
    else:
        any_page(route)


# # Main page with navigation
@ui.page('/')
def any_page(route):
    ui.add_head_html('''
        <link rel="stylesheet" href="/static/header.css">
    ''')
    with ui.header():
        with ui.row().classes('items-center'):
            ui.label("/").classes('text-white text-xl font-bold').style('width: 350px;')
            ui.html(create_menu())
    with ui.card().classes('p-4'):
        ui.label(f"Page not found: {route}").classes('text-red-500')

try:
    ui.run(dark=True, reload=False, port=8050)
except KeyboardInterrupt:
    app.storage.clear()
    app.shutdown()
    print("Received keyboard interrupt")
finally:
    print("Cleanup complete")