import pandas as pd
import os

if __name__ == "__main__":
    data = []

    csv_directory = '../data'
    filename = 'dataset_annonces.csv'
    COLUMN_NAME = 'DEALER_TYPE'

    df = pd.read_csv(f'{csv_directory}/{filename}')
    data.extend(df[COLUMN_NAME].tolist())

    data_unique = list(set(data))
    data_unique_string = map(str, data_unique)
    for value in data_unique_string:
        if value is not None and value != 'nan':
            print(value)