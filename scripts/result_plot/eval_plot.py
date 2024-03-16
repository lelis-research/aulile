import subprocess
import sys
import statistics as st
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from collections import OrderedDict
import pandas as pd
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
    maps = [["A-BUS", "BUS"], ["A-Bustle", "Bustle"], ["A-Bee", "Bee"], ["A-Crossbeam(8)", "A-Crossbeam(4)", "A-Crossbeam(2)", "Crossbeam(8)", "Crossbeam(4)", "Crossbeam(2)", "Crossbeam"]]
    
    line_styles = ['solid', (0, (5, 5)), (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1)), (0, (5, 10)), (0, (3, 5, 1, 5)), (0, (1, 10)), (0, (1, 1)), (0, (1, 1)), (5, (10, 3)), (0, (3, 10, 1, 10))]

    benchmarks = ["SyGuS", "38B"]
    
    for benchmark in benchmarks:
        
        # 2. Define the figure
        px = 1/plt.rcParams['figure.dpi'] 
        figfull, axs = plt.subplots(2, 2,figsize=(620*px, 540*px), sharey=False if benchmark == 'SyGuS' else True, gridspec_kw={'hspace': 0.35, 'wspace': 0.14, 'bottom':0.10, 'left':0.07, 'right':1.0, 'top':0.90})

        # put supxlabel on top of the figure
        figfull.text(0.5, 0.94, 'SyGuS Benchmark' if benchmark == 'SyGuS' else '38 Benchmark', ha='center', fontsize=16)
        # figfull.supxlabel('SyGuS Benchmark', fontsize=12)
        x_label = "Number of Programs Evaluated"
        y_label = "Problems Solved"

        y_start = 60 if benchmark == 'SyGuS' else 15
        y_end = 90 if benchmark == 'SyGuS' else 36
        
        # print(axs.shape)
        index = 0
        for ax_row in axs:
            for ax in ax_row:
                logkeys = maps[index]
                filename = ""
                for lk in logkeys:
                    filename += lk + "_"

                final_combined_dataframe = pd.read_csv(("SyGuS_" if benchmark == 'SyGuS' else '38B_') + filename + "evaluations_statistics.csv")
                
                # final_combined_dataframe = final_combined_dataframe.iloc[::1000, :]
                # Identify the rows where there is a change in values except the 'time' column
                mask = (final_combined_dataframe.drop(columns=['evaluations']).diff() != 0).any(axis=1)

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
                
                x_list = final_combined_dataframe['evaluations'].tolist()
                
                line_style_index = 0
                # Plot the data
                for lk in logkeys:
                    if index == 2 or index == 3 or index == 1:
                        # axis_fill
                        ax.fill_between(x_list, final_combined_dataframe[lk+"_avg"] - final_combined_dataframe[lk + "_std"], final_combined_dataframe[lk+"_avg"] + final_combined_dataframe[lk + "_std"], alpha=0.3)

                        # axis_line (with line_style)
                        ax.step(x_list, final_combined_dataframe[lk+"_avg"], label=lk.replace('Crossbeam', 'CB'), linestyle=line_styles[line_style_index])

                        ax.text(x_list[-1], round(final_combined_dataframe[lk+"_avg"].iloc[-1]) if benchmark != '38B' or lk!= 'A-Crossbeam(2)' else final_combined_dataframe[lk+"_avg"].iloc[-1]-0.5, final_combined_dataframe[lk+"_avg"].iloc[-1], fontsize=8)
                    elif index == 0:
                        ax.step(x_list, final_combined_dataframe[lk], label=lk, linestyle=line_styles[line_style_index])
                        
                        ax.text(x_list[-1], final_combined_dataframe[lk].iloc[-1], final_combined_dataframe[lk].iloc[-1], fontsize=8)
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
                if index == 3:
                    ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/10000) + 'x$10^4$' if x > 0 else str(x)))
                    # divide the legend into two columns
                    ax.legend(loc='upper left' if benchmark == 'SyGuS' else 'lower right', ncol=2, fontsize=8)
                elif index == 1:
                    ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/10000000) + 'x$10^7$' if x > 0 else str(x)))
                    # divide the legend into two columns
                    ax.legend(loc='lower right', ncol=1, fontsize=8)
                else:
                    ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/100000000) + 'x$10^8$' if x > 0 else str(x)))
                    ax.legend(loc='lower right', ncol=1, fontsize=8)
                y_label = "Problems Solved" if index % 2 == 0 else ''
                ax.set_xlabel(x_label, fontsize=10)
                ax.set_ylabel(y_label, fontsize=10)
                # ax.set_title("SyGuS Benchmark", fontsize=16)
                # y_label = ''
                
                ax.grid(False)
                
                index += 1

        # plt.tight_layout()
        # plt.show()
        # plt.savefig("./"+ benchmark + "_evals.pgf")
        plt.savefig("./"+ benchmark + "_evals.pdf")

    

if __name__ == "__main__":
    main()
