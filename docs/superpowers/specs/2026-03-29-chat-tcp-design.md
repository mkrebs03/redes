## Diseno: chat TCP basico en Python

### Objetivo

Construir una aplicacion cliente-servidor con sockets TCP en Python para demostrar el uso de los metodos principales del modulo `socket` y dejar una base simple de exponer en clase.

### Alcance

- `servidor_tcp.py` escuchara conexiones entrantes en `AF_INET` y `SOCK_STREAM`.
- `cliente_tcp.py` se conectara al servidor y enviara mensajes desde consola.
- El servidor respondera con una confirmacion automatica a cada mensaje recibido.
- La palabra `salir` cerrara la comunicacion de forma ordenada.
- `informe.md` incluira introduccion, desarrollo, conclusion, 10+ metodos del modulo `socket` y un diagrama de actividad.

### Flujo principal

1. El servidor crea el socket, hace `bind()`, `listen()` y espera con `accept()`.
2. El cliente crea el socket y se conecta mediante `connect()`.
3. El cliente envia mensajes con `sendall()`.
4. El servidor recibe datos con `recv()`, arma una respuesta y la devuelve con `sendall()`.
5. Cuando el cliente envia `salir`, ambos cierran sus sockets con `close()`.

### Criterios de exito

- El servidor y el cliente deben ejecutarse desde terminal.
- La comunicacion debe funcionar localmente en `127.0.0.1`.
- El informe debe poder entregarse como documento base para PDF o Word.
