
# Macros

all: clear py

py: base_impl mem_opt_1 mem_opt_2 mem_opt_3 time_opt_1 time_opt_2 time_opt_3
	
qutip_impl: clear
	python3.4 QFT_qutip_impl.py

base_impl: clear
	python3.4 QFT_base_impl.py

mem_opt_1: clear
	python3.4 QFT_mem_opt_1.py
	
mem_opt_2: clear
	python3.4 QFT_mem_opt_2.py

mem_opt_3: clear
	python3.4 QFT_mem_opt_3.py

time_opt_1: clear
	python3.4 QFT_time_opt_1.py
	
time_opt_2: 
	python3.4 QFT_time_opt_2.py

time_opt_3: 
	python3.4 QFT_time_opt_3.py

clean:
	rm tables/*

clear:
	clear

