import math
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import PlasmaCalcs

# INPUT PARAMETERS
path_to_folder = r"G:\My Drive\Research\eppic_out\eregion\lowerE"
fluid = 1
plot_quantity = "n"
plot_every = 11
n_columns = 2 # number of plot columns
slices = {"y": 0}
pdf_name = "den1_xz"

# LOAD DATA
ec = PlasmaCalcs.EppicCalculator.from_here(os.path.join(path_to_folder, "eppic.i"), kw_units={"M": 1}, u_l=1)
ec.fluid = fluid
sample_snaps = ec.snaps[::plot_every]

# CREATE CANVAS
n_rows = math.ceil(len(sample_snaps) / n_columns)
fig, axs = plt.subplots(nrows=n_rows, ncols=n_columns, squeeze=False, figsize=[8.5, 11])

# SET COUNTERS
this_row = 0
this_column = 0

# SET PDF PATH
pdf_path = os.path.join(path_to_folder, f"{pdf_name}.pdf")

with PdfPages(pdf_path) as pdf:
    # LOOP THROUGH SNAPS
    for snap in sample_snaps:
        time = snap.t
        ec.snap = snap
        # PLOT
        plot_title = f"Density {fluid} at t = {time}."
        this_axis = axs[this_row, this_column]
        array = ec(plot_quantity).isel(**slices)
        array.plot(cmap="plasma", ax=this_axis, rasterized=True)
        this_axis.set_title(plot_title)
        # UPDATE ROW & COLUMN
        if this_column == n_columns - 1:
            this_row += 1
            this_column = 0
        else:
            this_column += 1

    # MAKE SURE PLOTS DON'T OVERLAP
    plt.tight_layout()

    # SAVE TO PDF
    pdf.savefig()
    plt.close()
    print(f"File saved to {pdf_path}.")

