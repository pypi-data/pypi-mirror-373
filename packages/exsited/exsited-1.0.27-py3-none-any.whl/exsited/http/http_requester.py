import requests
from exsited.http.http_const import HTTPConst


class HTTPResponse:
    status: str
    httpCode: int
    data: any
    contentType: str

    def __init__(self):
        self.status = None
        self.httpCode = None
        self.data = None
        self.contentType = None

    def process_response(self, response) -> "HTTPResponse":
        self.httpCode = response.status_code
        if 200 <= self.httpCode < 300:
            self.status = HTTPConst.SUCCESS
        else:
            self.status = HTTPConst.ERROR
        self.set_data(response)
        return self

    def set_data(self, response):
        response.encoding = HTTPConst.UTF8_ENCODING
        self.contentType = response.headers["Content-Type"]
        if self.contentType and self.contentType.lower().startswith(HTTPConst.APPLICATION_JSON):
            if response.text and response.text != "":
                self.data = response.json()
        elif self.contentType and self.contentType.lower().startswith(HTTPConst.APPLICATION_PDF):
            self.data = response.content
        else:
            self.data = response.text

    @staticmethod
    def get_response(response) -> "HTTPResponse":
        http_response = HTTPResponse()
        http_response.process_response(response)
        return http_response


class HTTPRequester:
    def __init__(self):
        self.headers: dict = {}
        self.baseUrl: str

    def _get_url(self, url):
        return self.baseUrl + url

    def set_base(self, url) -> 'HTTPRequester':
        self.baseUrl = url
        return self

    def get(self, url: str, params: dict = None) -> HTTPResponse:
        url = self._get_url(url)
        response = requests.get(url, headers=self.headers, params=params)
        return HTTPResponse.get_response(response)

    def post(self, url: str, json_dict: dict = None, data: dict = None, file: dict = None) -> HTTPResponse:
        url = self._get_url(url)
        response = requests.post(url, headers=self.headers, json=json_dict, data=data, files=file)
        return HTTPResponse.get_response(response)

    def put(self, url: str, json_dict: dict = None, data: dict = None, file: dict = None) -> HTTPResponse:
        url = self._get_url(url)
        response = requests.put(url, headers=self.headers, json=json_dict, data=data, files=file)
        return HTTPResponse.get_response(response)

    def patch(self, url: str, json_dict: dict = None, data: dict = None, file: dict = None) -> HTTPResponse:
        url = self._get_url(url)
        response = requests.patch(url, headers=self.headers, json=json_dict, data=data, files=file)
        return HTTPResponse.get_response(response)

    def delete(self, url: str, params: dict = None) -> HTTPResponse:
        url = self._get_url(url)
        response = requests.delete(url, headers=self.headers, params=params)
        return HTTPResponse.get_response(response)

    def add_header(self, key: str, value) -> 'HTTPRequester':
        self.headers[key] = value
        return self

    def add_bearer_token(self, token) -> 'HTTPRequester':
        self.add_header("Authorization", f"Bearer {token}")
        return self

    def add_content_type(self, content_type) -> 'HTTPRequester':
        self.add_header("Content-Type", str(content_type))
        return self
