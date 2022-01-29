include("../CircuitS.jl")

circuit = create_circuit()
add_element([TransmissionLine, "T", [1, 0], [2, 3], ["Zc", "t"]], circuit)
add_element([Resistor, "R1", 2, 3], circuit)
add_element([Voltage, "Ug", 1, 0], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)