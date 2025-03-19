package common

import (
	"fmt"
	"io"	
	"encoding/binary"
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
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
	clientBet 	ClientBet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bet ClientBet) *Client {
	client := &Client{
		config: 	config,
		clientBet: 	bet,
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
func (c *Client) StartClientLoop() {
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
		c.ManageBet()
		time.Sleep(c.config.LoopPeriod)
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

// ManageBet serializa la apuesta del cliente y la envía al servidor.
func (c *Client) ManageBet() {
	// Serialize the bet
	betData := fmt.Sprintf("%s|%s|%s|%s|%s|%s",
	c.config.ID,
	c.clientBet.Name,
	c.clientBet.Lastname,
	c.clientBet.DNI,
	c.clientBet.Birthdate,
	c.clientBet.Number,
	)
	binary.Write(c.conn, binary.BigEndian, uint32(len(betData)))
	io.WriteString(c.conn, betData)
	buf := make([]byte, 1) // Buffer para un solo byte
	_, err := c.conn.Read(buf)	
	if err != nil {
		log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
			c.config.ID, err)
		return
	}
	var result string
	if buf[0] == 1 {
		result = "success"
	} else if buf[0] == 0 {
		result = "fail"
	} 
	log.Infof("action: apuesta_enviada | result: %v | dni: %v | numero: %v",
		result, c.clientBet.DNI, c.clientBet.Number)
}