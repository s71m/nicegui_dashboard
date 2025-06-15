import sys
from nicegui import ui

from web.webapp import webapp, webapp_shutdown

return_code = 1
try:
    webapp()
    ui.run(dark=True, port=8000, reload=False, favicon='🆖', title="dashboard")
except KeyboardInterrupt:
    print('SIGINT received, aborting')
    webapp_shutdown()
    return_code = 0
finally:
    sys.exit(return_code)