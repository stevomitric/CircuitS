include("../CircuitS.jl")

circuit = create_circuit()
add_element([VCCS, "VCCS", [1, 0], [2, 3], "A1"], circuit)
add_element([CCCS, "CCCS", [2, 3], [4, 5], "A2"], circuit)
add_element([Resistor, "R1", 4, 5], circuit)
add_element([Voltage, "Ug", 1, 0], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)