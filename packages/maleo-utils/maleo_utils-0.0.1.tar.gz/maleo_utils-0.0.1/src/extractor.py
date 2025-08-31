from fastapi import Request
from starlette.requests import HTTPConnection
from uuid import UUID


def extract_operation_id(request: Request) -> UUID:
    operation_id = request.state.operation_id
    if not isinstance(operation_id, UUID):
        raise TypeError(f"Invalid 'operation_id' type: '{operation_id}'")
    return operation_id


def extract_client_ip(conn: HTTPConnection) -> str:
    """Extract client IP with more robust handling of proxies"""
    # * Check for x-forwarded-for header (common when behind proxy/load balancer)
    x_forwarded_for = conn.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # * The client's IP is the first one in the list
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        return ips[0]

    # * Check for x-real-ip header (used by some proxies)
    x_real_ip = conn.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip

    # * Fall back to direct client connection
    return conn.client.host if conn.client else "unknown"
