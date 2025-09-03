"""
File Purpose: defaults in PlasmaCalcs
"""
import numpy as np

class _Defaults():
    '''stores defaults for PlasmaCalcs. Use DEFAULTS instead.
    (DEFAULTS is an instance of _Defaults(), instantiated at the bottom of defaults.py)
    '''
    def update(self, other_defaults):
        '''update self with other_defaults, overwriting any existing values.
        other_defaults: dict or _Defaults instance
            dict --> update from other_defaults.items()
            else --> update from other_defaults.__dict__.items()
        '''
        if not isinstance(other_defaults, dict):
            other_defaults = other_defaults.__dict__
        for key, value in other_defaults.items():
            setattr(self, key, value)

    TRACEBACKHIDE = True
    IMPORT_FAILURE_WARNINGS = False

    TAB = ' '*4   # size of a single tab, e.g. for docstrings.

    DEBUG = 0   # level of debugging; 0 = no debugging.
    PROGRESS_UPDATES_PRINT_FREQ = 2  # seconds between progress updates

    # skip these attrs during Behavior.label_array(), by default.
    SKIP_BEHAVIOR_ARRAY_LABELS = []

    # size limit for CachesLoader results writable to _pc_caches file.
    # crash with MemorySizeError before writing array larger than this to cache file.
    # (to set to no limit, use None)
    # default 1 MB easily allows <100,000 floats, which is great for 1D arrays,
    #   or timelines, e.g. mean_u across multiple fluids & components,
    #   but not good for values across maindims.
    CACHE_ARRAY_MBYTES_MAX = 1  # [MB]

    # raise MemorySizeError before loading arrays larger than this, by default.
    # (to set to no limit, use None)
    ARRAY_MBYTES_MAX = 1000  # [MB]

    # during memory_size_check, pretend array alements are at least as memory-intensive as this dtype:
    # (only used if array elements are smaller than this dtype.) (to set to no minimum, use None)
    ARRAY_MEMORY_CHECK_DTYPE_MIN = np.float64

    # during load_across_dims, use this many cpus by default, if ncpu not provided.
    # use None to automatically determine limit (based on number of cores available)
    LOADING_NCPU = 1
    # during load_across_dims, timeout after this many seconds, by default, if timeout not provided.
    # timeout numbers must be an integer (due to limitations of signal.alarm method).
    # For no time limit, use None, 0, or negative number.
    LOADING_TIMEOUT = None
    # during load_across_dims, if ncpu>1, group tasks into groups of size ncoarse before performing them.
    # use ncoarse=1 to avoid any coarsening.
    LOADING_NCOARSE = 1
    # during load_across_dims, use this builtins.multiprocessing.pool.Pool instead of making a new one.
    # (if provided, ncpu will be ignored.)
    # use None to make a new pool each time, when needed.
    LOADING_POOL = None

    # [EFF] when stats_dimpoint_wise is None, this tells min size before using stats_dimpoint_wise.
    #    if result would have size less than this, first try stats_dimpoint_wise=False.
    #    (this includes maindims shape.)
    #    (stats_dimpoint_wise True seems to be faster for larger arrays but slower for smaller arrays.)
    #    None --> no minimum, i.e. always prefer stats_dimpoint_wise = False.
    STATS_DIMPOINT_WISE_MIN_N = 512 * 512 * 200
    # [EFF] when stats_dimpoint_wise, this tells min length of dimension before loading across it,
    #   in the first attempt to load across dims implied. 1 --> no minimum.
    #   (if the first attempt fails, will repeat but with min_split=1.)
    STATS_DIMPOINT_WISE_MIN_SPLIT = 10

    # for displaying trees. See Tree._html for details.
    TREE_CSS = '''
    <style type="text/css">
    summary {display: list-item}          /* show arrows for details/summary tags */
    details > *:not(summary){margin-left: 2em;}   /* indent details/summary tags. */
    </style>
    '''
    TREE_SHOW_DEPTH = 4  # default depth to show when displaying trees.
    TREE_SHOW_MAX_DEPTH = 50  # max depth to render as html when displaying trees.
    TREE_SHORTHAND = False  # whether to use shorthand for Tree nodes when displaying trees.

    # fft renaming convention for dimensions, when rad=True, and freq_dims not provided.
    # dict of {old dim: new dim} pairs. Or, None, equivalent to empty dict.
    # for dims not appearing here, new dim will be 'freqrad_{dim}'.
    FFT_FREQ_RAD_DIMNAMES = {    
        'x': 'k_x',
        'y': 'k_y',
        'z': 'k_z',
        't': 'omega',
    }
    # default value for "keep" in xarray_fftN. Should be 0 < value <= 1.
    FFT_KEEP = 0.4
    # default value for "keep" in xarray_lowpass. Should be 0 < value <= 1.
    LOWPASS_KEEP = 0.4

    # default method to use for rounding fractional indexes to integers, as per interprets_fractional_indexing.
    # 'round' --> as per builtins.round(). round to nearest integer, ties toward even integers.
    # 'int' --> as per builtins.int(). round towards 0.
    # 'floor' --> as per math.floor(). round towards negative infinity.
    # 'ceil' --> as per math.ceil(). round towards positive infinity.
    # note that 'floor' is the default to avoid accidentally accessing using index=len(array).
    FRACTIONAL_INDEX_ROUNDING = 'floor'

    # default for gaussian filter sigma, if not provided.
    GAUSSIAN_FILTER_SIGMA = 1.0

    # if this number density in [m^-3] is too large for float32 in output units system,
    # then convert to float64. Commonly relevant if calculating 'n' in 'raw' units for an MhdCalculator.
    MHD_MAX_SAFE_N_SI = 1e30


class _PlotDefaults():
    '''stores defaults for PlasmaCalcs. Use DEFAULTS.PLOT instead.
    (DEFAULTS.PLOT is an instance of _PlotDefaults(), instantiated at the bottom of defaults.py)
    '''
    ASPECT = 'equal'  # default aspect ratio for plots
    LAYOUT = 'compressed'   # default layout for plots. 'constrained', 'compressed', 'tight', or 'none'

    # default for robust when determining vmin & vmax. True, False, or number between 0 and 50.
    # True --> use DEFAULTS.PLOT.ROBUST_PERCENTILE.
    ROBUST = True
    # default percentile for determining vmin & vmax, when using robust.
    ROBUST_PERCENTILE = 2.0

    # default for min_n_ticks on x and y axes
    # None --> use matplotlib default (which is 2, as of 2025-03-20).
    # tuple of (nx, ny) --> use nx as min for x-axis, ny as min for y-axis.
    MIN_N_TICKS = 3
    # whether it's okay for set_min_n_ticks() to fail silently within PlasmaCalcs plotting routines.
    MIN_N_TICKS_FAIL_OK = False

    # default for min_n_ticks on colorbars.
    # None --> use matplotlib default (which is 2, as of 2025-03-20).
    # tuple of (nx, ny) --> use nx as min for horizontal colorbars, ny as min for vertical colorbars.
    MIN_N_TICKS_CBAR = 3
    # whether it's okay for set_min_n_ticks() to fail silently when applied to colorbars
    MIN_N_TICKS_CBAR_FAIL_OK = True

    # # params for plotting.colorbar.make_cax # #
    CAX_PAD = 0.01
    CAX_SIZE = 0.02
    CAX_LOCATION = 'right'
    # # other colorbar params # #
    CAX_MODE = 'mpl'   # 'mpl' or 'pc'. 'mpl' uses matplotlib logic to make cax; 'pc' uses PlasmaCalcs.make_cax.
                        # note that 'pc' looks better if using layout='none', but worse with any other layout.

    # # params for movies # #
    FPS = 30   # frames per second (except for small movies). if None, use matplotlib defaults.
    BLIT = True  # whether to use blitting. if None, use matplotlib defaults.
    MOVIE_EXT = '.mp4'  # movie filename extension to use if none provided. if None, use matplotlib defaults.
    FPS_SMALL = 2  # default frames per second for small movies. if None, use matplotlib defaults.
    NFRAMES_SMALL = 20  # movies with this many or fewer frames use FPS_SMALL by default.

    MOVIE_TITLE_FONT = 'monospace'  # font for movie titles

    # [seconds] minimum time between progress updates when saving movie.
    # use 0 for no minimum; use -1 for "never print".
    MOVIE_PROGRESS_UPDATE_FREQ = 1

    # whether to print help message about how to display movie inline,
    # if it might be applicable (e.g., using ipython) and plt.rcParams['animation.html']=='none'.
    MOVIE_REPR_INLINE_HELP = True

    # # params for subplots # #
    # [chars] suggested width of titles for subplots;
    # some routines might make multiline title if title would be longer than this.
    SUBPLOT_TITLE_WIDTH = 20  

    # [chars] suggested width of suptitle
    # some routines might make multiline suptitle if suptitle would be longer than this.
    SUPTITLE_WIDTH = 40

    # default kwargs for rtitles in subplots
    RTITLE_KW = {
        'rotation': 270,
        'loc': 'outside center right',
        'fontsize': 'large',
    }

    # default kwargs for ttitles in subplots
    TTITLE_KW = {}

    # # other params # #
    # DIMS_INFER tell which array.dims to use for x axis, y axis, and time axis (if movie).
    #   each list will be checked in order, using first match in case of multiple matches.
    #   This only applies when trying to infer plot dims which were not specified.
    DIMS_INFER = {
        # plot time axis
        't': ('time', 't', 'snap', 'snapshot', 'frame'),
        # plot x axis
        'x': ('x', 'r', 'y', 'z',
              'freq_x', 'freq_y', 'freq_z',
              'kx', 'ky', 'kz',
              'k_x', 'k_y', 'k_z',
              'kt', 'k_t', 'ktheta', 'k_theta', 'kang', 'k_ang',
              ),
        # plot y axis
        'y': ('y', 'z',
              'freq_y', 'freq_z',
              'k_y', 'k_z', 'k_mod', 'kmod', 'log_kmod',
              ),
    }
    # if dim in any set in DIMS_SAME, then the other dims are "redundant" with that dim.
    # usually not used, but e.g. in infer_subplot_title, if t_plot_dim is 'snap' or 't',
    # don't include the other one in the subplot title either, since they appear together in a set in DIMS_SAME.
    DIMS_SAME = [
        {'time', 'snap', 't'},
    ]

    SUBPLOTS_MAX_NROWS_NCOLS = 15  # max number of rows or cols in a subplots grid before crashing.
    SUBPLOTS_AXSIZE = (2,2)  # default size of each subplot, in inches.

    # # params for plotting.timelines # #
    # maximum length of a dimension before crashing when plotting timelines.
    # (helps to avoid accidentally creating one line for each x,y,z coords...)
    # e.g. if 10, when plotting 'fluid' and 'component', require len(fluids)<=10 and len(component)<=10.
    TIMELINES_DMAX = 10  # use None for no limit.

    # cycles for timelines. each cycle can be:
    #   dict --> interpretted as {matplotlib kwarg: list of values},
    #   None --> plt.rcParams['axes.prop_cycle']
    #   Cyler (from cycler module)
    TIMELINES_CYCLE0 = None  # default cycle for first dim. 
    TIMELINES_CYCLE1 = {'ls': ['-', '--', ':', '-.', (0,(3,1,1,1,1,1))]}  # default cycle for second dim.
    #  (0,(3,1,1,1,1,1)) means "densely dashdotdotted".

    # max length of strings for xticklabels. Longer than this will be cutoff with ...
    XTICKLABEL_MAXLEN = 15

    # # params for scatter plots # #
    # generic scatter style
    SCATTER_STYLE = {
        'linewidths': 2,
    }
    # style for scatter_max()
    SCATTER_MAX = {
        'marker': 'x',
        'color': 'red',
    }
    # style for scatter_min()
    SCATTER_MIN = {
        'marker': 'o',
        'facecolors': 'none',
        'color': 'red',
    }

    # # params for faceplot # #
    # default viewing angle for 3D faceplots, as (elevation, azimuth, roll).
    # (-160, 30, 0) provides a decent angle for viewing x=0, y=0, z=0 faces.
    FACEPLOT_VIEW_ANGLE = (-160, 30, 0)

    # default kwargs for ax.plot of edges in 3D faceplots.
    # set to None to not plot edges.
    FACEPLOT_EDGE_KWARGS = {'color': '0.4', 'linewidth': 1, 'zorder': 1e3}

    # faceplot axes zoom factor. Default 1. Must be >0. See ax.set_box_aspect for details.
    FACEPLOT_AXES_ZOOM = 1.0

    # aspect for 3D plots
    # 'auto', 'equal', (x aspect, y aspect, z aspect),
    # or (1, x multiplier, y multiplier, z multiplier);
    #    multiplier multiplies aspect determined by data lengths. >1 --> longer.
    ASPECT3D = 'equal'

    # projection type for 3D plots. 'ortho' or 'persp'
    # For more details see mpl_toolkits.mplot3d.axes3d.Axes3D
    PROJ_TYPE = 'ortho'

    # for contour plots, if using colorbar, linewidth of lines in colorbar.
    # None --> use same width as contour lines.
    # 2-tuple of None or int: defines (min, max); None for no bound.
    #   E.g. (4, None) says "for thinner lines use 4; others same as contour lines".
    COLORBAR_LINEWIDTH = (4, None)

    # for contour plots, if using colorbar, linestyle of lines in colorbar.
    # None --> use same linestyle as contour lines.
    COLORBAR_LINESTYLE = None


class _PhysicalDefaults():
    '''stores physical values defaults for PlasmaCalcs. Use DEFAULTS.PHYSICAL instead.
    (DEFAULTS.PHYSICAL is an instance of _PhysicalDefaults(), instantiated at the bottom of defaults.py)
    '''
    # values of various physical constants in SI units
    CONSTANTS_SI = {
        'amu'     : 1.66054e-27,  # atomic mass unit
        'c'       : 2.99792E8,    # speed of light
        'kB'      : 1.38065E-23,  # boltzmann constant
        'eps0'    : 8.85419E-12,  # permittivity of free space
        'mu0'     : 1.256637E-6,  # permeability of free space
        'qe'      : 1.60218E-19,  # elementary charge
        'me'      : 9.10938E-31,  # electron mass
        'qme'     : 1.75882E11,   # q / m_e
        'hplanck' : 6.260701E-34, # planck constant (not hbar)
        'm_proton': 1.67262E-27,  # proton mass
        'eV'      : 1.602176634E-19,    # electron volt
        # also, see below for some additional derived constants:
    }
    CONSTANTS_SI['eV kB-1']  = CONSTANTS_SI['eV'] / CONSTANTS_SI['kB']
    CONSTANTS_SI['me amu-1'] = CONSTANTS_SI['me'] / CONSTANTS_SI['amu']
    for _key, _alias in (('qe', 'q_e'), ('me', 'm_e'), ('m_proton', 'm_p'), ('hplanck', 'h')):
        CONSTANTS_SI[_alias] = CONSTANTS_SI[_key]
    del _key, _alias

    # atomic weight [amu] of each element
    M_AMU = {
        'H' :  1.008,
        'He':  4.003,
        'C' : 12.01,
        'N' : 14.01,
        'O' : 16.0,
        'Ne': 20.18,
        'Na': 23.0,
        'Mg': 24.32,
        'Al': 26.97,
        'Si': 28.06,
        'S' : 32.06,
        'K' : 39.1,
        'Ca': 40.08,
        'Cr': 52.01,
        'Fe': 55.85,
        'Ni': 58.69,
        }

    # first ionization potential [eV] of each element
    IONIZE_EV = {
        'H' : 13.595,
        'He': 24.580,
        'C' : 11.256,
        'N' : 14.529,
        'O' : 13.614,
        'Ne': 21.559,
        'Na':  5.138,
        'Mg':  7.644,
        'Al':  5.984,
        'Si':  8.149,
        'S' : 10.357,
        'K' :  4.339,
        'Ca':  6.111,
        'Cr':  6.763,
        'Fe':  7.896,
        'Ni':  7.633,
        }

    # degeneracy of states, for saha ionization equation
    SAHA_G0 = {
        'H' :  2.0,
        'He':  1.0,
        'C' :  9.3,
        'N' :  4.0,
        'O' :  8.7,
        'Ne':  1.0,
        'Na':  2.0,
        'Mg':  1.0,
        'Al':  5.9,
        'Si':  9.5,
        'S' :  8.1,
        'K' :  2.1,
        'Ca':  1.2,
        'Cr': 10.5,
        'Fe': 26.9,
        'Ni': 29.5,
        }
    SAHA_G1 = {
        'H' :  1.0,
        'He':  2.0,
        'C' :  6.0,
        'N' :  9.0,
        'O' :  4.0,
        'Ne':  5.0,
        'Na':  1.0,
        'Mg':  2.0,
        'Al':  1.0,
        'Si':  5.7,
        'S' :  4.1,
        'K' :  1.0,
        'Ca':  2.2,
        'Cr':  7.2,
        'Fe': 42.7,
        'Ni': 10.5,
        }
    SAHA_G1G0 = {}
    for _e in SAHA_G0:
        SAHA_G1G0[_e] = SAHA_G1[_e] / SAHA_G0[_e]
    del _e


class _AddonDefaults():
    '''stores defaults for PlasmaCalcs. Use DEFAULTS.ADDONS instead.
    (DEFAULTS.ADDONS is an instance of _AddonDefaults(), instantiated at the bottom of defaults.py)
    '''
    # whether to try to load TFBI theory hookup module.
    # note - adjusting this value after importing PlasmaCalcs will have no effect;
    #    only relevant if adjusted before trying to import PlasmaCalcs.
    # 'attempt' --> try it, but if it fails, don't raise an error.
    # True --> try it, and if it fails, raise an error.
    # False --> don't try it.
    LOAD_TFBI = 'attempt'  # 'attempt', True, or False

    # default max number of ions to consider in TFBI theory, before printing a warning.
    # using more ions (e.g., 4, 5, 6+) gets much slower and less accurate.
    #   theory involves solving ratio of polynomials with degree = 4 * number of fluids.
    #   (numerator degree 2 smaller if using "QN" form of dispersion relation.)
    TFBI_MAX_NUM_IONS = 5

    # default tfbi_EBspeed_grid logmin, logmax, and logstep
    TFBI_EBSPEED_LOGMIN = 3
    TFBI_EBSPEED_LOGMAX = 4   # 4 is sufficient for all simulated TFBI suite points.
    TFBI_EBSPEED_LOGSTEP = 0.01

    # default max Mbytes for tfbi_inputs when solving tfbi_vs_EBspeed.
    # the tfbi_inputs Mbytes are checked before setting EBspeed to the EBspeed grid.
    TFBI_EBSPEED_INPUTS_MBYTES_MAX = 0.1

    # threshold for confirming "yes there is tfbi growth predicted here"
    # 0.0 is the theoretical threshold.
    # a small positive value (e.g. 0.001) helps to avoid tiny errors,
    #   and also ensures the growth is "not so slow that the background conditions might change",
    #   e.g. in the chromosphere the background might change after a few seconds;
    #       10 seconds corresponds to a threshold of 0.1.
    TFBI_GROWTH_THRESH = 0.001

    # default legend_kw for klines in growthplot.
    GROWTHPLOT_LEGEND_KW = dict(
        bbox_to_anchor=(0.2, 0.95),
        loc='upper right',
        fontsize='xx-small',
        handlelength=5,
    )

    # default legend_kw for klines in growthplots (plural).
    GROWTHPLOTS_LEGEND_KW = dict(
        bbox_to_anchor=(0.2, 0.8),
        loc='lower right',
        fontsize='xx-small',
        handlelength=5,
    )


class _EppicDefaults():
    '''stores defaults for PlasmaCalcs. Use DEFAULTS.EPPIC instead.
    (DEFAULTS.EPPIC is an instance of _EppicDefaults(), instantiated at the bottom of defaults.py)
    '''
    # how many digits to zfill eppic snapshot numbers with
    H5_SNAP_ZFILL = 6

    # eppic dx,dy,dz = unsafe_dspace * safety. Probably ~1 or a bit larger.
    # e.g. might use unsafe_dspace = electron ldebye.
    # larger values here are LESS safe.
    DSPACE_SAFETY = 1.1

    # eppic dt = smallest timescale * safety. Probably ~1 or a bit smaller.
    # larger values here are LESS safe.
    DT_SAFETY = 0.9

    # eppic Nx,Ny,Nz = unsafe_Nspace * safety. Probably ~10.
    # e.g. might use unsafe_Nspace = expected scale size of physical features (e.g. 1 wavelength)
    # Nx,Ny,Nz is the actual total number of grid cells in each dimension.
    # Nx=nx*nsubdomains; Ny=ny; Nz=nz.
    NSPACE_SAFETY = 5

    # eppic nt = unsafe_nt * safety. Probably ~20.
    # e.g. might use unsafe_nt = expected timescale of physical features (e.g. 1/growthrate)
    # nt is the total number of timesteps.
    NTIME_SAFETY = 40

    # default safety factor for runtime guess.
    # Consider setting requested time in .slurm file to n_processors * runtime guess * safety.
    # Seems like 1 is usually good enough.
    # (Checked on my tfbi2_eff_RUNS and a bunch of other runs.
    #   For the bigger "production" runs, 1 would have always been (just barely) good enough.
    #   For eff_RUNS, ~25% need >1.5, ~15% need >2, ~4% need >2.5, 0% need >2.7.
    RUNTIME_SAFETY = 1.2

    # eppic nout (before rounding) = min(waveprop_nout, growth_nout)
    # waveprop_nout = (waveprop_time / dt) * NOUT_WAVEPROP_SAFETY
    # growth_nout = (timescale_growth / dt) * NOUT_GROWTH_SAFETY
    # Larger values are LESS safe.
    # E.g. NOUT_WAVEPROP_SAFETY=0.25 implies "at least 4 snapshots per 1 wavelength of wave motion."
    # E.g. NOUT_GROWTH_SAFETY=0.1 implies "at least 10 snapshots per 1 e-folding of growth."
    NOUT_WAVEPROP_SAFETY = 0.25
    NOUT_GROWTH_SAFETY = 0.125

    # eppic nout (rounded appropriately) will be a multiple of NOUT_MULTIPLE * max safe_pow2_subcycle.
    # E.g., nout_multiple=5 causes nout to be a multiple of 10,
    #    assuming safe_pow2_subcycle > 1 for at least 1 specie
    #    (subcycle=2^N with N>0 --> subcycle * 5 will be divisible by 10).
    # Use nout_multiple=1 to ignore this value and just use the max safe_pow2_subcycle requirement.
    NOUT_MULTIPLE = 1

    # safety factor for Rosenberg's criterion for quasineutrality:
    #   quasineutrality is "reasonable" when (nusn / wplasma)^2 << 1.
    #   (use '<= EPPIC.ROSENBERG_SAFETY' instead of '<< 1'.)
    ROSENBERG_SAFETY = 0.5

    # number of "sigma" (thermal widths) to include in eppic vdist outputs.
    # e.g. if vout_nsigma = 3, then vdist will include -3 vthermal to +3 vthermal.
    VDIST_NSIGMA = 4

    # safety factor for subcycling in eppic. Larger is safer.
    # when making eppic input deck, will use subcycle = largest 2^N <= (best possible subcycling / safety)
    SUBCYCLE_SAFETY = 1.5

    # rounding to use for npd choices. None --> round to nearest int
    # e.g. use 10 if you want all npd choices to be rounded to the nearest 10.
    NPD_ROUNDING = 10

    # "target cost" of each subcycled species, when picking number of particles (npd).
    # the idea is to use npd(subcycled) = npd(unsubcycled) * npd_mul_cpu_cost * subcycling
    # e.g. if dist 1 has subcycling = 32, and NPD_MUL_CPU_COST = 0.1,
    #     and dist 0 has subcycling = 1, npd=1000,
    #    then dist 1 should target npd = 3200.
    # (might be lower or higher due to rounding; see NPD_MUL_MAX and NPD_MUL_INCREMENT.)
    NPD_MUL_CPU_COST = 0.2

    # maximum npd_mul to use for subcycled species.
    # e.g. if dist 1 has subcycling = 256, and NPD_MUL_CPU_COST = 0.1,
    #     and NPD_MUL_MAX = 5, then use npd_mul of 5 instead of 25.6.
    # None --> no maximum.
    NPD_MUL_MAX = 10

    # default ndim_space when making eppic input dicks via EppicInstabilityCalculator.
    NDIM_SPACE = 2

    # minimum value for nx when making eppic input decks via EppicInstabilityCalculator.
    #   (can vary total Nx via nsubdomains instead of just nx.
    #    if nx is too small, can see "particle jumps more than entire mesh" error, though.
    #    4 is okay for quick runs, 8 is usually safe, 16 is "always" safe.
    #    should probably be a power of 2.)
    NX_MIN = 16

    # maximum value for nsubdomains when making eppic input decks via EppicInstabilityCalculator.
    # if need more Nx than NX_MIN * NSUBDOMAINS_MAX, will use nx > NX_MIN.
    # [TODO] implement auto-check: ncpu / nsubdomains MUST be a whole number,
    #    so if ncpu is known, need to use nsubdomains max = min(NSUBDOMAINS_MAX, 2^N),
    #    with N == number of factors of 2 inside ncpu. (E.g. ncpu=56 == (2^3)*7 --> N=3)
    NSUBDOMAINS_MAX = 512

    # default nptotcelld for the uncycled distribution (not necessarily dist 0),
    #   when making eppic input decks via EppicInstabilityCalculator.
    NPTOTCELLD0 = 100

    # eppic iwrite = nout * IWRITE_NSNAP.
    #   I.e. writing dump every IWRITE_NSNAP snapshots.
    #   (If making input deck via EppicInstabilityCalculator.)
    IWRITE_NSNAP = 100

    # default values for "other" (e.g., numerical choices) global vars.
    # Nx, Nt, dx, dt handled elsewhere (these are physically meaningful choices, usually.)
    GLOB_DEFAULTS = {
        'nout_avg': 2,  # spatially averaging output arrays by this factor in each dimension.
        'hdf_output_arrays': 2,   # output type. Use 2 for parallel. (non-2 options are very old.)
        'npout': 4000,  # fraction of particles to output; irrelevant(?) when hdf_output_arrays == 2.
        'iwrite_nsnap': 50,  # Equivalent to using iwrite = iwrite_nsnap * nout.
        'iread': 0,  # start from t=0 (iread=0) or dump (iread=1)
        'divj_out_subcycle': -1,  # output divj every Nth timestep. -1 --> don't output divj.
        'fwidth': 3,  # k-space "width" for phi low-pass filter function
        'fsteep': 3,  # k-space "steepness" for phi low-pass filter function
    }

    # default values for "other" distribution vars.
    DIST_DEFAULTS = {
        'init_dist': 1,   # how to initialize the distribution. I've been using 1. (-SE 2025/02/10)
        'part_pad': 4.0,  # max number of particles ever on a single processor == initial amount * part_pad.
        'coll_type': 1,   # collision type for each distribution... I've been using 1. (-SE 2025/02/10)
        'pnvx': 64,  # number of points in the x direction when outputting vdist
        'pnvy': 64,  # number of points in the y direction when outputting vdist
        'pnvz': 32,  # number of points in the z direction when outputting vdist
        # output subcycles: output some info only every Nth snapshot.
        'vdist_out_subcycle': 64,  # velocity distributions. Info I'm not using, hence large number. (-SE 2025/02/10)
        'part_out_subcycle': 1,   # density info - probably want this every snapshot!
        'flux_out_subcycle': 8,   # I don't need flux or nvsqr info nearly as often as density info;
        'nvsqr_out_subcycle': 8,  #  subcycling these also significantly reduces output filesize. (-SE 2025/02/10)
    }


DEFAULTS = _Defaults()
DEFAULTS.PLOT = _PlotDefaults()  # e.g., can access CAX_PAD via DEFAULTS.PLOT.CAX_PAD
DEFAULTS.PHYSICAL = _PhysicalDefaults()  # e.g., can access M_AMU via DEFAULTS.PHYSICAL.M_AMU
DEFAULTS.ADDONS = _AddonDefaults()
DEFAULTS.EPPIC = _EppicDefaults()
