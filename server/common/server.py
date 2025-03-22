import socket
import logging
import sys
import signal
import time
from .utils import Bet, convertByteToNumber, get_winners, has_won, send_message
from .utils import store_bets

byte =  1

class Server:
    def __init__(self, port, listen_backlog, expected_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients_sockets = []
        self.is_finish = False
        self.last_client_id = 0
        self.expected_clients = expected_clients
        self.sockets_id = {}
        self.winners = {}
        self.agency_finish = {}

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

    def __handle_lottery(self, client_sock):
        if len(self.agency_finish) == int(self.expected_clients):
            if not self.is_finish:
                logging.info(f'action: sorteo | result: success')
                self.is_finish = True
            client_sock.sendall(b'S')  # Sending
            id = client_sock.recv(4).decode('utf-8').rstrip('\x00')
            winners = get_winners()
            agency_id = self.sockets_id.get(id, None)
            winners_list = winners.get(agency_id, [])
            send_message(client_sock, ';'.join(winners_list))
        else:
            client_sock.sendall(b'R')  # Retry



    def __handle_batches(self, client_sock):
        self.agency_finish[client_sock.getpeername()] = False
        while True:
            size = convertByteToNumber(client_sock.recv(4))
            if size == 0:
                self.agency_finish[client_sock.getpeername()] = True
                break
            bets_length = convertByteToNumber(client_sock.recv(4))
            id = client_sock.recv(4).decode('utf-8').rstrip('\x00')
            if id not in self.sockets_id:
                self.sockets_id[id] = self.last_client_id
                self.last_client_id += 1
            msg = client_sock.recv(size).decode('utf-8')
            isSuccess = True
            total_bets_received = 0
            bets = []
            for actual_bet in msg.split(";"):
                fields = actual_bet.split("|")
                if len(fields) == 5: 
                    bet = Bet(self.sockets_id[id], fields[0], fields[1], fields[2], fields[3], fields[4])
                    bets.append(bet)
                else:
                    isSuccess = False
            if len(bets) != bets_length:
                isSuccess = False
            total_bets_received += len(bets)
            if not isSuccess:
                client_sock.sendall(b'\x02')
                logging.info(f'action: apuesta_recibida | result: fail | cantidad: {bets_length - len(bets)}')
            else:
                client_sock.sendall(b'\x00')

            logging.info(f'action: apuesta_recibida | result: success | cantidad: {total_bets_received}')
            store_bets(bets)       


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            request = client_sock.recv(byte).decode('utf-8')
            if request == 'B':
                logging.info(f'el server recibe B')

                self.__handle_batches(client_sock)
            if request == 'W':
                logging.info(f'el server recibe W')
                self.__handle_lottery(client_sock)

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            client_sock.sendall(b'\x01')
        finally:
            client_sock.close()
            self.clients_sockets.remove(client_sock)


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
