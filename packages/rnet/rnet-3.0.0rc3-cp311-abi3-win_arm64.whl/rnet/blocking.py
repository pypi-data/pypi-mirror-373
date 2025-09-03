import datetime
from rnet import ClientParams, History, Message, Request, Streamer, WebSocketRequest
from typing import (
    Optional,
    Any,
    List,
    Unpack,
)

from rnet import Version, Method, SocketAddr, StatusCode
from rnet.header import HeaderMap
from rnet.cookie import Cookie


class Client:
    r"""
    A blocking client for making HTTP requests.
    """

    def __init__(
        cls,
        **kwargs: Unpack[ClientParams],
    ) -> "Client":
        r"""
        Creates a new blocking Client instance.

        Args:
            emulation: Browser fingerprint/Emulation config.
            user_agent: Default User-Agent string.
            headers: Default request headers.
            orig_headers: Original request headers (case-sensitive and order).
            referer: Automatically set Referer.
            allow_redirects: Allow automatic redirects.
            max_redirects: Maximum number of redirects.
            cookie_store: Enable cookie store.
            lookup_ip_strategy: IP lookup strategy.
            timeout: Total timeout (seconds).
            connect_timeout: Connection timeout (seconds).
            read_timeout: Read timeout (seconds).
            tcp_keepalive: TCP keepalive time (seconds).
            tcp_keepalive_interval: TCP keepalive interval (seconds).
            tcp_keepalive_retries: TCP keepalive retry count.
            tcp_user_timeout: TCP user timeout (seconds).
            tcp_nodelay: Enable TCP_NODELAY.
            tcp_reuse_address: Enable SO_REUSEADDR.
            pool_idle_timeout: Connection pool idle timeout (seconds).
            pool_max_idle_per_host: Max idle connections per host.
            pool_max_size: Max total connections in pool.
            http1_only: Enable HTTP/1.1 only.
            http2_only: Enable HTTP/2 only.
            https_only: Enable HTTPS only.
            http2_max_retry_count: Max HTTP/2 retry count.
            verify: Verify SSL or specify CA path.
            identity: Represents a private key and X509 cert as a client certificate.
            keylog: Key logging policy (environment or file).
            tls_info: Return TLS info.
            min_tls_version: Minimum TLS version.
            max_tls_version: Maximum TLS version.
            no_proxy: Disable proxy.
            proxies: Proxy server list.
            local_address: Local bind address.
            interface: Local network interface.
            gzip: Enable gzip decompression.
            brotli: Enable brotli decompression.
            deflate: Enable deflate decompression.
            zstd: Enable zstd decompression.

        # Examples

        ```python
        import asyncio
        import rnet

        client = rnet.blocking.Client(
            user_agent="my-app/0.0.1",
            timeout=10,
        )
        response = client.get('https://httpbin.org/get')
        print(response.text())
        ```
        """

    def request(
        self,
        method: Method,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given method and URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.request(Method.GET, "https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """

    def websocket(self, url: str, **kwargs: Unpack[WebSocketRequest]) -> "WebSocket":
        r"""
        Sends a WebSocket request.

        # Examples

        ```python
        import rnet
        import asyncio

        async def main():
            client = rnet.blocking.Client()
            ws = client.websocket("wss://echo.websocket.org")
            ws.send(rnet.Message.from_text("Hello, WebSocket!"))
            message = ws.recv()
            print("Received:", message.data)
            ws.close()

        asyncio.run(main())
        ```
        """

    def trace(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.trace("https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """

    def options(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.options("https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """

    def head(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.head("https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """

    def delete(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.delete("https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """

    def patch(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.patch("https://httpbin.org/anything", json={"key": "value"})
            print(response.text())

        asyncio.run(main())
        ```
        """

    def put(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.put("https://httpbin.org/anything", json={"key": "value"})
            print(response.text())

        asyncio.run(main())
        ```
        """

    def post(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.post("https://httpbin.org/anything", json={"key": "value"})
            print(response.text())

        asyncio.run(main())
        ```
        """

    def get(
        self,
        url: str,
        **kwargs: Unpack[Request],
    ) -> "Response":
        r"""
        Sends a request with the given URL.

        # Examples

        ```python
        import rnet
        import asyncio
        from rnet import Method

        async def main():
            client = rnet.blocking.Client()
            response = client.get("https://httpbin.org/anything")
            print(response.text())

        asyncio.run(main())
        ```
        """


class Response:
    r"""
    A blocking response from a request.
    """

    url: str
    r"""
    Get the URL of the response.
    """

    status: StatusCode
    r"""
    Get the status code of the response.
    """

    version: Version
    r"""
    Get the HTTP version of the response.
    """

    headers: HeaderMap
    r"""
    Get the headers of the response.
    """

    cookies: List[Cookie]
    r"""
    Get the cookies of the response.
    """

    content_length: int
    r"""
    Get the content length of the response.
    """

    remote_addr: Optional[SocketAddr]
    r"""
    Get the remote address of the response.
    """

    local_addr: Optional[SocketAddr]
    r"""
    Get the local address of the response.
    """

    history: List[History]
    r"""
    Get the redirect history of the Response.
    """

    peer_certificate: Optional[bytes]
    r"""
    Get the DER encoded leaf certificate of the response.
    """

    def text(self) -> str:
        r"""
        Get the text content of the response.
        """

    def text_with_charset(self, encoding: str) -> str:
        r"""
        Get the text content of the response with a specific charset.

        # Arguments

        * `encoding` - The default encoding to use if the charset is not specified.
        """

    def json(self) -> Any:
        r"""
        Get the JSON content of the response.
        """

    def bytes(self) -> bytes:
        r"""
        Get the bytes content of the response.
        """

    def stream(self) -> Streamer:
        r"""
        Get the response into a `Stream` of `Bytes` from the body.
        """

    def close(self) -> None:
        r"""
        Close the response connection.
        """

    def __enter__(self) -> "Response": ...
    def __exit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any) -> None: ...


class WebSocket:
    r"""
    A blocking WebSocket response.
    """

    status: StatusCode
    r"""
    Get the status code of the response.
    """
    version: Version
    r"""
    Get the HTTP version of the response.
    """
    headers: HeaderMap
    r"""
    Get the headers of the response.
    """
    cookies: List[Cookie]
    r"""
    Get the cookies of the response.
    """
    remote_addr: Optional[SocketAddr]
    r"""
    Get the remote address of the response.
    """
    protocol: Optional[str]
    r"""
    Get the WebSocket protocol.
    """

    def __enter__(self) -> "WebSocket": ...
    def __exit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any) -> None: ...

    def recv(self, timeout: datetime.timedelta | None = None) -> Optional[Message]:
        r"""
        Receives a message from the WebSocket.
        """

    def send(self, message: Message) -> None:
        r"""
        Sends a message to the WebSocket.

        # Arguments

        * `message` - The message to send.
        """

    def close(
        self,
        code: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> None:
        r"""
        Closes the WebSocket connection.

        # Arguments

        * `code` - An optional close code.
        * `reason` - An optional reason for closing.
        """
