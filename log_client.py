import requests


class Log:
    def __init__(self, host, port, log=True):
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}'
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.log = log

    def _log(self, endpoint, data):
        if self.log:
            try:
                response = self.session.post(self.url + endpoint, json=data)
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Error: {e}")

    def info(self, message):
        self._log('/info', {"message": message})

    def warning(self, message):
        self._log('/warning', {"message": message})

    def error(self, message):
        self._log('/error', {"message": message})

    def panic(self, message):
        self._log('/panic', {"message": message})

    def debug(self, message):
        self._log('/debug', {"message": message})