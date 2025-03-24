import socket
import logging
import sys
import signal
import time
import multiprocessing
from .utils import Bet, convertByteToNumber, get_winners, has_won, send_message
from .utils import store_bets

byte =  1
locks = {
    "get_winners": multiprocessing.Lock(),
    "agency_finish": multiprocessing.Lock(),
    "save_bets": multiprocessing.Lock(),
}
AGENCY_ID = 0
FINISH = 1

# agency_finish = {client peername = (agency_id, is_finish), ...}

class Server:
    def __init__(self, port, listen_backlog, expected_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients_sockets = []
        self.expected_clients = expected_clients
        self.winners = {}
        self.clients_processes = [] 
        self.locks = locks
        manager = multiprocessing.Manager()
        self.shared_data = manager.dict({"is_finish":  False, "agency_finish" : manager.dict(), "last_client_id": 0})


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
        for process in self.clients_processes:
            process.join() 
            logging.info(f'action: closing_process | result: success')
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
            # self.__handle_client_connection(client_sock)
            process = multiprocessing.Process(
                target=self.__handle_client_connection, args=(client_sock, self.locks)
            )
            process.daemon = True  # Permite que el proceso termine cuando el padre muera
            process.start()
            self.clients_processes.append(process)


    def __handle_lottery(self, client_sock, locks):
        """
        Handles the lottery request from the client.
        Sends the winners list if all agencies have finished, otherwise sends retry signal.
        """
        with locks["agency_finish"]:
            if len(self.shared_data["agency_finish"]) == int(self.expected_clients) and all(is_finish for _, is_finish in self.shared_data["agency_finish"]):
                if not self.shared_data["is_finish"]:
                    logging.info(f'action: sorteo | result: success')
                    self.shared_data["is_finish"] = True
                client_sock.sendall(b'S')  # Sending
                id = client_sock.recv(4).decode('utf-8').rstrip('\x00')
                with locks["get_winners"]:
                    winners = get_winners()
                    agency_id = self.shared_data["agency_finish"][client_sock.getpeername()[0]][AGENCY_ID]
                    winners_list = winners.get(agency_id, [])
                    send_message(client_sock, ';'.join(winners_list))
            else:
                client_sock.sendall(b'R')  # Retry



    def __handle_batches(self, client_sock, locks):
        """
        Handles batch processing of bets from a client.
        Stores received bets and sends appropriate responses.
        """
        while True:
            size = convertByteToNumber(client_sock.recv(4))
            if size == 0:
                with locks["agency_finish"]:
                    logging.info(f'lo que tengo en este lock es: {self.shared_data["agency_finish"]}')
                    self.shared_data["agency_finish"][client_sock.getpeername()[0]][FINISH] = True
                    break
            bets_length = convertByteToNumber(client_sock.recv(4))
            msg = client_sock.recv(size).decode('utf-8')
            isSuccess = True
            total_bets_received = 0
            bets = []
            for actual_bet in msg.split(";"):
                fields = actual_bet.split("|")
                if len(fields) == 5: 
                    bet = Bet(self.shared_data["agency_finish"][client_sock.getpeername()[0]][AGENCY_ID], fields[0], fields[1], fields[2], fields[3], fields[4])
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

            # logging.info(f'action: apuesta_recibida | result: success | cantidad: {total_bets_received}')
            with locks["save_bets"]:
                store_bets(bets)       

    def new_client(self, client_sock, locks):
        with locks["agency_finish"]:
            peername = client_sock.getpeername()[0]
            if peername not in self.shared_data["agency_finish"]:
                self.shared_data["agency_finish"][peername] = [self.shared_data["last_client_id"], False]
            self.shared_data["last_client_id"] += 1


    def __handle_client_connection(self, client_sock, locks):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self.new_client(client_sock, locks)
        try:
            request = client_sock.recv(byte).decode('utf-8')
            if request == 'B':
                logging.info(f'el server recibe Bets')
                self.__handle_batches(client_sock, locks)
            if request == 'W':
                logging.info(f'el server recibe solicitud de Winners')
                self.__handle_lottery(client_sock, locks)
                client_sock.close()
                self.clients_sockets.remove(client_sock)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            client_sock.sendall(b'\x01')


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
