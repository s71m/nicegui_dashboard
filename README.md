
This repository demonstrates how quickly and elegantly you can create dashboards with **NiceGUI**. After trying Streamlit, Dash, Panel, and now NiceGUI, I've found that [NiceGUI](https://nicegui.io/) is fast, intuitive, and supports many plugins.

The purpose of this repository is to provide a friendly starting point for developers who want to work with NiceGUI.

----------

## Add new page  
  
- Explore [example_page.py](web%2Fpages%2Fexamples%2Fexample_page.py) to see how a page is built.  
- Create a new folder under `web/pages/` (e.g., `new_folder`).  
- Add a `new_page.py` file with a `NewPage` class.  
- Click the "Reload" button and watch it appear automatically in the application!.  
  
----------  
  ### **How to Start**

1.  Install the required dependencies using:
    `pip install -r requirements.txt` 
    
2.  Launch the application:
    `python web/app.py` 
    
3.  Open your browser and navigate to:
    `http://localhost:8080`



### Explanation of project structure: `nicegui_dashboard`

#### **web/**

-   **`app.py`**: Main entry point for the application.
-   **`header.py`**: Defines the UI layout and functionality for the application's header.
-   **`pageconf.yaml`**: YAML configuration file for page settings.
-   **`pagetemplate.py`**: Base template for creating pages with a common structure.

----------

#### **web/components/**

-   **`modulereloader.py`**: Handles reloading of modules for dynamic updates during development without restarting the server.
-   **`pageconf.py`**: Manages page configurations stored in the YAML file.
-   **`pageinfo.py`**: Provides metadata about each page (e.g., route, name).
-   **`pagemanager.py`**: Creates the page structure (`{folder}/{module}`) and handles page routing.

----------

#### **web/pages/**

-   **`examples/example_page.py`**: Demonstrates how to create a new page using `PageTemplate`.
-   **`cards/cards_page.py`**: Implements a page displaying grid of cards.
-   **`cards/cards_polars_page.py`**: Similar to `cards_page.py` but with using Polars.
-   **`tools/project_modules_page.py`**: Visualizes currently running project modules, allowing for reloading.

----------

#### **web/static/**

-   Static files for styling and interactivity.
    -   **`drawer.js`**: JavaScript for dynamically changing the width of `ui.left_drawer` (sidebar).
    -   **`header.css`**: CSS for styling the application's header.
    -   **`styles.css`**: Global styles for the dashboard.






https://github.com/user-attachments/assets/cadec471-1204-446f-bb4e-2ad72adeebfd

## VueFlow for NiceGUI

https://github.com/user-attachments/assets/11dba36d-17fe-47e8-82b2-8f94fa83de84










