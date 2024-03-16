import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import matplotlib
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
    # Maps for each benchmark
    maps = [["A-BUS_Lev_1.0", "A-BUS_Lev_0.75", "A-BUS_Lev_0.50", "A-BUS_Lev_0.25"]]
    labels = [r"A-BUS ($l = 1.00$)", r"A-BUS ($l = 0.75$)", r"A-BUS ($l = 0.50$)", r"A-BUS ($l = 0.25$)"]

    line_styles = ['solid', (0, (5, 5)), (0, (5, 1)), (0, (3, 1, 1, 1)), 
                   (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1)), 
                   (0, (5, 10)), (0, (3, 5, 1, 5)), (0, (1, 10)), 
                   (0, (1, 1)), (0, (1, 1)), (5, (10, 3)), 
                   (0, (3, 10, 1, 10))]

    benchmarks = ["SyGuS", "38B"]

    # Define the figure size and DPI
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(1, 2, figsize=(620*px, 270*px), 
                            gridspec_kw={'hspace': 0.35, 'wspace': 0.14, 'bottom':0.15, 'left':0.07, 'right':1.0, 'top':0.85})

    for ax, benchmark in zip(axs, benchmarks):
        ax.set_title('SyGuS Benchmark' if benchmark == 'SyGuS' else '38 Benchmark', fontsize=16)

        for logkeys in maps:
            filename = "_".join(logkeys)
            try:
                final_combined_dataframe = pd.read_csv((f"{benchmark}_" if benchmark == 'SyGuS' else '38B_') + filename + "_evaluations_statistics.csv")
            except FileNotFoundError:
                print(f"File not found: {filename}_evaluations_statistics.csv")
                continue

            # Data filtering logic
            mask = (final_combined_dataframe.drop(columns=['evaluations']).diff() != 0).any(axis=1)
            indices_to_keep = [i for i, change in enumerate(mask) if change or i % 1000 == 0]
            final_combined_dataframe = final_combined_dataframe.iloc[indices_to_keep, :]
            
            x_list = final_combined_dataframe['evaluations'].tolist()

            for lk, style, lb in zip(logkeys, line_styles, labels):
                ax.step(x_list, final_combined_dataframe[lk], label=lb, linestyle=style)
                ax.text(x_list[-1], final_combined_dataframe[lk].iloc[-1], str(final_combined_dataframe[lk].iloc[-1]), fontsize=8)

            # Set plot limits and labels
            y_start = 60 if benchmark == 'SyGuS' else 20
            y_end = 89 if benchmark == 'SyGuS' else 35

            ax.set_ylim(y_start, y_end)
            ax.set_xticks(np.linspace(0, x_list[-1], NUMBER_TICKS, dtype=int))

            # Corrected linspace for y-ticks
            if benchmark == 'SyGuS':
                y_ticks = np.linspace(y_start, y_end, (y_end - y_start) // 5 + 1, dtype=int)
            else:
                y_ticks = np.linspace(y_end, y_start, (y_end - y_start) // 5 + 1, dtype=int)[::-1]  # reverse for descending order

            ax.set_yticks(y_ticks)
            
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.margins(x=0.12, y=0.12)

            # Formatter and labels
            ax.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, pos: f'{x/100000000:.0f}x$10^8$' if x > 0 else str(x)))
            ax.legend(loc='lower right', fontsize=8)
            ax.set_xlabel("Number of Programs Evaluated", fontsize=10)
            ax.set_ylabel("Problems Solved" if benchmark == 'SyGuS' else '', fontsize=10)
            ax.grid(False)

    # Save the figure
    plt.savefig("./evals_Lev_0.25_0.50_0.75_1.0.pdf")

if __name__ == "__main__":
    main()
