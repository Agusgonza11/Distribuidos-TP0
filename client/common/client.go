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

// ClientConfig almacena la configuración utilizada por el cliente.
type ClientConfig struct {
	ID            string   
	ServerAddress string   
	LoopAmount    int       
	LoopPeriod    time.Duration 
	BatchMaxAmount int        
}

// Client representa una entidad cliente que interactúa con el servidor.
type Client struct {
	config ClientConfig // Configuración del cliente
	conn   net.Conn    // Conexión con el servidor
}

// NewClient inicializa un nuevo cliente con la configuración dada.
func NewClient(config ClientConfig) *Client {
	return &Client{config: config}
}

// createClientSocket inicializa un socket para conectarse al servidor.
// Si falla, registra el error y devuelve nil.
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID, err,
		)
		return err
	}
	c.conn = conn
	return nil
}

// StartClientLoop maneja la conexión del cliente con el servidor.
// Se encarga de enviar apuestas y solicitar ganadores.
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

	c.createClientSocket()
	c.ManageBets(batches)
	c.requestWinners()
	time.Sleep(c.config.LoopPeriod)
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


// ShowResult muestra el resultado de la transacción basada en la respuesta del servidor.
func (c *Client) ShowResult(buf byte) {
	var result string
	switch buf {
	case 0:
		result = "success"
	case 1:
		result = "fail"
	case 2:
		result = "partial success"
	default:
		log.Errorf("action: send_bet | result: fail | client_id: %v | error: unknown response %v", c.config.ID, buf)
		return
	}
	log.Infof("action: apuestas_enviadas | result: %v", result)
}

// requestWinners solicita los ganadores al servidor.
func (c *Client) requestWinners() {
	for {
		c.createClientSocket()
		c.conn.Write([]byte{'W'})
		log.Infof("El cliente está solicitando Winners")

		buffer := make([]byte, 1)
		_, err := c.conn.Read(buffer)
		if err != nil {
			log.Errorf("Error al leer del socket: %v", err)
			c.conn.Close()
			return
		}

		switch buffer[0] {
		case 'R':
			log.Infof("No finalizó el sorteo, volver a intentar")
			c.conn.Close()
			time.Sleep(c.config.LoopPeriod)
			continue

		case 'S':
			log.Infof("El sorteo ha finalizado")
			var buf bytes.Buffer
			fixedID := make([]byte, 4)
			copy(fixedID, c.config.ID)
			buf.Write(fixedID)
			_, err := c.conn.Write(buf.Bytes())
			if err != nil {
				log.Errorf("Error al enviar el header: %v", err)
				c.conn.Close()
				return
			}

			winners, err := c.receiveWinners()
			if err != nil {
				log.Errorf("action: receive_winners | result: fail | client_id: %v | error: %v", c.config.ID, err)
				c.conn.Close()
				return
			}

			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(winners))
			c.conn.Close()
			return
		}
	}
}

// receiveWinners recibe los ganadores del servidor.
func (c *Client) receiveWinners() ([]string, error) {
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

	messageBuf := make([]byte, size)
	_, err = io.ReadFull(c.conn, messageBuf)
	if err != nil {
		return nil, fmt.Errorf("error leyendo mensaje completo: %w", err)
	}

	messageStr := string(messageBuf)
	if messageStr == "" {
		return []string{}, nil
	}
	return strings.Split(messageStr, ";"), nil
}

// sendHeader envía un encabezado con información sobre el batch al servidor.
func sendHeader(conn net.Conn, batch int, batchAmount int) {
	batchSize := uint32(batch)
	maxAmount := uint32(batchAmount)

	var buf bytes.Buffer
	binary.Write(&buf, binary.BigEndian, batchSize)
	binary.Write(&buf, binary.BigEndian, maxAmount)

	_, err := conn.Write(buf.Bytes())
	if err != nil {
		log.Errorf("Error al enviar el header: %v", err)
	}
}

// ManageBets maneja el envío de apuestas al servidor.
func (c *Client) ManageBets(batches []string) {
	c.conn.Write([]byte{'B'})
	log.Infof("El cliente está enviando Bets")

	for _, batch := range batches {
		// log.Infof("El cliente esta enviando la %v batch de %v", i, len(batches))

		sendHeader(c.conn, len(batch), len(strings.Split(batch, ";")))
		io.WriteString(c.conn, batch)

		buf := make([]byte, response)
		n, err := c.conn.Read(buf)
		if err != nil || n == 0 {
			log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v", c.config.ID, err)
			return
		}
		//c.ShowResult(buf[0])
	}
	log.Infof("El cliente termino de enviar las bets")
	c.conn.Write([]byte{0, 0, 0, 0})
	c.conn.Close()
}
