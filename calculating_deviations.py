import os
import boto3
import io
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import datetime as dt


def deviation():
    slab_deviation_track = pd.DataFrame()
    curtime = dt.datetime.now()
    c = str(curtime)

    s3_boto3 = boto3.resource(
        's3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='ru-central-01',
        endpoint_url='https://storage.yandexcloud.net/'
    )

    name_dir = f'Data_deviation_csv_23'
    if not os.path.exists(name_dir):
        os.mkdir(name_dir)
    #
    for i in range(6, 9):
        file_counter = 0
        bucket = s3_boto3.Bucket('')
        slabs = list(bucket.objects.filter(Prefix=f''))
        # slabs = list(bucket.objects.filter(Prefix=f''))
        for slab in slabs:
            buffer = io.BytesIO()
            slab_obj = s3_boto3.slab
            # # slab_obj = s3_boto3.Object(bucket_name='',
            # #                            key=f'')
            slab_obj.download_fileobj(buffer)
            slab_df_iba = pd.read_parquet(buffer)
            print(f'файл {slab.key} загружен')

            slab_1 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 1]
            slab_2 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 2]
            slab_3 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 3]
            slab_4 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 4]
            slab_5 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 5]
            slab_6 = slab_df_iba.loc[slab_df_iba.iloc[:, 1876] == 6]

            slab_1_time = pd.to_datetime(slab_1['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            slab_2_time = pd.to_datetime(slab_2['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            slab_3_time = pd.to_datetime(slab_3['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            slab_4_time = pd.to_datetime(slab_4['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            slab_5_time = pd.to_datetime(slab_5['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            slab_6_time = pd.to_datetime(slab_6['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            # print(slab_1_time)
            slab_1_y = slab_1.iloc[:, 1433]
            slab_2_y = slab_2.iloc[:, 1440]
            slab_3_y = slab_3.iloc[:, 1444]
            slab_4_y = slab_4.iloc[:, 1470]
            slab_5_y = slab_5.iloc[:, 1471]
            slab_6_y = slab_6.iloc[:, 1472]

            df_iba_y = pd.concat([slab_1_y, slab_2_y, slab_3_y, slab_4_y, slab_5_y, slab_6_y], axis=0)
            df_iba_time = pd.concat([slab_1_time, slab_2_time, slab_3_time, slab_4_time, slab_5_time, slab_6_time],
                                    axis=0)
            df = pd.concat([df_iba_time, df_iba_y], axis=1)
            df_sorted = df.sort_values(by=['Time'], ascending=True)

            df_csv = pd.read_csv(
                f'slab_tracking_script/Data_tracking_csv_{c[8:10]}/slabdata2023-08-{c[8:10]}_1{i}_{file_counter}.csv')
            # df_csv = pd.read_csv(
            #     f'Data_tracking_csv_23/slabdata2023-08-23_1{i}_{file_counter}.csv')

            df_csv_fixed = df_csv.iloc[::2]
            df_csv_fixed = df_csv_fixed.reset_index()
            df_csv_fixed = df_csv_fixed.iloc[:, 1:]
            df_sorted_time = pd.to_datetime(df_sorted['Time'].apply(lambda x: str(x)[:22]),
                                            format='%Y-%m-%d %H:%M:%S.%f')
            df_csv_fixed_time = pd.to_datetime(df_csv_fixed['current time'].apply(lambda x: str(x)[:22]),
                                               format='%Y-%m-%d %H:%M:%S.%f')
            df_sorted['Time'] = df_sorted_time
            df_csv_fixed['current time'] = df_csv_fixed_time
            merged_df_sorted = df_sorted[df_sorted['Time'].isin(df_csv_fixed['current time'])]
            merged_df_fixed = df_csv_fixed[df_csv_fixed['current time'].isin(df_sorted['Time'])]

            merged_df_sorted = merged_df_sorted.reset_index()
            merged_df_sorted = merged_df_sorted.iloc[:, 1:]

            merged_df_fixed = merged_df_fixed.reset_index()
            merged_df_fixed = merged_df_fixed.iloc[:, 1:]

            abs = merged_df_sorted.iloc[:, 1] - pd.to_numeric(merged_df_fixed.iloc[:, 0])
            rel = pd.to_numeric(merged_df_fixed.iloc[:, 0]) / merged_df_sorted.iloc[:, 1]

            df_deviation = pd.concat([abs, rel, merged_df_sorted['Time']], axis=1)

            slab_deviation_track = pd.concat([slab_deviation_track, df_deviation], axis=0)

            filename = f'slab_deviation_2023-08-{c[8:10]}_1{i}_{file_counter}.csv'
            # filename = f'slab_deviation_2023-08-23_1{i}_{file_counter}.csv'
            fullname = os.path.join(name_dir, filename)

            df_deviation.to_csv(fullname, index=False)

            buffer.flush()
            buffer.seek(0)

            print(f'файл_{file_counter}{i} успешно создан')

            file_counter += 1

    name_dir_plot = f'slab_tracking_script/BigData_deviation_parquet_plot_{c[8:10]}'
    if not os.path.exists(name_dir_plot):
        os.mkdir(name_dir_plot)
    filename_plot = f'slab_deviation_plot_2023-08-{c[8:10]}.parquet'
    fullname_plot = os.path.join(name_dir_plot, filename_plot)

    table = pa.Table.from_pandas(slab_deviation_track)
    pq.write_table(table, fullname_plot)
