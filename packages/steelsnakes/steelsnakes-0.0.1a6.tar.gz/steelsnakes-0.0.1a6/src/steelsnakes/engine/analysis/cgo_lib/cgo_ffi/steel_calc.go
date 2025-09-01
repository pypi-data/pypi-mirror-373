package main

import "C"
import (
	"encoding/json"
	"fmt"
)

// Simple steel calculation
type Input struct {
	SectionModulus float64 `json:"section_modulus"` // cm³
	YieldStrength  float64 `json:"yield_strength"`  // N/mm²
}

type Output struct {
	MomentCapacity float64 `json:"moment_capacity"` // Nmm
	Message        string  `json:"message"`
}

//export calculate
func calculate(jsonInput *C.char) *C.char {
	// Parse input
	var input Input
	if err := json.Unmarshal([]byte(C.GoString(jsonInput)), &input); err != nil {
		result := Output{0, fmt.Sprintf("Error: %v", err)}
		bytes, _ := json.Marshal(result)
		return C.CString(string(bytes))
	}

	// Simple calculation: M = S * fy * 1000
	capacity := input.SectionModulus * input.YieldStrength * 1000

	// Return result
	result := Output{capacity, "Success"}
	bytes, _ := json.Marshal(result)
	return C.CString(string(bytes))
}

func main() {} // Required for CGO
