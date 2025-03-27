package common

import (
	"net"
)

// Controla el short write
func sendExact(conn net.Conn, data []byte) error {
    totalSent := 0
    for totalSent < len(data) {
        sent, err := conn.Write(data[totalSent:])
        if err != nil {
            return err 
        }
        totalSent += sent
    }
    return nil
}

// Controla el short read
func recvExact(conn net.Conn, n int) ([]byte, error) {
    buf := make([]byte, n)
    totalRead := 0
    for totalRead < n {
        read, err := conn.Read(buf[totalRead:])
        if err != nil {
            return nil, err 
        }
        totalRead += read
    }
    return buf, nil
}
