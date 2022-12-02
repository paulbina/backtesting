
import pandas as pd
import numpy as np

def display_desired_numbered_of_collumns():#display the desired number of collumns
    desired_width=200
    pd.set_option('display.width',desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns',15)
display_desired_numbered_of_collumns()
def display_desired_number_of_row():
    pd.set_option('display.max_rows', 3000)
display_desired_number_of_row()