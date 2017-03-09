from common_module import *
import cmath
import multiprocessing



# Diff con mem_opt_1 -> 
class QFT_time_opt_2(QFT_Iteration):
    
    def __init__(self):
        super().__init__()
        self.filename = "time_opt_2"
        self.it = "Time optimization - multithreading"
        self.pool = None
        
    def execute(self, v):
        cpus = os.cpu_count()
        N = v.shape[0]
        
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        
        if self.pool == None:
            self.pool = multiprocessing.Pool(cpus)
        
        partial_results = [self.pool.apply_async(QFT_time_opt_2().operate, (v, N, t, cpus)) for t in range(cpus)]
        
        already_processed = []
        
        try:
            while len(already_processed) < len(partial_results):
                for p in partial_results:
                    if p.ready() and (p not in already_processed):
                        already_processed.append(p)
                        (r, w, min_j) = p.get()
                        for j in range(w):
                            result[min_j + j, 0] = r[j, 0]
        except:
            self.pool.terminate()
            raise
            
        r = qutip.Qobj(result)
        
        get_mem_used()
        
        self.memory_spent = get_mem_used_python_lib()
        
        return r
    
    # p == 0 for the first proces and p == max_p - 1 for the last one
    def operate (self, v, N, p, max_p, limit_test=0):
        
        if (N > max_p) and (p > N):
            return ([], 0, 0)
        
        if (N % max_p) == 0:                            # Calculates the number of elements by thread to preocess
            work = int (N / max_p)
            items = work
        else:
            work = int (N / (max_p - 1))                    # If the data are not equally distributed, the last process has less items to process
            items = work
            if (p == max_p - 1):
                items = N % p
        
        # Controlar caso como 100 elementos y 11 procesos -> ultimo proceso con 0 elementos y el resto con 10, o todos con 9 y sobra un elemento
        if items == 0:
            return ([], 0, 0)
        
        if (limit_test and items > 1):
                items = 1
        
        result = np.zeros((items, 1), dtype=np.complex128)  # column vector for the result state
        F = np.zeros((1, N), dtype=np.complex128)       # row vector for the partial operator
        C1 = 2*cmath.pi*1j/N                            # Constant of the algorithm
        C2 = cmath.sqrt(N)                              # Constant of the algorithm
        
        min_j = work * p
        
        for j in range (items):
            for k in range (N):
                jk = (j + min_j)*k
                F[0, k] = cmath.exp(C1*(jk%N)) / C2
            Fq = qutip.Qobj(F) 
            result[j,0] = (Fq * v).data[0,0]
        
        np.around (result, 5, result)
        
        if c_raise:
            print ("Child {0} (PID {1})- Mem {2}".format(p, os.getpid(), get_mem_used_python_lib()/1024))
        
        return (result, items, min_j)
        
        
       
    
    
    
    def test_limits_imp(self, v, loops=1):
        if c_verbose:
            print("\t\t-Init")
        cpus = os.cpu_count()
        N = v.shape[0]
        
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        
        if self.pool == None:
            self.pool = multiprocessing.Pool(cpus)
        
        partial_results = [self.pool.apply_async(QFT_time_opt_2().operate, (v, N, t, cpus, 1)) for t in range(cpus)]
        
        if c_verbose:
            print("\t\t-Processes launched")
        
        j = 0
        
        already_processed = []
        
        try:
            while len(already_processed) < len(partial_results):
                #print ("\n\nMemory - ", get_mem_used()/1024, "\n\n")
                for p in partial_results:
                    
                    m = get_mem_used_python_lib()
                    if self.memory_spent < m:
                        self.memory_spent = m
                        
                    if (p not in already_processed) and p.ready():
                        if c_verbose:
                            print("\t\t-Process ended")
                        already_processed.append(p)
                        (r, w, min_j) = p.get()
                        for j in range(w):
                            result[min_j + j, 0] = r[j, 0]
                        if c_verbose:
                            print("\t\t\t-Process result processed")
        except:
            self.pool.terminate()
            raise
            
        r = qutip.Qobj(result)
        if c_verbose:
            print("\t\t-Result conversion")
        
        if c_verbose:
            print("\t\t-Return")
        return self.memory_spent


    # p == 0 for the first proces and p == max_p - 1 for the last one
    def operate_test_limits (self, v, N, p, max_p):
        try:
            if (N > max_p) and (p > N):
                return ([], 0, 0)
            
            if (N % max_p) == 0:                            # Calculates the number of elements by thread to preocess
                work = int (N / max_p)
                items = work
            else:
                work = int (N / (max_p - 1))                    # If the data are not equally distributed, the last process has less items to process
                items = work
                if (p == max_p - 1):
                    items = N % p
            
            # Controlar caso como 100 elementos y 11 procesos -> ultimo proceso con 0 elementos y el resto con 10, o todos con 9 y sobra un elemento
            if items == 0:
                return ([], 0, 0)
            
            if (items > 1):
                items = 1
            
            result = np.zeros((items, 1), dtype=np.complex128)  # column vector for the result state
            F = np.zeros((1, N), dtype=np.complex128)       # row vector for the partial operator
            C1 = 2*cmath.pi*1j/N                            # Constant of the algorithm
            C2 = cmath.sqrt(N)                              # Constant of the algorithm
            
            min_j = work * p
            
            for j in range (items):
                for k in range (N):
                    jk = (j + min_j)*k
                    F[0, k] = cmath.exp(C1*(jk%N)) / C2
                if c_raise:
                    print ("Process {0} row {1} operated".format(p, j + min_j))
                Fq = qutip.Qobj(F)
                result[j,0] = (Fq * v).data[0,0]
            
            np.around (result, 5, result)
            
            return (result, items, min_j)
        except:
            print ("Process {0} raised an exception".format(p))
            raise


if c_execute:

    #print ("\n\n")

    if c_test:
        QFT_time_opt_2().test()
    elif not c_execute_limit_test:
        QFT_time_opt_2().measure         (c_repetitions, c_min_q, c_max_q, c_verbose)
    else:
        QFT_time_opt_2().test_limits     (c_min_q_l, c_max_q_l, c_verbose)



    print ("\n\n")