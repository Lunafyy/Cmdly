from typing import List, Dict, Any
import socket
import threading
import json
import sys
from datetime import datetime
from core.core_types.command import BaseCommand
from core.logger import get_logger

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init()
except ImportError:

    class _Dummy:
        def __getattr__(self, name):
            return ""

    Fore = Style = _Dummy()


def safe_print(msg: str, prompt: str, *, redraw: bool = True) -> None:
    """
    Prints a message to stdout, clearing the current line and optionally redrawing the prompt.

    Args:
        msg (str): The message to print.
        prompt (str): The prompt string to display after the message if `redraw` is True.
        redraw (bool, optional): If True, appends the prompt after the message; otherwise, only prints the message. Defaults to True.

    Returns:
        None
    """
    sys.stdout.write("\r\033[K" + msg + ("\n" + prompt if redraw else "\n"))
    sys.stdout.flush()


class Chat(BaseCommand):
    """
    Chat command for a client–server chat system.
    This command allows users to either host a chat server or join an existing chat session as a client. It supports real-time message broadcasting between multiple clients and the host, with features for handling user nicknames, connection management, and graceful shutdowns.
    Attributes:
        author (str): The author of the command.
        date_created (str): The creation date of the command.
        description (str): A brief description of the command.
        help (str): Usage instructions for the command.
        fun (bool): Indicates if the command is intended to be fun.
    Methods:
        execute(*args, **kwargs) -> int:
            Parses command-line arguments and starts the chat server or client accordingly.
        start_server(port: int, host_name: str) -> None:
            Starts a TCP chat server that listens for incoming client connections, manages nicknames, broadcasts messages, and handles disconnections. Allows the host to send messages via the console and gracefully shuts down on interruption.
        start_client(ip: str, port: int, name: str) -> None:
            Connects to a chat server as a client, sends the user's nickname, listens for incoming messages, and allows the user to send messages via the console. Handles disconnection and shutdown gracefully.
    """

    author = "CJ"
    date_created = "2025-06-17"
    description = "Client–server chat command"
    help = (
        "Usage:\n"
        "  chat host <port> --name <your_name>\n"
        "  chat join <ip:port> --name <your_name>"
    )
    fun = False

    def execute(self, *args, **kwargs) -> int:
        """
        Executes the chat command in either 'host' or 'join' mode.
        Parameters:
            *args: Variable length argument list.
                - args[0]: mode (str): Either 'host' to start a server or 'join' to connect to a server.
                - args[1]: target (str): For 'host', the port number as a string. For 'join', the target in 'ip:port' format.
            **kwargs: Arbitrary keyword arguments.
                - name (str, optional): The display name to use. Defaults to "Anonymous".
        Returns:
            int: 0 on success, 1 on failure.
        Behavior:
            - If insufficient arguments are provided, prints help and returns 1.
            - In 'host' mode, starts a server on the specified port.
            - In 'join' mode, connects to the specified IP and port.
            - Prints and logs errors for invalid modes or port numbers.
        """
        if len(args) < 2:
            print(self.help)
            return 1

        mode, target = args[0], args[1]
        name = kwargs.get("name", "Anonymous")

        try:
            if mode == "host":
                self.start_server(int(target), name)
            elif mode == "join":
                ip, port_str = target.split(":")
                self.start_client(ip, int(port_str), name)
            else:
                print("Invalid mode. Use 'host' or 'join'.")
                get_logger("chat").error(
                    f"Invalid mode '{mode}' provided. Expected 'host' or 'join'."
                )
                return 1
        except ValueError:
            print("Invalid port number.")
            get_logger("chat").error(f"Invalid port number '{target}' provided.")
            return 1

        return 0

    def start_server(self, port: int, host_name: str) -> None:
        """
        Starts a TCP chat server that listens for incoming client connections and facilitates real-time message broadcasting.
        Args:
            port (int): The port number on which the server will listen for incoming connections.
            host_name (str): The display name to use for the server host when sending messages.
        Behavior:
            - Accepts multiple client connections using threads.
            - Receives nicknames from clients and maintains a list of connected clients and their nicknames.
            - Broadcasts messages from clients and the host to all connected clients.
            - Handles client disconnections and notifies remaining clients.
            - Allows the host to send messages via the console.
            - Gracefully shuts down on KeyboardInterrupt, notifying all clients and closing sockets.
        Logging:
            - Logs server events, client connections/disconnections, and message broadcasts using the "chat" logger.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", port))
        server.listen()
        print(f"{Fore.YELLOW}[Hosting] Chat server on port {port}{Style.RESET_ALL}")
        get_logger("chat").info(f"Hosting chat server on port {port}")

        clients: list[socket.socket] = []
        nicknames: dict[socket.socket, str] = {}
        prompt_host = f"{Fore.MAGENTA}(localhost:{port}){Style.RESET_ALL} >> "

        running = True

        def broadcast(msg: str, sender: str = "System", *, redraw: bool = True) -> None:
            """
            Broadcasts a message to all connected clients.

            Sends the specified message to each client in the `clients` list. If a client connection fails, the client is removed from the list and closed. The message is also printed to the local console with a timestamp and sender information.

            Args:
                msg (str): The message to broadcast.
                sender (str, optional): The name of the sender. Defaults to "System".
                redraw (bool, optional): Whether to redraw the prompt after printing the message. Defaults to True.

            Returns:
                None
            """
            if not running:
                return
            payload = json.dumps({"sender": sender, "message": msg})
            for cli in clients[:]:
                try:
                    cli.send(payload.encode())
                    get_logger("chat").info(
                        f"Broadcasting message from {sender}: {msg}"
                    )
                except Exception:
                    clients.remove(cli)
                    try:
                        cli.close()
                    except Exception:
                        pass
            ts = datetime.now().strftime("%H:%M:%S")
            line = f"{Fore.CYAN}[{ts}] {Fore.GREEN}{sender}{Style.RESET_ALL}: {msg}"
            safe_print(line, prompt_host, redraw=redraw)

        def handle_client(sock: socket.socket):
            """
            Handles communication with a connected chat client.

            Receives the client's nickname, adds the client to the active clients list, and broadcasts join/leave messages.
            Continuously listens for incoming messages from the client and broadcasts them to all connected clients.
            Cleans up client resources and notifies others when the client disconnects.

            Args:
                sock (socket.socket): The socket object representing the client connection.

            Side Effects:
                - Modifies the global `clients` list and `nicknames` dictionary.
                - Sends broadcast messages to all connected clients.
                - Logs client disconnection events.

            Exceptions:
                - Handles exceptions during message receiving and socket closing gracefully.
            """
            try:
                nickname = sock.recv(1024).decode() or f"Guest-{sock.fileno()}"
                nicknames[sock] = nickname
                clients.append(sock)
                broadcast(f"📢 {nickname} joined the chat!")
                while running:
                    try:
                        data = sock.recv(1024)
                    except Exception:
                        break
                    if not data:
                        break
                    broadcast(data.decode(), nickname)
            finally:
                if sock in clients:
                    clients.remove(sock)
                broadcast(f"❌ {nicknames.get(sock,'Unknown')} left.")
                get_logger("chat").info(
                    f"Client {nicknames.get(sock, 'Unknown')} disconnected."
                )
                try:
                    sock.close()
                except Exception:
                    pass

        def accept_clients():
            """
            Continuously accepts incoming client connections while the server is running.

            For each accepted client socket, starts a new daemon thread to handle the client
            using the handle_client function. Stops accepting clients if an exception occurs.

            Raises:
                Exception: If an error occurs during client acceptance, the loop breaks.
            """
            while running:
                try:
                    client_sock, _ = server.accept()
                    threading.Thread(
                        target=handle_client, args=(client_sock,), daemon=True
                    ).start()
                except Exception:
                    break

        threading.Thread(target=accept_clients, daemon=True).start()

        try:
            while running:
                msg = input(prompt_host)
                get_logger("chat").info(f"Host input: {msg}")
                if msg.strip():
                    broadcast(msg, host_name, redraw=False)
        except KeyboardInterrupt:
            pass

        running = False
        print("\n[Server] Shutting down.")
        get_logger("chat").info("Shutting down chat server.")

        for cli in clients[:]:
            try:
                cli.send(
                    json.dumps(
                        {"sender": "System", "message": "[Server] Shutting down."}
                    ).encode()
                )
            except Exception:
                pass
            try:
                cli.shutdown(socket.SHUT_RDWR)
                cli.close()
            except Exception:
                pass
        clients.clear()

        try:
            server.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        server.close()

    def start_client(self, ip: str, port: int, name: str) -> None:
        """
        Starts a chat client that connects to a chat server at the specified IP address and port.
        Args:
            ip (str): The IP address of the chat server to connect to.
            port (int): The port number of the chat server.
            name (str): The name to use as the client's identifier in the chat.
        Behavior:
            - Establishes a TCP connection to the chat server.
            - Sends the client's name to the server upon connection.
            - Listens for incoming messages from the server in a background thread and displays them with timestamps.
            - Allows the user to send messages to the server via standard input.
            - Handles graceful disconnection on errors or keyboard interruption.
            - Logs connection, message receipt, and disconnection events.
        Note:
            This method blocks until the client disconnects or an error occurs.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send(name.encode())

        get_logger("chat").info(f"Connected to chat server at {ip}:{port} as {name}")

        prompt_client = f"{Fore.MAGENTA}({ip}:{port}){Style.RESET_ALL} >> "

        running = True

        def listen():
            """
            Listens for incoming messages on the socket in a loop while `running` is True.
            Receives data from the socket, decodes it as JSON, and formats the message with a timestamp and sender information.
            Logs received messages and prints them to the client, optionally redrawing the prompt if the sender is not the current user.
            Handles exceptions by breaking the loop and ensures the socket is closed when finished.
            Raises:
                Exception: If an error occurs during receiving or processing messages.
            """
            nonlocal running
            while running:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    payload = json.loads(data.decode())
                    ts = datetime.now().strftime("%H:%M:%S")
                    line = f"{Fore.CYAN}[{ts}] {Fore.GREEN}{payload['sender']}{Style.RESET_ALL}: {payload['message']}"

                    get_logger("chat").info(
                        f"Received message from {payload['sender']}: {payload['message']}"
                    )

                    redraw = payload["sender"] != name
                    safe_print(line, prompt_client, redraw=redraw)
                except Exception:
                    break
            running = False
            try:
                sock.close()
            except Exception:
                pass

        threading.Thread(target=listen, daemon=True).start()

        try:
            while running:
                msg = input(prompt_client)
                if not running:
                    break
                if msg.strip():
                    try:
                        sock.send(msg.encode())
                    except Exception:
                        break
        except KeyboardInterrupt:
            pass

        running = False
        print("\n[Client] Disconnected.")
        get_logger("chat").info("Disconnecting from chat server.")
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass
