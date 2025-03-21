import csv
import datetime
import time


""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574

def convertByteToNumber(byte: int) -> int:
    return (byte[0] << 24) | (byte[1] << 16) | (byte[2] << 8) | byte[3]

def int_to_bytes(n, length=4):
    """Convierte un entero en una secuencia de bytes de longitud fija (4 bytes)."""
    return bytes([(n >> (8 * i)) & 0xFF for i in range(length - 1, -1, -1)])

def send_message(sock, message):
    encoded_message = message.encode('utf-8')  # Convertir el string a bytes
    message_length = len(encoded_message)      # Obtener el tamaño
    length_bytes = int_to_bytes(message_length)  # Convertir tamaño a 4 bytes
    
    sock.sendall(length_bytes + encoded_message)  # Enviar tamaño + mensaje

def get_winners():
    bets_saved = load_bets()
    winners_by_agency = {} 
    for bet in bets_saved:
        if has_won(bet): 
            if bet.agency not in winners_by_agency:
                winners_by_agency[bet.agency] = []  
            winners_by_agency[bet.agency].append(bet.document) 
    
    return winners_by_agency

""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

