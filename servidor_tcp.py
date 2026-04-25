import argparse
import socket
import threading

BUFFER_SIZE = 1024
EXIT_WORD = "salir"

clientes: dict[socket.socket, tuple[str, int]] = {}
lock = threading.Lock()


def agregar_cliente(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    with lock:
        clientes[client_socket] = client_address


def quitar_cliente(client_socket: socket.socket) -> None:
    with lock:
        clientes.pop(client_socket, None)


def broadcast(mensaje: str, origen_socket: socket.socket | None = None) -> None:
    """Envia el mensaje a todos los clientes excepto al que lo mando."""
    with lock:
        destinatarios = [cliente for cliente in clientes if cliente != origen_socket]

    desconectados = []
    for cliente in destinatarios:
        try:
            cliente.sendall(f"{mensaje}\n".encode("utf-8"))
        except OSError:
            desconectados.append(cliente)

    for cliente in desconectados:
        quitar_cliente(cliente)
        try:
            cliente.close()
        except OSError:
            pass


def manejar_cliente(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    """Hilo que maneja a un cliente individual."""
    nombre = f"{client_address[0]}:{client_address[1]}"
    buffer = ""
    print(f"Cliente conectado: {client_address}")
    agregar_cliente(client_socket, client_address)

    broadcast(f"[{nombre} se unio al chat]", client_socket)

    try:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
            except ConnectionResetError:
                break

            if not data:
                break

            buffer += data.decode("utf-8")
            lineas = buffer.split("\n")
            buffer = lineas.pop()

            for mensaje in lineas:
                mensaje = mensaje.strip()
                if not mensaje:
                    continue

                print(f"[{nombre}]: {mensaje}")

                if mensaje.lower() == EXIT_WORD:
                    return

                broadcast(f"[{nombre}]: {mensaje}", client_socket)

    except OSError as error:
        print(f"Error con {client_address}: {error}")
    finally:
        quitar_cliente(client_socket)
        broadcast(f"[{nombre} abandono el chat]", client_socket)

        try:
            client_socket.close()
        except OSError:
            pass

        print(f"Cliente desconectado: {client_address}")


def run_server(host: str, port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        print(f"Chatroom escuchando en {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(client_socket, client_address),
                daemon=True,
            )
            hilo.start()
    except KeyboardInterrupt:
        print("\nServidor finalizado.")
    finally:
        with lock:
            sockets = list(clientes)
            clientes.clear()

        for client_socket in sockets:
            try:
                client_socket.close()
            except OSError:
                pass

        server_socket.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor chatroom TCP.")
    parser.add_argument("--host", default="0.0.0.0", help="IP del servidor.")
    parser.add_argument("--port", default=5000, type=int, help="Puerto de escucha.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port)
