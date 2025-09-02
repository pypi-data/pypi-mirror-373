import os
import sys
import pandas as pd

def convert_to_excel(folder_path):
    files = os.listdir(folder_path)
    i = 0
    for file in files:
        filename = os.path.join(folder_path, file)
        if os.path.isfile(filename):
            if file.endswith('.csv'):
                df = pd.read_csv(filename, dtype=str, encoding='latin')
            elif file.endswith('.tsv'):
                df = pd.read_csv(filename, dtype=str, delimiter='\t', encoding='latin')
            else:
                continue  # skip non-csv/tsv files

            i += 1
            output_file = os.path.splitext(filename)[0] + ".xlsx"
            df.to_excel(output_file, index=False)
            sys.stdout.write(f"\rFile No. {i} - {file} Processing")
            sys.stdout.flush()

    print(f"\nConversion completed. {i} files processed.")