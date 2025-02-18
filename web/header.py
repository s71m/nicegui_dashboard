from nicegui import ui
from components.modulereloader import ModuleReloader

from components.pagemanager import pagemanager


reloader = ModuleReloader()

def create_menu():
    # Group pages by folder
    grouped_pages  = {}
    for route, page_info in pagemanager.get_pages().items():
        folder = page_info.folder
        if folder not in grouped_pages:
            grouped_pages[folder] = []
        grouped_pages[folder].append((route, page_info))

    # Create the menu using HTML for better hover control
    menu_html = '<div class="menu-container">'

    # Add folder dropdowns
    for folder, pages in grouped_pages.items():
        if folder != 'pages_root':
            menu_html += f'''
                <div class="dropdown-container">
                    <button class="dropdown-button">{folder.title()}/</button>
                    <div class="dropdown-content">
            '''

            for route, page_info in pages:
                menu_html += f'''
                    <a href="{page_info.route}" class="dropdown-link">
                        {page_info.display}
                    </a>
                '''

            menu_html += '''
                    </div>
                </div>
            '''

    # Add root pages last
    if 'pages_root' in grouped_pages:
        for route, page_info in grouped_pages['pages_root']:
            menu_html += f'''
                <button class="dropdown-button"><a href="{page_info.route}" class="menu-link">
                    {page_info.display}
                </a></button>
            '''

    menu_html += '</div>'

    # Add the menu to the UI
    return menu_html

def _organize_pages_by_folder(pages: dict) -> dict:
    """
    Organize pages by folder for the dropdown menus.
    Returns a dictionary with folder names as keys and lists of PageInfo as values.
    """
    folder_pages = {}
    for route, page_info in pages.items():
        # Skip if route doesn't match expected pattern
        if not route.startswith('/'):
            continue

        # Split route into parts and get folder name
        parts = route.split('/')
        if len(parts) >= 3:  # Should have ['', folder, page]
            folder = parts[1]  # Get folder name
            if folder not in folder_pages:
                folder_pages[folder] = []
            folder_pages[folder].append(page_info)

    # Sort pages within each folder by display name
    for folder in folder_pages:
        folder_pages[folder].sort(key=lambda x: x.display)

    return dict(sorted(folder_pages.items()))  # Return sorted by folder name

def reload_modules():

    try:
        modules_reloaded = reloader.reload_project_modules()
        ui.notify(f'Successfully reloaded {len(modules_reloaded)} modules', type='positive')
    except Exception as e:
        ui.notify(f'Error reloading dependencies: {str(e)}', type='negative')

    finally:
        ui.navigate.reload()