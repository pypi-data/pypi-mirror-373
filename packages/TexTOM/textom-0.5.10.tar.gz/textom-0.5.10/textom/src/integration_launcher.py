import os
import fabio
import h5py
import pyFAI
from time import time
import numpy as np
import argparse, sys
import importlib

from textom.src.pyfai_plugins import flexible_integrator, update_filelist

def parallel_launcher( k_task, sample_dir ):
    """starts the pyfai integration and is optimized to be called on parallel CPUs

    Parameters
    ----------
    k_task : int
        task index
    sample_dir : str
        textom sample base directory
    """
    # import integration parameters
    intpar_path_sample = os.path.join(sample_dir,'integration_parameters.py')
    par = import_module_from_path('integration_parameters', intpar_path_sample)
    
    fid_in, filtered_datasets = update_filelist(sample_dir,par)

    flat=None
    if isinstance( par.flatfield_correction, str ):
        flat = fabio.open(par.flatfield_correction).data

    mask = fabio.open(par.mask_path).data
    ai = pyFAI.load(par.poni_path)

    t0 = time()
    cnt = 0
    n_tot = len(filtered_datasets)
    for l in range ( k_task, n_tot, par.n_tasks):
        try:
            flexible_integrator(sample_dir, fid_in, filtered_datasets[l], par, ai, flat, mask)
        except:
            pass
        
        cnt += 1
        print('\tTask %d: %d/%d done, av. time per scan: %.2f s' % (
            k_task, l+1, n_tot, (time()-t0)/cnt))
    fid_in.close()

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--k_task", type=int, default=0)
    parser.add_argument("-d", "--dir_out_full", type=str, default=0)
    # argcomplete.autocomplete(parser)
    args = parser.parse_args()

    parallel_launcher(args.k_task,args.dir_out_full)

if __name__ == "__main__":
    main(sys.argv[1:])