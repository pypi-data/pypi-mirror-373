import os
# set num threads to 1 before importing numpy
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import matplotlib.pyplot as plt
from time import time
import sys

from src.model import model
import src.plotting as myplt
import src.rotation as rot
import textom.src.symmetries as sym

#################### input ####################
input_file = 'input.input_simsample'

gaussian_std = 40 * np.pi/180 # standard deviation in rad
nmax = 12 # maximum HSH order

K = None # apply Mason kernel on the result 
#(only necessary for low orders or sharp distributions)
###############################################

# mean orientation of gaussian (zero by default)
gaussian_mu = np.array( (0, np.pi/2, np.pi), np.float64 )
# initialize model
mod = model(input_file, single=True)
mod.Gc[mod.Gc[:,0]==0,0] = 0.001
gen = sym.generators(mod.symmetry)

def gaussian_3d( g, mu, gen, std ):
    # make quaternion from mu
    q_mu = rot.QfromOTP( np.array([mu]) )[0]
    # make quaternions from angles
    Q_points = rot.QfromOTP( g )
    # for omega_mu = 0, then dg is omega
    dg = rot.ang_distance(Q_points, np.tile(q_mu,(Q_points.shape[0],1)), gen)
    odf = np.exp( - dg**2/(2*std**2) )
    return odf/( odf @ mod.dV )

# gaussian reference-ODF
odf_g = gaussian_3d( mod.Gc, gaussian_mu, gen, gaussian_std )

mod.set_orders( nmax )
# initialize HSH coefficients
c = np.zeros( mod.sHSHs.shape[0]+1 )
c[0]=1
c_next = c.copy()

# functions for optimizing HSHs against the gaussian
def f_loss( c ):
    odf_mod = mod.odfFromC( c, info=False )
    return (( odf_g - odf_mod )**2).sum()

def f_jac( c ):
    odf_mod = mod.odfFromC( c, info=False )
    return - 2 * mod.sHSHs @ ( odf_g - odf_mod )

def vnorm( v ):
    if isinstance(v,np.ndarray):
        return (v**2).sum()**(1/2)
    else:
        return 1

# optimization using gradient descent
loss = f_loss(c)
grad = f_jac(c)
nGrad = vnorm(grad)
gam = 1/np.abs(grad).max() * np.ones_like(grad)
iter, prec, fgam = 0, 1, 1
t1 = time()
while ( 
    ( prec > 0.001 ) and 
    ( iter < 500 ) and
    ( fgam >= 0.001 )
 ):
    c_next[1:] = c[1:] - gam * grad # update
    loss_next = f_loss(c_next)
    if loss_next < loss:
        iter += 1
        c = c_next
        loss = loss_next
        grad = f_jac(c)
        nGrad_m1 = nGrad
        nGrad = vnorm(grad)
        prec = np.abs(nGrad_m1-nGrad)/nGrad
    else:
        gam *= 0.8
        fgam *= 0.8
    
    t_iter_av = (time()-t1)/ (iter+1)
    sys.stdout.write('\r\tIt: %d, loss: %.1f, av t/it: %.2e s' % (iter,loss,t_iter_av))
print(', precision %.3f' % prec)

# make the odf from the result
odf1 = mod.odfFromC(c, info=True)

myplt.onion( odf_g, mod.Gc, title='3D gaussian' )
myplt.onion( odf1, mod.Gc, title='3D gaussian' )
f,ax = plt.subplots()
ax.plot( odf1, label='Fit, max order %d' % mod.ns[-1] )

# apply the kernel 
if K:
    c = mod.apply_kernel(c,K)
    odf2 = mod.odfFromC(c, info=True)
    myplt.onion( odf2, mod.Gc, title='Fit, max order %d, k = %.2f' % (mod.ns[-1], K) )
    ax.plot( odf2, label='Fit, max order %d, k = %.2f' % (mod.ns[-1], K))

path = 'output/gaussian_n%d_std%d.txt' %(nmax, np.round(gaussian_std*180/np.pi))
with open( path , 'w' ) as fid:
    [fid.write( '%.6e  ' % cl ) for cl in c ]

# plot the original gaussian and cosmetics
ax.plot( odf_g, label='3D gaussian, std = %d °' % np.round(gaussian_std*180/np.pi) )
ax.set_ylabel('ODf', fontsize=12)
ax.set_xlabel('Rotations projected to 1D (index)', fontsize=12)
ax.legend( fontsize=14 )
plt.show()