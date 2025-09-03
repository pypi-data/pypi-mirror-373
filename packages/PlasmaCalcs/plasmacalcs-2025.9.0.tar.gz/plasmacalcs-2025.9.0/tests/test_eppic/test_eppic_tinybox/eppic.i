; EPPIC parameter file
    title = 'tfbi2a_test0_tinybox B10G E9V e- H+ C+'
; Parameters for EPPIC-2a run, but the box is tiny.
; Results to be included in PlasmaCalcs CI.
;
; Mesh size and Grid size
    ndim_space = 2
    nsubdomains = 4
    nx = 8
    dx = 1.1e-02
    ny = 32
    dy = 1.1e-02
    nz = 1
    dz = 1.1e-02
; Time step, number of time steps to run, and time-steps between output:
    dt = 1.5e-08
    nt = 25600
    nout = 2560
; spatially averaging output arrays by this factor in each dimension
    nout_avg = 2
; output type (use 2 for parallel)
    hdf_output_arrays = 2
; Fraction of particles to output
    npout = 4000
; Define the dielectric of free space (default epsilon=8.8542e-12)
    eps = 8.85419E-12
; Bz (MKS system, scaled by units scaling implied by this file. Tesla if eps in SI units.)
    Bz = 1.0E-3
; Damping width: (try fwidth=3)
;   fwidth = 3
; Damping steepness: (try fsteep=3)
;   fsteep = 3
; Time steps beteen dumps
    iwrite = 51200
; Start from t=0 (iread=0) or dump (iread=1)
    iread = 0
; Number of distributions to initialize
    ndist = 3
; Limit the frequency of outputing divj:
    divj_out_subcycle = 100
; Neutral parameters:
    vth_neutral = 5.744e+03  ; T = 4000 K.
    m_neutral = 1.6738E-27
; E FROM PROD0 (matched t=0 of Ebysus)
    ; External Electric field: 8.91 V/m, -73.2 deg from x-axis
    ; Ex0_external = 2.58  ; 2.579 matches t=0 of Ebysus
    ; Ey0_external = -8.53  ; -8.528 matches t=0 of Ebysus
; External Electric field (matches t=0.002 of Ebysus)
    ; 8.932 V/m, -72.71 deg from x-axis
    Ex0_external = 2.655
    Ey0_external = -8.528


; -----   e-   -----
    dist = 0
    nptotcelld0 = 400
    part_pad=4.0
    n0d0 = 3.600e+11
    md0 = 9.10938E-31
    qd0 = -1.60218E-19
    coll_type0 = 1
    coll_rate0 = 1.6E7
    vxthd0 =  3.294e+05
    vythd0 =  3.294e+05
    vzthd0 =  3.294e+05
    vx0d0 = 0
    vy0d0 = 0
    vz0d0 = 0
    pnvx0 = 64
    pnvy0 = 64
    pnvz0 = 64
    pvxmin0 = -6.0E6
    pvxmax0 = 6.0E6
    pvymin0 = -6.0E6
    pvymax0 = 6.0E6
    pvzmin0 = -6.0E6
    pvzmax0 = 6.0E6
    init_dist0 = 1
    vdist_out_subcycle0 = 100
    part_out_subcycle0 = 1
    flux_out_subcycle0 = 1
    nvsqr_out_subcycle0 = 1

; -----   H+   -----
    dist1 = 1
    nptotcelld1 = 2000
    part_pad=4.0
    n0d1 = 3.000e+11
    md1 = 1.67262E-27
    qd1 = 1.60218E-19
    coll_type1 = 1 
    coll_rate1 = 6.7E5
    vx0d1 = 0
    vy0d1 = 0
    vz0d1 = 0
    vxthd1 = 5.789e+03
    vythd1 = 5.789e+03
    vzthd1 = 5.789e+03
    pnvx1 = 64
    pnvy1 = 64
    pnvz1 = 64
    pvxmin1 = -2.0E4
    pvxmax1 = 2.0E4
    pvymin1 = -2.0E4
    pvymax1 = 2.0E4
    pvzmin1 = -2.0E4
    pvzmax1 = 2.0E4
    init_dist1 = 1
    subcycle1 = 32
    vdist_out_subcycle1 = 100
    part_out_subcycle1 = 1
    flux_out_subcycle1 = 1
    nvsqr_out_subcycle1 = 1

; -----   C+   -----
    dist = 2
    nptotcelld2 = 2000
    part_pad=4.0
    n0d2 = 6.000e+10
    md2 = 1.99E-26
    qd2 = 1.60218E-19
    coll_type2 = 1
    coll_rate2 = 1.35E4
    vx0d2 = 0
    vy0d2 = 0
    vz0d2 = 0
    vxthd2 = 1.831e+03
    vythd2 = 1.831e+03
    vzthd2 = 1.831e+03
    pnvx2 = 64
    pnvy2 = 64
    pnvz2 = 64
    pvxmin2 = -5000.
    pvxmax2 = 5000.
    pvymin2 = -5000.
    pvymax2 = 5000.
    pvzmin2 = -5000.
    pvzmax2 = 5000.
    init_dist2 = 1
    subcycle2 = 64
    vdist_out_subcycle2 = 100
    part_out_subcycle2 = 1
    flux_out_subcycle2 = 1
    nvsqr_out_subcycle2 = 1
