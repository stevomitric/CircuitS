include("../CircuitS.jl")

circuit = create_circuit()
add_element([Resistor, "R1", 0, 2], circuit)
add_element([Resistor, "R2", 2, 3], circuit)
add_element([Resistor, "R3", 0, 3], circuit)
add_element([Resistor, "R4", 4, 1], circuit)
add_element([Voltage, "Ug", 4, 0], circuit)
add_element([OpAmp, "OpAmp", [1, 2], 3], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)