import os
from pathlib import Path
import matplotlib.lines as lines
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class PlotterMap2d:
    """
    Class for plotting map2d data
    """

    def __init__(
            self,
            parsed_results_path: Path,
            verbose: bool = True
    ):
        """
        :param parsed_results_path: full path to Analysis PostProcess output folder
        """
        self.parsed_results_path = parsed_results_path

    def plot_multiple_areas(self, ax, areas, color=None):
        """
        Functions takes in a list of area objects and plot them on axis ax.
        :param ax: Axis to create plots.
        :param areas: list of SIGMA area objects.
        :param color: Color of the object
        :return:
        """
        for area in areas:
            if color:
                self.plot_area(ax, area, color)
            else:
                self.plot_area(ax, area)

    def plot_area(self, ax, area, color=None):
        """
        Plots one SIGMA area object on axis ax
        :param ax: Axis to create plots.
        :param area: SIGMA area object.
        :param color: Color of the object
        :return:
        """
        if not color:
            color = 'black'
        points = []
        hls = area.getHyperLines()
        for hl in hls:
            last_dot_index = hl.toString().rfind('.')
            at_index = hl.toString().find('@')
            class_name = hl.toString()[last_dot_index + 1:at_index]
            if class_name == 'Line':
                points.append([hl.getKp1().getX(), hl.getKp1().getY()])
                points.append([hl.getKp2().getX(), hl.getKp2().getY()])
            elif class_name == 'Arc':
                start_angle = np.arctan2(hl.getKp1().getY() - hl.getKpc().getY(),
                                         hl.getKp1().getX() - hl.getKpc().getX()) * 180 / np.pi
                end_angle = start_angle + hl.getDTheta() * 180 / np.pi
                r = np.sqrt((hl.getKp1().getY() - hl.getKpc().getY()) ** 2 + (hl.getKp1().getX() - hl.getKpc().getX()) ** 2)
                ax.add_patch(patches.Arc([hl.getKpc().getX(), hl.getKpc().getY()], 2 * r, 2 * r, 0,
                                         min(start_angle, end_angle), max(start_angle, end_angle), color=color))
            elif class_name == 'Circumference':
                r = hl.getRadius()
                ax.add_patch(patches.Arc([hl.getCenter().getX(), hl.getCenter().getY()], 2 * r, 2 * r, 0, 0, 360))
            else:
                raise ValueError('Not supported Hyperline object!')

        ax.add_line(lines.Line2D([points[0][0], points[3][0]], [points[0][1], points[3][1]], color=color))
        ax.add_line(lines.Line2D([points[1][0], points[2][0]], [points[1][1], points[2][1]], color=color))

    def write_result_summary(self, df, n1, n2):
        with open("error_summary.txt", "a") as myfile:
            mean_Bmod_error = (df["Bmod_error"]).mean() * 1000
            abs_mean_Bmod_error = abs(df["Bmod_error"]).mean() * 1000
            std_Bmod_error = (df["Bmod_error"]).std() * 1000
            max_Bmod_error = abs(df["Bmod_error"]).max() * 1000
            min_Bmod_error = abs(df["Bmod_error"]).min() * 1000
            myfile.write(
                f"{n1 * n2} {mean_Bmod_error} {std_Bmod_error} {abs_mean_Bmod_error} {max_Bmod_error} {min_Bmod_error}\n")
            max_index = abs(df["Bmod_error"]).idxmax()
            print(f"Absolute Bmod error mean: {abs_mean_Bmod_error}")

            print(f"Absolute Bmod error mean max index : {max_index}")

    def plot_Bmod(self, df, map2d_name1, map2d_name2, fig, ax, type, cmap='plasma'):
        fig.suptitle(f"Bmod: {map2d_name1} and {map2d_name2} (mT)")
        ax[0, 0].set_title(f"Bmod: {map2d_name1} (mT)")
        ax[0, 0].set_xlabel('x-coordinate/mm')
        ax[0, 0].set_ylabel('y-coordinate/mm')
        ax[0, 1].set_title(f"Bmod: {map2d_name2} (mT)")
        ax[0, 1].set_xlabel('x-coordinate/mm')
        ax[0, 1].set_ylabel('y-coordinate/mm')
        ax[1, 0].plot(df["Bmod1"] * 1000, '.')
        ax[1, 0].set_title(f"Bmod scatter: {map2d_name1} (mT)")
        ax[1, 0].set_xlabel('Strand number')
        ax[1, 0].set_ylabel(f'Bmod scatter: {map2d_name1} (mT)')
        ax[1, 1].plot(df["Bmod2"] * 1000, '.')
        ax[1, 1].set_xlabel('Strand number')
        ax[1, 1].set_ylabel('Scatter Bmod (mT)')
        ax[1, 1].set_title(f"Bmod scatter: {map2d_name2} (mT)")
        ax[0, 0].set_aspect("equal")
        ax[0, 1].set_aspect("equal")
        if type == "coil":
            f11 = ax[0, 0].scatter(df["x"], df['y'], c=df["Bmod1"] * 1000, cmap=cmap)
            f12 = ax[0, 1].scatter(df["x"], df['y'], c=df["Bmod2"] * 1000, cmap=cmap)
            fig.colorbar(f11, ax=ax[0, 0])
            fig.colorbar(f12, ax=ax[0, 1])
        elif type == "mesh":
            x = np.array(df['x'].tolist())
            y = np.array(df['y'].tolist())
            z1 = np.array(df['Bmod1'].tolist()) * 1000
            z2 = np.array(df['Bmod2'].tolist()) * 1000
            np.random.seed(1234)  # fix seed for reproducibility

            tpc1 = ax[0, 0].tripcolor(x, y, z1, shading='gouraud', cmap=cmap)
            tpc2 = ax[0, 1].tripcolor(x, y, z2, shading='gouraud', cmap=cmap)

            fig.colorbar(tpc1)
            fig.colorbar(tpc2)

    def plot_B_mod_error(self, df, map2d_name1, map2d_name2, fig, ax, type, cmap='winter'):
        fig.suptitle(f"Bmod error: {map2d_name1} - {map2d_name2} (mT)")
        ax[0].set_title(f"Bmod error (mT)")
        ax[0].set_xlabel('x-coordinate/mm', fontsize=9)
        ax[0].set_ylabel('y-coordinate/mm', fontsize=9)
        ax[0].set_aspect("equal")
        ax[1].set_title(f"Bmod error scatter (mT)")

        ax[1].set_xlabel('x')
        ax[1].set_ylabel('y')
        ax[1].plot(df["Bmod_error"] * 1000, '.')
        if type == "coil":
            f11 = ax[0].scatter(df["x"], df['y'], c=df["Bmod_error"] * 1000, cmap=cmap)
            fig.colorbar(f11, ax=ax[0])
        elif type == "mesh":
            x = np.array(df['x'].tolist())
            y = np.array(df['y'].tolist())
            z1 = np.array(df['Bmod_error'].tolist()) * 1000

            np.random.seed(1234)  # fix seed for reproducibility

            tpc = ax[0].tripcolor(x, y, z1, shading='gouraud', cmap=cmap)
            fig.colorbar(tpc)

    def plot_relative_error_x_y(self, df, map2d_name1, map2d_name2, fig, ax, type, cmap='CMRmap'):
        if df['rel_err_x'] is not None and df['rel_err_y'] is not None:
            fig.suptitle(f"Relative error: {map2d_name1} and {map2d_name2} (T)")
            ax[0, 0].set_aspect("equal")
            ax[0, 1].set_aspect("equal")

            ax[0, 0].set_title(f"Relative error Bx %")
            ax[0, 0].set_xlabel('x-coordinate/mm')
            ax[0, 0].set_ylabel('y-coordinate/mm')
            ax[0, 1].set_title(f"Relative error By %")
            ax[0, 1].set_xlabel('x-coordinate/mm')
            ax[0, 1].set_ylabel('y-coordinate/mm')

            ax[1, 0].plot(df["rel_err_x"] * 100, '.')
            ax[1, 0].set_title(f"Scatter Relative error  Bx %")
            ax[1, 0].set_xlabel('Strand number')
            ax[1, 0].set_ylabel('Relative error Bx %')
            ax[1, 1].plot(df["rel_err_y"] * 100, '.')
            ax[1, 1].set_xlabel('Strand number')
            ax[1, 1].set_ylabel('Relative error By %')
            ax[1, 1].set_title(f"Scatter Relative error  By %")
            if type == "coil":
                f31 = ax[0, 0].scatter(df["x"], df['y'], c=df["rel_err_x"] * 100, cmap=cmap)
                f32 = ax[0, 1].scatter(df["x"], df['y'], c=df["rel_err_y"] * 100, cmap=cmap)
                fig.colorbar(f31, ax=ax[0, 0])
                fig.colorbar(f32, ax=ax[0, 1])
            elif type == "mesh":
                x = np.array(df['x'].tolist())
                y = np.array(df['y'].tolist())
                z1 = np.array(df['rel_err_x'].tolist()) * 100
                z2 = np.array(df['rel_err_y'].tolist()) * 100
                np.random.seed(1234)  # fix seed for reproducibility

                tpc1 = ax[0, 0].tripcolor(x, y, z1, shading='gouraud', cmap=cmap)
                tpc2 = ax[0, 1].tripcolor(x, y, z2, shading='gouraud', cmap=cmap)

                fig.colorbar(tpc1)
                fig.colorbar(tpc2)

    def plot_Bx_By(self, df, map2d_name1, map2d_name2, fig, ax, type, cmap='seismic', plot_coil=False):
        fig.suptitle(f"Bx and By field: {map2d_name1} and {map2d_name2} (mT)", fontsize=12)

        ax[0, 0].set_title(f"Bx {map2d_name1} (mT)", fontsize=10)
        ax[0, 0].set_ylabel('y-coordinate/mm', fontsize=9)
        ax[0, 0].set_aspect("equal")
        ax[0, 1].set_aspect("equal")
        ax[1, 0].set_aspect("equal")
        ax[1, 1].set_aspect("equal")
        ax[0, 1].set_title(f"By {map2d_name1} (mT)", fontsize=10)
        ax[0, 1].set_ylabel('y-coordinate/mm', fontsize=9)

        ax[1, 0].set_title(f"Bx {map2d_name2} (mT)", fontsize=10)
        ax[1, 0].set_xlabel('x-coordinate/mm', fontsize=9)
        ax[1, 0].set_ylabel('y-coordinate/mm', fontsize=9)
        ax[1, 1].set_title(f"By {map2d_name2} (mT)", fontsize=10)
        ax[1, 1].set_xlabel('x-coordinate/mm', fontsize=9)
        ax[1, 1].set_ylabel('y-coordinate/mm', fontsize=9)
        ax[2, 0].set_title(f"Bx scatter (mT)", fontsize=14, loc='left')
        ax[2, 0].set_ylabel('Bx scatter (mT)', fontsize=9)
        ax[2, 0].plot(df["Bx1"] * 1000, '.', color='b', label=f"{map2d_name1}")
        ax[2, 0].plot(df["Bx2"] * 1000, '.', color='r', label=f"{map2d_name2}")
        ax[2, 1].set_title(f"By scatter (mT)", fontsize=14, loc='left')
        ax[2, 1].set_ylabel('By scatter (mT)', fontsize=9)

        ax[2, 1].plot(df["By1"] * 1000, '.', color='b', label=f"{map2d_name1}")
        ax[2, 1].plot(df["By2"] * 1000, '.', color='r', label=f"{map2d_name2}")
        ax[2, 0].legend()
        ax[2, 1].legend()

        if type == "coil":
            f41 = ax[0, 0].scatter(df["x"], df['y'], c=df["Bx1"] * 1000, cmap=cmap)
            f42 = ax[0, 1].scatter(df["x"], df['y'], c=df["By1"] * 1000, cmap=cmap)
            f43 = ax[1, 0].scatter(df["x"], df['y'], c=df["Bx2"] * 1000, cmap=cmap)
            f44 = ax[1, 1].scatter(df["x"], df['y'], c=df["By2"] * 1000, cmap=cmap)
            fig.colorbar(f41, ax=ax[0, 0])
            fig.colorbar(f42, ax=ax[0, 1])
            fig.colorbar(f43, ax=ax[1, 0])
            fig.colorbar(f44, ax=ax[1, 1])
        elif type == "mesh":
            x = np.array(df['x'].tolist())
            y = np.array(df['y'].tolist())
            Bx1 = np.array(df['Bx1'].tolist()) * 1000
            By1 = np.array(df['By1'].tolist()) * 1000
            Bx2 = np.array(df['Bx2'].tolist()) * 1000
            By2 = np.array(df['By2'].tolist()) * 1000
            np.random.seed(1234)  # fix seed for reproducibility

            tpc1 = ax[0, 0].tripcolor(x, y, Bx1, shading='gouraud', cmap=cmap)
            tpc2 = ax[0, 1].tripcolor(x, y, By1, shading='gouraud', cmap=cmap)
            tpc3 = ax[1, 0].tripcolor(x, y, Bx2, shading='gouraud', cmap=cmap)
            tpc4 = ax[1, 1].tripcolor(x, y, By2, shading='gouraud', cmap=cmap)

            fig.colorbar(tpc1, ax=ax[0, 0])
            fig.colorbar(tpc2, ax=ax[0, 1])
            fig.colorbar(tpc3, ax=ax[1, 0])
            fig.colorbar(tpc4, ax=ax[1, 1])

    def plot_difference_Bx_By(self, df, map2d_name1, map2d_name2, fig, ax, type, cmap='seismic', plot_coil=False):
        fig.suptitle(f"Difference: {map2d_name1} - {map2d_name2} (mT)")
        ax[0, 0].set_title(f"Difference Bx (mT)")
        ax[0, 0].set_xlabel('x-coordinate/mm')
        ax[0, 0].set_ylabel('y-coordinate/mm')
        ax[0, 1].set_title(f"Difference By (mT)")
        ax[0, 1].set_xlabel('x-coordinate/mm')
        ax[0, 1].set_ylabel('y-coordinate/mm')
        ax[1, 0].plot(df["diff_x"] * 1000, '.')
        ax[1, 0].set_title(f"Scatter difference Bx (mT)")
        ax[1, 0].set_xlabel('Strand number')
        ax[1, 0].set_ylabel('Difference Bx (mT)')
        ax[1, 1].plot(df["diff_y"] * 1000, '.')
        ax[1, 1].set_xlabel('Strand number')
        ax[1, 1].set_ylabel('Scatter difference By (mT)')
        ax[1, 1].set_title(f"Scatter difference By (mT)")
        ax[0, 0].set_aspect("equal")
        ax[0, 1].set_aspect("equal")
        if (type == "coil"):
            f11 = ax[0, 0].scatter(df["x"], df['y'], c=df["diff_x"] * 1000, cmap=cmap)
            f12 = ax[0, 1].scatter(df["x"], df['y'], c=df["diff_y"] * 1000, cmap=cmap)
            fig.colorbar(f11, ax=ax[0, 0])
            fig.colorbar(f12, ax=ax[0, 1])
        elif (type == "mesh"):

            x = np.array(df['x'].tolist())
            y = np.array(df['y'].tolist())
            diff_x = np.array(df['diff_x'].tolist()) * 1000
            diff_y = np.array(df['diff_y'].tolist()) * 1000

            np.random.seed(1234)  # fix seed for reproducibility
            tpc1 = ax[0, 0].tripcolor(x, y, diff_x, shading='gouraud', cmap=cmap)
            tpc2 = ax[0, 1].tripcolor(x, y, diff_y, shading='gouraud', cmap=cmap)

            fig.colorbar(tpc1, ax=ax[0, 0])
            fig.colorbar(tpc2, ax=ax[0, 1])

    def get_df_map2d(self, map2d_files):

        df1 = pd.read_csv(map2d_files[0], delim_whitespace=True)
        df2 = pd.read_csv(map2d_files[1], delim_whitespace=True)
        df = pd.DataFrame()
        df['x'] = df1["X-POS/MM"]
        df['y'] = df1["Y-POS/MM"]
        df["Bx1"] = df1["BX/T"]
        df["By1"] = df1["BY/T"]

        df["Bx2"] = df2["BX/T"]
        df["By2"] = df2["BY/T"]
        df = df.apply(pd.to_numeric)
        df["diff_x"] = df["Bx1"] - df["Bx2"]
        df["diff_y"] = df["By1"] - df["By2"]
        try:
            df["rel_err_x"] = abs((df["Bx1"] - df["Bx2"]) / df["Bx2"])
        except:
            print("Can't create rel_err_x plots")
            df["rel_err_x"] = None
        try:
            df["rel_err_y"] = abs((df["By1"] - df["By2"]) / df["By2"])
        except:
            print("Can't create rel_err_y plots")
            df["rel_err_y"] = None
        df["abs_err_x"] = abs(df["Bx1"] - df["Bx2"])
        df["abs_err_y"] = abs(df["By1"] - df["By2"])
        df["Bmod1"] = np.sqrt(df["Bx1"] ** 2 + df["By1"] ** 2)
        df["Bmod2"] = np.sqrt(df["Bx2"] ** 2 + df["By2"] ** 2)
        df["Bmod_error"] = abs(df["Bmod1"] - df["Bmod2"])
        return df

    def generate_report_from_map2d(self, comparison_name: str, files_names: dict, plot_type: str, save: bool = True):
        """
        Generate plots for comparing two map2d files. Method generates the following plots:
        Bmod fields, Bmod error, relative error Bx/By, Bx/By field, Bx/By error, absolut difference Bx/By
        :return:
        """
        sources = list(files_names.keys())
        paths = [os.path.join(self.parsed_results_path, name) for name in files_names.values()]
        df = self.get_df_map2d(paths)
        fig1, ax1 = plt.subplots(2, 2, figsize=(12, 12))
        fig2, ax2 = plt.subplots(1, 2, figsize=(12, 12))
        fig3, ax3 = plt.subplots(3, 2, figsize=(12, 12))
        fig4, ax4 = plt.subplots(2, 2, figsize=(12, 12))
        fig5, ax5 = plt.subplots(2, 2, figsize=(12, 12))
        self.plot_Bmod(df, sources[0], sources[1], fig1, ax1, plot_type)
        self.plot_B_mod_error(df, sources[0], sources[1], fig2, ax2, plot_type)
        self.plot_Bx_By(df, sources[0], sources[1], fig3, ax3, plot_type)
        text1 = f"{sources[0]} file path: {paths[0]}"
        text2 = f"{sources[1]} file path: {paths[1]}"
        x_pos = 0.5  # X position of the text (0.0 to 1.0)
        y_pos = 0.05  #
        fig5.text(x_pos, y_pos, text1, ha='center')

        # Add the second line of text
        fig5.text(x_pos, y_pos - 0.03, text2, ha='center')

        # Show the figure
        try:
            self.plot_relative_error_x_y(df, sources[0], sources[1], fig4, ax4, plot_type)
        except:
            print("Couldn't generate relative error plots.")
        self.plot_difference_Bx_By(df, sources[0], sources[1], fig5, ax5, plot_type)
        print("----Bmod error description----- ")
        print(df["Bmod_error"].describe())
        print(df["Bmod_error"].nlargest(10))

        print("----Rel error x description----- ")
        print(df["rel_err_x"].describe())
        print(df["rel_err_x"].nlargest(10))
        print("----Rel error y description----- ")
        print(df["rel_err_y"].describe())
        print(df["rel_err_y"].nlargest(10))
        to_export = {'B_mod_diff_max': df["Bmod_error"].max(), 'B_mod_diff_mean': df["Bmod_error"].mean(),
                     'B_mod_diff_std': df["Bmod_error"].std(),
                     'B_x_diff_max': abs(df["diff_x"]).max(), 'B_x_diff_mean': abs(df["diff_x"]).mean(),
                     'B_x_diff_std': abs(df["diff_x"]).std(),
                     'B_y_diff_max': abs(df["diff_y"]).max(), 'B_y_diff_mean': abs(df["diff_y"]).mean(),
                     'B_y_diff_std': abs(df["diff_y"]).std()}

        if save:
            fig1.savefig(os.path.join(self.parsed_results_path, f"{comparison_name}_plot_Bmod_{sources[0]}_{sources[1]}.png"))
            fig2.savefig(os.path.join(self.parsed_results_path, f"{comparison_name}_plot_B_mod_error_{sources[0]}_{sources[1]}.png"))
            fig3.savefig(os.path.join(self.parsed_results_path, f"{comparison_name}_plot_Bx_By_{sources[0]}_{sources[1]}.png"))
            fig4.savefig(os.path.join(self.parsed_results_path, f"{comparison_name}_plot_relative_error_x_y_{sources[0]}_{sources[1]}.png"))
            fig5.savefig(os.path.join(self.parsed_results_path, f"{comparison_name}_plot_difference_Bx_By_{sources[0]}_{sources[1]}.png"))

        # displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)
        plt.close('all')
        return to_export

    def plot_roxie_coil(self, roxie_data):
        xPos = []
        yPos = []
        xBarePos = []
        yBarePos = []
        iPos = []
        for coil_nr, coil in roxie_data.coil.coils.items():
            for pole_nr, pole in coil.poles.items():
                for layer_nr, layer in pole.layers.items():
                    for winding_key, winding in layer.windings.items():
                        for block_key, block in winding.blocks.items():
                            for halfTurn_nr, halfTurn in block.half_turns.items():
                                insu = halfTurn.corners.insulated
                                bare = halfTurn.corners.bare
                                xPos.append([insu.iH.x, insu.oH.x, insu.oL.x, insu.iL.x])
                                yPos.append([insu.iH.y, insu.oH.y, insu.oL.y, insu.iL.y])
                                xBarePos.append([bare.iH.x, bare.oH.x, bare.oL.x, bare.iL.x])
                                yBarePos.append([bare.iH.y, bare.oH.y, bare.oL.y, bare.iL.y])
                                iPos.append(block.current_sign)
        return (xPos, yPos, xBarePos, yBarePos, iPos)

    def plotEdges(self, xPos, yPos, xBarePos, yBarePos, iPos, ax):
        # Plot edges
        for c, (cXPos, cYPos) in enumerate(zip(xPos, yPos)):
            pt1, pt2, pt3, pt4 = [cXPos[0] * 1000, cYPos[0] * 1000], [cXPos[1] * 1000, cYPos[1] * 1000], [
                cXPos[2] * 1000, cYPos[2] * 1000], [cXPos[3] * 1000, cYPos[3] * 1000]
            points = [pt1, pt2, pt3, pt4] * 1000
            if iPos[c] > 0:
                line = patches.Polygon(points, facecolor='k', zorder=1, fill=False)
            else:
                line = patches.Polygon(points, facecolor='k', zorder=1, fill=False)
            ax.add_patch(line)

        for c, (cXBarePos, cYBarePos) in enumerate(zip(xBarePos, yBarePos)):
            pt1, pt2, pt3, pt4 = [cXBarePos[0] * 1000, cYBarePos[0] * 1000], [cXBarePos[1] * 1000, cYBarePos[1] * 1000], \
                                 [cXBarePos[2] * 1000, cYBarePos[2] * 1000], [cXBarePos[3] * 1000, cYBarePos[3] * 1000]
            points = [pt1, pt2, pt3, pt4]
            if iPos[c] > 0:
                line = patches.Polygon(points, facecolor='k', zorder=1, fill=False)
            else:
                line = patches.Polygon(points, facecolor='k', zorder=1, fill=False)
            ax.add_patch(line)
