package common

import (
	"encoding/csv"
	"os"
	"strings"
)

// ReadBetsFromCSV lee un archivo CSV y divide los datos en lotes según batchMaxAmount y batchMaxSize
func ReadBetsFromCSV(filePath string, batchMaxAmount int, batchMaxSize int) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var batches []string
	var currentBatch []string
	currentSize := 0

	for _, record := range records {
		line := strings.Join(record, "|")
		lineSize := len(line) + 1 // +1 por el `;` que agregaremos después

		// Si agregar esta línea excede las restricciones, guardamos el batch actual y creamos uno nuevo
		if len(currentBatch) >= batchMaxAmount || (currentSize+lineSize) > batchMaxSize {
			batches = append(batches, strings.Join(currentBatch, ";"))
			currentBatch = []string{}
			currentSize = 0
		}

		// Agregar línea al batch actual
		currentBatch = append(currentBatch, line)
		currentSize += lineSize
	}

	// Guardar el último batch si tiene datos
	if len(currentBatch) > 0 {
		batches = append(batches, strings.Join(currentBatch, ";"))
	}

	return batches, nil
}
