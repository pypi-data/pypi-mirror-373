package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Input struct {
	SectionModulus float64 `json:"section_modulus"`
	YieldStrength  float64 `json:"yield_strength"`
}

type Output struct {
	MomentCapacity float64 `json:"moment_capacity"`
	Message        string  `json:"message"`
}

func main() {
	var input Input

	// Read JSON from stdin
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		output := Output{0, fmt.Sprintf("Input error: %v", err)}
		json.NewEncoder(os.Stdout).Encode(output)
		return
	}

	// Calculate: M = S * fy * 1000
	capacity := input.SectionModulus * input.YieldStrength * 1000

	// Write JSON to stdout
	output := Output{capacity, "Success"}
	json.NewEncoder(os.Stdout).Encode(output)
}
