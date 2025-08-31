import csv
import os

import matplotlib.pyplot as plt

# import pandas as pd

x = [i for i in range(10)]
y = [i * 2 for i in range(10)]


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../../"))
DATA = os.path.abspath(os.path.join(HOME, "data/csv"))
CSV_DIR = os.path.abspath(os.path.join(DATA, "20221028_50_agg_test.csv"))
print(CSV_DIR)


def load_and_plot_data():
  """Load data and create visualization if file exists."""
  try:
    with open(CSV_DIR) as f:
      lines = csv.reader(f, delimiter=",")
      for row in lines:
        x.append(row[0])
        y.append(row[1])

    plt.plot(x, y)
    plt.title("Inline_mixer", fontsize=10)
    # plt.grid()
    plt.legend()
    plt.show()
  except FileNotFoundError:
    print(f"Data file not found: {CSV_DIR}")
    print("Using default sample data for visualization")
    plt.plot(x, y)
    plt.title("Inline_mixer (sample data)", fontsize=10)
    # plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
  load_and_plot_data()
