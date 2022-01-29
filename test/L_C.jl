include("../CircuitS.jl")

circuit = create_circuit()
add_element([Resistor, "R1", 2, 4], circuit)
add_element([Resistor, "R2", 1, 0], circuit)
add_element([Capacitor, "C1", 2, 1], circuit)
add_element([Inductor, "L1", 1, 0], circuit)
add_element([Voltage, "Ug", 4, 0], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)