import qutip
import numpy as np
import time
import resource
import os
import sys
import gc
import psutil


#
#   Constants to manage the execution of the diferent implementations for measurement
#

c_execute = 1
c_verbose = 1
c_raise = 1

c_test = 0
c_execute_limit_test = 1          # If the execution is going to be about the limit of qubits or the complete algorithm

c_min_q_t = 1
c_max_q_t = 13

c_repetitions = 1

c_min_q = 14
c_max_q = 15

c_min_q_l = 19
c_max_q_l = 26


c_round_dist = 5


def ket(st, bits):
    return qutip.basis(2**bits, st)

def random_ket (qubits):
    return qutip.rand_ket (2**qubits)

def hadamard(bits):
    return qutip.Qobj(qutip.hadamard_transform(bits).data)

def identity(bits):
    return qutip.identity(2**bits)

# Returns the memory usage by the process in Bytes
def get_mem_used_python_lib(show = 0):
    father = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    if show:
        print ("\nMeasurement  with Python core\n")
        print ("\tFather - {0}\n\n\t\tChildrens - {1}\n\n".format(father/1024, children/1024))
    return father + children
    
# Version suposedly for the main process and the children
def get_mem_used(show = 0):
    current_process = psutil.Process(os.getpid())
    mem = current_process.memory_info().rss
    if show:
        print("\nMeasurement process by process\n")
        print ("\tFather - PID ", os.getpid(), " - ", current_process.memory_info().rss/(1024 * 1024), "\n")
    for child in current_process.children(recursive=True):
        mem += child.memory_info().rss
        if show:
            print ("\t\tChildren - PID ", child.pid, " - ", child.memory_info().rss/(1024 * 1024))
    
    if show:
        print ("\n\tTotal - ", mem/(1024 * 1024), "\n\n")
    return mem/1024
    

class QFT_Implementation:
    def __init__(self):
        self.implementation= "-"
        self.filename = ""
        self.memory_spent = 0
    
    def update_memory_spent(self):
        mem = get_mem_used_python_lib()     # Register the maximum memory needed
        if mem > self.memory_spent:
            self.memory_spent = mem
    
    def measure(self, steps=1, min_q=1, max_q=15, verbose=0):
        err = 0;
        res_col = 5
        result = np.zeros([max_q - min_q + 1, res_col], dtype=np.float64)
        for q in range(min_q, max_q + 1):     # For each number of qubits
            
            print ("qubits: ", q)
            
            ind = q - min_q
            
            if err:
                result[ind, 0] = q
                result[ind, res_col-1] = 1
                continue
            
            timing = np.zeros(steps, dtype=np.float64)
            try:
                mem = 0
                
                for i in range(steps):
                    #v = ket(0, q)           # Prepare a random input for the function
                    v = random_ket (q)
                    
                    tic = time.time()      # Time before the execution
                    fv = self.execute(v)    # Execute the function and retrieves the result
                    toc = time.time()      # Time after the execution
                    
                    if self.memory_spent > mem:
                        mem = self.memory_spent
                    
                    timing[i] = toc-tic     # The diference is the time spent by the executed function
                
                result[ind, 0] = q
                result[ind, 1] = np.average (timing)
                result[ind, 2] = np.std (timing, dtype=np.float64)
                result[ind, 3] = mem
                result[ind, res_col-1] = 0
                
                if (verbose):
                    print ("\nStatistics\n")
                    print ("\t-time - {0:7.5f}\t\t-std - {1:7.5f}".format(result[ind, 1], result[ind, 2]))
                    print ("\n\t-Memory - ", result[ind, 3] / 1024, " MB \n")


            except:
                result[ind, 0] = q
                result[ind, res_col-1] = 1
                err = 1;
                
                if c_raise:
                    raise 
            
        self.to_latex_table_content (result)
       
    # Function that tests how many qubits are operable before it runs out of memory
    def test_limits (self, min_q=1, max_q=25, verbose=0):
        result = np.zeros([max_q - min_q + 1, 4], dtype=np.float64)
        err = 0
        for q in range(min_q, max_q + 1):     # For each number of qubits
            
            ind = q - min_q
            
            print ("qubits: ", q)
            
            if err:
                result[ind, 0] = q
                result[ind, 3] = 1
                continue
            
            try:
                v = ket(0, q)           # Prepare a random input for the function
                #v = random_ket (q)
                
                gc.collect()            # Send a signal to the garbage collector to retrieve unused memory

                tic = time.time()      # Time before the execution
                m = self.test_limits_imp(v)    # Execute the function and retrieves the result
                toc = time.time()      # Time after the execution
                
                result[ind, 0] = q
                result[ind, 1] = toc - tic
                result[ind, 2] = m
                
                print ("\n\t-Memory - {0:7.4f} MB \t\t-Execution time - {1:7.4f}\n".format(result[ind, 2] / 1024, result[ind, 1]))

            except:
                toc = time.time()      # Time after the execution
                
                result[ind, 0] = q
                result[ind, 3] = 1
                
                err = 1;
                
                print ("\n\t-Memory error with {0} qubits \t\t-Execution time - {1:7.4f}\n\n".format(q, toc - tic))
                
                if c_raise:
                    raise
                
                
        self.to_latex_table_content_limits (result)
        return result
                
        
    
    # Function that tests the algoritm output for controled inputs
    def test (self):
        print("Testing " + self.implementation + "\n\n")
        from qutip.qip.algorithms.qft import qft
        
        for n in range (c_min_q_t, c_max_q_t):
            print("\t- {0:2d} qubits".format(n))
            
            #v = ket(0, n)
            v = random_ket (n)
            
            f1 = qft(n)
            f1 = f1.full()            # To change the shape and distribution in order to be able to operate
            f1 = qutip.Qobj(f1)
        
            f1v = (f1 * v).full()
            np.around (f1v, 5, f1v)
        
            f1v = qutip.Qobj(f1v)
            
            f2v = self.execute(v)
            
            if (f1v != f2v):
                print ("Error with the operation for {0:2} qubit(s). Expected result and obstained result doesn't match".format(n))
                
                if (c_verbose):
                    print ("\n\n\t-Input:\n{0}\n\n\t-Expected:\n{1}\n\n\t-Obtained:\n{2}".format(v, f1v, f2v))
                    
                    if c_raise:
                        N = 2**n
                        for j in range (N):
                            if f1v[j,0] != f2v[j,0]:
                                print ("posicion {0} tiene valor {1} pero se esperaba {2}".format(j, f1v[j,0], f2v[j,0]))
                    
                return True
            else:
                print("\t\t\t-> Succeded")
                
        return False
    
    def execute(self, v): pass
    
    def test_limits_imp(self, v, loops): pass
    
    def to_latex_table_content (self, d):
        
        filename = "./tables/" + self.filename + "_time_measure.tex"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'w')
        cols = d.shape[1]
        line = "% \tmemoria \tmedia(t) \tdesviación (t)\n"
        f.write(line)
        for i in range(d.shape[0]):
            line = ""
            if d[i, cols-1] == 0:
                line = '{0:2.0f} \t& \t{1:7.5f} \t& \t{2:7.5f} \t& \t{3:7.5f}  \t\\\\ \hline \n'.format(d[i,0], d[i,3]/1024, d[i,1], d[i,2])
            else:
                line = '{0:2.0f} \t& \t\tx \t\t& \t\tx \t\t& \t\tx \t\t\\\\ \hline \n'.format(d[i,0])
            f.write(line)
        f.close()
    
    def to_latex_table_content_limits (self, d):
        
        filename = "./tables/" + self.filename + "_memory_limits.tex"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'w')
        cols = d.shape[1]
        line = "% \tmemoria \tmedia(t) \tdesviación (t)\n"
        f.write(line)
        for i in range(d.shape[0]):
            line = ""
            if d[i, cols-1] == 0:
                line = '{0:2.0f} \t& \t{1:7.5f} \t\\\\ \hline \n'.format(d[i,0], d[i,2]/1024)
            else:
                line = '{0:2.0f} \t& \t\tx \t\t\\\\ \hline \n'.format(d[i,0])
            f.write(line)
        f.close()

