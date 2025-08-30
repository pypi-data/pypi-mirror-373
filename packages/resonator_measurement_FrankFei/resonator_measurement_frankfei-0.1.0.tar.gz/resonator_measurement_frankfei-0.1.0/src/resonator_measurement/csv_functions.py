import csv
        
def append_row_to_csv(filename, new_row):
    """Appends new_row as a new row to a CSV file.

    Args:
        filename (str): The path to the CSV file.
        number (int or float): The number to append.
    """
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)
