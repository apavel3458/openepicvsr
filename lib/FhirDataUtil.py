import pandas as pd
import numpy as np


class FhirDataUtil:
    # rxcui_map has ['INGREDIENT_LIST', 'ING_RXCUI_LIST']
    # rxnormIngr has ['RXCUI', 'INGREDIENT', 'ING_RXCUI']
   def __init__(self, verbose=True):
      self.verbose = verbose

   def load_conditions(self, fhir_conditions_file, remove_health_concerns=False):
      self.conditions_raw = pd.read_csv(fhir_conditions_file, delimiter=',')
      self.conditions = self.conditions_raw
      print(f'RAW FHIR conditions: {len(self.conditions)}')
      self.conditions.loc[self.conditions.coding_system == 'urn:oid:2.16.840.1.113883.6.96', 'coding_system'] = 'SNOMED'
      self.conditions.loc[self.conditions.coding_system == 'urn:oid:2.16.840.1.113883.6.90', 'coding_system'] = 'ICD10'
      self.conditions['recordeddate_d'] = pd.to_datetime(self.conditions['recordeddate'], format="%Y-%m-%d", errors="coerce")
      self.conditions['start_d'] = pd.to_datetime(self.conditions['start'], format="%Y-%m-%d", errors="coerce")
      self.conditions['end_d'] = pd.to_datetime(self.conditions['end'], format="%Y-%m-%d", errors="coerce")
      # condUtil.conditions = condUtil.conditions.set_index(['coding_code', 'resource_id'])['coding_code'].unstack()
      if (remove_health_concerns):
         self.conditions = self.conditions.loc[self.conditions.category == 'Problem List Item', :]

      # self.conditions_per_row = self.fhir_pivot()
      print(f'FHIR conditions after pre-processing: {len(self.conditions)}')
         
   def load_demographics(self, fhir_demographics_file):
      self.demographics = pd.read_csv(fhir_demographics_file)

   def fhir_pivot(self):
      pivot = self.conditions
      cols = list(pivot.columns)
      cols.remove('coding_code')
      cols.remove('coding_system')
      pivot = pivot.drop_duplicates()
      pivot = pivot.pivot_table(values='coding_code', index=cols, columns=['coding_system'], aggfunc=', '.join)
      pivot = pivot.reset_index().rename_axis("index", axis=1)
      return pivot

   def load_medications(self, medications_fhir_file, medications_ref_fhir_file):
      print(f'----- Loading Medications ------')
      self.medications_raw = pd.read_csv(medications_fhir_file)
      print(f'Raw FHIR records: {len(self.medications_raw)}')

      # Truncate the first 11 characters (Medication/....id...)
      self.medications_raw['med_ref_id'] = self.medications_raw['medication_reference'].str[11:]
      
      # Duplicate to make working copy
      self.medications = self.medications_raw.copy()

      # duplicated by dose_text (ordered, calculated, admin-amount), only want ordered
      # Checked Dec 15, 2022 - dose_text = ordered represents ALL meds, others are duplicated.
      self.medications = self.medications[self.medications['dose_text'] == 'ordered']
      print(f'After de-duplicated: {len(self.medications)}')

      self.medications['authoredon_d'] = pd.to_datetime(self.medications['authoredon'])

      # Download medication_references
      self.medications_ref = pd.read_csv(medications_ref_fhir_file)

      # Merge medications with references to get access to coded data 
      self.medications = self.medications.merge(self.medications_ref[['id', 'coding_code']], left_on='med_ref_id', right_on='id', how="left", indicator='ref_merge')
      self.medications = self.medications.rename(columns={'id_x': 'medication_id', 'id_y': 'reference_id'})
      self.medications = self.medications.drop('med_ref_id', axis=1)
      
      singles = self.medications.drop_duplicates(subset='medication_id',keep='first')# meds_coded = fhirUtil.get_coded_medications(drugUtil)
      print(f'Merge with reference counts:')
      print(singles['ref_merge'].value_counts(dropna=False))

      print(f'Loaded FHIR medication records' , len(self.medications), ' Includes multiple code mappings')
      print(f'Unique users with fhir medications: ', self.medications["user_id"].nunique())
      print(f'------  Done Loading Medications -----')

   def get_coded_medications(self, drugUtil, verbose=True):
      # Filter to only ones with reference data
      meds_coded = self.medications[self.medications['ref_merge'] == 'both']
      def filter_ingredients(row):
         return row['coding_code'] in drugUtil.rxnormIngr['ING_RXCUI'].values
      if verbose: print("Unique medications have have a reference: ", meds_coded['medication_id'].nunique())
      meds_coded = meds_coded[~meds_coded['coding_code'].isna()]
      if verbose: print("After removing nan codes: ", meds_coded['medication_id'].nunique())
      meds_coded = meds_coded[meds_coded.apply(filter_ingredients, axis=1)]
      meds_coded.coding_code = meds_coded.coding_code.astype(int)
      
      if verbose: print("Unique medications that have a reference & have ingredient code: ", meds_coded['medication_id'].nunique())

      return meds_coded

   def searchFHIRandCCS(self, ccsUtil, search_icd10_codes, ccs_field, ccs_yes_values=[1], ccs_no_values=[2], condition_title=None, verbose=True):
      # search_icd10_codes: an array of strings of ICD10 prefixes (i.e. E10 will match E10.3)
      # ccs_field: field in the ccs dataset I.e. "diabets" or "hbp" for hypertension
      # ccs_yes_values: a list of values that will equate to yes, usually [1]
      # ccs_yes_values: a list of values that will equate to no, usually [2]
      # condition_title: what the condition will be called, i.e. "Essential Hypertension"

      # Returns: dictionary with result_both, result_ccs_only, and result_fhir_only   (prints users with that condition) - max one per user. 

      # Diabetes codes:
      # E08, E09, E11, E13
      if (condition_title is None):
         condition_title = ccs_field
      intersection = self.conditions_per_row.merge(ccsUtil.conditions, on='user_id', how='inner')
      if (verbose):
         print(f'Total CCS/FHIR conditions on users in both datasets: {len(intersection)}')

      def filter_fn_both(row):
         if (row[ccs_field] in ccs_yes_values):
               for s in search_icd10_codes:
                  for code in str(row['ICD10']).split(','):
                     if str(code).startswith(s):
                           return True
         return False

      def filter_fn_both_no(row):
         if (row[ccs_field] in ccs_no_values):
               for s in search_icd10_codes:
                  for code in str(row['ICD10']).split(','):
                     if str(code).startswith(s):
                           return False
               return True
         return False

      def filter_fn_fhir(row):
         for code in str(row['ICD10']).split(','):
            for s in search_icd10_codes:
               if (str(code).startswith(s)):
                           return True # CCS says no and FHIR says yes
         return False

      result_both = intersection[intersection.apply(filter_fn_both, axis=1)]
      result_ccs_only = intersection[~intersection.loc[:,'user_id'].isin(result_both['user_id'])] # remove everyone who has both FHIR and CCS
      result_ccs_only = result_ccs_only[result_ccs_only[ccs_field].isin(ccs_yes_values)]   # select only ones with CCS field from remaining

      result_fhir_only = intersection[~intersection.loc[:,'user_id'].isin(result_both['user_id'])] # remove everyone who has both FHIR and CCS
      result_fhir_only = result_fhir_only[result_fhir_only.apply(filter_fn_fhir, axis=1)]

      result_both_negative = intersection[~intersection.loc[:,'user_id'].isin(result_both['user_id'])]
      result_both_negative = result_both_negative[~result_both_negative.loc[:,'user_id'].isin(result_fhir_only['user_id'])]
      result_both_negative = result_both_negative[result_both_negative[ccs_field].isin(ccs_no_values)]

      if (verbose):
         print(f'users in FHIR: {len(self.conditions_per_row["user_id"].drop_duplicates())}')
         print(f'users in CCS: {len(ccsUtil.conditions["user_id"].drop_duplicates())}')
         print(f'users in FHIR and CCS: {len(intersection["user_id"].drop_duplicates())}')
         print('')

      both_len = len(result_both["user_id"].drop_duplicates())
      ccs_len = len(result_ccs_only["user_id"].drop_duplicates())
      fhir_len = len(result_fhir_only["user_id"].drop_duplicates())
      both_negative_len = len(result_both_negative["user_id"].drop_duplicates())
      total_users = len(intersection["user_id"].drop_duplicates())
      

      total_len = both_len + ccs_len + fhir_len
      both_percent = round((both_len*100)/total_len)
      ccs_percent = round((ccs_len*100)/total_len)
      fhir_percent = round((fhir_len*100)/total_len)
      both_negative_percent = round((both_negative_len*100)/(total_users-total_len))
      

      if (verbose):
         print(f'Total users that match FHIR or CCS: {total_len}')
         print(f'FHIR users that match criteria:{both_len+fhir_len}')
         print(f'CCS users that match criteria:{both_len+ccs_len}')
         print('')
         print(f'FHIR/CCS users who have {condition_title} in both datasets {both_len} ({both_percent}%)')
         print(f'FHIR/CCS users who have {condition_title} = NO in both datasets {both_negative_len} ({both_negative_percent}%)')
         print(f'FHIR/CCS users who have {condition_title} in CCS only {ccs_len} ({ccs_percent}%)')
         print(f'FHIR/CCS users who have {condition_title} in FHIR only {fhir_len} ({fhir_percent}%)')
      return { 'both': result_both, 
               'both_negative': result_both_negative,
               'ccs_only': result_ccs_only, 
               'fhir_only': result_fhir_only,
               'both_len': both_len,
               'both_negative_len': both_negative_len,
               'ccs_only_len': ccs_len,
               'fhir_only_len': fhir_len,
               'intersection': intersection,
               'total_yes': total_len,
               'total_no': total_users-total_len
            }

   def getFhirCCSComparisonTable(self, ccsUtil, comparison_config):
      result = []
      for config in comparison_config:
         print('Processing ', config['title'])
         comp = self.searchFHIRandCCS(
                                       ccsUtil=ccsUtil,
                                       search_icd10_codes=config['codes'], 
                                       ccs_field=config['ccs_field'], 
                                       ccs_yes_values=config['ccs_yes'], 
                                       ccs_no_values=config['ccs_no'],
                                       condition_title=config['title'],
                                       verbose=False)
         
         resultRow = {
            'title': config['title'],
            'Both Pos': comp['both_len'],
            'CF %': round((comp['both_len']*100)/comp['total_yes']),
            'CCS Pos': comp['ccs_only_len'],
            'C %': round((comp['ccs_only_len']*100)/comp['total_yes']),
            'FHIR Pos': comp['fhir_only_len'],
            'F %': round((comp['fhir_only_len']*100)/comp['total_yes']),
            'Both Negative': comp['both_negative_len'],
            'BN %': round((comp['both_negative_len']*100)/(comp['total_no']))
         }
         result.append(resultRow)
      result_df = pd.DataFrame(result)
      return result_df

   