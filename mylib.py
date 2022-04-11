from collections.abc import Iterable
import numpy as np
import pandas as pd
from IPython.display import display, HTML

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el



class EurekaUtil:
    # rxcui_map has ['INGREDIENT_LIST', 'ING_RXCUI_LIST']
    # rxnormIngr has ['RXCUI', 'INGREDIENT', 'ING_RXCUI']
    def __init__(self, rxnorm_ingredient_file_path):
        self.rxnormIngr = pd.read_csv(rxnorm_ingredient_file_path, delimiter='|')
        self.rxcui_map = self.createProductIngredientList()

    def searchIngredientByName(self, substring, verbose=False):
        result = self.rxnormIngr[self.rxnormIngr['INGREDIENT'].str.contains(substring, case=False)].value_counts(['INGREDIENT', 'ING_RXCUI']).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'Results: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result[['ING_RXCUI', 'INGREDIENT']]
        else:
            return None

    def findIngredientsByProductName(self, substring, verbose=False):
        return None
        # to do... need to load rxnorm db

    def getIngredientNameByRxcui(self, rxcui, verbose=False):
        result = self.rxnormIngr[self.rxnormIngr['ING_RXCUI'] == rxcui].value_counts(['INGREDIENT', 'ING_RXCUI']).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'getIngredientName: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result['ING_RXCUI'][0], result['INGREDIENT'][0]
        else:
            return None


    ## Add custom mappings
    def addIngredientsToCustomDrugs(self, df, drug_substring, ing_rxcui,
            df_medication_name_column='medication_name',
            ingredient_name_list_column='INGREDIENT_LIST', 
            ingredient_rxcui_list_column='ING_RXCUI_LIST',
            verbose=False):
            # df                             - df that will have fields added
            # df_medication_name_column      - column in df where the search for drug_substring will take place
            # drug_substring                 - df will be searched (column df_medication_name_column) by this substring to determine which rows to assign 
            #                                    INGREDIENT_LIST AND ING_RXCUI_LIST columns
            # ingredient_name_list_column    - Leave as default, this is from rx_norm
            # ingredient_rxcui_list_column    - Leave as default, this is from rx_norm. 

        # ensure ing_rxcui is a list (if not, convert it to list)
        if (not isinstance(ing_rxcui, list)):
            ing_rxcui = [ing_rxcui]
            
        ing_rxcui_list = []
        ing_name_list = []
        for i in ing_rxcui:
            rxcui, ing_name = self.getIngredientNameByRxcui(i)
            if (ing_name == None):
                print(f'Unable to find ing_rxcui {i} in rxnormIngr')
            else:
                ing_rxcui_list.append(rxcui)
                ing_name_list.append(ing_name)

        if verbose == True: print(f'found {len(ing_rxcui_list)} records in ingredient database')
        count = len(df[df[df_medication_name_column].str.contains(drug_substring, na=False, case=False)
                    & df.custom_entry == True])
        if verbose: print(f'Found {count} df_meds records matching {drug_substring}')
        df.loc[df[df_medication_name_column].str.contains(drug_substring, na=False, case=False)
                    & df.custom_entry == True, 
                    ingredient_name_list_column] = [pd.Series([ing_name_list])]*count
        df.loc[df[df_medication_name_column].str.contains(drug_substring, na=False, case=False)
                    & df.custom_entry == True, 
                    ingredient_rxcui_list_column] = [pd.Series([ing_rxcui_list])]*count
        return df, count, ing_name_list, ing_rxcui_list


    def createProductIngredientList(self):
        ## Aggregate RxCui into a map --->   RXCUI (index) |  [INGREDIENT_LIST]   | [ING_RXCUI_LIST]
        rxcui_ingredient = self.rxnormIngr.groupby('RXCUI')['INGREDIENT'].apply(list)
        rxcui_ingRxcui = self.rxnormIngr.groupby('RXCUI')['ING_RXCUI'].apply(list)
        rxcui_map = pd.merge(rxcui_ingredient, rxcui_ingRxcui, how="inner", on="RXCUI")
        rxcui_map.rename(columns={'INGREDIENT': 'INGREDIENT_LIST', 'ING_RXCUI': 'ING_RXCUI_LIST'}, inplace=True)
        return rxcui_map

    def addIngredientColumns(self, df_meds, left_rxcui="rxcui"):
        # Adds "INGREDIENT" and "ING_RXCUI" columns to df_meds
        # reads df_mds['rxcui']
        # df_meds - DF that has medications
        # left_rxcui - DF column name with rxcuis for each medication
        df_meds_mapped = pd.merge(df_meds, self.rxcui_map, how="left", left_on=left_rxcui, right_on='RXCUI')
        return df_meds_mapped


    def test(self, verbose=False):
        ## JUST RUNS THE TEST TO MAKE SURE RX_CUI DATABASE IS CORRECTLY LOADED
        if verbose: print(list(self.rxnormIngr))
        # rxnormIngr[rxnormIngr['INGREDIENT'].str.contains('hydrochlorothiazide', case=False)].value_counts(['INGREDIENT', 'ING_RXCUI'])

        query = 'thyroxine'
        if verbose: print(self.searchIngredientByName(query))
        if verbose: print(self.getIngredientNameByRxcui(10582))
        print('All EurekaMeds tests completed successfully!')

    def addIngredientsForCustomMedications(self, df_meds, mapping_dictionary, verbose=0):
        # ADDS [INGREDIENT_LIIST] AND [ING_RXCUI_LIST] COLUMNS TO DF, USING COLUMN LABELED '
        # df_meds = df with string column 'medication_name' <string> and 'custom_entry' <boolean>
        # verbose - verbose level (0 = no verbose), (1 - partial verbose), (2 - max verbose for debugging)
        for key, value in mapping_dictionary.items():
            df_meds, count, ing_name, ing_rxcui = self.addIngredientsToCustomDrugs(df_meds, key, value, verbose=(verbose==2))
            if verbose > 0: display(HTML(f'Searched <b>{key}</b> found <b>{ing_name}</b>, added ingredients to <b>{count}</b> records'))
        return df_meds


    def loadAllClasses(self, rxclass_types=['ATC1-4']):
        print("Reading classes from RxClass API")
        param = ' '.join(iter(rxclass_types))
        url_s = f'https://rxnav.nlm.nih.gov/REST/rxclass/allClasses.json?classTypes={param}'
        # with urllib.request.urlopen(url_s) as url:
        #     json = json.loads(url.read().decode())
        json = pd.read_json(url_s)

        classes = json['rxclassMinConceptList']['rxclassMinConcept']
        classes = pd.DataFrame(classes)
        self.rxclasses = classes
        print(f'Successfully read {len(classes)} classes from RxClass API!')