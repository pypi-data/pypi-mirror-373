import os
# Housekeeping, set num threads to 1 before importing numpy
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import matplotlib.pyplot as plt
import pickle

import src.handle as hdl
from src.model import model
from textom.src.data import data
from src.fitting import fitting
import src.plotting as myplt
from src.optimizer import optimize
import src.rotation as rot
import textom.src.symmetries as sym
from config import pickle_path

# this is to avoid an error on greenland
import matplotlib 
matplotlib.use('TkAgg')

#################### INPUT ##################

mod = model( 'input.input_simsample' )
projections = 'full' #'notilt'
n_max = 12 # maximum order to optimize

#############################################

with open(os.path.join(pickle_path, 'data_%s.txt' % mod.title),'rb') as fid:
    dat = pickle.load(fid)
fit = fitting(dat,mod)
qmask = np.array([False, False, False, False, False, False, False,  True,  True,
        True, False, False,  True,  True,  True,  True, False, False,
        True,  True, False,  True, False, False, False, False, False,
        True,  True, False, False, False, False, False, False, False,
       False,  True,  True,  True, False,  True, False, False,  True,
       False,  True,  True, False, False])
fit.mask_q( mask = qmask )
hdl.save_pickle('fit_%s' % mod.title, fit, 'fit')

fit.choose_projections( projections ) 

loss_all, MDL = [], []
print( 'Optimize 0 and lowest order to get orienations')
fit.C, opt0 = optimize( fit, 0 ) # opimize c0 from average intensity
fit.set_orders( mod, 4 )
fit.C, opt = optimize( fit, 1 ) # optimize only 4th order
loss_all.append(opt['loss'])
fit.C, opt = optimize( fit, 2, tol=1e-3 ) # optimize all together
loss_all.append(opt['loss'])
MDL.append( fit.MDL(opt['loss'][-1]) )
c_res = fit.C.copy()

# make figure that shows the deviation from the real mean direction
g_pref = mod.g_ML_sample( fit.C[mod.mask_voxels] )
file = hdl.read_vtk( 'output/sim_%s.vtk' % mod.title )
mu = file[1]['mu'][mod.mask_voxels]
gen = sym.generators(mod.symmetry)
dis = rot.ang_distance(rot.QfromOTP(g_pref),rot.QfromOTP(mu),gen)
plt.figure()
plt.hist(dis*180/np.pi)
plt.ylabel('No of voxels')
plt.xlabel('dg [%s]' % chr(176))

print( 'Optimize higher orders for full ODF' )
for n in range(6,n_max+1,2):
    fit.set_orders(mod,n)
    fit.C, opt = optimize( fit, 1 ) # optimize only n-th order
    loss_all.append(opt['loss'])
    fit.C, opt = optimize( fit, 2, tol=1e-3 ) # optimize all together
    loss_all.append(opt['loss'])
    MDL.append( fit.MDL(opt['loss'][-1]) )
    if np.min(MDL) == MDL[-1]:
        c_res = fit.C.copy()

# plot the development of the loss function
plt.figure()
t0 = 0
for k, loss in enumerate(loss_all):
    plt.plot(range(t0,t0+len(loss)), loss, 
             label='n = %d' % fit.ns[int(k/2)+1])
    t0 += len(loss)
plt.legend()
plt.xlabel('Iterations')
plt.ylabel('Loss function')

# plot the minimum description length
plt.figure()
plt.plot(fit.ns[1:],MDL)
plt.xlabel('n')
plt.ylabel('MDL')

# get variances using the result with min(MDL)
n_chosen = fit.ns[np.argmin(MDL) + 1]
mod.set_orders(n_chosen)
stds = mod.std_sample( c_res[mod.mask_voxels], g_pref )
plt.figure()
plt.hist(stds *180/np.pi, bins=20)
plt.xlabel('%s [%s]' % (chr(963),chr(176)))
plt.ylabel('No of Voxels')

# export vtk-file for paraview
a_pref, b_pref, c_pref = mod.abc_pref_sample( g_pref )
path = 'output/fit_%s.vtk' % mod.title
hdl.write_vtk_direct( mod, path, mod.mask_voxels,
                     scalars = [
                        ['scaling', c_res[mod.mask_voxels,0]],
                        ['std', stds ]
                      ],
                     vectors = [
                        ['a_pref', a_pref],
                        ['b_pref', b_pref],
                        ['c_pref', c_pref],
                        ]
                    )
print('Saved mean orientations to file: %s' % path)

plt.show()