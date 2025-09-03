import hashlib
import json
import threading

import httplib2

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from . import lightrun_config
from .lightrun_native import native


class HTTPResponseCodes(object):
    HTTP_OK = 200
    HTTP_UPGRADE_REQUIRED = 426


class HTTPException(Exception):
    """
    Helper class to wrap exceptions in order to propagate the error code and response with the thrown exception.
    """

    def __init__(self, response_code, error_response):
        self.response_code = response_code
        self.error_response = error_response


class LightrunHTTPSConnection(httplib2.HTTPSConnectionWithTimeout, object):
    def connect(self):
        super(self.__class__, self).connect()

        if not lightrun_config.GetBooleanConfigValue("default_certificate_pinning_enabled"):
            return

        pinned_certs = lightrun_config.config.get("pinned_certs")
        pinned_certs = [] if not pinned_certs else [cert.strip() for cert in pinned_certs.split(",")]

        cert = self.sock.getpeercert(binary_form=True)
        public_key = x509.load_der_x509_certificate(cert, default_backend()).public_key()
        public_key_bytes = public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

        key_hash = hashlib.sha256(public_key_bytes).hexdigest()

        if key_hash not in pinned_certs:
            raise Exception("Certificate Pinning Failed!")


class ConnectionManager(object):
    """
    A helper class to manage the agent's connections with the backend.
    """

    DEFAULT_CONNECTION_TIMEOUT = 30000

    _active_connections = []
    _active_connections_lock = threading.RLock()

    class ActiveConnection(object):
        """
        Helper class to automatically close connections.
        """

        def __init__(self, conn):
            self._conn = conn
            with ConnectionManager._active_connections_lock:
                ConnectionManager._active_connections.append(self._conn)

        def __enter__(self):
            return self._conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

        def close(self):
            if self._conn is not None:
                with ConnectionManager._active_connections_lock:
                    ConnectionManager._active_connections.remove(self._conn)
                self._conn.close()

    def __init__(self, backend_base_url, connection_timeout=DEFAULT_CONNECTION_TIMEOUT):
        self._backend_base_url = backend_base_url
        self._in_shutdown = False
        self.connection_timeout = connection_timeout
        self._proxy_info = ConnectionManager._GetProxyInfo()

    @property
    def connection_timeout(self):
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, value):
        if value is None or value >= 0:
            self._connection_timeout = value
        else:
            raise ValueError("Timeout value must be greater than or equal to 0, or None to use the system default timeout")

    def Shutdown(self):
        """
        Close the connection manager and disconnect all active connections.
        """
        self._in_shutdown = True
        with ConnectionManager._active_connections_lock:
            for connection in ConnectionManager._active_connections:
                connection.close()

    def SendHttpRequest(self, method, endpoint_path, request_body=None):
        if request_body is not None:
            request_body = json.dumps(request_body)
        return self.SendHttpRequestByteArray(method, endpoint_path, request_body, "application/json")

    def SendHttpRequestByteArray(self, method, endpoint_path, request_body, content_type):
        """
        Send an HTTP request to the server.
        :param method: The HTTP method of the request.
        :param endpoint_path: The url endpoint. This value will be appended to the backendBaseURL path that was
                              given in the constructor.
        :param request_body: The contents of the request. Can be null. If this parameter is null, no write action
                             is performed on the connection.
        :return A tuple containing the response code and response content, if it exists.
        """
        url = str(self._backend_base_url + endpoint_path)
        with self._OpenConnection() as conn:
            headers = {"Authorization": "Bearer " + lightrun_config.GetCompanySecret(), "Content-Type": content_type}
            resp_headers, resp_content = conn.request(url, method=method, body=request_body, headers=headers, connection_type=LightrunHTTPSConnection)
            resp_status = int(resp_headers["status"])
            if resp_status != HTTPResponseCodes.HTTP_OK:
                raise HTTPException(resp_status, resp_content)

        return resp_status, resp_content

    def _OpenConnection(self):
        https_conn = httplib2.Http(cache=None, timeout=self.connection_timeout, disable_ssl_certificate_validation=True, proxy_info=self._proxy_info)
        # We implement our own type of certificate validation in LightrunHTTPSConnection.connect

        if self._in_shutdown:
            # We don't need to call "disconnect" here (The creation of the Httplib2.Http object doesn't
            # actually establish the connection, so calling "disconnect" will have no effect)
            raise RuntimeError("Shutdown in progress")

        return self.ActiveConnection(https_conn)

    @staticmethod
    def _GetProxyInfo():
        host = lightrun_config.GetProxyHost()
        if host is None:
            return None  # no proxy config
        port = lightrun_config.GetProxyPort()
        if port is None:
            native.LogError("proxy_port is not set")
            return None
        proxy = httplib2.ProxyInfo(
            proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
            proxy_host=host,
            proxy_port=port,
            proxy_user=lightrun_config.GetProxyUsername(),
            proxy_pass=lightrun_config.GetProxyPassword(),
        )
        native.LogInfo(f"Using proxy server: {proxy}")
        return proxy
