import argparse
import socket
import threading

BUFFER_SIZE = 1024
EXIT_WORD = "salir"

# Lista compartida de clientes conectados
clientes = []
lock = threading.Lock()

def broadcast(mensaje, origen_socket):
    """Envía el mensaje a todos los clientes excepto al que lo mandó."""
    with lock:
        for cliente in clientes:
            if cliente != origen_socket:
                try:
                    cliente.sendall(mensaje.encode("utf-8"))
                except:
                    clientes.remove(cliente)

def manejar_cliente(client_socket, client_address):
    """Hilo que maneja a un cliente individual."""
    print(f"Cliente conectado: {client_address}")
    with lock:
        clientes.append(client_socket)

    broadcast(f"[{client_address[0]} se unió al chat]", client_socket)

    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break

            mensaje = data.decode("utf-8").strip()
            print(f"[{client_address[0]}]: {mensaje}")

            if mensaje.lower() == EXIT_WORD:
                break

            broadcast(f"[{client_address[0]}]: {mensaje}", client_socket)

        except:
            break

    # Cliente se desconecta
    with lock:
        if client_socket in clientes:
            clientes.remove(client_socket)

    broadcast(f"[{client_address[0]} abandonó el chat]", client_socket)
    client_socket.close()
    print(f"Cliente desconectado: {client_address}")

def run_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)
    print(f"Chatroom escuchando en {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(client_socket, client_address))
        hilo.daemon = True
        hilo.start()

def parse_args():
    parser = argparse.ArgumentParser(description="Servidor chatroom TCP.")
    parser.add_argument("--host", default="0.0.0.0", help="IP del servidor.")
    parser.add_argument("--port", default=5000, type=int, help="Puerto de escucha.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port)