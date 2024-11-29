from nicegui import ui, app
from fastapi import Request
import importlib
from loguru import logger

from web.components.pageinfo import PageInfo
from web.components.pagemanager import pagemanager
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
    pageinfo: PageInfo = pages.get(route)

    if pageinfo is not None:
        try:
            module = importlib.import_module(pageinfo.modulepath)
            if hasattr(module, pageinfo.classname):
                ModuleClass = getattr(module, pageinfo.classname)

                ModuleClass(pageinfo=pageinfo, request=request)
            else:
                ui.label(f"Class {pageinfo.classname} not found in module").classes('text-red-500')
        except Exception as e:
            logger.error(f"Error instantiating {module}\n {pageinfo}: \n{str(e)}")
            ui.label(f"Error instantiating {module}\n {pageinfo}: \n{str(e)}").classes('text-red-500')
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
    ui.run(dark=True, reload=False)
except KeyboardInterrupt:
    app.storage.clear()
    app.shutdown()
    print("Received keyboard interrupt")
finally:
    print("Cleanup complete")