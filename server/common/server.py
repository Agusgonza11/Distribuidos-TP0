import socket
import logging
import sys
import signal
from .utils import Bet
from .utils import store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients_sockets = []

    def __handle_sigterm_signal(self, signal, frame):
        """
        Handles SIGTERM signal for graceful shutdown.

        Closes all active client connections, shuts down the server socket, 
        and exits the process cleanly.
        """
        logging.info("Server: Recibida señal SIGTERM. Cerrando conexiones")
        for client in self.clients_sockets:
            client.close()
            logging.info(f'action: closing_socket | result: success')
        self._server_socket.close()
        sys.exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        signal.signal(signal.SIGTERM, self.__handle_sigterm_signal)
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self.clients_sockets.append(client_sock)
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            data_size = client_sock.recv(4)
            size = (data_size[0] << 24) | (data_size[1] << 16) | (data_size[2] << 8) | data_size[3]
            msg = client_sock.recv(size).decode('utf-8').split("|")
            bet = Bet(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {msg[3]} | numero: {msg[5]}')
            client_sock.sendall(b'\x01')
            store_bets([bet])
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            client_sock.sendall(b'\x00')
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
