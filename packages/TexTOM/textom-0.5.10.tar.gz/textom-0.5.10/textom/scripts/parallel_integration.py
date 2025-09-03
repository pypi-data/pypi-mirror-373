from subprocess import Popen
from textom.input.integration_parameters import *
import shutil, os
from time import time
from src.misc import cp_addno

print('Starting parallel pyFAI integration')
t0 = time()

dir_out_full = os.path.join(
    dir_out, 
    title,
)
os.makedirs(dir_out_full, exist_ok=True )

# shutil.copy(
#     'integration_parameters.py',
#     dir_out_full
#     )
cp_addno('data_integration/integration_parameters.py', dir_out_full)
print('\tSaved integration parameters to %s' % (dir_out_full))

pids = []
for k in range(n_tasks):
    command = [
        'taskset', '-c', '%d-%d' % (k*cores_per_task, (k+1)*cores_per_task),
        'python', 'data_integration/integration_launcher.py', 
        '-k', '%d' % (k),
        '-d', '%s' % (dir_out_full),
    ]

    p = Popen(command)
    pids.append(p)

for p in pids:
    p.wait()

# for p in pids:
#     p.kill()

print('Integrations finished, total time: %d s' % (time()-t0))
