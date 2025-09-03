import pandas as pd
import numpy as np
import ast, os
from typing import Type, List

class DP_DataCleaner:
    """
    This class is used to clean the data in the data provider file
    The class reads the file and uses the methods for fundamental
    data and target data to clean the input data. The class saves
    the cleaned data in a new file with the tabs "funadmendal_data" and
    "target_data" in the same location as the input file.
    """
    def __init__(self, path: str):
        self.errors = []
        self.file_path = path
        self.input_data = pd.read_excel(path, sheet_name=None, skiprows=0)

    def prepare_target_data(self, target_data: pd.DataFrame) -> pd.DataFrame:
        """
        This method is used to check the target_data tab of the excel input file
    
        :param target_data: A pandas DataFrame containing the target data 
        :return: the cleaned target data 
        """
        # Set all missing coverage values to 0.0
        target_data[['coverage_s1', 'coverage_s2', 'coverage_s3', 'reduction_ambition']] = \
            target_data[['coverage_s1', 'coverage_s2', 'coverage_s3', 'reduction_ambition']].fillna(0.0)
        target_data[['achieved_reduction']] = target_data[['achieved_reduction']].fillna(0.0)
        target_data[['end_year']] = target_data[['end_year']].fillna(0)
        target_data[['base_year_ghg_s1', 'base_year_ghg_s2', 'base_year_ghg_s3']] = \
            target_data[['base_year_ghg_s1', 'base_year_ghg_s2', 'base_year_ghg_s3']].fillna(0.0)
        target_data['scope'] = target_data['scope'].replace({'S1S2S3': 'S1+S2+S3'})
        target_data['scope'] = target_data['scope'].replace({'S1S2': 'S1+S2'})
 
        # Convert string representations of lists to actual lists        
        if 's3_category' in target_data.columns:
            target_data['s3_category'] = target_data['s3_category'].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
        target_data = self._process_s3categories(target_data)
        target_data = target_data.dropna(subset=['s3_category'])
        # Loop through the rows and ensure that target type T_score is S3
        indices_to_drop = []
        for index, row in target_data.iterrows():
            if row['target_type'].lower == 't_score' and row['scope'] != 'S3':
                self.errors.append(f"Row {index}: Target type T_score must have scope S3")
                indices_to_drop.append(index)
        target_data = target_data.drop(indices_to_drop)

        target_data.sort_values(by='target_ids', inplace=True)
        return target_data

    def _process_s3categories(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        This method is used to process the rows in the target data DataFrame
        :param data: A pandas DataFrame containing the target data
        :return: the cleaned target data
        """
        target_data = data.copy()
        new_rows = []
        # Loop through the rows and process the s3_category column
        for index, row in target_data.iterrows():
            
            if row['scope'] in ['S3', 'S1+S2+S3']:
                if isinstance(row['s3_category'], list):
                    if any(pd.isna(x) or x == 0 for x in row['s3_category']):
                        target_data.at[index, 's3_category'] = 0
                    else:
                        # Loop through the list and add a new row for each category
                        # The new row will have the same values as the original row
                        # except for the s3_category column. Values outside the range
                        # 1-15 will be discarded.
                        # The new rows will be appended to the target_data DataFrame
                        for category in row['s3_category']:
                            if 1 <= category <= 15:
                                new_row = row.copy()
                                new_row['s3_category'] = category
                                new_rows.append(new_row)
                            # else:
                            #     self.errors.append(f"Row {index}: Invalid s3_category value: {category}")
                            #     target_data.at[index, 's3_category'] = np.nan
                        target_data.at[index, 's3_category'] = np.nan
                else:
                    if pd.isna(row['s3_category']) or row['s3_category'] == 0:
                        target_data.at[index, 's3_category'] = 0
                    else:
                        if (row['s3_category'] < 0 or
                            row['s3_category'] > 15):
                            target_data.at[index, 's3_category'] = np.nan
                            self.errors.append(f"Row {index}: Invalid s3_category value: {row['s3_category']}")
                     
            else:
                target_data.at[index, 's3_category'] = -1
        if new_rows:
            target_data = pd.concat([target_data, pd.DataFrame(new_rows)], ignore_index=True)

        return target_data

    def prepare_fundamental_data(self, fundamental_data: pd.DataFrame) -> pd.DataFrame:
        """
        This method is used to check the fundamental_data tab of the excel input file
    
        :param fundamental_data: A pandas DataFrame containing the fundamental data 
        :return: the cleaned fundamental data 
        """
        # Make sure that the column "company_id contains unique values"
        if not fundamental_data['company_id'].is_unique:
            self.errors.append('The column "company_id" must contain unique values')
        # TODO add check for ISIC code
        
        # Check for optional columns in 'fundamental_data' and handle missing values
        optional_columns = ['ghg_s1', 'ghg_s2', 'ghg_s1s2', 'ghg_s3']
        for col in optional_columns:
            if col not in fundamental_data.columns:
                fundamental_data[col] = 0.0
            else:
                fundamental_data[col] = fundamental_data[col].fillna(0.0)

        return fundamental_data
        

    def data_cleaner_DP(self):
        """
        This is a method to clean the data in the data provider file
        The method reads the file and uses the methods for fundamental
        data and target data to clean the input data. The method saves
        the cleaned data in a new file with the tabs "funadmendal_data" and
        "target_data" in the same location as the input file.
        :param: path: The path to the input file
        :return: 

        """
        
        # Make sure that there are no empty rows in the data    
        target_data = self.input_data['target_data'].dropna(how='all')
        fundamental_data = self.input_data['fundamental_data'].dropna(how='all')

        target_data = self.prepare_target_data(target_data)
        fundamental_data = self.prepare_fundamental_data(fundamental_data)

        # Write the file back to disk
        directory, file_name = os.path.split(self.file_path)
        base_name, ext = os.path.splitext(file_name)
        new_file_name = f"{base_name}_cleaned{ext}"
        self.file_path = os.path.join(directory, new_file_name)
        with pd.ExcelWriter(self.file_path, engine='xlsxwriter') as writer:
            fundamental_data.to_excel(writer, sheet_name='fundamental_data', index=False)
            target_data.to_excel(writer, sheet_name='target_data', index=False)
        return self.errors
    
    
    