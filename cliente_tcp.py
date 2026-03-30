import argparse
import socket

BUFFER_SIZE = 1024
EXIT_WORD = "salir"


def run_client(host: str, port: int, timeout: float) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

    try:
        client_socket.settimeout(timeout)
        client_socket.connect((host, port))

        print(f"Conectado al servidor en {client_socket.getpeername()}")
        print(f"Socket local del cliente: {client_socket.getsockname()}")
        print("Ingrese un mensaje y presione Enter. Use 'salir' para terminar.")

        while True:
            try:
                message = input("Cliente> ").strip()
            except EOFError:
                message = EXIT_WORD

            if not message:
                print("Debe ingresar un mensaje no vacio.")
                continue

            client_socket.sendall(message.encode("utf-8"))

            try:
                response = client_socket.recv(BUFFER_SIZE)
            except socket.timeout:
                print("Tiempo de espera agotado al recibir la respuesta del servidor.")
                break

            if not response:
                print("El servidor cerro la conexion.")
                break

            print(f"Servidor> {response.decode('utf-8').strip()}")

            if message.lower() == EXIT_WORD:
                break

    except OSError as error:
        print(f"Error del cliente: {error}")
    finally:
        client_socket.close()
        print("Cliente finalizado.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cliente TCP basico con sockets.")
    parser.add_argument("--host", default="127.0.0.1", help="Direccion IP del servidor.")
    parser.add_argument("--port", default=5000, type=int, help="Puerto del servidor.")
    parser.add_argument(
        "--timeout",
        default=120.0,
        type=float,
        help="Tiempo maximo de espera para conectar y recibir datos.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_client(arguments.host, arguments.port, arguments.timeout)
