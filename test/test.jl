include("../CircuitS.jl")

circuit = create_circuit()
add_element([Voltage, "Ug", 1, 0], circuit)
add_element([OpAmp, "OpAmp1", [1, 4], 5], circuit)
add_element([OpAmp, "OpAmp2", [1, 2], 3], circuit)
add_element([Resistor, "R1", 4, 0], circuit)
add_element([Resistor, "R3", 5, 2], circuit)
add_element([Resistor, "R4", 2, 3], circuit)
add_element([Resistor, "R5", 1, 3], circuit)
add_element([Capacitor, "C2", 4, 5], circuit)


# circuit = create_circuit()
# add_element([Voltage, "Ug", 1, 0], circuit)
# add_element([VCVS, "VCVS", [1, 0], [2, 3], "m" ], circuit)
# add_element([Resistor, "R1", 2, 3], circuit)

# circuit = create_circuit()
# add_element([VCCS, "VCCS1", [1, 0], [2, 0], "a1"], circuit)
# add_element([VCCS, "VCCS2", [2, 0], [2, 0], "a2"], circuit)
# add_element([VCCS, "VCCS3", [2, 0], [3, 0], "a3"], circuit)
# add_element([VCCS, "VCCS4", [3, 0], [0, 2], "a4"], circuit)
# add_element([Resistor, "R1", 4, 1], circuit)
# add_element([Capacitor, "C1", 2, 0,], circuit)
# add_element([Capacitor, "C2", 3, 0], circuit)
# add_element([Voltage, "Ug", 4, 0], circuit)




init_circuit(circuit)
result = simulate(circuit)

println(result)