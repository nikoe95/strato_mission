from multiprocessing import Pool
from multiprocessing import cpu_count
import time
import psutil


def stresser(x):
    timeout = time.time() + 10
    while True:
        if time.time() > timeout:
            break
        x*x


def stress_test(nr_of_tests, log_path):
    processes = psutil.cpu_count()

    with open(log_path, 'w') as start_f:
        start_f.write('Starting stress test\n')
        start_f.write(f'CPU_COUNT: {processes}\n\n')
    
    for num in range(nr_of_tests):
        pool = Pool(processes)
        pool.map(stresser, range(processes))
   
        with open(log_path, 'a') as f:
            f.write(f'TEST_NR: {num}\n')
            f.write(f'CPU_TIMES: {psutil.cpu_times(percpu=True)}\n')
            f.write(f'CPU_STATS: {psutil.cpu_stats()}\n')
            f.write(f'CPU_USAGE: {psutil.cpu_percent() / psutil.cpu_count()}%\n')
            f.write(f'TEMP: {psutil.sensors_temperatures()}\n')
            f.write(f'RAM_USAGE: {psutil.virtual_memory().percent}%\n')
            f.write(f'DISK_USAGE: {psutil.disk_usage("/")}\n')
            f.write(f'CPU_FREQ: {psutil.cpu_freq(percpu=True)}\n\n')

    with open(log_path, 'a') as end_f:
        end_f.write(f'End of the test!\n')
    
    return 5037;


if __name__ == '__main__':
    stress_test(10, 'log_stress.txt')


