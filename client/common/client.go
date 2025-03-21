package common


import (
	"io"	
	"encoding/binary"
	"net"
	"time"
	"os"
	"strings"
	"os/signal"
	"syscall"
	"bytes"
	"github.com/op/go-logging"
)

var header int = 12
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

	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()
		c.ManageBets(batches)
		time.Sleep(c.config.LoopPeriod)
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}


func sendHeader(conn net.Conn, batch int, batchAmount int) {
	batchSize := uint32(batch)
	maxAmount := uint32(batchAmount)

	// Crear un buffer para escribir todos los datos juntos
	var buf bytes.Buffer

	// Escribir los datos en orden
	binary.Write(&buf, binary.BigEndian, batchSize)  // 4 bytes - tamaño del batch
	binary.Write(&buf, binary.BigEndian, maxAmount)  // 4 bytes - cantidad máxima de apuestas por batch
}

func (c *Client) ManageBets(batches []string) {
	for _, batch := range batches {
		sendHeader(c.conn, len(batch), len(strings.Split(batch, ";")))
		io.WriteString(c.conn, batch)

		buf := make([]byte, 1) // Buffer para un solo byte
		_, err := c.conn.Read(buf)	
		if err != nil {
			log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
				c.config.ID, err)
			return
		}
		var result string
		if buf[0] == 0 {
			result = "success"
		} else if buf[0] == 1 {
			result = "fail"
		} 
		log.Infof("action: apuesta_enviada | result: %v | batch: %v", result, batch)

	}
}

