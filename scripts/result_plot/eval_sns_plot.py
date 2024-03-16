import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

NUMBER_TICKS = 5

def main():
    # 1. Maps
    maps = [["A-Bee", "Bee"], ["A-Bustle", "Bustle"], ["A-BUS", "BUS"], ["A-Crossbeam(8)", "A-Crossbeam(4)", "A-Crossbeam(2)", "Crossbeam(8)", "Crossbeam(4)", "Crossbeam(2)", "Crossbeam"]]
    
    benchmarks = ["SyGuS", "38B"]
    
    for benchmark in benchmarks:
        
        # 2. Define the figure
        px = 1/plt.rcParams['figure.dpi'] 
        figfull, axs = plt.subplots(2, 2, figsize=(620*px, 540*px), sharey=False if benchmark == 'SyGuS' else True, gridspec_kw={'hspace': 0.35, 'wspace': 0.14, 'bottom':0.10, 'left':0.07, 'right':1.0, 'top':0.90})

        # Put supxlabel on top of the figure
        figfull.text(0.5, 0.94, 'SyGuS Benchmark' if benchmark == 'SyGuS' else '38 Benchmark', ha='center', fontsize=16)
        x_label = "Number of Programs Evaluated"
        y_label = "Problems Solved"

        y_start = 60 if benchmark == 'SyGuS' else 15
        y_end = 90 if benchmark == 'SyGuS' else 36
        
        index = 0
        for ax_row in axs:
            for ax in ax_row:
                logkeys = maps[index]
                filename = ""
                for lk in logkeys:
                    filename += lk + "_"

                final_combined_dataframe = pd.read_csv(("SyGuS_" if benchmark == 'SyGuS' else '38B_') + filename + "evaluations_statistics.csv")

                # Code for filtering the DataFrame...
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

                # If fill_between is required, use Matplotlib to plot it
                if index == 0 or index == 3 or index == 1:
                    for lk in logkeys:
                        ax.fill_between(x_list, final_combined_dataframe[lk+"_avg"] - final_combined_dataframe[lk + "_std"], final_combined_dataframe[lk+"_avg"] + final_combined_dataframe[lk + "_std"], alpha=0.3)
                        # ax.text(x_list[-1], round(final_combined_dataframe[lk+"_avg"].iloc[-1]) if benchmark != '38B' or lk!= 'A-Crossbeam(2)' else final_combined_dataframe[lk+"_avg"].iloc[-1]-0.5, final_combined_dataframe[lk+"_avg"].iloc[-1], fontsize=8)
                # if index == 2:
                #     ax.text(x_list[-1], final_combined_dataframe[lk].iloc[-1], final_combined_dataframe[lk].iloc[-1], fontsize=8)

                # Create a new DataFrame with long format
                value_vars = [f"{lk}_avg" for lk in logkeys] if index == 0 or index == 3 or index == 1 else logkeys
                long_format_df = pd.melt(final_combined_dataframe, id_vars=['evaluations'], value_vars=value_vars, var_name='key', value_name='value')

                # Plot the data using Seaborn, mapping the 'style' parameter to the 'key' column
                sns.lineplot(x='evaluations', y='value', hue='key', style='key', data=long_format_df, ax=ax, legend=False)

                # Additional code for setting axes properties...
                if index == 3:
                    ax.set_ylim(y_start, 77 if benchmark == 'SyGuS' else y_end)
                else: ax.set_ylim(y_start, y_end)
                x_ticks = np.linspace(0, x_list[-1], NUMBER_TICKS, dtype=int)
                y_ticks = np.linspace(y_start, y_end, NUMBER_TICKS, dtype=int) if index != 3 else np.linspace(y_start, 77 if benchmark == 'SyGuS' else y_end, NUMBER_TICKS, dtype=int)
                ax.set_xticks(x_ticks)
                ax.set_yticks(y_ticks)
                ax.tick_params(axis='both', which='major', labelsize=10)
                ax.margins(x=0.12, y=0.12)
                ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/100000000) + 'x$10^8$' if x > 0 else str(x)))
                if index == 3:
                    ax.legend(loc='upper left' if benchmark == 'SyGuS' else 'lower right', ncol=2, fontsize=8)
                else:
                    ax.legend(loc='lower right', ncol=1, fontsize=8)
                ax.set_xlabel(x_label, fontsize=10)
                ax.set_ylabel(y_label if index % 2 == 0 else '', fontsize=10)
                ax.grid(False)

                index += 1

        # plt.savefig("./"+ benchmark + "_evals_sns.pgf")
        plt.show()

if __name__ == "__main__":
    main()
