import math
import os

import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation, FFMpegWriter

import PlasmaCalcs

# SET PATH TO FFMPEG
working_from_home = False

laptop_ffmpeg_path = r'C:\\Users\\ratta\\PycharmProjects\\pythonProject\\1D_PIC\\EM1D_PIC\\ffmpeg\\bin\\ffmpeg.exe'
bu_ffmpeg_path = r'C:\\Users\\ratta\\PycharmProjects\\EM1D\\ffmpeg\\bin\\ffmpeg.exe'

if working_from_home:
    ffmpeg_path = laptop_ffmpeg_path
else:
    ffmpeg_path = bu_ffmpeg_path

# SET VIDEO WRITER PATH
rcParams['animation.ffmpeg_path'] = ffmpeg_path

# INPUT PARAMETERS
path_to_folder = r"G:\My Drive\Research\eppic_out\eregion"
folder_names = {"FBI, normal": "FBI_normal", "FBI, Maxwell": "FBI_maxwell", "laminar, normal": "laminar_normal",
                "laminar, Maxwell": "laminar_maxwell"}  # key: nickname, value: folder name
n_columns = 4
run_axis = "cols"  # The axis where runs differ: "rows" or "cols"
species_to_plot = {1: "Ion"}  # key: number, value: name
plot_quantity = "n"
plot_every = 1
slices = ({"x": 0}, {"y": 0}, {"z": 0})
# slices = ({"x": 0},)
mp4_name = f"den{''.join(map(str, species_to_plot))}"


# FUNCTION TO MERGE RIGHT SUBPLOTS (modified from a function in Save2541/1DEMPyPIC/animation.py)
def merge_right_subplots(fig, axs):
    """
    Merge all subplots in the right column to create a tall subplot for the colorbar
    :param fig: figure
    :param axs: axes
    :return: merged right axis
    """
    gs = axs[0, -1].get_gridspec()
    # Remove the underlying axes
    for ax in axs[:, -1]:
        ax.remove()
    return fig.add_subplot(gs[:, -1])


# CREATE CANVAS
n_plots = len(folder_names) * len(species_to_plot) * len(slices)
n_rows = math.ceil(n_plots / n_columns)
column_ratios = [1] * n_columns
column_ratios.append(0.05)
fig, axs = plt.subplots(nrows=n_rows, ncols=n_columns + 1, width_ratios=column_ratios, squeeze=False,
                        figsize=[20, 11.25])
cb_ax = merge_right_subplots(fig, axs)

# SET MEMORY LIMIT
PlasmaCalcs.DEFAULTS.ARRAY_MBYTES_MAX = 50000

# LOAD INPUT DECKS
ec_list = []
snap_list = []
for run in folder_names:
    this_path = os.path.join(path_to_folder, folder_names[run], "eppic.i")
    ec = PlasmaCalcs.EppicCalculator.from_here(this_path, kw_units={"M": 1}, u_l=1)
    ec_list.append(ec)
    sample_snaps = ec.snaps[::plot_every]
    snap_list.append(sample_snaps)

# GET NUMBER OF TIME STEPS TO RUN (EQUAL TO THE TIME STEP OF THE RUN WITH THE LEAST TIME STEPS)
number_of_time_steps_to_run = min([len(x) for x in snap_list])


# FUNCTION TO GET THE NEXT ROW, COLUMN
def get_next_coordinates(current_coordinates=None, shape=(n_rows, n_columns), mode=run_axis, reset=False):
    """
    Get next (row, column) from the current (row, current).
    """
    if reset:
        return 0, 0
    current_row, current_column = current_coordinates
    number_of_rows, number_of_columns = shape
    if mode == "cols":
        if current_row < number_of_rows - 1:
            current_row += 1
        elif current_column < number_of_columns - 1:
            current_column += 1
            current_row = 0
        else:
            return 0, 0
    elif mode == "rows":
        if current_column < number_of_columns - 1:
            current_column += 1
        elif current_row < number_of_rows - 1:
            current_row += 1
            current_column = 0
        else:
            return 0, 0
    else:
        assert False, "NotImplemented"
    return current_row, current_column


# GET PLOT TITLES
plot_titles = {}
this_row, this_column = get_next_coordinates(reset=True)
for description in folder_names:
    for species in species_to_plot:
        species_name = species_to_plot[species]
        for _ in slices:
            plot_titles.setdefault(this_row, {})[this_column] = f"{species_name} Density ({description})"
            this_row, this_column = get_next_coordinates((this_row, this_column))


# GET MINIMUM AND MAXIMUM VALUES
def get_min_max(array, old_minimum, old_maximum):
    """
    Get minimum and maximum values
    """
    new_minimum = array.min().item()
    new_maximum = array.max().item()
    if old_minimum is not None:
        new_minimum = min(new_minimum, old_minimum)
    if old_maximum is not None:
        new_maximum = min(new_maximum, old_maximum)
    return new_minimum, new_maximum


# CONTAINER OF PLOT OBJECTS
plot_list = []
title_list = []
cb_list = []


# INITIALIZE PLOTS
def initialize_plots():
    """
    Initialize plots
    """
    current_coordinates = get_next_coordinates(reset=True)
    data_list = []
    time_list = []
    minimum, maximum = None, None
    for run_number in range(len(ec_list)):
        ec = ec_list[run_number]
        this_snap = snap_list[run_number][0]
        ec.snap = this_snap
        for species in species_to_plot:
            ec.fluid = species
            for slice_dict in slices:
                # GET DATA
                array = ec(plot_quantity).isel(**slice_dict)
                minimum, maximum = get_min_max(array, minimum, maximum)
                data_list.append(array)
                time_list.append(this_snap.t)
    for plot_number in range(len(time_list)):
        # GET AXIS
        this_axis = axs[current_coordinates[0], current_coordinates[1]]
        # GET PLOT TITLE
        title = plot_titles[current_coordinates[0]][current_coordinates[1]] + f" (Time = {time_list[plot_number]} s.)"
        # PLOT ON AXIS
        data = data_list[plot_number]
        x_label, y_label = data.indexes
        x_values, y_values = data.indexes.values()
        plot_extent = (x_values[0], x_values[-1], y_values[0], y_values[-1])
        plot = this_axis.imshow(data.T, cmap="plasma", vmin=minimum, vmax=maximum, aspect="auto", extent=plot_extent,
                                origin="lower")
        this_axis.set_xlabel(x_label)
        this_axis.set_ylabel(y_label)
        # SET TITLE & ADD TO TITLE LIST
        title_list.append(this_axis.set_title(title))
        # ADD TO PLOT LIST
        plot_list.append(plot)
        # UPDATE ROW & COLUMN
        current_coordinates = get_next_coordinates(current_coordinates)

    # TIGHT LAYOUT
    plt.tight_layout()

    # CREATE COLOR BAR
    cb_list.append(plt.colorbar(plot_list[0], cax=cb_ax))


# EXTRACT DATA (FOR EACH TIME STEP)
def animate(time_step):
    """
    Extract data for each time step
    """
    current_coordinates = get_next_coordinates(reset=True)
    data_list = []
    time_list = []
    minimum, maximum = None, None
    for run_number in range(len(ec_list)):
        ec = ec_list[run_number]
        this_snap = snap_list[run_number][time_step]
        ec.snap = this_snap
        for species in species_to_plot:
            ec.fluid = species
            for slice_dict in slices:
                # GET DATA
                try:
                    array = ec(plot_quantity).isel(**slice_dict)
                except:
                    old_snap = snap_list[run_number][time_step - 1]
                    ec.snap = old_snap
                    array = ec(plot_quantity).isel(**slice_dict)
                    ec.snap = this_snap
                minimum, maximum = get_min_max(array, minimum, maximum)
                data_list.append(array)
                time_list.append(f"{this_snap.t:.4f}")
    for plot_number in range(len(time_list)):
        # UPDATE PLOT
        this_plot = plot_list[plot_number]
        this_plot.set_data(data_list[plot_number].T)
        this_plot.set_clim(minimum, maximum)
        # UPDATE TITLE
        this_title = title_list[plot_number]
        title = plot_titles[current_coordinates[0]][current_coordinates[1]] + f" (Time = {time_list[plot_number]} s.)"
        this_title.set_text(title)
        # UPDATE ROW & COLUMN
        current_coordinates = get_next_coordinates(current_coordinates)

    # UPDATE COLOR BAR
    # cb_list[0].mapable.set_clim(minimum, maximum)

    # TIGHT LAYOUT
    # plt.tight_layout()

    # PRINT TIME STEP
    print(time_step)

    # RETURN ARTISTS
    return plot_list, title_list, cb_list


# ANIMATE
anim = FuncAnimation(fig, animate, init_func=initialize_plots, save_count=number_of_time_steps_to_run)
# SAVE ANIMATION
f = os.path.join(path_to_folder, f"{mp4_name}.mp4")
os.makedirs(os.path.dirname(f), exist_ok=True)
writer_video = FFMpegWriter(fps=24)
anim.save(f, writer=writer_video)
print(f"Finished writing to {f}.")
plt.close()
