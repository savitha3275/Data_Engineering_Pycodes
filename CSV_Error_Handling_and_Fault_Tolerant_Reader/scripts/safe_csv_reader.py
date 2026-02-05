# Build fault tolerant reader

import csv
import os

def safe_read_csv(file_path):
    '''
    safely reads the csv file - handles all errors gracefully
    returns a dict : success : True/False
    data : rows (if succesful)
    error : error message (if failed)
    '''

    # check if file exists or not
    if not os.path.exists(file_path):
        print(f"File not found : {file_path}")
        return {
            'success' : False,
            'error' : f"File not found : {file_path}"
        }

    # check if the file is empty (0 bytes)
    if os.path.getsize(file_path) == 0:
        print(f"File is empty : {file_path}")
        return {
            'success' : False,
            'error' : f"File is empty {file_path}"
        }

    # try to read the file
    try:
        with open(file_path,"r",encoding='utf-8') as file:
            reader = csv.DictReader(file)
            columns = reader.fieldnames

            # check if the file has headers
            if not columns:
                print(f"File has no headers : {file_path}")
                return {
                    'success' : False,
                    'error' : f"csv file has no headers : {file_path}"
                }

            # read the rows
            rows= list(reader)

            # does it have any data rows
            if len(rows) == 0:
                print(f"File has headers but no data : {file_path}")
                return {
                    'success' : False,
                    'error' : f"csv file has only headers and no data : {file_path}"
                }

            print(f"Successfully read {len(rows)} rows from {file_path}")
            return {
                'success' : True,
                'data' : rows,
                'columns' : columns,
                'row_count' : len(rows)
            }

    except PermissionError:
        print(f"Permission denied to read file : {file_path}")
        return {
            'success' : False,
            'error' : f"Permission denied to read file : {file_path}"
        }
    except Exception as e:
        print(f"Failed to read file : {file_path}")
        return {
            'success' : False,
            'error' : f"Failed to read file : {file_path}"
        }

    except UnicodeDecodeError:
        print(f"File encoding error : {file_path}")
        return {
            'success' : False,
            'error' : f"File encoding error : {file_path}"
        }

    except Exception as e:
        print(f"Unexpected error : {file_path}")
        return {
            'success' : False,
            'error' : f"Unexpected error : {file_path}"
        }

print("------Testing all scenarios------\n")

if __name__ == "__main__":
    print("------testing fault tolerant reader------")

    print("1.Reading valid file")
    result = safe_read_csv("../data/valid_data.csv")
    if result['success']:
        print(f"Data : {result['data'][0]}")
    print()

    print("2. Missing file....")
    result = safe_read_csv("../data/missing_file.csv")
    print()

    print("3. Empty file....")
    result = safe_read_csv("../data/empty_file.csv")
    print()

    print("4. Headers only file....")
    result = safe_read_csv("../data/headers_only.csv")
    print()

    print("----------All tests completed-----------")