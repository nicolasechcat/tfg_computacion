from common_module import *
import math
from qutip.qip.algorithms.qft import qft


# Without any optimization
class QFT_qutip_impl(QFT_Implementation):
    
    def __init__(self):
        super().__init__()
        self.filename = "qutip_impl"
        self.it = "Implementation de qutip"
    
    
    def qft_operator(self, N):
        n = int(math.log(N, 2))
        F = qft(n)
        F = F.full()
        np.around (F, c_round_dist, F)
        return qutip.Qobj(F)
        
    def execute(self, v):
        N = v.shape[0]
        n = int(math.log(N, 2))
        F = qft(n)
        F = F.full()            # To change the shape and distribution in order to be able to operate
        F = qutip.Qobj(F)
        
        result = (F * v).full()
        np.around (result, 5, result)
        r = qutip.Qobj(result)
        
        self.memory_spent = get_mem_used()
        
        return r
    
    def test_limits_imp(self, v, loops=1):                
        self.execute (v)
        return get_mem_used()
    
    def test (self): pass


if c_execute:
    
    
    print ("\n\n")


    if c_test:
        QFT_qutip_impl().test()
    elif not c_execute_limit_test:
        QFT_qutip_impl().measure         (c_repetitions, c_min_q, c_max_q, c_verbose)
    else:
        QFT_qutip_impl().test_limits     (c_min_q_l, c_max_q_l, c_verbose)



    print ("\n\n")