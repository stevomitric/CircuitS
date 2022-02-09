using Symbolics

@enum ELEM_TYPE Resistor=1 Inductor Capacitor Voltage Current Impedance Admitance OpAmp ABCDElem VCVS VCCS CCVS CCCS IdealT InductiveT TransmissionLine

mutable struct Circuit
    elements::Array{Any}
    num_nodes::Int

    eq_current::Array{Any}
    eq_current_mult::Array{Any}
    eq_potential::Array{Any}
    var_voltage::Array{Any}
    var_current::Array{Any}
    var_element::Dict

    sym_s::Any
    time::Bool
end

function create_circuit()
    """Creates and returns a default circuit object"""
    circuit::Circuit = Circuit([], 0, [], [], [], [], [], Dict(), 0, false)
    return circuit
end

function add_element(elem, circuit::Circuit)
    """Adds 'elem' defined in format [TYPE, parms ...] to the circuit"""
    push!(circuit.elements, elem)
end

function init_circuit(circuit::Circuit)
    """Prepares the circuit for simulation"""
    
    # calculate number of nodes
    circuit.num_nodes = 0
    for elem in circuit.elements
        if (!(elem[4] isa Number))
            circuit.num_nodes = max(circuit.num_nodes, elem[3][1], elem[3][2], elem[4][1], elem[4][2])
        elseif (!(elem[3] isa Number))
            circuit.num_nodes = max(circuit.num_nodes, elem[3][1], elem[3][2], elem[4])
        else
            circuit.num_nodes = max(circuit.num_nodes, elem[3], elem[4])
        end
    end
    circuit.num_nodes += 1

    # Set base equation for KZS and node potential
    circuit.eq_current = [0 for item in 1:circuit.num_nodes]
    circuit.eq_current_mult = [1 for item in 1:circuit.num_nodes]
    circuit.eq_potential = [Symbolics.variables("V"*string(item) )[1] for item in 0:circuit.num_nodes-1]
    circuit.eq_potential[1] = 0

    # Create element symbols
    for elem in circuit.elements
        circuit.var_element[elem[2]] = Symbolics.variables(elem[2])[1]
    end
    
    # init s
    circuit.sym_s = Symbolics.variables("s")[1]

    # calculate equations from elements
    for elem in circuit.elements
        elemType::ELEM_TYPE = elem[1]

        if (elemType == Resistor || elemType == Impedance)
            circuit.eq_current_mult[ elem[3] + 1 ] *= circuit.var_element[elem[2]]
            circuit.eq_current_mult[ elem[4] + 1 ] *= circuit.var_element[elem[2]]
            circuit.eq_current[ elem[3] + 1 ] += (circuit.eq_potential[elem[3]+1] - circuit.eq_potential[elem[4]+1]) / circuit.var_element[elem[2]]
            circuit.eq_current[ elem[4] + 1 ] += (circuit.eq_potential[elem[4]+1] - circuit.eq_potential[elem[3]+1]) / circuit.var_element[elem[2]]
        elseif (elemType == Admitance)
            circuit.eq_current[ elem[3] + 1 ] += (circuit.eq_potential[elem[3]+1] - circuit.eq_potential[elem[4]+1]) * circuit.var_element[elem[2]]
            circuit.eq_current[ elem[4] + 1 ] += (circuit.eq_potential[elem[4]+1] - circuit.eq_potential[elem[3]+1]) * circuit.var_element[elem[2]]
        elseif (elemType == Inductor)
            I0 = if (length(elem) == 5 && !circuit.time) Symbolics.variables(elem[5])[1] else 0 end
            circuit.eq_current_mult[ elem[3] + 1 ] *= (circuit.sym_s * circuit.var_element[elem[2]])
            circuit.eq_current_mult[ elem[4] + 1 ] *= (circuit.sym_s * circuit.var_element[elem[2]])
            circuit.eq_current[ elem[3] + 1 ] += (circuit.eq_potential[elem[3]+1] - circuit.eq_potential[elem[4]+1]) / (circuit.sym_s * circuit.var_element[elem[2]]) + (I0/circuit.sym_s)
            circuit.eq_current[ elem[4] + 1 ] += (circuit.eq_potential[elem[4]+1] - circuit.eq_potential[elem[3]+1]) / (circuit.sym_s * circuit.var_element[elem[2]]) - (I0/circuit.sym_s)
        elseif (elemType == Capacitor)
            U0 = if (length(elem) == 5 && !circuit.time) Symbolics.variables(elem[5])[1] else 0 end
            circuit.eq_current[ elem[3] + 1 ] += (circuit.eq_potential[elem[3]+1] - circuit.eq_potential[elem[4]+1]) * circuit.sym_s * circuit.var_element[elem[2]] - U0*circuit.var_element[elem[2]]
            circuit.eq_current[ elem[4] + 1 ] += (circuit.eq_potential[elem[4]+1] - circuit.eq_potential[elem[3]+1]) * circuit.sym_s * circuit.var_element[elem[2]] + U0*circuit.var_element[elem[2]]
        elseif (elemType == Voltage)
            branch_current = Symbolics.variables("I_"*elem[2])[1]
            push!(circuit.var_current, branch_current)
            push!(circuit.var_voltage, circuit.eq_potential[elem[3]+1] - circuit.eq_potential[elem[4]+1] - circuit.var_element[elem[2]])
            circuit.eq_current[elem[3]+1] += branch_current
            circuit.eq_current[elem[4]+1] -= branch_current
        elseif (elemType == Current)
            circuit.eq_current[elem[3]+1] += circuit.var_element[elem[2]]
            circuit.eq_current[elem[4]+1] -= circuit.var_element[elem[2]]
        elseif (elemType == OpAmp)
            branch_current = Symbolics.variables("I_"*elem[2])[1]
            push!(circuit.var_current, branch_current)
            push!(circuit.var_voltage, (circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1]) )
            circuit.eq_current[elem[4]+1] += branch_current
        elseif (elemType == ABCDElem)
            a11, a12, a21, a22 = Symbolics.variables(elem[5][1])[1], Symbolics.variables(elem[5][2])[1], Symbolics.variables(elem[5][3])[1], Symbolics.variables(elem[5][4])[1]
            
            I_A, I_B = Symbolics.variables("I_"*elem[2]*"_"*string(elem[3][1]))[1], Symbolics.variables("I_"*elem[2]*"_"*string(elem[4][1]))[1]

            circuit.eq_current[elem[3][1]+1] += I_A
            circuit.eq_current[elem[3][2]+1] -= I_A
            circuit.eq_current[elem[4][1]+1] -= I_B
            circuit.eq_current[elem[4][2]+1] += I_B

            push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[4][1]+1] - (a11 * circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1] + a12*I_B ) )
            push!(circuit.var_voltage, I_A - (a21*circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1] + a22*I_B ) )

            push!(circuit.var_current, I_A)
            push!(circuit.var_current, I_B)
        elseif (elemType == VCVS)
            amp = Symbolics.variables(elem[5])[1]
            I = Symbolics.variables("I_"*elem[2])[1]
            circuit.eq_current[elem[4][1]+1] += I
            circuit.eq_current[elem[4][2]+1] -= I
            push!(circuit.var_voltage, circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1] - amp* (circuit.eq_potential[elem[3][1]+1] - elem[3][2]+1) )
            push!(circuit.var_current, I)
        elseif (elemType == VCCS)
            trans = Symbolics.variables(elem[5])[1]
            circuit.eq_current[elem[4][1]+1] += trans*(circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1])
            circuit.eq_current[elem[4][2]+1] -= trans*(circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1])
        elseif (elemType == CCCS)
            amp = Symbolics.variables(elem[5])[1]
            I = Symbolics.variables("I_"*elem[2])[1]
            circuit.eq_current[elem[3][1]+1] += I
            circuit.eq_current[elem[3][2]+1] -= I
            circuit.eq_current[elem[4][1]+1] += amp*I
            circuit.eq_current[elem[4][2]+1] -= amp*I
            push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1])
            push!(circuit.var_current, I)
        elseif (elemType == CCVS)
            trans = Symbolics.variables(elem[5])[1]
            I = Symbolics.variables("I_"*elem[2])[1]
            circuit.eq_current_mult[elem[3][1]+1] *= trans
            circuit.eq_current_mult[elem[3][2]+1] *= trans
            circuit.eq_current[elem[3][1]+1] += (circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1])/trans
            circuit.eq_current[elem[3][2]+1] -= (circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1])/trans
            circuit.eq_current[elem[4][1]+1] += I
            circuit.eq_current[elem[4][2]+1] -= I
            push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1])
            push!(circuit.var_current, I)
        elseif (elemType == IdealT)
            I = Symbolics.variables("I_"*elem[2])[1]
            m = Symbolics.variables(elem[5])[1]
            
            #TODO: struja transformatora ide u pogresnim smerovima? (2 linije ispod)
            circuit.eq_current[elem[3][1]+1] += I
            circuit.eq_current[elem[3][2]+1] -= I
            circuit.eq_current[elem[4][1]+1] += -m * I
            circuit.eq_current[elem[4][2]+1] -= -m * I
            
            eq = circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1] - m * (circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1])
            push!(circuit.var_voltage, eq)
            push!(circuit.var_current, I)
        elseif (elemType == InductiveT)
            L1 = Symbolics.variables(elem[5][1])[1]
            L2 = Symbolics.variables(elem[5][2])[1]
            L12 = Symbolics.variables(elem[5][3])[1]
            I01 = 0
            I02 = 0

            if length(elem) == 6 && !circuit.time
                if elem[6][1] != 0
                    I01 = Symbolics.variables(elem[6][1])[1]
                end
                if elem[6][2] != 0
                    I02 = Symbolics.variables(elem[6][2])[1]
                end
            end
            
            IK_A = Symbolics.variables("I_" * elem[2] * "_" * string(elem[3][1]))[1]
            IK_B = Symbolics.variables("I_" * elem[2] * "_" * string(elem[4][1]))[1]
    
            circuit.eq_current[elem[3][1]+1] += IK_A
            circuit.eq_current[elem[3][2]+1] -= IK_A
            circuit.eq_current[elem[4][1]+1] += IK_B
            circuit.eq_current[elem[4][2]+1] -= IK_B
            
            push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1] - ( L1 * circuit.sym_s * IK_A - L1 * I01 + 
            L12 * circuit.sym_s * IK_B - L12 * I02 ))
            push!(circuit.var_voltage, circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1] - ( L12 * circuit.sym_s * IK_A - L12 * I01 + 
            L2 * circuit.sym_s * IK_B - L2 * I02 ) )
        
            push!(circuit.var_current, IK_A)
            push!(circuit.var_current, IK_B)
        elseif (elemType == TransmissionLine)
            #TODO: Zasto Zc i tau NE treba da budu simboli?
            Zc = Symbolics.variables(elem[5][1])[1] #elem[5][1] 
            tau = Symbolics.variables(elem[5][2])[1] #elem[5][2]
            
            IA_A = Symbolics.variables("I_" * elem[2] * "_" * string(elem[3][1]))[1]
            IA_B = Symbolics.variables("I_" * elem[2] * "_" * string(elem[4][1]))[1]
            
            if (!circuit.time)
                circuit.eq_current[elem[3][1]+1] += IA_A
                circuit.eq_current[elem[3][2]+1] -= IA_A
                circuit.eq_current[elem[4][1]+1] += IA_B
                circuit.eq_current[elem[4][2]+1] -= IA_B
                
                push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1] - (Zc*IA_A + Zc*IA_B*exp(-tau*circuit.sym_s) + (circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[3][1]+1])*exp(-tau*circuit.sym_s)))
                push!(circuit.var_voltage, circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1] - (Zc*IA_B + Zc*IA_A*exp(-tau*circuit.sym_s) + (circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1])*exp(-tau*circuit.sym_s)))
            else
                theta = tau
                circuit.eq_current[elem[3][1]+1] += IA_A
                circuit.eq_current[elem[3][2]+1] -= IA_A
                circuit.eq_current[elem[4][1]+1] -= IA_B
                circuit.eq_current[elem[4][2]+1] += IA_B

                push!(circuit.var_voltage, circuit.eq_potential[elem[3][1]+1] - circuit.eq_potential[elem[3][2]+1] - (cos(theta)*(circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1]) + im*Zc*sin(theta)*IA_B))
                push!(circuit.var_voltage, IA_A - (im*(1/Zc)*sin(theta)*(circuit.eq_potential[elem[4][1]+1] - circuit.eq_potential[elem[4][2]+1]) + cos(theta)*IA_B))
            end
            
            push!(circuit.var_current, IA_A)
            push!(circuit.var_current, IA_B)
        end
    
    end

end

function simulate(circuit::Circuit)
    """Simulates the circuit by calculating all potentials and currents"""

    for i in 1:length(circuit.eq_current)
        circuit.eq_current[i] *= circuit.eq_current_mult[i]
        circuit.eq_current[i] = simplify(circuit.eq_current[i])
    end

    # equations to solve
    equations::Array{Num} = circuit.eq_current[2:length(circuit.eq_current)]
    equations = vcat(equations, circuit.var_voltage)
    tmp = [];
    for i in 1:length(equations)
        if (string(equations[i]) != "0")
            push!(tmp, equations[i])
        end
    end
    equations = tmp

    # variables to solve for
    variables::Array{Num} = circuit.eq_potential[2:length(circuit.eq_potential)]
    variables = vcat(variables, circuit.var_current)
    tmp = []
    for i in 1:length(variables)
        if ( occursin(string(variables[i]), string(equations)))
            push!(tmp, variables[i])
        end
    end
    variables = tmp

    println(equations)
    println(variables)

    #println(equations)
    #println(variables)
    #println(typeof(equations))
    #println(typeof(variables))

    #result = Symbolics.solve_for(equations, variables)
    #println("resenje: ")
    #println(result)
    result = Symbolics.solve_for(equations, variables, simplify=true)

    return result
end


# Test
# circuit = create_circuit()
# add_element([Resistor, "R1", 0, 1], circuit)
# add_element([Current, "Ig", 0, 1], circuit)
# init_circuit(circuit)
# result = simulate(circuit)

# print(result)