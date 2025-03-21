import socket
import logging
import sys
import signal
from .utils import Bet, convertByteToNumber
from .utils import store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients_sockets = []
        self.last_client_id = 0
        self.sockets_id = {}

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
            self.sockets_id[client_sock.getpeername()] = self.last_client_id
            self.last_client_id += 1
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                size = convertByteToNumber(client_sock.recv(4))
                if size == 0:
                    break
                bets_length = convertByteToNumber(client_sock.recv(4))
                msg = client_sock.recv(size).decode('utf-8')
                isSuccess = True
                bets = []
                for actual_bet in msg.split(";"):
                    fields = actual_bet.split("|")
                    if len(fields) == 5:  # Validar que tenga todos los campos
                        bet = Bet(self.sockets_id[client_sock.getpeername()], fields[0], fields[1], fields[2], fields[3], fields[4])
                        bets.append(bet)
                    else:
                        isSuccess = False
                if len(bets) != bets_length:
                    isSuccess = False

                if not isSuccess:
                    client_sock.sendall(b'\x02')
                    logging.info(f'action: apuesta_recibida | result: fail | cantidad: {bets_length - len(bets)}')
                else:
                    client_sock.sendall(b'\x00')

                logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
                store_bets(bets)

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            client_sock.sendall(b'\x01')
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
