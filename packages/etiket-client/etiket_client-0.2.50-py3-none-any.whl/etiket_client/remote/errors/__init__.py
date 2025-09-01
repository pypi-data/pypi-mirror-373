import requests, urllib3, socket, ssl

# More specific network-related errors
CONNECTION_ERRORS = (
    requests.exceptions.ConnectionError,  # Covers DNS, refused, etc. for requests
    requests.exceptions.Timeout,          # Covers connect and read timeouts for requests
    
    urllib3.exceptions.NewConnectionError,
    urllib3.exceptions.ConnectTimeoutError, # More specific than urllib3.exceptions.TimeoutError
    urllib3.exceptions.ReadTimeoutError,    # More specific than urllib3.exceptions.TimeoutError
    urllib3.exceptions.MaxRetryError,
    urllib3.exceptions.ProtocolError,     # Can indicate a broken connection
    
    # socket.error is an alias for OSError. We want to be more specific.
    socket.gaierror,                      # Address info errors (DNS failure)
    socket.timeout,                       # Socket timeouts
    ConnectionRefusedError,
    ConnectionAbortedError,
    ConnectionResetError,
    # TimeoutError, # socket.timeout often covers this, or is an alias
    
    ssl.SSLError                          # SSL-specific errors
)