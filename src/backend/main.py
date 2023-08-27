import logging
from server import server
import webview

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    window = webview.create_window('My first pywebview application',server,width=600,resizable=False)
    webview.start(debug=True)