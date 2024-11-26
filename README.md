
This repository demonstrates how quickly and elegantly you can create dashboards with **NiceGUI**. After trying Streamlit, Dash, Panel, and now NiceGUI, I've found that [NiceGUI](https://nicegui.io/) is fast, intuitive, and supports many plugins.

The purpose of this repository is to provide a friendly starting point for developers who want to work with NiceGUI.

----------

## Get Started

-   Explore [example_page.py](web%2Fpages%2Fexamples%2Fexample_page.py) to see how a page is built.
-   Create a new folder under `web/pages/` (e.g., `new_folder`).
-   Add a `new_page.py` file with a `NewPage` class.
-   Click the "Reload" button and watch it appear automatically in the application!.

----------



### Short Explanation of Project Structure: `nicegui_dashboard`

#### **web/**

-   Core application logic, templates, and configurations.
    -   **`app.py`**: Main entry point for the application.
    -   **`header.py`**: Defines the UI layout and functionality for the application's header.
    -   **`pageconf.yaml`**: YAML configuration file for page settings.
    -   **`pagetemplate.py`**: Base template for creating pages with a common structure.

----------

#### **web/components/**

-   Reusable components for building pages.
    -   **`modulereloader.py`**: Handles reloading of modules for dynamic updates during development without restarting the server.
    -   **`pageconf.py`**: Manages page configurations stored in the YAML file.
    -   **`pageinfo.py`**: Provides metadata about each page (e.g., route, name).
    -   **`pagemanager.py`**: Creates the page structure (`{folder}/{module}`) and handles page routing.

----------

#### **web/pages/cards/**

-   **`cards_page.py`**: Implements a page displaying grid of cards.
-   **`cards_polars_page.py`**: Similar to `cards_page.py` but with using Polars.

----------

#### **web/pages/examples/**

-   **`example_page.py`**: Demonstrates how to create a new page using `PageTemplate`.

----------

#### **web/pages/tools/**

-   **`project_modules_page.py`**: Visualizes currently running project modules, allowing for reloading.

----------

#### **web/static/**

-   Static files for styling and interactivity.
    -   **`drawer.js`**: JavaScript for dynamically changing the width of `ui.left_drawer` (sidebar).
    -   **`header.css`**: CSS for styling the application's header.
    -   **`styles.css`**: Global styles for the dashboard.





https://github.com/user-attachments/assets/c466f497-b046-457b-906b-b98d78024a7d

