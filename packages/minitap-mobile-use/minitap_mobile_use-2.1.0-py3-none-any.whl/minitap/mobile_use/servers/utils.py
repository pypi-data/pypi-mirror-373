import psutil


def is_port_in_use(port: int):
    for conn in psutil.net_connections():
        if conn.status == psutil.CONN_LISTEN and conn.laddr:
            if hasattr(conn.laddr, "port") and conn.laddr.port == port:
                return True
            elif isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2 and conn.laddr[1] == port:
                return True
    return False
