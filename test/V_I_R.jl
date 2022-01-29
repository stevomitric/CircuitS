include("../CircuitS.jl")
#using CircuitS

circuit = create_circuit()
add_element([Resistor, "R1", 4, 3], circuit)
add_element([Resistor, "R2", 0, 3], circuit)
add_element([Resistor, "R3", 0, 1], circuit)
add_element([Voltage, "Ug", 0, 4], circuit)
add_element([Current, "Ig", 1, 0], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)