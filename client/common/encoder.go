package common

import (
	"bytes"
	"encoding/binary"
	"net"
)

// EncodeString convierte un string en un slice de bytes con su tamaño al inicio
func EncodeString(msg string) []byte {
	length := uint32(len(msg)) // Tamaño del mensaje
	buf := new(bytes.Buffer)
	binary.Write(buf, binary.BigEndian, length) // Escribir tamaño
	buf.WriteString(msg)                        // Escribir mensaje
	return buf.Bytes()
}



// SendData envía un mensaje asegurándose de escribir todo
func SendData(conn net.Conn, data string) error {
	encoded := EncodeString(data)
	_, err := conn.Write(encoded) // Enviar mensaje serializado
	return err
}

// ReceiveData recibe un mensaje asegurando la lectura completa
func ReceiveData(conn net.Conn) (byte, error) {
	buf := make([]byte, 1)
	_, err := conn.Read(buf) // Leer 1 byte
	if err != nil {
		return 0, err
	}
	return buf[0], nil // Devolver el byte leído correctamente
}