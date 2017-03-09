from common_module import *
import cmath
import multiprocessing



# Diff con mem_opt_1 -> Paralelization of the calculus and precalculation of the posible operator values
class QFT_time_opt_3(QFT_Implementation):
    
    def __init__(self):
        super().__init__()
        self.filename = "time_opt_3"
        self.implementation = "Time optimization - multithreading and operation reduction"
        self.pool = None
        
    def execute(self, v):
        self.memory_spent = 0
        cpus = os.cpu_count()
        vm = v.data
        N = v.shape[0]
        
        values = np.zeros((1, N), dtype=np.complex128) 
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        
        if self.pool == None:
            self.pool = multiprocessing.Pool(cpus)
        
        partial_results = [self.pool.apply_async(QFT_time_opt_3().calculate_values, (N, t, cpus)) for t in range(cpus)]        
        already_processed = []
        try:
            while len(already_processed) < len(partial_results):
                
                self.update_memory_spent()
                
                for p in partial_results:
                    if p.ready() and (p not in already_processed):
                        already_processed.append(p)
                        (r, w, min_j) = p.get()
                        for j in range(w):
                            values[0, min_j + j] = r[0, j]
        except:
            self.pool.terminate()
            raise
        
        partial_results = [self.pool.apply_async(QFT_time_opt_3().operate, (vm, N, values, t, cpus)) for t in range(cpus)]
        
        already_processed = []
        
        try:
            while len(already_processed) < len(partial_results):
                
                self.update_memory_spent()
                
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
        
        self.update_memory_spent()
        
        return r
    
    def calculate_values (self, N, p, max_p):
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
        
        values = np.zeros((1, items), dtype=np.complex128)  # column vector for the result state
        
        C1 = 2*cmath.pi*1j/N                            # Constant of the algorithm
        C2 = cmath.sqrt(N)                              # Constant of the algorithm
        
        min_j = work * p
        
        for j in range (items):
            values[0, j] = cmath.exp(C1*(min_j + j)) / C2
        
        return (values, items, min_j)
            
    
    # p == 0 for the first proces and p == max_p - 1 for the last one
    def operate (self, v, N, values, p, max_p, limit_test=0):
        
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
        
        if (limit_test and items > limit_test):
                items = limit_test
        
        result = np.zeros((items, 1), dtype=np.complex128)  # column vector for the result state
        F = np.zeros((1, N), dtype=np.complex128)       # row vector for the partial operator
        C1 = 2*cmath.pi*1j/N                            # Constant of the algorithm
        C2 = cmath.sqrt(N)                              # Constant of the algorithm
        
        min_j = work * p
        
        for j in range (items):
            for k in range (N):
                jk = ((j + min_j)*k)%N
                F[0, k] = values [0, jk]
            result[j,0] = (F * v)[0,0]
        
        np.around (result, 5, result)
        
        if c_verbose:
            print ("Child {0} (PID {1})- Mem {2}".format(p, os.getpid(), get_mem_used_python_lib()/1024))
        
        return (result, items, min_j)
        
        
       
    
    
    
    def test_limits_imp(self, v, loops=1):
        self.memory_spent = 0
        cpus = os.cpu_count()
        vm = v.data
        N = v.shape[0]
        
        values = np.zeros((1, N), dtype=np.complex128) 
        result = np.zeros((N, 1), dtype=np.complex128)  # column vector for the result state
        
        if self.pool == None:
            self.pool = multiprocessing.Pool(cpus)
        
        partial_results = [self.pool.apply_async(QFT_time_opt_3().calculate_values, (N, t, cpus)) for t in range(cpus)]        
        already_processed = []
        try:
            while len(already_processed) < len(partial_results):
                
                self.update_memory_spent()
                
                for p in partial_results:
                    if p.ready() and (p not in already_processed):
                        already_processed.append(p)
                        (r, w, min_j) = p.get()
                        for j in range(w):
                            values[0, min_j + j] = r[0, j]
        except:
            self.pool.terminate()
            raise
        
        partial_results = [self.pool.apply_async(QFT_time_opt_3().operate, (vm, N, values, t, cpus, 2)) for t in range(cpus)]
        
        already_processed = []
        
        try:
            while len(already_processed) < len(partial_results):
                
                self.update_memory_spent()
                
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
        
        self.update_memory_spent()
        
        return self.memory_spent



if c_execute:

    #print ("\n\n")

    if c_test:
        QFT_time_opt_3().test()
    elif not c_execute_limit_test:
        QFT_time_opt_3().measure         (c_repetitions, c_min_q, c_max_q, c_verbose)
    else:
        QFT_time_opt_3().test_limits     (c_min_q_l, c_max_q_l, c_verbose)



    print ("\n\n")