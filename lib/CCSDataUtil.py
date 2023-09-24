import pandas as pd
import numpy as np
from IPython.display import display, HTML


class CCSDataUtil:   
   
   def __init__(self, drugUtil, verbose=True):
      self.verbose = verbose
      self.drugUtil = drugUtil

   def load_conditions(self, ccs_conditions_file):
      self.conditions = pd.read_csv(ccs_conditions_file, delimiter=',')
      to_numeric_fields = ['diabetes', 'hbp', 'blockages_in_your_coronary', 'heart_attack', 'chf', 'stroke', 'afib', 'sleep_apnea', 'copd', 'asthma', 'cancer', 'immunodeficiency', 'HIV', 'anemia', 'pregnant']
      for field in to_numeric_fields:
         self.conditions[field] = pd.to_numeric(self.conditions[field], downcast='integer', errors='coerce')
      print(f'Loaded CCS conditions records: {len(self.conditions)}')

   def load_medications(self, ccs_medications_file):
      self.medications_raw = pd.read_csv(ccs_medications_file)
      self.medications_raw["submitted_at"] = pd.to_datetime(self.medications_raw["submitted_at"])
      self.medications = self.medications_raw
      # latest_date_per_user = self.medications_raw.groupby('user_id')['submitted_at'].max().reset_index()
      # self.medications = self.medications_raw.merge(self.medications_raw.groupby('user_id')['submitted_at'].max().reset_index(),
      #                       on=['user_id', 'submitted_at'], how='inner')

   def load_medications_preprocessed(self, ccs_medications_preprocessed_file):
      self.medications = pd.read_csv(ccs_medications_preprocessed_file)

   def add_ingredient_column(self):
      print("Adding ingredient columns, this may take a while (need to look up each one)")
      print('Total number of medication records ', len(self.medications))


      def generate_ingredients_column(row, stringCol=None, rxcuiCol='rx', indexCol='', total=0):
         s = self.drugUtil.findIngredientsByRxcui(row[rxcuiCol], verbose=False)
         if (row['index'] % 1000 == 0): 
            print('Processing ', str(row['index']), '/', total)
         if s is not None:
            return s['ING_RXCUI'].array
         else:
            try:
               if stringCol is not None and isinstance(stringCol, str) and len(row[stringCol]) > 3:
                  searchString = row[stringCol]
                  result = self.drugUtil.findIngredientsByNameOrBrandnameL(searchString)
                  if len(result) == 1 and result.iloc[0]['match'] <=1:
                     return result['ING_RXCUI_LIST'].array
            except Exception as e: 
               print(e)
            return np.nan

      self.medications.reset_index(inplace=True)
      self.medications = self.medications.rename(columns={'index':'index_orig'})
      self.medications['index'] = self.medications.index

      self.medications['rxcui_ing'] = self.medications.apply(lambda r: generate_ingredients_column(r, stringCol='medication_name', rxcuiCol='rxcui', total=len(self.medications)), axis=1)
      print("Finished adding ingredient columns, now doing custom entries")

      mapping_dictionary = {
         'ASPIRIN': 1191,
         'asprin': 1191,
         'thyroxine': 10582, 
         'synthroid': 10582,
         'albuterol': 435, 
         'ventolin': 435,
         'vitamin d': 2418,
         'vitamin c': 1151,
         'Ethinyl estradiol/Inert ingredients/Norgestimate': [4124, 31994]
      }

      self.medications = self.add_custom_ingredients(self.medications, mapping_dictionary, verbose=1)
      self.medications = self.medications.explode('rxcui_ing')

   def load_demographics(self, ccs_demographics):
      self.demographics = pd.read_csv(ccs_demographics)
      print(f'Loaded demographics file with entries: ', len(self.demographics))

   def add_custom_ingredients(self, df_meds, mapping_dictionary, search_column="medication_name",
                           ing_rxcui_column="rxcui_ing",
                           ing_name_column="ing_name", verbose=1):
    # ADDS [INGREDIENT_LIIST] AND [ING_RXCUI_LIST] COLUMNS TO DF, USING COLUMN LABELED '
    # df_meds = df with string column 'medication_name' <string> and 'custom_entry' <boolean>
    # verbose - verbose level (0 = no verbose), (1 - partial verbose), (2 - max verbose for debugging)
      for substring, ing_rxcui in mapping_dictionary.items():
        if (not isinstance(ing_rxcui, list)): ing_rxcui = [ing_rxcui]
        ing_rxcui_list = []
        ing_name_list = []
        for i in ing_rxcui:
            rxcui, ing_name = self.drugUtil.findIngredientByRxcui(rxcui_ing=i)
            if (ing_name == None):
                print(f'Unable to find ing_rxcui {i} in rxnormIngr')
            else:
                ing_rxcui_list.append(rxcui)
                ing_name_list.append(ing_name)
        
        if len(ing_rxcui_list) == 0: 
            print(f'NOT found {substring}, {ing_rxcui} records in ingredient database')
            continue
        
        search_filter = df_meds[search_column].str.contains(substring, na=False, case=False) & df_meds.custom_entry == True
        count = len(df_meds[search_filter])
#         if verbose: print(f'Found {count} df_meds records matching {substring}')
        df_meds.loc[search_filter, 
                    ing_name_column] = [pd.Series([ing_name_list])]*count
        df_meds.loc[search_filter, 
                    ing_rxcui_column] = [pd.Series([ing_rxcui_list])]*count
        if verbose > 0: display(HTML(f'Searched <b>{substring}</b> found <b>{ing_name}</b>, added ingredients to <b>{count}</b> records'))
      return df_meds
   
# 1 min sample every 15 min if no accelerometer
# continuously 