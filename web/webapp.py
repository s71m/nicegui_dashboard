from nicegui import ui, app
from fastapi import Request
import importlib
from components.pageinfo import PageInfo
from components.pagemanager import pagemanager

from header import create_menu, reload_modules
from loguru import logger

def webapp():
    app.add_static_files('/static', 'web/static')

    @ui.page('/{path:path}')
    async def dynamic_module_page(request: Request):


        path = request.url.path.strip('/')
        venue = path.split('/')[0] if '/' in path else None
        route = f'/{path}'

        pages = pagemanager.get_pages()
        pageinfo: PageInfo = pages.get(route)
        # logger.debug(pageinfo)

        if pageinfo is not None:
            module = None
            try:
                module = importlib.import_module(pageinfo.modulepath)
                if hasattr(module, pageinfo.classname):
                    ModuleClass = getattr(module, pageinfo.classname)
                    ModuleClass(pageinfo=pageinfo, request=request)
                else:
                    error_msg = f"Class {pageinfo.classname} not found in module"
                    logger.error(error_msg)
                    any_page(route, error_msg)
            except Exception as e:
                error_msg = f"Error instantiating {'unknown module' if module is None else module}\n {pageinfo}: \n{str(e)}"
                logger.error(error_msg)
                any_page(route, error_msg)
        else:
            any_page(route)

    @ui.page('/')
    def any_page(route, error_message=None):
        ui.add_head_html('''
            <link rel="stylesheet" href="/static/header.css">
        ''')
        with ui.header():
            with ui.row().classes('items-center'):
                ui.label("/").classes('text-white text-xl font-bold').style('width: 350px;')
                ui.html(create_menu())
                # Right side - Module controls
                with ui.row().classes('gap-2'):
                    ui.button(icon='sync', on_click=reload_modules).props(
                        'flat color=white')
        with ui.card().classes('p-4'):
            if error_message:
                ui.label(error_message).classes('text-red-500')
            else:
                ui.label(f"Page not found: {route}").classes('text-red-500')


def webapp_shutdown():
    app.storage.clear()
    app.shutdown()
    logger.debug('SIGINT received, aborting ...')