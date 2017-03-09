from common_module import *
import cmath



# Diff con it1 -> no convierte el operador a un objeto de qutip
class QFT_mem_opt_2(QFT_Implementation):
    
    def __init__(self):
        super().__init__()
        self.filename = "mem_opt_2"
        self.implementation = "Memory optimization - simplified strctures"
    
    def execute(self, v):
        self.memory_spent = 0
        vm = v.data
        N = v.shape[0]
        F = np.zeros((N,N), dtype=np.complex128)
        C1 = 2*cmath.pi*1j/N            # Constant of the algorithm
        C2 = cmath.sqrt(N)              # Constant of the algorithm
        
        for j in range (N):
            for k in range (N):
                F[j,k] = cmath.exp(C1*((j*k)%N))

        result = F * vm
        result = result / C2
        
        np.around (result, 5, result)
        r = qutip.Qobj(result)
        
        self.update_memory_spent()
        
        return r
    
    def test_limits_imp(self, v, loops=1):   
        self.memory_spent = 0             
        self.execute (v)
        return self.memory_spent


if c_execute:
        
    print ("\n\n") 
            
    if c_test:
        QFT_mem_opt_2().test()
    elif not c_execute_limit_test:
        QFT_mem_opt_2().measure         (c_repetitions, c_min_q, c_max_q, c_verbose)
    else:
        QFT_mem_opt_2().test_limits     (c_min_q_l, c_max_q_l, c_verbose)



    print ("\n\n")
