package common


import (
	"io"	
	"encoding/binary"
	"net"
	"time"
	"fmt"
	"os"
	"strings"
	"os/signal"
	"syscall"
	"bytes"
	"github.com/op/go-logging"
)

var response int = 1
var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            	string
	ServerAddress 	string
	LoopAmount   	int
	LoopPeriod    	time.Duration
	BatchMaxAmount	int
}

type ClientBet struct {
	Name      string
	Lastname  string
	DNI       string
	Birthdate string
	Number    string
}

// Client Entity that encapsulates how
type Client struct {
	config 		ClientConfig
	conn   		net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(batches []string) {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-sigs
		log.Infof("Client %v: Received SIGTERM. Closing connection", c.config.ID)
		if c.conn != nil {
			c.conn.Close()
		}
		os.Exit(0)
	}()


	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()
	c.ManageBets(batches)
	time.Sleep(c.config.LoopPeriod)
	
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


func sendHeader(conn net.Conn, batch int, batchAmount int) {
	// Envía el encabezado con el tamaño del batch y la cantidad máxima de apuestas.

	batchSize := uint32(batch)
	maxAmount := uint32(batchAmount)

	// Crear un buffer para escribir todos los datos juntos
	var buf bytes.Buffer

	// Escribir los datos en orden
	binary.Write(&buf, binary.BigEndian, batchSize)  // 4 bytes - tamaño del batch
	binary.Write(&buf, binary.BigEndian, maxAmount)  // 4 bytes - cantidad máxima de apuestas por batch
	// Escribir el buffer en la conexión
	_, err := conn.Write(buf.Bytes())
	if err != nil {
		log.Errorf("Error al enviar el header: %v", err)
	}
}

func (c *Client) ShowResult(buf byte) {
	var result string
	switch buf {
	case 0:
		result = "success"
	case 1:
		result = "fail"
	case 2:
		result = "fail/success"
	default:
		log.Errorf("action: send_bet | result: fail | client_id: %v | error: unknown response %v",
			c.config.ID, buf)
		return
	}
	log.Infof("action: apuesta_enviada | result: %v ", result)
}

func (c *Client) receiveWinners() ([]string, error)  {
	// Leer los primeros 4 bytes para obtener el tamaño
	sizeBuf := make([]byte, 4)
	_, err := io.ReadFull(c.conn, sizeBuf)
	if err != nil {
		return nil, fmt.Errorf("error leyendo tamaño del mensaje: %w", err)
	}

	var size uint32
	buf := bytes.NewReader(sizeBuf)
	if err := binary.Read(buf, binary.BigEndian, &size); err != nil {
		return nil, fmt.Errorf("error convirtiendo tamaño: %w", err)
	}

	// Leer exactamente 'size' bytes del mensaje
	messageBuf := make([]byte, size)
	_, err = io.ReadFull(c.conn, messageBuf)
	if err != nil {
		return nil, fmt.Errorf("error leyendo mensaje completo: %w", err)
	}

	messageStr := string(messageBuf)
	winners := strings.Split(messageStr, ";")
	return winners, nil
}

func (c *Client) ManageBets(batches []string) {
	// Envía apuestas en lotes al servidor y gestiona las respuestas.

	for _, batch := range batches {

		sendHeader(c.conn, len(batch), len(strings.Split(batch, ";")))
		io.WriteString(c.conn, batch)

		buf := make([]byte, response) // Buffer para un solo byte
		n, err := c.conn.Read(buf)	
		if err != nil {
			log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
				c.config.ID, err)
			return
		}
		if n == 0 {
			log.Errorf("action: send_bet | result: fail | client_id: %v | error: no data received",
				c.config.ID)
			return
		}
		c.ShowResult(buf[0])
	}
	c.conn.Write([]byte{0, 0, 0, 0})
	winners, error_winners := c.receiveWinners()
	if error_winners != nil {
		log.Errorf("action: receive_winners | result: fail | client_id: %v | error: %v",
			c.config.ID, error_winners)		
		return
	}

	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(winners))

}

