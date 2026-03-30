import argparse
import socket
from datetime import datetime

BUFFER_SIZE = 1024
EXIT_WORD = "salir"


def build_response(message: str, client_address: tuple) -> str:
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return (
        f"[{timestamp}] Servidor: mensaje recibido desde "
        f"{client_address[0]}:{client_address[1]} -> {message}"
    )


def run_server(host: str, port: int, timeout: float) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    client_socket = None

    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print(f"Servidor TCP escuchando en {host}:{port}")
        print(f"Socket local del servidor: {server_socket.getsockname()}")
        print("Esperando una conexion...")

        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(timeout)

        print(f"Cliente conectado: {client_socket.getpeername()}")
        print("Escriba 'salir' en el cliente para finalizar la conversacion.")

        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
            except socket.timeout:
                print("Tiempo de espera agotado. Cerrando la conexion.")
                break

            if not data:
                print("El cliente cerro la conexion.")
                break

            message = data.decode("utf-8").strip()
            print(f"Mensaje recibido: {message}")

            if message.lower() == EXIT_WORD:
                client_socket.sendall("Servidor: conexion finalizada.".encode("utf-8"))
                break

            response = build_response(message, client_address)
            client_socket.sendall(response.encode("utf-8"))

    except OSError as error:
        print(f"Error del servidor: {error}")
    finally:
        if client_socket is not None:
            client_socket.close()
        server_socket.close()
        print("Servidor finalizado.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor TCP basico con sockets.")
    parser.add_argument("--host", default="127.0.0.1", help="Direccion IP del servidor.")
    parser.add_argument("--port", default=5000, type=int, help="Puerto de escucha.")
    parser.add_argument(
        "--timeout",
        default=120.0,
        type=float,
        help="Tiempo maximo de espera para recibir datos.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_server(arguments.host, arguments.port, arguments.timeout)
