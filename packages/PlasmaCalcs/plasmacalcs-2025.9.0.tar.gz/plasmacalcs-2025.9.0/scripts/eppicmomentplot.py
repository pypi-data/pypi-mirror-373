import math
import os

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

import PlasmaCalcs

# SET PATH
path_to_folder = r"G:\My Drive\Research\eppic_out\eregion"
folder_names = {"FBI, normal": "FBI_normal", "FBI, Maxwell": "FBI_maxwell", "laminar, normal": "laminar_normal", "laminar, Maxwell": "laminar_maxwell"}  # key: nickname, value: folder name

# SET SPECIES
species_names = ("Electron", "Ion")  # list ALL species names IN THE SAME ORDER as in the simulation

# SET PLOT SPECIFICATIONS
moment_to_plot = (1,)  # 1: mean, 2: variance, etc.
plot_absolute_value = True
directions_to_plot = ("y",)

# SET PLOT CONFIGURATIONS
separate_species = True  # True: one species per plot, False: all species in one plot
separate_runs = False  # True: one run per plot, False: all runs in one plot

# SPECIAL CONFIGURATIONS
n_columns = 2  # number of plot columns
convert_variance_to_temperature = True  # plot variance in units of temperature instead of velocity squared

# SET PDF NAME
pdf_name = None  # Set to None for auto naming
if pdf_name is None:
    pdf_name = "_vs_".join(folder_names.keys())
    pdf_name += "_moment"
    for number in moment_to_plot:
        pdf_name += str(number)

# SET Y LABEL
y_label = None  # Set to None for auto naming
if y_label is None:
    if len(moment_to_plot) == 1:
        moment, = moment_to_plot
        if moment == 1:
            if plot_absolute_value:
                y_label = "|Velocity| (m/s)"
            else:
                y_label = "Velocity (m/s)"
        elif moment == 2:
            if convert_variance_to_temperature:
                y_label = "Temperature (K)"
            else:
                y_label = "Variance (m2 s-2)"
        elif moment == 3:
            y_label = "Third moment (m3 s-3)"
        elif moment == 4:
            y_label = "Fourth moment (m4 s-4)"
        else:
            assert False, "Invalid moment"
    else:
        y_label = "Value"


# FUNCTION TO GET PLOT TITLES
def _get_plot_titles(all_runs, all_species, number_of_columns, title_prefix="", title_suffix=""):
    """
    Get plot titles
    """
    n_sp = len(all_species)
    n_r = len(all_runs)
    title_list = []
    if separate_runs and n_r > 1:
        if separate_species and n_sp > 1:
            number_of_rows = math.ceil(n_sp * n_r / number_of_columns)
            for key in all_runs:
                for species in all_species:
                    title_list.append(f"{title_prefix} {species} ({key}) {title_suffix}")
        else:
            number_of_rows = math.ceil(n_r / number_of_columns)
            for key in all_runs:
                title_list.append(f"{title_prefix} {key} {title_suffix}")
    else:
        if separate_species and n_sp > 1:
            number_of_rows = math.ceil(n_sp / number_of_columns)
            for species in all_species:
                title_list.append(f"{title_prefix} {species} {title_suffix}")
        else:
            number_of_rows = 1
            number_of_columns = 1
            title_list.append(f"{title_prefix} {title_suffix}")

    # RESHAPE LIST
    reshaped_title_list = []
    title_counter = 0
    for _ in range(number_of_rows):
        temporary_list = []
        for _ in range(number_of_columns):
            if title_counter == len(title_list):
                temporary_list.append(None)
            else:
                temporary_list.append(title_list[title_counter])
                title_counter += 1
        reshaped_title_list.append(temporary_list)

    return reshaped_title_list


# SET PLOT TITLE
plot_titles = None  # Set to None for auto naming
title_prefix = "3D"
title_suffix = "drift parallel to E0"
if plot_titles is None:
    plot_titles = _get_plot_titles(folder_names, species_names, n_columns, title_prefix=title_prefix, title_suffix=title_suffix)
    print(plot_titles)

# GET SHAPE
n_rows = len(plot_titles)
n_columns = len(plot_titles[0])

# CREATE CANVAS
fig, axs = plt.subplots(n_rows, n_columns, figsize=[15, 8.5], squeeze=False)

# SET PDF PATH
pdf_path = os.path.join(path_to_folder, list(folder_names.values())[-1], f"{pdf_name}.pdf")

# SET COUNTERS
this_row = 0
this_column = 0

# NAME COLUMNS IN moments{fluid}.out (MIGHT NOT BE THE SAME FOR 2D RUNS!!!)
column_names = ['Index', 'Vx_Mean', 'Vx_Variance', 'Vx_Moment3', 'Vx_Moment4', 'Vy_Mean', 'Vy_Variance',
                'Vy_Moment3', 'Vy_Moment4', 'Vz_Mean', 'Vz_Variance', 'Vz_Moment3', 'Vz_Moment4']
assert len(column_names) == len(set(column_names)), "Duplicate column names"

# GET THE NAMES OF USED COLUMNS
columns_to_use = []
columns_to_convert_to_temperature = []
direction_dict = {"x": 0, "y": 4, "z": 8}
for moment in moment_to_plot:
    assert moment in (1, 2, 3, 4), "Invalid Moment"
    for direction in directions_to_plot:
        index = direction_dict[direction] + moment
        column_name = column_names[index]
        columns_to_use.append(column_name)
        if moment == 2 and convert_variance_to_temperature:
            columns_to_convert_to_temperature.append(column_name)

# MAKE THE PDF
with PdfPages(pdf_path) as pdf:

    # LOOP THROUGH EACH RUN
    for run in folder_names:

        # GET PATH
        this_path = os.path.join(path_to_folder, folder_names[run])

        # LOAD INPUT DECK
        ec = PlasmaCalcs.EppicCalculator.from_here(os.path.join(this_path,"eppic.i"), kw_units={"M": 1}, u_l=1)

        # GET NUMBER OF FLUIDS
        n_fluids = len(ec.fluids)

        # GET TIMES
        times = ec.snaps.t

        # GET kB
        kb = ec.u("kB")

        # LOOP THROUGH EACH SPECIES
        for fluid in range(n_fluids):
            # GET PATH TO FILE
            file_path = os.path.join(this_path, "domain000", f"moments{fluid}.out")

            # LOAD DATA
            data = pd.read_csv(file_path, sep='\s+', header=None, skiprows=1,
                               names=column_names, usecols=columns_to_use)

            # SPECIFY AXIS
            this_axis = axs[this_row, this_column]

            # SET TIMES
            data["Time"] = times

            # GET SPECIES MASS
            m = ec.fluids.m[fluid]

            # CONVERT VARIANCE TO TEMPERATURE
            factor = m / kb
            for column_name in columns_to_convert_to_temperature:
                data[column_name] *= factor

            # CONVERT TO ABSOLUTE VALUE
            if plot_absolute_value:
                for column_name in columns_to_use:
                    data[column_name] = abs(data[column_name])

            # RENAMING COLUMNS (FOR LEGENDS)
            new_names = {}
            if separate_species:
                if separate_runs:
                    for old_name in columns_to_use:
                        new_names[old_name] = old_name
                else:
                    for old_name in columns_to_use:
                        new_names[old_name] = f"{old_name} ({run})"
            else:
                if separate_runs:
                    for old_name in columns_to_use:
                        new_names[old_name] = f"{species_names[fluid]} {old_name}"
                else:
                    for old_name in columns_to_use:
                        new_names[old_name] = f"{species_names[fluid]} {old_name} ({run})"

            data.rename(columns=new_names, inplace=True)

            # PLOT DATA
            data.plot(x="Time", ax=this_axis)

            # SET TITLE AND LABELS
            this_axis.set_title(plot_titles[this_row][this_column])
            this_axis.set_xlabel("Time (s)")
            this_axis.set_ylabel(y_label)

            # ADVANCE AXIS
            if separate_species:
                if this_column == n_columns - 1:
                    this_row += 1
                    this_column = 0
                else:
                    this_column += 1

        # ADVANCE AXIS
        if separate_runs:
            if this_column == n_columns - 1:
                this_row += 1
                this_column = 0
            else:
                this_column += 1

        else:
            this_row = 0
            this_column = 0

    # MAKE LOWER LEFT (0, 0)
    for each_row in range(n_rows):
        for each_column in range(n_columns):
            this_axis = axs[each_row, each_column]
            this_axis.set_xlim(left=0)
            this_axis.set_ylim(bottom=0)

    # MAKE SURE PLOTS DON'T OVERLAP
    plt.tight_layout()

    # SAVE TO PDF
    pdf.savefig()
    plt.close()
    print(f"File saved to {pdf_path}.")
