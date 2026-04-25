import argparse
import socket
import threading

BUFFER_SIZE = 1024
EXIT_WORD = "salir"


def receive_messages(client_socket: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = client_socket.recv(BUFFER_SIZE)
        except OSError:
            break

        if not data:
            print("\nEl servidor cerro la conexion.")
            stop_event.set()
            break

        print(f"\n{data.decode('utf-8').strip()}\nCliente> ", end="", flush=True)


def run_client(host: str, port: int, timeout: float) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    stop_event = threading.Event()

    try:
        client_socket.settimeout(timeout)
        client_socket.connect((host, port))
        client_socket.settimeout(None)

        print(f"Conectado al servidor en {client_socket.getpeername()}")
        print(f"Socket local del cliente: {client_socket.getsockname()}")
        print("Ingrese un mensaje y presione Enter. Use 'salir' para terminar.")

        receiver = threading.Thread(
            target=receive_messages,
            args=(client_socket, stop_event),
            daemon=True,
        )
        receiver.start()

        while not stop_event.is_set():
            try:
                message = input("Cliente> ").strip()
            except EOFError:
                message = EXIT_WORD
            except KeyboardInterrupt:
                print()
                message = EXIT_WORD

            if not message:
                print("Debe ingresar un mensaje no vacio.")
                continue

            try:
                client_socket.sendall(f"{message}\n".encode("utf-8"))
            except OSError as error:
                print(f"Error al enviar el mensaje: {error}")
                break

            if message.lower() == EXIT_WORD:
                stop_event.set()
                break

    except OSError as error:
        print(f"Error del cliente: {error}")
    finally:
        stop_event.set()
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
