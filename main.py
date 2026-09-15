from __future__ import annotations

import argparse
import socket
import sys
import time
import urllib
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description="Скрипт для замера времени ответа сервера.")
parser.add_argument("url", type=str, help="URL адрес для проверки")
parser.add_argument(
    "-r",
    "--retries",
    type=int,
    default=10,
    help="Количество повторов запроса (по умолчанию: 10)",
)

BYTES_TO_MEGABYTES_COEF = 1024 * 1024
CHUNK_SIZE = 8192


def measure_one_request(url: str) -> tuple[int, float]:
    start_time = time.perf_counter()
    try:
        with urllib.request.urlopen(url) as response:
            bytes_received = 0
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                bytes_received += len(chunk)
        end_time = time.perf_counter()
        network_time = end_time - start_time

        return bytes_received, network_time
    except urllib.error.HTTPError as e:
        print(f"\n[Ошибка HTTP {e.code}]: {e.reason}")
    except urllib.error.URLError as e:
        print(f"\n[Ошибка сети]: {e.reason}")
    except (socket.timeout, TimeoutError):
        print("\n[Ошибка]: Превышено системное время ожидания")
    except Exception as e:
        print(f"\n[Непредвиденная ошибка]: {e}")
    sys.exit(1)


def get_args() -> tuple[str, int]:
    args = parser.parse_args()
    return args.url, args.retries


def main():
    url, retries = get_args()

    all_speed = 0.0
    for x in range(retries):
        bytes_received, network_time = measure_one_request(url)
        speed = (bytes_received / BYTES_TO_MEGABYTES_COEF) / network_time
        all_speed += speed

        print(f"Скорость запроса #{x+1}: {speed:.4f} мб/с")

    print(f"Средняя скорость: {all_speed/retries:.4f} мб/c")


if __name__ == '__main__':
    main()
