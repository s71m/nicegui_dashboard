from pathlib import Path
from loguru import logger
from omegaconf import OmegaConf
from nicegui import ui
from typing import Callable


from utils.common.decorators import singleton

PAGECONF_FILENAME = Path(__file__).parent.parent / "pageconf.yaml"

# Simple default settings dict
PAGECONF_DEFAULT = {
    "sidebar_width": 350,
    "sidebar_cards_grid_height": 500,
    "cards_per_row": 3,
    "card_height": 450,
    "date_filter": {
        "enabled": True,
        "default_end": "2024-10-10",
        "days_before": 10
    }
}


@singleton
class GlobalPageConf:
    """Singleton class for managing page configurations globally using NiceGUI dialog."""

    def __init__(self):
        """Initialize configuration if not yet initialized."""
        self.initialize_pageconf()
        self._conf = OmegaConf.load(PAGECONF_FILENAME)
        self._conf_default = self._conf.get("default", PAGECONF_DEFAULT)


    def show_notification(self, message: str, type: str = 'positive', duration: int = 5000):
        """Helper method to show notifications with consistent styling."""
        ui.notify(
            message,
            position='bottom-right',
            type=type,
            multi_line=True,
            close_button='Dismiss',
            timeout=duration,
            classes='text-subtitle1'
        )

    def initialize_pageconf(self):
        """Ensure the configuration file exists and initialize with defaults if it is empty."""
        pageconf_path = Path(PAGECONF_FILENAME)
        if not pageconf_path.exists():
            error_message = f"Settings file '{PAGECONF_FILENAME}' not found: {pageconf_path.resolve().parent}"
            logger.error(error_message)
            self.show_notification(error_message, 'negative', 10000)

            return

        if pageconf_path.stat().st_size == 0:
            default_conf = OmegaConf.create({"default": PAGECONF_DEFAULT})
            OmegaConf.save(default_conf, PAGECONF_FILENAME)
            logger.info(f"Initialized {PAGECONF_FILENAME} with default settings")
            self.show_notification(f"Initialized {PAGECONF_FILENAME} with default settings", 'info')

    def load(self, route):
        """Retrieve the full configuration for a specific route."""
        return self._conf.get(route, self._conf_default)

    def save(self, route, yaml_str):
        """Save the configuration for a specific route using a YAML string."""
        try:
            if not yaml_str.strip():
                self.delete(route)
            else:
                conf = OmegaConf.create(yaml_str)
                self._conf[route] = conf
                OmegaConf.save(self._conf, PAGECONF_FILENAME)
        except Exception as e:
            error_message = f"{route} Error message: {str(e)}"
            logger.error(error_message)
            self.show_notification(error_message, 'negative', 8000)

            raise

    def delete(self, route):
        """Delete the configuration entry for a specified route."""
        if route in self._conf:
            del self._conf[route]
            OmegaConf.save(self._conf, PAGECONF_FILENAME)
            logger.info(f"Deleted settings for '{route}'")
            self.show_notification(f"Deleted settings '{route}'", 'info')

    def get(self, route, key):
        """Retrieve a specific setting for a route."""
        conf = self.load(route)
        logger.debug(f"Configuration for '{route}': {conf}")

        value = conf.get(key, self._conf_default.get(key))

        # Raise error if value is None
        if value is None:
            expected_yaml = OmegaConf.to_yaml({route: {key: "value"}})
            error_message = (
                f"Configuration error: Required setting '{key}' for '{route}' must not be None.\n"
                f"Expected YAML format:\n{expected_yaml}"
            )

            logger.error(error_message)
            self.show_notification(error_message, 'negative', 10000)
            raise KeyError(error_message)
        return value

    def to_yaml(self, route):
        """Convert the configuration for a route to a YAML string."""
        return OmegaConf.to_yaml(self.load(route))

    def open_settings_dialog(self, pageinfo, on_save: Callable = None):
        """Open a dialog for editing the page configuration using NiceGUI."""
        with ui.dialog() as dialog, ui.card().style('min-width: 1000px; max-width: 1000px; height: 500px; top: -17%;'):
            with ui.column().classes('w-full').style('height: 100%; display: flex; flex-direction: column;'):
                # Content row with flex layout
                with ui.row().classes('w-full').style('flex: 1; gap: 2rem; padding: 1.5rem; overflow: hidden;'):
                    # Left Column - PageInfo (minimal width)
                    with ui.column().style('flex: 0 0 auto; padding-top: 0.5rem;'):
                        ui.label('PageInfo').classes('text-subtitle text-weight-medium')
                        with ui.grid(columns=2).style(
                                'display: grid; grid-template-columns: auto 1fr; margin-top: 1rem;'):
                            for key, value in vars(pageinfo).items():
                                ui.label(f"{key}:").classes('text-grey-5 text-left whitespace-nowrap')
                                ui.label(f"{value}").classes('text-white')

                    # Right Column - YAML Configuration (fills remaining space)
                    with ui.column().style('flex: 1 1 0; padding-top: 0.5rem; height: 100%; overflow: hidden;'):
                        ui.label('YAML Configuration').classes('text-subtitle text-weight-medium')
                        yaml_content = self.to_yaml(pageinfo.route)

                        editor = ui.codemirror(
                            value=yaml_content,
                            language='YAML',
                            theme='basicDark',
                        ).classes('w-full').props('''
                            lineHeight: "1.6em"
                        ''').style('''
                            margin-top: 0;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 4px;
                            height: calc(100% - 2rem);
                            overflow-y: auto;
                        ''')

                # Footer with Save button (fixed at bottom)
                with ui.row().classes('w-full justify-center'):
                    ui.button(
                        'SAVE',
                        on_click=lambda: save_and_close(),
                        color='primary'
                    ).props('icon-right="save"').classes('w-48 rounded-sm')  # added rounded-lg

        def save_and_close():
            try:
                self.save(pageinfo.route, editor.value)
                self.show_notification('Configuration saved successfully', 'positive')
                if on_save:
                    on_save()
                dialog.close()
            except Exception as e:
                logger.error(f'Error saving configuration: {str(e)}')
                self.show_notification(
                    f'Error saving configuration: {str(e)}',
                    'negative',
                    8000
                )

        dialog.open()


# Global instance
globalpageconf = GlobalPageConf()