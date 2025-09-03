import math
import os
import numpy as np
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
#folder_names = {"FBI, normal": "FBI_normal"}
folder_names = {"FBI, normal": "FBI_normal", "FBI, Maxwell": "FBI_maxwell", "laminar, normal": "laminar_normal",
                "laminar, Maxwell": "laminar_maxwell"}  # key: nickname, value: folder name
n_columns = 4
species_to_plot = {1: "Ion"}  # key: number, value: name
plot_quantity = "u"
plot_every = 80
n_bins = 64
plot_range = [[-2000, 2000], [-2000, 2000]] #  [[xmin, xmax], [ymin, ymax]]
slices = (("x", "y"), ("y", "z"), ("x", "z"))
mp4_name = f"test{''.join(map(str, species_to_plot))}"


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
fig, axs = plt.subplots(nrows=n_rows, ncols=n_columns + 1, width_ratios=column_ratios, squeeze=False, figsize=[20, 11.25])
cb_ax = merge_right_subplots(fig, axs)


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
def get_next_coordinates(current_coordinates=None, shape=(n_rows, n_columns), reset=False):
    """
    Get next (row, column) from the current (row, current).
    """
    if reset:
        return 0, 0
    current_row, current_column = current_coordinates
    number_of_rows, number_of_columns = shape
    if current_row < number_of_rows - 1:
        current_row += 1
    elif current_column < number_of_columns - 1:
        current_column += 1
        current_row = 0
    else:
        return 0, 0
    return current_row, current_column


# GET PLOT TITLES AND AXIS LABELS
plot_titles = {}
x_labels = {}
y_labels = {}
this_row, this_column = get_next_coordinates(reset=True)
for description in folder_names:
    for species in species_to_plot:
        species_name = species_to_plot[species]
        for components in slices:
            x_labels.setdefault(this_row, {})[this_column] = f"v{components[0]} (m/s)"
            y_labels.setdefault(this_row, {})[this_column] = f"v{components[1]} (m/s)"
            plot_titles.setdefault(this_row, {})[this_column] = f"{species_name} velocity distribution ({description})"
            this_row, this_column = get_next_coordinates((this_row, this_column))


# CONTAINER OF PLOT OBJECTS
plot_list = []
title_list = []
x_edges_list = []
y_edges_list = []
cb_list = []

# INITIALIZE PLOTS
def initialize_plots():
    """
    Initialize plots
    """
    current_coordinates = get_next_coordinates(reset=True)
    data_list = []
    time_list = []
    for run_number in range(len(ec_list)):
        ec = ec_list[run_number]
        this_snap = snap_list[run_number][0]
        ec.snap = this_snap
        for species in species_to_plot:
            ec.fluid = species
            for components in slices:
                data_pair = []
                for component in components:
                    ec.component = component
                    # GET DATA
                    array = ec(plot_quantity).values.ravel()
                    data_pair.append(array)
                data_list.append(data_pair)
                time_list.append(this_snap.t)

    for plot_number in range(len(time_list)):
        # GET AXIS
        this_axis = axs[current_coordinates[0], current_coordinates[1]]
        # GET PLOT TITLE
        title = plot_titles[current_coordinates[0]][current_coordinates[1]] + f" (Time = {time_list[plot_number]} s.)"
        # PLOT ON AXIS
        xdata, ydata = data_list[plot_number]
        _, x_edges, y_edges, plot = this_axis.hist2d(xdata, ydata, bins=n_bins, range=plot_range, norm="log", density=True)
        this_axis.set_xlabel(x_labels[current_coordinates[0]][current_coordinates[1]])
        this_axis.set_ylabel(y_labels[current_coordinates[0]][current_coordinates[1]])
        # SET TITLE & ADD TO TITLE LIST
        title_list.append(this_axis.set_title(title))
        # ADD TO PLOT LIST
        plot_list.append(plot)
        # ADD TO EDGES LIST
        x_edges_list.append(x_edges)
        y_edges_list.append(y_edges)
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
    for run_number in range(len(ec_list)):
        ec = ec_list[run_number]
        this_snap = snap_list[run_number][time_step]
        ec.snap = this_snap
        for species in species_to_plot:
            ec.fluid = species
            for components in slices:
                data_pair = []
                for component in components:
                    ec.component = component
                    # GET DATA
                    try:
                        array = ec(plot_quantity).values.ravel()
                    except:
                        old_snap = snap_list[run_number][time_step - 1]
                        ec.snap = old_snap
                        array = ec(plot_quantity).values.ravel()
                        ec.snap = this_snap
                    data_pair.append(array)
                data_list.append(data_pair)
                time_list.append(f"{this_snap.t:.4f}")

    for plot_number in range(len(time_list)):
        # UPDATE PLOT
        this_plot = plot_list[plot_number]
        data_pair = data_list[plot_number]
        data = np.histogram2d(*data_pair, bins=[x_edges_list[plot_number], y_edges_list[plot_number]])[0]
        this_plot.set_array(data)
        # UPDATE TITLE
        this_title = title_list[plot_number]
        title = plot_titles[current_coordinates[0]][current_coordinates[1]] + f" (Time = {time_list[plot_number]} s.)"
        this_title.set_text(title)
        # UPDATE ROW & COLUMN
        current_coordinates = get_next_coordinates(current_coordinates)

    # UPDATE COLOR BAR
    #cb_list[0].mapable.set_clim(minimum, maximum)

    # TIGHT LAYOUT
    #plt.tight_layout()

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
