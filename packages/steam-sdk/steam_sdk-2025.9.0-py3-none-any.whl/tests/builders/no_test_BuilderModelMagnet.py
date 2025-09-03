# This file contains useful scripts but it is not run as a test

import os
import matplotlib.pyplot as plt

from steam_sdk.builders.BuilderModel import BuilderModel
# from steam_sdk.parsers.ParserRoxie import get_conductor_corners
from steam_sdk.plotters.PlotterRoxie import plotEdges

if __name__ == "__main__":
    magnet_name = 'MCBRD'
    file_model_data = os.path.join('model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
    output_path = os.path.join('model_library', 'magnets', magnet_name, 'output')
    BM = BuilderModel(file_model_data=file_model_data, software=['LEDET'], flag_build=True,
                      output_path=output_path, verbose=False, flag_plot_all=False)
    x_insulated, y_insulated, x_bare, y_bare, i_conductor, x_strand, y_strand, i_strand, strandToHalfTurn = get_conductor_corners(BM.roxie_data)
    # TODO: Check that the corner position values are correct

    selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}
    plotEdges(x_insulated, y_insulated, x_bare, y_bare, i_conductor, selectedFont)
    plt.show()