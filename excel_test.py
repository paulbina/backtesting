import pandas as pd
import xlsxwriter

def define_writer(filename, writer):
    filename = "ma_results_test.xlsx"
    writer = pd.ExcelWriter(filename,engine="xlsxwriter")
    writer.save()

