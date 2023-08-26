import glob
import os

import matplotlib.pyplot as plt
import csv
from collections import deque
from dateutil.parser import parse
import datetime as dt
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from tqdm import tqdm


def addSecs(tm, secs):
    fulldate = dt.datetime(tm.year,tm.month,tm.day, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate + dt.timedelta(seconds=secs)
    return fulldate


# cols=[1,2,3]
# df = pd.read_csv("one_giant_file.csv",usecols=cols)
#
# df.to_csv("one_giant_file.csv", index=False)
def start():
    curtime = dt.datetime.now()
    c = str(curtime)
    files = glob.glob(f'Data_tracking_csv_{c[8:10]}/*.csv')
    x = []
    y = []
    y1 = []
    i = 0
    velocity =[]
    t=[]
    d_t_sec=[]
    d_y =[]
    my_df_parquet = pd.DataFrame()
    # name_curtime = c[:10] + "_" + c[11:13] + "_" + c[14:15]
    #
    # name_dir_parquet = f'Data_tracking_parquet_{c[8:10]}'
    #
    # if not os.path.exists(name_dir_parquet):
    #     os.mkdir(name_dir_parquet)

    # with open('one_giant_file.csv', 'r') as csvfile:
    #     lines = csv.reader(csvfile, delimiter=',')
    name_dir_csv_fixed = f'Data_tracking_csv_fixed_{c[8:10]}'
    if not os.path.exists(name_dir_csv_fixed):
        os.mkdir(name_dir_csv_fixed)

    name_dir_parquet_fixed = f'Data_tracking_parquet_fixed_{c[8:10]}'
    if not os.path.exists(name_dir_parquet_fixed):
        os.mkdir(name_dir_parquet_fixed)
    filename_csv = f'slabdataMetrALL_{c[8:10]}.csv'
    filename_parquet = f'slabdataMetrALL_{c[8:10]}.parquet'
    fullname_name_dir_csv_fixed = os.path.join(name_dir_csv_fixed, filename_csv)
    fullname_name_dir_parquet_fixed = os.path.join(name_dir_parquet_fixed, filename_parquet)

    for file in files:
        with open(file, 'r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                i += 1
                if row[2] != "current time":
                    row_time = row[2]
                    time_datetime_format = parse(row_time)

                    t.append(time_datetime_format)
                    row_time_shift = addSecs(time_datetime_format, -25)
                    # print(row_time_shift)
                    # x.append(row_time[11:22])
                    x.append(str(row_time_shift))
                    # y.append(-float(row[0]))
                    y = (-float(row[0]) / (9+0.005*float(row[0]))) + 93
                    y1.append(y)

                    slabdata_metr = pd.DataFrame([{'y':y, 'current time':str(row_time_shift)}])
                    slabdata_metr_parquet = pd.DataFrame([[str(y), str(row_time_shift)]])

                    slabdata_metr.to_csv(fullname_name_dir_csv_fixed,
                                         mode='a', index=False, header=False)

                    # filename_parquet = f'slabdata{name_curtime}.parquet'
                    # fullname_parquet = os.path.join(name_dir_parquet, filename_parquet)
                    #
                    # table = pa.Table.from_pandas(slabdata_metr)
                    # pq.write_table(table, fullname_parquet)

                    my_df_parquet = pd.concat([my_df_parquet, slabdata_metr_parquet], ignore_index=True)

    df = pd.read_csv(fullname_name_dir_csv_fixed)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, fullname_name_dir_parquet_fixed)

    print("finish")

# df = pd.read_csv(filename)
# df = df.drop(df.index[1::2])
# df = df.reset_index(drop=True)
# df.to_csv(filename, index=False)
#
#
#
#
#
# t_sec=list(map(lambda x: float(x.timestamp()),t))
# n=0
# m=0
# b = len(t_sec)
# for i in range(0,b):
#     d_t_sec.append((t_sec[i])-n)
#     d_y.append(y1[i]-m)
#     velocity.append((y1[i]-m)/((t_sec[i])-n)*0.05)
#     n=t_sec[i]
#     m=y1[i]
#
#
#
#
# print(velocity)
# # slabdata_metr = pd.DataFrame([[y1, velocity, x]], columns=['ylist', 'velocity','current time'])
# # slabdata_metr.to_csv(f'slabdataMetr0308.csv', mode='a',index=False)
#
# x=x[:5000]
# # y=y[:100]
# velocity=velocity[:5000]
# y1=y1[:5000]
# fig, axs = plt.subplots(2)
# # plt.plot(x, y, color='g', linestyle='dashed',
# #          marker='o', label="Velocity Data")
# axs[0].plot(x, y1)
# axs[1].plot(x,velocity)
# axs[0].tick_params(axis='x', labelrotation = 90,labelsize=8)
# axs[1].tick_params(axis='x', labelrotation = 90,labelsize=8)
# plt.xlabel('time')
# # plt.ylabel('distance(m)')
# axs[0].grid()
# axs[1].grid()
#
# # plt.legend()
# # plt.show()
