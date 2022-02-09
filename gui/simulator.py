from multiprocessing import Process, Queue
import time

from sympy import EX

class Simulate:
    def __init__(self, callback):
        self.callback = callback

    def buildCircuit(self):
        data = self.callback.elements.juliaCircuit()
        data += "init_circuit(circuit)\n"
        data += "result = simulate(circuit)\n"

        return data

    def createProcess(self, circuitS):
        queue = Queue(100)
        proc = Process(target=Simulate.simulate, args=(self.buildCircuit(), circuitS, queue ))
        proc.start()
        
        return proc, queue

    @staticmethod
    def simulate(data, circuitS, queue):
    
        try:
            queue.put("Loading julia...")
            from julia import Main

            queue.put("Loading symbolics.jl...")
            Main.eval("using Symbolics")

            queue.put("Loading CircuitS.jl...")
            Main.eval(circuitS)

            queue.put("Running simulation...")
            r = Main.eval(data)
           
            data = ''
            for item in r:
                x = Main.eval('string(result["'+item+'"])')
                data += f"{item} = {x}\n"

            queue.put("S " + str(data))
        except:
            queue.put("F ")