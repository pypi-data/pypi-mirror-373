from PyQt5.QtCore import QUrl, QUrlQuery, QEventLoop, QTimer
from PyQt5.QtNetwork import QTcpServer, QTcpSocket

class RedirectHandler(QTcpServer):
    def __init__(self, port : int, parent=None):
        super().__init__(parent)
        self.port = port
        self.auth_code = None
        self.event_loop = None

    def incomingConnection(self, socketDescriptor):
        socket = QTcpSocket(self)
        if socket.setSocketDescriptor(socketDescriptor):
            socket.readyRead.connect(lambda: self.handle_request(socket))

    def handle_request(self, socket):
        request_data = socket.readAll().data().decode('utf-8')
        request_lines = request_data.split('\r\n')

        if request_lines:
            # Extract the GET request path
            request_line = request_lines[0]
            url = QUrl(request_line.split(' ')[1])  # Extract the URL from the GET request
            query = QUrlQuery(url)

            if query.hasQueryItem('code'):
                self.auth_code = query.queryItemValue('code')
                response = "Authorization successful! You can close this window."
            elif query.hasQueryItem('error'):
                error = query.queryItemValue('error')
                self.auth_code = None
                response = f"Authorization failed: {error}. You can close this window."
            else:
                self.auth_code = None
                response = "No authorization code received. You can close this window."

            response_data = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{response}"
            socket.write(response_data.encode('utf-8'))
            socket.flush()
            socket.disconnectFromHost()

            # Exit the event loop once we have handled the request
            if self.event_loop and self.event_loop.isRunning():
                self.event_loop.quit()

    def wait_for_auth_code(self, timeout=120):
        if not self.listen(port=self.port):
            raise RuntimeError(f"Failed to start the server on port {self.port}")

        self.event_loop = QEventLoop()

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.event_loop.quit)
        timer.start(timeout * 1000)

        self.event_loop.exec_()
        if self.auth_code is None:
            raise TimeoutError("Authorization code not received within the specified timeout")
        
        self.close()

        return self.auth_code

def TCP_auth_code_handler(port : int):
    handler = RedirectHandler(port)
    return handler.wait_for_auth_code()