import numpy as np

def load_csv(filename):
    # 1. Read the header of the CSV (first line of the file).
    csv_dict = {}
    with open(filename, "r") as file:
        i = 0 # ???
        for line in file:
            if i == 0:
                headers = line.split(',')
                headers[-1] = headers[-1][0:-1]
                for header in headers:
                    csv_dict[header] = []
            else:
                data = line.split(',')
                for value, header in zip(data, headers):
                    if(header != 'Date'):
                        csv_dict[header].append(float(value))
                    else:
                        csv_dict[header].append(np.datetime64(value))
            i += 1
    # 2. Create a dictionary with column name as a Key. Initialize each Key's value to an empty list
    # 3. Iterate through the rest of the CSV filling the keys lists with their values.
    return csv_dict
        
def extractInfoFromLine(line_string):
    # Example line: <tr class="wr"><td align="left">09/07/2010</td><td class="nr">$50.08</td></tr>
    # First get the date string.

    # Find substring that contains the date.
    i = 0
    for i, ch in enumerate(line_string):
        # First ocurrence of a digit + 10 characters.
        if(ch.isnumeric()):
            date_string = line_string[i:i+10]
            break
        i += 1

    # .find() will return the INDEX.
    start_val_idx = line_string[i+10:].find('$') + i + 10
    end_val_idx = line_string[start_val_idx:].find('/td') + start_val_idx
    value_string = line_string[start_val_idx+1:end_val_idx-1]
    value = float(value_string)
    
    # Break it down in a tuple.
    # Convert to np.datetime64
    _date = (int(date_string[0:2]),
             int(date_string[3:5]),
             int(date_string[6:]))
    # np.datetime64('2005-02-25')
    # Create a string with _date[0], _date[1], _date[2]
    day_string = str(_date[1])
    month_string = str(_date[0])
    year_string = str(_date[2])
    if len(day_string) == 1:
        day_string = '0' + day_string
    if len(month_string) == 1:
        month_string = '0' + month_string
    

    _date = year_string + '-' + month_string + '-' + day_string
    _date = np.datetime64(_date)
    
    return _date, value

def loadDataFromHTMLFiles(filenames):
    # Line just above the table.
    START_PATTERN = "<tr><th class=\"left\">Date</th><th class=\"nr\">NAV</th></tr>\n"
    # Line just after the table.
    END_PATTERN = "</tbody>\n"

    # Create a dictionary, where the KEY is the filename of the HMTL file, and the value
    # is an empty list.
    data_dict = {}
    for fn in filenames:
        data = []
        foundStartPattern = False # Boolean flag. True or False
        with open(fn, "r") as file:
            for line in file:
                if line == END_PATTERN and foundStartPattern == True:
                    break
                if foundStartPattern == True:
                    # Get information from line.
                    _date, value = extractInfoFromLine(line)
                    data.append((_date, value))
                if line == START_PATTERN:
                    #print("FOUND PATTERN.")
                    foundStartPattern = True
    
        # Insert the `data` into `data_dict`, with the filename as the key.
        data_dict[fn] = data
    # Iterate through each filename ("keys"). Print the filename. Print the first and last entry of the value in the dictionary.
    dates_list = [] # 9-7-2010 --------------> 5-28-2021
    values_list = [] # Corresponding values
    firstFlag = False
    for filename in filenames:
        # Fill out the lists
        for d, v in data_dict[filename]:
            # Is the date already there?
            if (firstFlag == False):
                dates_list.append(d)
                values_list.append(v)
                firstFlag = True
            elif (d != dates_list[-1]):
                dates_list.append(d)
                values_list.append(v)

    assert len(dates_list) == len(values_list)
    # Pretty print, iterate using zip
    return dates_list, values_list