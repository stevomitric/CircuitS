include("../CircuitS.jl")

circuit = create_circuit()
add_element([Impedance, "Z", 1, 0], circuit)
add_element([Admitance, "Y", 1, 0], circuit)
add_element([Voltage, "Ug", 1, 0], circuit)

init_circuit(circuit)
result = simulate(circuit)

println(result)