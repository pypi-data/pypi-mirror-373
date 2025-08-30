from datetime import datetime, timezone
import time
import os


def wait_until_file_stable(path, check_interval=0.5, timeout=10):
    """
    Aguarda até que o arquivo 'path' não mude de tamanho por 'check_interval' segundos.
    Retorna True se o arquivo estabilizar, False se estourar o timeout.
    """
    start_time = time.time()

    if not os.path.exists(path):
        return False

    last_size = -1
    while True:
        try:
            current_size = os.path.getsize(path)
        except FileNotFoundError:
            return False

        if current_size == last_size and current_size > 0:
            return True

        last_size = current_size
        time.sleep(check_interval)

        if time.time() - start_time > timeout:
            return False
    

def get_utc_now() -> str:
    """
    Get the current date and time in UTC format as an ISO string.

    Returns:
        str: Current UTC datetime in ISO format with 'Z' suffix (e.g., '2024-01-15T10:30:45.123Z')
    """
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')