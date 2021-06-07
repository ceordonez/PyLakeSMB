import pandas as pd

def filterdata(t_data, lake, date, filt):

    if filt: #Filter data
        ld_data = t_data[lake][date].reset_index()
        fdata = ld_data.drop(filt)
        fdata = fdata.set_index(['Distance'])
    else:
        fdata = t_data[lake][date]
    return fdata
