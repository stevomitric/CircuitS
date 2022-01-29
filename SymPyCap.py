# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 00:24:14 2020
@authors: 
    Katarina Stanković (sk180183d@student.etf.bg.ac.rs)
    Matija Dodović (dm180072d@student.etf.bg.ac.rs)
"""
import sympy
from sympy import I as j
from sympy.functions import exp
class Circuit(object):    
    def __init__(self, element_list):
        """
        
        Parameters
        ----------
        element_list : list
            list of all electric circuit elements defined in the documentation:
            https://github.com/mdodovic/SymPyCAP/blob/main/documentation/Documentation.pdf
        Returns
        -------
        None.
        """
        self.element_list = element_list
        self.number_of_nodes = self.__number_of_nodes()
        self.node_currents = [] # J
        self.node_potentials = [] # V
        self.voltage_equations = [] # JJ
        self.current_variables = [] # VV
        self.element_symbols = {} # electric circuit symbols
        
        self.equations = []
        self.variables = []
        self.time_domain = False
        
        self.solutions = {}       
        self.replacement_rule = {}
        self.evaluated_solutions = {}
        
        self.correct_solution_flag = True
        self.solution_at_specific_frequency = True
        
    def __node_currents_init(self):
        self.node_currents = [0 for i in range(self.number_of_nodes)]
    
    def __potential_symbols_definition(self):
        self.node_potentials = [sympy.symbols('V' + str(i)) for i in range(self.number_of_nodes)]
        self.node_potentials[0] = 0 # potential of node 0 is equal to 0
        
    def __number_of_nodes(self):
        nodes = {0} # ground node is always necessary
        for element in self.element_list:                
            if isinstance(element[2], list):
                nodes.add(element[2][0])
                nodes.add(element[2][1])
            else:
                nodes.add(element[2])
                nodes.add(element[3])
            
        return max(nodes) + 1
        
    def __make_MNA_equation(self, element):
        type_of_element = element[0]
        symbol = self.element_symbols[element[1]]
        
        if type_of_element == 'R':
            node_A = element[2] # plus node
            node_B = element[3] # minus node
            R = symbol
            self.node_currents[node_A] += (self.node_potentials[node_A] - self.node_potentials[node_B]) / R
            self.node_currents[node_B] += (self.node_potentials[node_B] - self.node_potentials[node_A]) / R
            return True
        
        elif type_of_element == 'V':
            node_A = element[2]
            node_B = element[3]
            Ug = symbol 
            IUg = sympy.symbols('I' + element[1]) 
            self.node_currents[node_A] += IUg
            self.node_currents[node_B] -= IUg 
            self.voltage_equations.append(self.node_potentials[node_A] - self.node_potentials[node_B] - Ug)
            self.current_variables.append(IUg)
            return True

        elif type_of_element == 'OpAmp':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B = element[3]

            IOpAmp = sympy.symbols('I' + element[1])  

            self.node_currents[node_B] += IOpAmp
            self.voltage_equations.append(self.node_potentials[node_A1] - self.node_potentials[node_A2])
            self.current_variables.append(IOpAmp)
            return True
        
        elif type_of_element == 'I':
            node_A = element[2]
            node_B = element[3]
            Ig = symbol
            self.node_currents[node_A] += Ig
            self.node_currents[node_B] -= Ig 
            return True
        
        elif type_of_element == 'VCVS':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            amplification = sympy.symbols(element[4])
            I2 = sympy.symbols('I' + element[1])
            self.node_currents[node_B1] += I2
            self.node_currents[node_B2] -= I2
            eq = self.node_potentials[node_B1] - self.node_potentials[node_B2] - \
                amplification * (self.node_potentials[node_A1] - self.node_potentials[node_A2])
            self.voltage_equations.append(eq)
            self.current_variables.append(I2)
            return True

        elif type_of_element == 'VCCS':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            transconductance = sympy.symbols(element[4])
            self.node_currents[node_B1] += transconductance * (self.node_potentials[node_A1] - self.node_potentials[node_A2])
            self.node_currents[node_B2] -= transconductance * (self.node_potentials[node_A1] - self.node_potentials[node_A2])
            return True

        elif type_of_element == 'CCCS':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            amplification = sympy.symbols(element[4])
            I1 = sympy.symbols('I' + element[1])
            self.node_currents[node_A1] += I1
            self.node_currents[node_A2] -= I1
            self.node_currents[node_B1] += amplification * I1
            self.node_currents[node_B2] -= amplification * I1
            self.voltage_equations.append(self.node_potentials[node_A1] - self.node_potentials[node_A2])
            self.current_variables.append(I1)
            return True

        elif type_of_element == 'CCVS':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            transresistance = sympy.symbols(element[4])
            I2 = sympy.symbols('I' + element[1])
            self.node_currents[node_A1] += (self.node_potentials[node_B1] - self.node_potentials[node_B2])/transresistance
            self.node_currents[node_A2] -= (self.node_potentials[node_B1] - self.node_potentials[node_B2])/transresistance
            self.node_currents[node_B1] += I2
            self.node_currents[node_B2] -= I2
            self.voltage_equations.append(self.node_potentials[node_A1] - self.node_potentials[node_A2])
            self.current_variables.append(I2)
            return True

        elif type_of_element == 'L':
            node_A = element[2]
            node_B = element[3]
            I0 = 0
            if len(element) == 5:
                I0 = sympy.Symbol(element[4])

            if self.time_domain == True:
                 I0 = 0
            L = symbol
            self.node_currents[node_A] += (self.node_potentials[node_A] - self.node_potentials[node_B]) / (self.s * L) + I0 / self.s
            self.node_currents[node_B] += (self.node_potentials[node_B] - self.node_potentials[node_A]) / (self.s * L) - I0 / self.s
            return True
            
        elif type_of_element == 'C':
            node_A = element[2]
            node_B = element[3]
            U0 = 0
            if len(element) == 5:
                U0 = sympy.Symbol(element[4])

            if self.time_domain == True:
                 U0 = 0
            C = symbol
            self.node_currents[node_A] += (self.node_potentials[node_A] - self.node_potentials[node_B]) * self.s * C - U0 * C
            self.node_currents[node_B] += (self.node_potentials[node_B] - self.node_potentials[node_A]) * self.s * C + U0 * C
            
            return True

        elif type_of_element == 'IdealT':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]

            IT = sympy.symbols('I' + element[1])  
            m = sympy.symbols(element[4])
            
            self.node_currents[node_A1] += IT
            self.node_currents[node_A2] -= IT
            self.node_currents[node_B1] += - m * IT
            self.node_currents[node_B2] -= m * IT
            
            self.voltage_equations.append(self.node_potentials[node_A1] - self.node_potentials[node_A2] - m * (self.node_potentials[node_B1] - self.node_potentials[node_B2]))
            self.current_variables.append(IT)
                        
            return True

        elif type_of_element == 'InductiveT':
            
            # L1, L2, L12, I01, I02
            
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            
            L1 = sympy.symbols(element[4][0])
            L2 = sympy.symbols(element[4][1])
            L12 = sympy.symbols(element[4][2]) 

            I01 = 0
            I02 = 0

            if len(element) == 6:  
                if element[5][0] != 0:
                    I01 = sympy.Symbol(element[5][0])
                if element[5][1] != 0:
                    I02 = sympy.Symbol(element[5][1])
                
            if self.time_domain == True:
                I01 = 0
                I02 = 0
            
            IK_A = sympy.symbols('I' + element[1] + "_" + str(node_A1))
            IK_B = sympy.symbols('I' + element[1] + "_" + str(node_B1))
    
            self.node_currents[node_A1] += IK_A
            self.node_currents[node_A2] -= IK_A
            self.node_currents[node_B1] += IK_B
            self.node_currents[node_B2] -= IK_B
            
            self.voltage_equations.append(
                self.node_potentials[node_A1] - self.node_potentials[node_A2] - 
                ( L1 * self.s * IK_A - L1 * I01 + 
                L12 * self.s * IK_B - L12 * I02 ) )
            
            self.voltage_equations.append(
                self.node_potentials[node_B1] - self.node_potentials[node_B2] - 
                ( L12 * self.s * IK_A - L12 * I01 + 
                L2 * self.s * IK_B - L2 * I02 ) )
            
            self.current_variables.append(IK_A)
            self.current_variables.append(IK_B)
            
            return True
        
        elif type_of_element == '4-A':
            
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]

            a11 = sympy.symbols(element[4][0])
            a12 = sympy.symbols(element[4][1])
            a21 = sympy.symbols(element[4][2]) 
            a22 = sympy.symbols(element[4][3]) 

            IA_A = sympy.symbols('I' + element[1] + "_" + str(node_A1))
            IA_B = sympy.symbols('I' + element[1] + "_" + str(node_B1))
        
            self.node_currents[node_A1] += IA_A
            self.node_currents[node_A2] -= IA_A
            self.node_currents[node_B1] -= IA_B
            self.node_currents[node_B2] += IA_B

            self.voltage_equations.append(
                self.node_potentials[node_A1] - self.node_potentials[node_A2] - 
                (a11 * self.node_potentials[node_B1] - self.node_potentials[node_B2]
                 + a12 * IA_B) 
            )

            self.voltage_equations.append(
                IA_A - 
                (a21 * self.node_potentials[node_B1] - self.node_potentials[node_B2]
                 + a22 * IA_B) 
            )
             
            self.current_variables.append(IA_A)
            self.current_variables.append(IA_B)                
            
            return True

        elif type_of_element == 'Z':
            node_A = element[2] # plus node
            node_B = element[3] # minus node
            Z = symbol
            self.node_currents[node_A] += (self.node_potentials[node_A] - self.node_potentials[node_B]) / Z
            self.node_currents[node_B] += (self.node_potentials[node_B] - self.node_potentials[node_A]) / Z            

            return True

        elif type_of_element == 'Y':
            node_A = element[2] # plus node
            node_B = element[3] # minus node
            Y = symbol
            self.node_currents[node_A] += (self.node_potentials[node_A] - self.node_potentials[node_B]) * Y
            self.node_currents[node_B] += (self.node_potentials[node_B] - self.node_potentials[node_A]) * Y

            return True
        
        elif type_of_element == 'T' and self.time_domain:
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            Zc = element[4][0] # sympy.symbols(element[4][0])
            theta = element[4][1] # sympy.symbols(element[4][1]) 
            
            IA_A = sympy.symbols('I' + element[1] + "_" + str(node_A1))
            IA_B = sympy.symbols('I' + element[1] + "_" + str(node_B1))
            
            self.node_currents[node_A1] += IA_A
            self.node_currents[node_A2] -= IA_A
            self.node_currents[node_B1] -= IA_B
            self.node_currents[node_B2] += IA_B
            
            self.voltage_equations.append(
                self.node_potentials[node_A1] - self.node_potentials[node_A2] 
                - (sympy.cos(theta)*(self.node_potentials[node_B1] - self.node_potentials[node_B2]) + 
                   j*Zc*sympy.sin(theta)*IA_B)
                )
            
            self.voltage_equations.append(
                IA_A - (j*(1/Zc)*sympy.sin(theta)*(self.node_potentials[node_B1] - self.node_potentials[node_B2]) + 
                   sympy.cos(theta)*IA_B)
                )
            
            self.current_variables.append(IA_A)
            self.current_variables.append(IA_B) 
            
            return True
        
        elif type_of_element == 'T':
            node_A1 = element[2][0]
            node_A2 = element[2][1]
            node_B1 = element[3][0]
            node_B2 = element[3][1]
            Zc = element[4][0] # sympy.symbols(element[4][0])
            tau = element[4][1] # sympy.symbols(element[4][1]) 
            
            IA_A = sympy.symbols('I' + element[1] + "_" + str(node_A1))
            IA_B = sympy.symbols('I' + element[1] + "_" + str(node_B1))
            
            self.node_currents[node_A1] += IA_A
            self.node_currents[node_A2] -= IA_A
            self.node_currents[node_B1] += IA_B
            self.node_currents[node_B2] -= IA_B
            
            self.voltage_equations.append(
                self.node_potentials[node_A1] - self.node_potentials[node_A2] 
                - (Zc*IA_A + Zc*IA_B*exp(-tau*self.s) + 
                   (self.node_potentials[node_B1] - self.node_potentials[node_B2])*exp(-tau*self.s))
                )
            
            self.voltage_equations.append(
                self.node_potentials[node_B1] - self.node_potentials[node_B2] 
                - (Zc*IA_B + Zc*IA_A*exp(-tau*self.s) + 
                   (self.node_potentials[node_A1] - self.node_potentials[node_A2])*exp(-tau*self.s))
                )
            
            self.current_variables.append(IA_A)
            self.current_variables.append(IA_B) 
            
            return True

        #------------- In progress -------------------------------------------- 
        elif type_of_element == '4-R':
            #...
            
            #return True
            return False

        elif type_of_element == '4-G':
            #...
            
            #return True
            return False

        elif type_of_element == '4-H':
            #...
            
            #return True
            return False

        else:
            return False
        
    def __reinitialization(self):        
        self.voltage_equations = [] # JJ
        self.current_variables = [] # VV
        self.time_domain = False
        self.solutions = {} 
        self.replacement_rule = {} 

    def __make_replacement_rule(self, list_of_rules):  
        self.replacement_rule = list_of_rules
        
    def __replace_by_rule(self):
        if self.replacement_rule != {}:
            self.evaluated_solutions = {str(var): sol for var, sol in self.solutions.items()}
            
            for elem, val in self.replacement_rule.items():    
                for unknown, solution in self.evaluated_solutions.items():
                    self.evaluated_solutions[unknown] = solution.subs(elem, val, simultaneous = True)
            
    def symPyCAP(self, **kwargs):
        
        """
        Parameters
        ----------
        Possible keyworded arguments are:
            w -- symbol/symbolic expression of frequency for time invariant analysis
            omega -- another name for w
            r -- dictionary of replacements in the form: {..., "id" : symbolic_value, ...}
            replacement -- another name for r
        Returns
        -------
        dictionary
            Keys are potentials and specific currents, values are solutions 
        """

        #------------- Empty all reused elements ------------------------------
        omega = ""
        self.__reinitialization()
        
        #------------- Reading values for omega and replacement list ----------
        for arg in kwargs:
            if arg == "w" or arg == "omega":
                omega = kwargs.get(arg)
            if arg == "replacement" or arg == "r":
                 self.__make_replacement_rule(kwargs.get(arg))
        
        #------------- Time (in)variant analysis ------------------------------
        if omega == "":
            self.time_domain = False
            self.s = sympy.Symbol('s')
        else:
            self.time_domain = True
            if  isinstance(omega, str):
                self.s = j*sympy.Symbol(omega)
            else:
                self.s = j*(omega)
            
        #------------ Init of J = {0} and V to symbols Vi ---------------------
        self.__node_currents_init()
        self.__potential_symbols_definition() # define Vi potentials 
        
        #-------------- Init of user defined symbols --------------------------
        for element in self.element_list:
            self.element_symbols[element[1]] = sympy.symbols(element[1])

        #------------- For every element in circuit, creating MNA equations ---
        result = list(map(self.__make_MNA_equation, self.element_list))

        #------------- Check validity of every element: TRY-CATCH-FINALLY -----
        for validation in result:
            if not validation:
                print("Unknown element:", self.element_list[result.index(validation)][0])
                return[]
                
        #------------- Solving linear system of equations by variables --------
        self.equations = self.node_currents[1:self.number_of_nodes]
        self.equations.extend(self.voltage_equations)    
        
        self.variables = self.node_potentials[1:self.number_of_nodes]
        self.variables.extend(self.current_variables)

        #------------- Returning solution -------------------------------------
        if omega == "":        
            #------------- System is linear, use linsolve ---------------------
            solutions = sympy.linsolve(self.equations, self.variables)

            if len(solutions) == 0:
                self.solutions = {}
                self.correct_solution_flag = False
            else:
                self.variables = [str(variable) for variable in self.variables]
                self.solutions = dict(zip(self.variables, next(iter(solutions)))) 
                
        else:
            #------------- System is complex, use most general solver ---------
            solutions = sympy.solve(self.equations, self.variables)            

            if len(solutions) == 0:
                self.solutions = {}
                self.correct_solution_flag = False
            else:
                self.solutions = {str(var): sol for var, sol in solutions.items()}

        self.__replace_by_rule()

        for sol in self.evaluated_solutions:
            if self.evaluated_solutions[str(sol)].has(sympy.zoo):
                self.solution_at_specific_frequency = False
                
    def electric_circuit_specifications(self):
        print("Circuit specifications: ")
        print("Number of nodes: " + str(self.number_of_nodes))
        print("Input elements:")
        for element in self.element_list:
            print(element)
        print("Replacement rule: ",self.replacement_rule)
        print("Equations: ", self.equations)
        print("Variables: ", self.variables)
        if self.time_domain == True:
            print("Frequency: ", (-self.s * j))
        print()

    def print_solutions(self):      
        if self.correct_solution_flag == False:
            print("Solution does not exist!")
            return
        if self.solutions == {}:
            print("Solutions aren't computed yet!")
        else:
            for sol in self.solutions:
                print(sol, ":", sympy.simplify(self.solutions[str(sol)]),"\n")
    
    def print_specific_solutions(self):
        if self.correct_solution_flag == False:
            print("Solution does not exist!")
            return

        if self.solution_at_specific_frequency == False:
            print("Steady-state response does not exist at frequency " + str(-self.s * j))
            return
        
        if self.solutions == {}:
            print("Solutions aren't computed yet!")
        else:
            if self.evaluated_solutions == {}:
                print("A replacement rule hasn't been forwarded!")
            else:
                for sol in self.evaluated_solutions:
                    print(sol, ":", sympy.simplify(self.evaluated_solutions[str(sol)]),"\n")

    def get_solutions(self):
        return self.solutions
    
    def get_specific_solutions(self):
        return self.evaluated_solutions

if __name__ == "__main__":
    obj = Circuit([ ["V","Ug",0,1], ["R", "R1",0,1], ["R","R2",0,1] ])
    obj.symPyCAP()
    obj.print_solutions()
    print(obj.number_of_nodes)