from common_module import *
import cmath



# Diff con mem_opt_3 -> Precalcuslation of the posible operator values
class QFT_time_opt_1(QFT_Implementation):
    
    def __init__(self):
        super().__init__()
        self.filename = "time_opt_1"
        self.implementation = "Time optimization - operation reduction"
        
    def execute(self, v):
        self.memory_spent = 0
        N = v.shape[0]
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        F = np.zeros((1, N), dtype=np.complex128)       # row vector for the partial operator
        C1 = 2*cmath.pi*1j/N                            # Constant of the algorithm
        C2 = cmath.sqrt(N)                              # Constant of the algorithm
        
        vm = v.data
        
        values = np.zeros((1, N), dtype=np.complex128) 
        for j in range (N):                             # Precalculate the w^{jk} values
            values[0, j] = cmath.exp(C1*j) / C2
        
        for j in range (N):
            for k in range (N):
                jk = (j*k)%N
                F[0, k] = values [0, jk]
                
            result[j,0] = (F * vm)[0,0]
        
        np.around (result, 5, result)
        r = qutip.Qobj(result)
        
        self.memory_spent = get_mem_used_python_lib()
        
        return r
    
    def test_limits_imp(self, v, loops=1):
        self.memory_spent = 0
        N = v.shape[0]
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        F = np.zeros((1, N), dtype=np.complex128)       # row vector for the partial operator
        C1 = 2*cmath.pi*1j/N            # Constant of the algorithm
        C2 = cmath.sqrt(N)              # Constant of the algorithm
        
        values = np.zeros((N), dtype=np.complex128) 
        for j in range (N):                             # Precalculate the w^{jk} values
            values[j] = cmath.exp(C1*j) / C2
        
        for j in range (loops):
            for k in range (N):
                F[0, k] =  values [(j*k)%N]
                
            F = qutip.Qobj(F) 
            result[j,0] = (F * v).data[0,0]
        
        np.around (result, 5, result)
        
        self.update_memory_spent()
        
        return self.memory_spent



if c_execute:

    print ("\n\n")

    if c_test:
        QFT_time_opt_1().test()
    elif not c_execute_limit_test:
        QFT_time_opt_1().measure         (c_repetitions, c_min_q, c_max_q, c_verbose)
    else:
        QFT_time_opt_1().test_limits     (c_min_q_l, c_max_q_l, c_verbose)



    print ("\n\n")