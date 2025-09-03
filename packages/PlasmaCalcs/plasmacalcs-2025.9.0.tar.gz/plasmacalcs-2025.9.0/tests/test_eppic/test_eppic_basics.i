; EPPIC parameter file (also readable by IDL)
    title = 'Chromosphere 1024 dev1_longer B10G E9V e- H+ C+'
; edited, inspired by from dropbox folder chromo2048meRealB10GE9V211111
; modified for use with PlasmaCalcs tests.
;
; Mesh size and Grid size
    ndim_space = 2
    nsubdomains = 32
    nx = 32
    dx = 1.1e-02
    ny = 1024
    dy = 1.1e-02
    nz = 1
    dz = 1.1e-02
; Time step, number of time steps to run, and time-steps between output:
    dt = 3.0e-08  ; previously=1.6E-8
    nt = 128000
    nout = 640
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
    iwrite = 25600
; Start from t=0 (iread=0) or dump (iread=1)
    iread = 0
; Number of distributions to initialize
    ndist = 3
; Limit the frequency of outputing divj:
    divj_out_subcycle = 100
; Neutral parameters:
    vth_neutral = 5.744e+03  ; T = 4000 K.  ; previously=5716.4
    m_neutral = 1.6738E-27
; External Electric field in x-direction
    Ex0_external = 9.0

; -----   e-   -----
    dist = 0
    npd0 = 250000
    part_pad=2.0
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
    ;denft_out_subcycle1 = 100
    denft_out_kmax1 = 16.

; -----   H+   -----
    dist1 = 1
    npd1 = 1000000
    part_pad=2.0
    n0d1 = 3.000e+11
    md1 = 1.67262E-27
    qd1 = 1.60218E-19
    coll_type1 = 1 
    coll_rate1 = 6.7E5
    vx0d1 = 0
    vy0d1 = 0
    vz0d1 = 0
    vxthd1 = 5.789e+03  ; previously=5.746e+03
    vythd1 = 5.789e+03  ; previously=5.746e+03
    vzthd1 = 5.789e+03  ; previously=5.746e+03
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
    ;denft_out_subcycle1 = 100
    denft_out_kmax1 = 20.

; -----   C+   -----
    dist = 2
    npd2 = 320000
    part_pad=2.0
    n0d2 = 6.000e+10
    md2 = 1.99E-26
    qd2 = 1.60218E-19
    coll_type2 = 1
    coll_rate2 = 1.4E4
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
    ;denft_out_subcycle2 = 100
    denft_out_kmax2 = 20.
