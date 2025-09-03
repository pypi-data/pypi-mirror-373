import sys
from time import time
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
import numpy as np

from orix import plot
# from orix.quaternion import Orientation, Misorientation, Rotation
from orix.vector import Vector3d, AxAngle
from orix.quaternion import Orientation, OrientationRegion, Rotation, Misorientation
import orix.quaternion.symmetry as osym #import C1, Oh, D2
from orix.crystal_map import Phase
from orix.vector import Miller, Vector3d

from .model import model
from . import symmetries as sym
from . import rotation as rot
from .misc import crop_to_non_nan_region, smallest_subvolume
from ..config import data_type

############################################################################################+
    
def odf_cloud( mod:model, c, num_samples=1000, title='', kernel=False, odf_info=True ):
    # Calculate the odf
    if not kernel:
        odf = mod.odfFromC( c, clip=True, info=odf_info )
    else:
        odf = mod.odfFromC( c, K=kernel, info=odf_info )

    # draw samples out of it
    odf_eff = odf * mod.dV
    cdf = np.cumsum( odf_eff/odf_eff.sum() )

    # Draw random samples from a uniform distribution
    random_numbers = np.random.rand(int(num_samples))

    # Find the corresponding indices in the CDF
    indices = np.searchsorted(cdf, random_numbers)
    indices[indices==odf.size] = 0

    # make them quaternions
    quat = rot.QfromOTP( mod.Gc[indices] )
    sample_r = Rotation([quat])
    sample = Orientation(sample_r)
    sample.symmetry = getattr( osym, sym.get_SFnotation( mod.symmetry ) )

    # plots a 3D odf in the fundamental zone
    sample.scatter()
    plt.title(title)
    
def odf_cloud_general( orientations, odf, symmetry, num_samples=1000, title='' ):

    # draw samples out of the odf
    cdf = np.cumsum( odf/odf.sum() )

    # Draw random samples from a uniform distribution
    random_numbers = np.random.rand(int(num_samples))

    # Find the corresponding indices in the CDF
    indices = np.searchsorted(cdf, random_numbers)
    indices[indices==odf.size] = 0

    # make them quaternions
    quat = rot.QfromOTP( orientations[indices] )
    # sample_r = Rotation([quat])
    # sample = Orientation(sample_r)
    # sample.symmetry = getattr( osym, sym.get_SFnotation( symmetry ) )

    # # plots a 3D odf in the fundamental zone
    # sample.scatter()
    plot_points_in_fz( quat, symmetry )
    plt.title(title)

def plot_points_in_fz( unit_quaterions, symmetry, title='' ):
    # make them quaternions
    # quat = rot.QfromOTP( orientations )
    sample_r = Rotation([unit_quaterions])
    sample = Orientation(sample_r)
    sample.symmetry = getattr( osym, sym.get_SFnotation( symmetry ) )

    # plots a 3D odf in the fundamental zone
    sample.scatter()

    plt.title(title)

############################################################################################+
# from orix.quaternion import Orientation, OrientationRegion, Rotation, Misorientation
# import orix.quaternion.symmetry as osym #import C1, Oh, D2
# # plot a single piont in a unit cell with vector pointing to it
# axan = np.array([[np.pi/2,np.pi/4,np.pi/4]])
# # f,ax = plt.subplots(4)
# symmetries = ['2','222','6','432']#
# k=1
# for symmetry in symmetries:
#     quat = rot.QfromOTP(axan)
#     axan_vec = quat[0,1:]/np.linalg.norm(quat[0,1:]) * axan[0,0]
#     oror = Orientation(Rotation(quat))
#     oror.symmetry = getattr( osym, sym.get_SFnotation(symmetry))
#     # f.add_axes([0.1, 0.1, 0.8, 0.8])
#     oror.scatter()#figure=f,position=(4,1,k))
#     k+=1
#     # plt.quiver(0,0,0,*axan_vec,color='r')
############################################################################################+

def inverse_pf_map( g, ppgrp ):
    """"""
    orix_pg = getattr( osym, sym.get_SFnotation( ppgrp ) )
    ori = make_ori(g,orix_pg)

    ckey = plot.IPFColorKeyTSL(orix_pg)

    directions = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    titles = ["X", "Y", "Z"]

    fig, axes = plt.subplots( 2,2, figsize=(15, 10))
    for i, ax in enumerate(axes.flatten()[:3]):
        ckey.direction = Vector3d(directions[i])
        # Invert because orix assumes lab2crystal when coloring orientations
        ax.imshow(ckey.orientation2color(~ori).transpose(1,0,2))
        ax.set_title(f"IPF-{titles[i]}")
        ax.axis("off")

    # Add color key
    ax_ipfkey = plt.subplot( 224,
        # [0.932, 0.37, 0.1, 0.1],  # (Left, bottom, width, height)
        projection="ipf",
        symmetry=ori.symmetry.laue,
    )
    ax_ipfkey.plot_ipf_color_key()
    ax_ipfkey.set_title("")
    # axes[1,1].set_projection = "ipf"
    # axes[1,1].symmetry=ori.symmetry.laue
    # axes[1,1].plot_ipf_color_key()
    # axes[1,1].set_title("")
    fig.subplots_adjust(wspace=0.01)

def inverse_pf_stack( g, mod:model ):
    """Creates an inverse pole figure map of every slice of a 

    Parameters
    ----------
    g : ndarray
        orientations in OTP notation
    ppgrp : str
        proper point group

    Returns
    -------
    list
        for x/y/z: 3D inv polefigures
    """
    orix_pg = getattr( osym, sym.get_SFnotation( mod.symmetry ) )
    ori = make_ori( g.reshape((np.prod(g.shape[:-1]),g.shape[-1])), orix_pg )

    ckey = plot.IPFColorKeyTSL(orix_pg)

    directions = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    
    col_stack = []
    for k in range(len(directions)):
        ckey.direction = Vector3d(directions[k])
        colors = np.zeros((np.prod(g.shape[:-1]),3), data_type)
        # Invert because orix assumes lab2crystal when coloring orientations
        colors[mod.mask_voxels] = ckey.orientation2color(~ori[mod.mask_voxels])
        col_stack.append(colors.reshape((*g.shape[:-1],g.shape[-1])))

    return np.array(col_stack)#.transpose((1,2,3,0,4))#col_stack

def plot_ipf_movie( data, ppgrp, sliceplane='z', save_vid_path=False, fps=5, show=True ):

    if sliceplane == 'x':
        xl,yl = 'y','z' # labels for plot
    elif sliceplane == 'y':
        data=data.transpose(0,2,1,3,4)
        xl,yl = 'x','z' # labels for plot
    elif sliceplane == 'z':
        data=data.transpose(0,3,1,2,4)
        xl,yl = 'x','y' # labels for plot
    else:
        print('\tsliceplane not recognized')
        return
    
    data = np.array([smallest_subvolume(d)[0] for d in data])
    num_images = data.shape[1]
    # Initial dataset and image index
    current_image_index = 0

    fig, axes = plt.subplots( 2,2, figsize=(15, 10))
    fig.delaxes(axes[1,1])
    titles = ["X", "Y", "Z"]
    imgs_display = []
    for i, ax in enumerate(axes.flatten()[:3]):
        # Invert because orix assumes lab2crystal when coloring orientations
        imgs_display.append(ax.matshow(data[i,data.shape[1]//2].transpose(1,0,2)))
        ax.set_title(f"IPF-{titles[i]}")
        ax.axis("off")
    orix_pg = getattr( osym, sym.get_SFnotation( ppgrp ) )
    # Add color key
    ax_ipfkey = plt.subplot( 224,
        # [0.932, 0.37, 0.1, 0.1],  # (Left, bottom, width, height)
        projection="ipf",
        symmetry=orix_pg.laue,
    )
    ax_ipfkey.plot_ipf_color_key()
    ax_ipfkey.set_title("")
    # Create a slider for switching between images within a dataset
    ax_image_slider = plt.axes([0.25, 0.03, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    image_slider = Slider(ax_image_slider, sliceplane, 0, num_images - 1, valinit=0, valstep=1)
    def update(val):
        current_image_index = int(image_slider.val)  # Get the image index from the slider
        current_image = data[:,current_image_index]
        for i, ax in enumerate(axes.flatten()[:3]):
            imgs_display[i].set_data( current_image[i].transpose(1,0,2) )  # Update the image data
        fig.canvas.draw_idle()  # Redraw the figure

    # Attach the update functions to the sliders
    image_slider.on_changed(update)

    # Add a button for playing the video
    ax_button = plt.axes([0.1, 0.03, 0.1, 0.04])
    button = Button(ax_button, 'Play')

    playing = [False]  # Use a mutable object to toggle playing state

    def toggle_play(event):
        playing[0] = not playing[0]  # Toggle state
        if playing[0]:
            button.label.set_text("Pause")
            ani.event_source.start()
        else:
            button.label.set_text("Play")
            ani.event_source.stop()

    button.on_clicked(toggle_play)

    # Automatic playback with animation
    def update_frame(i):
        if playing[0]:
            next_frame = (int(image_slider.val) + 1) % num_images
            image_slider.set_val(next_frame)

    ani = FuncAnimation(fig, update_frame, frames=num_images, interval=100)  # Interval in milliseconds

    if save_vid_path:
        toggle_play(None)
        # Save the animation as an MP4 file
        ani.save(save_vid_path, writer='pillow', fps=fps)
        toggle_play(None)

    if show:
        plt.show()

def plot_pole_figure( mod:model, c, hkl=(1,0,0), 
                     recenter = False,
                     hemisphere = 'upper',
                     mode='image', title='',
                     num_samples=1e4, alpha=0.05 ):
    # Calculate the odf
    odf = mod.odfFromC( c, clip=True )

    if recenter:
        ig = np.argmax(odf) # index of the maximum of the odf
        g_max = mod.Gc[ig]
        Rs = mod.get_Rs( (-g_max[0], g_max[1], g_max[2]) )
        odf = mod.odfFromC( Rs @ c, clip=True )

    # draw samples out of it
    odf_eff = odf * mod.dV
    cdf = np.cumsum( odf_eff/odf_eff.sum() )

    # Draw random samples from a uniform distribution
    random_numbers = np.random.rand(int(num_samples))

    # Find the corresponding indices in the CDF
    indices = np.searchsorted(cdf, random_numbers)-1

    # make them quaternions
    quat = rot.QfromOTP( mod.Gc[indices] )
    sample_r = Rotation([quat])
    sample = Orientation(sample_r)
    sample.symmetry = getattr( osym, sym.get_SFnotation( mod.symmetry ) )

    g = Miller(hkl=hkl, phase=Phase(point_group=sample.symmetry))
    g = g.symmetrise(unique=True)
    poles = sample.inv().outer(g, lazy=True, progressbar=True, chunk_size=2000)

    plt.rcParams.update(
        {
            "figure.figsize": (6, 5),
            "lines.markersize": 2,
            "font.size": 15,
            "axes.grid": False,
        }
    )
    w, h = plt.rcParams["figure.figsize"]
    if mode=='scatter':
        poles.scatter(
            hemisphere=hemisphere,
            alpha=alpha,
            figure_kwargs={"figsize": (2 * h, h)},
            axes_labels=["X", "Y"],
        )
    else:
        poles.pole_density_function(
            hemisphere=hemisphere, log=False, figure_kwargs={"figsize": (2 * h, h)}
        )
    plt.suptitle( title )

def plot_pole_figure_from_odf( orientations, odf, symmetry,
                    hkl=(1,0,0), 
                    hemisphere = 'upper',
                    mode='image', title='',
                    num_samples=1e4, alpha=0.05 ):

    # draw samples out of the odf
    cdf = np.cumsum( odf/odf.sum() )
    random_numbers = np.random.rand(int(num_samples))
    indices = np.searchsorted(cdf, random_numbers)-1

    # make them quaternions
    quat = rot.QfromOTP( orientations[indices] )
    sample_r = Rotation([quat])
    sample = Orientation(sample_r)
    sample.symmetry = getattr( osym, sym.get_SFnotation( symmetry ) )

    g = Miller(hkl=hkl, phase=Phase(point_group=sample.symmetry))
    g = g.symmetrise(unique=True)
    poles = sample.inv().outer(g, lazy=True, progressbar=True, chunk_size=2000)

    plt.rcParams.update(
        {
            "figure.figsize": (6, 5),
            "lines.markersize": 2,
            "font.size": 15,
            "axes.grid": False,
        }
    )
    w, h = plt.rcParams["figure.figsize"]
    if mode=='scatter':
        poles.scatter(
            hemisphere=hemisphere,
            alpha=alpha,
            figure_kwargs={"figsize": (2 * h, h)},
            axes_labels=["X", "Y"],
        )
    else:
        poles.pole_density_function(
            hemisphere=hemisphere, log=False, figure_kwargs={"figsize": (2 * h, h)}
        )
    plt.suptitle( title )

def make_ori( g, sym ):
    # print('\tSetting up orix orientations')
    g_flat = g.reshape((np.prod(g.shape[:-1]),g.shape[-1])) # flatten orientations
    quat = rot.QfromOTP( g_flat ) # make quaternions
    ori_rot = Rotation([quat]) # convert to orix rotations
    ori = Orientation(ori_rot) # convert to orix orientations
    ori = ori.reshape((g.shape[:-1])) # bring back to original shape
    ori.symmetry = sym # apply symmetry
    ori = ori.map_into_symmetry_reduced_zone() # check if this is necessary
    return ori

def test_mori(g, ppgrp):
    orix_pg = getattr( osym, sym.get_SFnotation( ppgrp ) )
    ori = make_ori(g, orix_pg).flatten()
    g_fl = g.reshape((np.prod(g.shape[:-1]),g.shape[-1]))
    msk = ~np.isnan(g_fl[:,0])

    ori = ori[msk]
    g_fl = g_fl[msk]

    t0=time()
    mori_all = Misorientation(~ori[:-1] * ori[1:], symmetry=(orix_pg,orix_pg))
    mori_all.map_into_symmetry_reduced_zone()
    dis_mori = mori_all.angle
    print(time()-t0)
    # t0=time() # this takes much longer
    # for k in range(ori.size-1):
    #     mori_single = Misorientation(~ori[k] * ori[k+1], symmetry=(orix_pg,orix_pg))
    #     mori_single.map_into_symmetry_reduced_zone()
    #     mori_single.angle
    # print(time()-t0)
    t0=time()
    gen = sym.generators(ppgrp)
    dis = rot.ang_distance(rot.QfromOTP(g_fl[:-1]),rot.QfromOTP(g_fl[1:]),gen)
    dis_mori_rot = rot.misorientation(rot.QfromOTP(g_fl[:-1]),rot.QfromOTP(g_fl[1:]),gen)
    print(time()-t0)
