import subprocess
import sys
import statistics as st
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from collections import OrderedDict
import pandas as pd
import glob
import numpy as np

matplotlib.use('pgf')
matplotlib.rcParams.update({
  'pgf.texsystem': 'pdflatex',
  'font.family': 'serif',
  'text.usetex': True,
  'pgf.rcfonts': False,
})


NUMBER_TICKS = 5

def main():
    
    # 1. Maps
    maps = ["A-BUS", "A-Bustle", "A-Bee", "A-Crossbeam"]
    
    line_styles = ['solid',  (0, (5, 5)), (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1)), (0, (5, 10)), (0, (3, 5, 1, 5)), (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (5, (10, 3)), (0, (3, 10, 1, 10))]

    benchmarks = ["SyGuS", "38B"]
            
    # 2. Define the figure
    px = 1/plt.rcParams['figure.dpi'] 
    figfull, axs = plt.subplots(1, len(benchmarks),figsize=(620*px, 270*px), sharey=False, gridspec_kw={'hspace': 0.0, 'wspace': 0.14, 'bottom':0.15, 'left':0.07, 'right':1.00, 'top':0.90})

    x_label = "Running Time in Seconds"
    y_label = "Problems Solved"

    for index, benchmark in enumerate(benchmarks):
        ax = axs[index]
        y_start = 60 if benchmark == 'SyGuS' else 15
        y_end = 90 if benchmark == 'SyGuS' else 40
        final_combined_dataframe = pd.DataFrame()
        for file_name_index, lk in enumerate(maps):
            pattern = '*' + lk + '*'
            filename_pattern = ("SyGuS_" if benchmark == 'SyGuS' else '38B_') + pattern + "times_statistics.csv"
            # read all the csv files that match the filename_pattern
            file_names = [f for f in glob.glob(filename_pattern)]
            print(filename_pattern, " ", file_names)
            combined_dataframe = pd.read_csv(file_names[0], index_col=None)
            if file_name_index != 0:
                # get the times column and the lk+_std, lk+_avg columns
                combined_dataframe = combined_dataframe[['time', lk+'_std', lk+'_avg']]
            else:
                combined_dataframe = combined_dataframe[['time', lk]]
            # if the final_combined_dataframe is empty, then just assign the combined_dataframe to it, else merge on the times column
            if final_combined_dataframe.empty:
                final_combined_dataframe['time'] = np.arange(0, (3600 * 24) + 1, 1)
            final_combined_dataframe = pd.merge(final_combined_dataframe, combined_dataframe, on='time', how='outer')
        
        final_combined_dataframe.fillna(method='ffill', inplace=True)
        
        # save the final_combined_dataframe to csv
        final_combined_dataframe.to_csv(("SyGuS_" if benchmark == 'SyGuS' else '38B_') + "times_statistics_combined.csv", index=False)
        
        # # take take all first 5000 rows, then take every 500th row
        # final_combined_dataframe_new =  final_combined_dataframe.iloc[0:2000]
        # # add the rest of the every 500th row
        # final_combined_dataframe_new = pd.concat([final_combined_dataframe_new, final_combined_dataframe.iloc[2000::500, :]])
                            # final_combined_dataframe = final_combined_dataframe.iloc[::1000, :]
        # Identify the rows where there is a change in values except the 'time' column
        mask = (final_combined_dataframe.drop(columns=['time']).diff() != 0).any(axis=1)

        # Identify the indices where there are changes, or every 1000th row if no changes
        indices_to_keep = []
        last_change_index = None
        for i, change in enumerate(mask):
            if change or (i % 1000 == 0 and (last_change_index is None or i - last_change_index >= 1000)):
                indices_to_keep.append(i)
                if change:
                    last_change_index = i

        # Select the rows based on the identified indices
        final_combined_dataframe = final_combined_dataframe.iloc[indices_to_keep, :]        
        # final_combined_dataframe = final_combined_dataframe_new
        
        x_list = final_combined_dataframe['time'].tolist()
        
        line_style_index = 0
        # Plot the data
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

        for file_name_index, lk in enumerate(maps):
            current_color = color_cycle[file_name_index % len(color_cycle)]

            if file_name_index != 0:
                # axis_fill
                ax.fill_between(x_list, final_combined_dataframe[lk+"_avg"] - final_combined_dataframe[lk + "_std"], final_combined_dataframe[lk+"_avg"] + final_combined_dataframe[lk + "_std"], color = current_color, alpha=0.3)
                # axis_line (with line_style)
                ax.step(x_list, final_combined_dataframe[lk+"_avg"], label=lk, linestyle=line_styles[line_style_index], color=current_color)
                if file_name_index == 2 or file_name_index == 1:
                    ax.text(x_list[-1], round(final_combined_dataframe[lk+"_avg"].iloc[-1]-1) if benchmark == '38B' else round(final_combined_dataframe[lk+"_avg"].iloc[-1]), final_combined_dataframe[lk+"_avg"].iloc[-1], fontsize=8)
                else:
                    ax.text(x_list[-1], final_combined_dataframe[lk+"_avg"].iloc[-1] if benchmark == '38B' else round(final_combined_dataframe[lk+"_avg"].iloc[-1]), final_combined_dataframe[lk+"_avg"].iloc[-1], fontsize=8)
            else:
                ax.step(x_list, final_combined_dataframe[lk], label=lk, linestyle=line_styles[line_style_index], color=current_color )
                ax.text(x_list[-1], final_combined_dataframe[lk].iloc[-1] if benchmark == "38B" else round(final_combined_dataframe[lk].iloc[-1]), final_combined_dataframe[lk].iloc[-1], fontsize=8)
            line_style_index += 1
        
        if index == 3:
            ax.set_ylim(y_start, 77 if benchmark == 'SyGuS' else y_end)
        else: ax.set_ylim(y_start, y_end)
        # ax.set_xlim(left=0)
        x_ticks = np.linspace(0, x_list[-1], NUMBER_TICKS, dtype=int)
        if index == 3:
            y_ticks = np.linspace(y_start, 77 if benchmark == 'SyGuS' else y_end, NUMBER_TICKS, dtype=int)
        else:
            y_ticks = np.linspace(y_start, y_end, NUMBER_TICKS, dtype=int)
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)
        ax.tick_params(axis='both', which='major', labelsize=10)
        # set the border margin
        ax.margins(x=0.12, y=0.12)
        # ax.tick_params(axis='both', which='minor', labelsize=14)
        ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/10000) + 'x$10^4$' if x > 0 else str(x)))
        ax.legend(loc='lower right', ncol=1, fontsize=8)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        y_label = ''
        ax.set_title( ("SyGuS" if benchmark == "SyGuS" else "38") + " Benchmark", fontsize=15)
        
        ax.grid(False)

    # plt.tight_layout()
    # plt.show()
    # plt.savefig("./times.pgf")
    plt.savefig("./times.pdf")
    plt.savefig("./times.png", dpi=300)

if __name__ == "__main__":
    main()
