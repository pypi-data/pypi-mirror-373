### base coordinate system: ###
beam_direction = (1,0,0) # p in mumott
transverse_horizontal = (0,1,0) # j in mumott
transverse_vertical = (0,0,1) # k in mumott
################################ don't change

# detector geometry:
flip_detector_ud=False
flip_detector_lr=False
detector_direction_origin = (0,-1,0)
detector_direction_positive_90 = (0,0,-1)

# sample movements:
inner_axis = (0,0,1) # inner rotation axis
outer_axis = (0,1,0) # outer rotation axis
scan_mode = 'line' #'column' # 'line_snake' # 'column_snake'
flip_fov=False # flip fast and slow axis argument (for the case it was defined the reverse way in the integrated data files)

# For calculating projectors:
Dbeam = 0.3 # beam size in um (FWHM)
Dstep = 0.5 # scanning step size in um
