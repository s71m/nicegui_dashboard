
Project Structure:  `nicegui_dashboard`

----------

utils/

-   Utility modules for reusable functionality.
    -   common/
        -   `decorators.py`: Defines reusable decorators for wrapping or enhancing functions or classes.
        -   `registry.py`: Handles a registry for tracking components or modules dynamically.

----------

web/

-   Core application logic, templates, and configurations.
    -   `app.py`: Main entry point for the application.
    -   `header.py`: Defines the UI layout or functionality for the application's header.
    -   `pageconf.yaml`: YAML configuration file for page settings.
    -   `pagetemplate.py`: Base template for creating pages with a common structure.

web/components/

-   Reusable components for building pages.
    -   `modulereloader.py`: Handles reloading of modules for dynamic updates during development without restarting server.
    -   `pageconf.py`: Manages page configuration in YAML configuration file.
    -   `pageinfo.py`: Provides metadata about page.
    -   `pagemanager.py`: Create page structure {folder}/{module}, handles page routing.

web/pages/cards

-   `cards_page.py`: Implements a page displaying cards (e.g., grid or list).
-   `cards_polars_page.py`: Similar to  `cards_page.py`  with additional Polars-based functionality.

web/pages/examples

-   `example_page.py`: Demonstrates how to create a new page using PageTemplate.

web/pages/tools/

-   `project_modules_page.py`: A tool-focused page for managing or visualizing project modules.

----------

web/static/

-   Static files for styling and interactivity.
    -   `drawer.js`: JavaScript for managing ui.left_drawer (sidebar) behavior.
    -   `header.css`: CSS for styling the application's header.
    -   `styles.css`: Global styles for the dashboard.
    
https://github.com/user-attachments/assets/c466f497-b046-457b-906b-b98d78024a7d

