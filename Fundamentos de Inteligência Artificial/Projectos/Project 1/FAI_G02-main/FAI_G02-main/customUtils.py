from pathlib import Path
import json
import pandas as pd
import re


def create_dataframe_from_json(json_filename, keys_to_include):
    """
    Function to create a pandas dataframe from the Json file created
    with the result of the solver

    Args:
        json_filename (str): Name of the json file
        keys_to_include (list[str]): List of keys (classes from each class) to include on the dataframe
        Example: The classes on the Lesi list
    Returns:
        Pandas Dataframe: Dataframe for each class
    """
    
    json_file_path = Path(json_filename)
    if json_file_path.exists():
        with json_file_path.open('r') as file:
            json_data = json.load(file)
        
        data = {}
        for key, value in json_data.items():
            if key in keys_to_include:
                data[key] = {
                    "Slot": value.get("Slot"),
                    "Teacher": value.get("Teacher"),
                    "Classroom": value.get("Classroom")
                }

        # Create dataframe
        df = pd.DataFrame.from_dict(data, orient='index')
        return df
    else:
        print(f"File {json_file_path} not found.")
        return None


def search_dict(my_dict, search_value):
    """
    Function to search a dictionary for a particular value

    Args:
        my_dict (dict): Dictionary to search
        search_value (str): Value to search

    Returns:
        str: Correspondent key to the value passed
    """
    for key, value_list in my_dict.items():
        if search_value in value_list:
            return key

    return None


def add_days_hours_columns(src_df, day_maps, hour_maps):
    """
    Function to add columns day and hour to the source dataframe

    Args:
        src_df (Pandas Dataframe): Source pandas dataframe
        day_maps (dict): Day to slots mapping
        hour_maps (dict): Hours to slots mapping

    Returns:
        Pandas Dataframe: Modified Pandas Df (with 2 new columns)
    """
    src_df['Day'] = src_df['Slot'].map({slot: day for day, slots in day_maps.items() for slot in slots})
    src_df['Hour'] = src_df['Slot'].map({slot: hour for hour, slots in hour_maps.items() for slot in slots}) 
    return src_df   


def create_classSchedule_dataframe(src_df, indexes, day_maps, hour_maps):
    """
    Function to create a new DataFrame with the content of src_df rearranged
    by time blocks and weekdays

    Args:
        src_df (Pandas Datframe): Original Dataframe
        indexes (list): List of the indexes (rows) for the new df
        day_maps (dict): Day to slots mapping
        hour_maps (dict): Hours to slots mapping

    Returns:
        Pandas Dataframe: New dataframe created
    """
    dst_df = pd.DataFrame(index=indexes, columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    for day, slots in day_maps.items():
        for slot in slots:
            matching_rows = src_df[src_df['Slot'] == slot]
            if not matching_rows.empty:
                dst_df.at[search_dict(hour_maps, search_value=slot), day] = src_df.loc[src_df['Slot'] == slot].index[0]

    # Empty space instead of NaN
    dst_df.fillna('', inplace=True)

    return dst_df


def get_pairs_TandTP(my_list):
    """
    Function to get the pairs T and Tp of the same subject
    Example: ('D1_T', 'DI_TP') 

    Args:
        my_list (list): list of the variables/subjects 

    Returns:
        list[tuple]: List of pair tuples T and TP
    """
    class_pairs = []
    for cls in my_list:
        match = re.search(r'^[A-Za-z]+\d*_TP$', cls)
        if match:
            prefix = cls.split('_')[0]
            pair = [f'{prefix}_T', cls]
            if pair[0] in set(my_list):
                class_pairs.append(tuple(pair))
    return class_pairs
    
    
def generate_subsets(start, end, sub_size=4):
    """
    Function to generate subsets of 4 elements of the original subset

    Args:
        start (int): First value
        end (int): Last value
        sub_size (int, optional): Size of the subsets. Defaults to 4.

    Returns:
        list[set]: List of all the subsets generated
    """
    subsets = []
    for i in range(start, end + 1, sub_size):
        subset = set(range(i, i + sub_size))
        subsets.append(subset)
    return subsets


def save_dict_to_json(solver_dict, teachers_dict, classrooms_dict, filename=""):
    """
    Function to save the result of the solver to a Json file

    Args:
        solver_dict (dict): Output of the solver
        teachers_dict (dict): Dictionary mapping teachers to the correspondent classes they lecture
        classrooms_dict (dict): Dictionary mapping classrooms with the respective classes that take place there
        filename (str, optional): Name for the Json file. Defaults to "".
    """
    new_dict = {}
    for key, value in solver_dict.items():
        teachers_list = [teacher for teacher, subjects in teachers_dict.items() if key in subjects]
        classrooms_list = [classroom for classroom, subjects in classrooms_dict.items() if key in subjects]

        new_dict[key] = {
            "Slot": value,
            "Teacher": teachers_list[0] if teachers_list else None,
            "Classroom": classrooms_list[0] if classrooms_list else None
        }

    with open(filename,'w') as file:
        json.dump(new_dict, file, indent=4)