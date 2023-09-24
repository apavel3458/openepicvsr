from collections.abc import Iterable
import numpy as np
import pandas as pd
from IPython.display import display, HTML
import re

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el



class DrugUtil:
    # rxcui_map has ['INGREDIENT_LIST', 'ING_RXCUI_LIST']
    # rxnormIngr has ['RXCUI', 'INGREDIENT', 'ING_RXCUI']
    def load(self, rxnorm_ingredients_file, rxnorm_file=None, rxclass_file=None, verbose=True):
        self.rxnormIngr = pd.read_csv(rxnorm_ingredients_file, delimiter='|')
        self.rxcui_map = self.createProductIngredientList()
        if (rxclass_file is not None):
            if verbose: print("Reading rxclass file...")
            self.rxclass = pd.read_csv(rxclass_file)
        if (rxnorm_file is not None):
            if verbose: print("Reading rxnorm file...")
            self.rxnorm = pd.read_csv(rxnorm_file, delimiter='|')

    def searchIngredientByName(self, substring, verbose=False):
        result = self.rxnormIngr[self.rxnormIngr['INGREDIENT'].str.contains(substring, case=False)].value_counts(['INGREDIENT', 'ING_RXCUI']).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'Results: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result[['ING_RXCUI', 'INGREDIENT']]
        else:
            return None

    def search_DFByIngredientName(self, df_meds_mapped, substring):
        # QUERY BY INGREDIENT (EXAMPLE)
        # nan shows up as floats. 
        mask = df_meds_mapped.INGREDIENT_LIST.apply(lambda x: not isinstance(x, float) and substring in x)
        return df_meds_mapped[mask]

# takes in substring, searches ingredient list for it
    def findIngredientByName(self, substring, ingredients=True, productname=True, verbose=False):
        result = pd.DataFrame()
        if (ingredients is True):
            result = self.rxnormIngr[self.rxnormIngr['INGREDIENT'].str.contains(substring, case=False)].value_counts(['INGREDIENT', 'ING_RXCUI']).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'Results: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result[['ING_RXCUI', 'INGREDIENT']]
        else:
            return None
        return None

    # takes in substring and searches rxnorm brand_name or full_name for it
    def findDrugByName(self, substring):
        result = self.rxnorm[(self.rxnorm['FULL_NAME'].str.contains(substring, case=False)) 
                     | (self.rxnorm['BRAND_NAME'].str.contains(substring, case=False))]
        return result


    def _collapseIngredients(self, df_ing):
        df = df_ing[['RXCUI', 'INGREDIENT', 'ING_RXCUI']]
        changes = ['INGREDIENT', 'ING_RXCUI']
        df = df.groupby('RXCUI')[changes].agg(list).reset_index().reindex(df.columns, axis=1)
        df = df.rename(columns={'INGREDIENT': 'INGREDIENT_LIST', 'ING_RXCUI': 'ING_RXCUI_LIST'})
        df_ing_1 = df_ing.drop(['INGREDIENT', 'ING_RXCUI'], axis=1)
        df = df.merge(df_ing_1, on="RXCUI")
        df = df.drop_duplicates(subset=['RXCUI'], keep='first')
        return df


    def findIngredientsByNameOrBrandnameL(self, substring, multi_result=False):
        # 
        # L for Levenshtein distance (distance in # of keystrokes)
        from Levenshtein import distance
        results_brand = self.findBrandNameL(substring)
        results_ing = self.findIngredientNameL(substring)
        result = {}
        # results_brand = results_brand.sort_values('match')
        # print(list(results_brand))
        # result = pd.concat([results_brand, results_ing], axis=0, ignore_index=True)
        
        # result =  self._collapseIngredients(result)
        # result = result.sort_values('match')
        # return result

        if len(results_ing) > 0 and results_ing.iloc[0]['match'] < results_brand.iloc[0]['match']:
            if (multi_result is False):
                row = results_ing.iloc[0]
                result = row.copy()
                result['BRAND'] = np.NaN
                result = result.to_frame().T
                return self._collapseIngredients(result)
            else:
                result = results_ing.copy()
                result['BRAND'] = np.NaN
                if not isinstance(result, pd.DataFrame):
                    result = result.to_frame().T
                result =  self._collapseIngredients(result)
                result = result.sort_values('match')
                return result
        #         return pd.DataFrame([[row['']]], columns=['Numbers'])
        else:
            brand = results_brand.iloc[0]
            brand = brand.copy()
            r = self.findIngredientsByRxcui(rxcui=brand['RXCUI'], verbose=False)
            r = r.assign(BRAND_NAME=brand['BRAND_NAME'])
            r = r.assign(match=brand['match'])
            return self._collapseIngredients(r)

    def findBrandNameL(self, substring, min_length=4):
        from Levenshtein import distance
        def match(string, query):
            noMatch = 100
            # If one is nan, return full length of query
            if (pd.isnull(string) or len(query) < min_length): return noMatch
            # Split string by non-alphanumeric character
            string = string.lower()
            query = query.lower()
            regex = '[^a-zA-Z]'
            stringSplit = re.split(regex, string)
            stringSplit = [f for f in stringSplit if len(f) > 3]
            # Split query by non-alphanuemric character, and take longest word (only support one word search)
            if (len(stringSplit) == 0): return noMatch
            querySplit = re.split(regex, query)
            queryBiggestWord = max(querySplit, key=len) if isinstance(querySplit, list) else querySplit
            
            distances = [distance(word, queryBiggestWord) for word in stringSplit]
            return min(distances) if len(distances) > 0 else noMatch
        
        result = self.rxnorm
        result['match'] = result.apply(lambda x: match(x['BRAND_NAME'], substring), axis=1)
        # drug_util.rxnorm.sort_values('test')[['test','FULL_NAME']]
        result = result.sort_values('match')
        return result

    def findIngredientNameL(self, substring, maxdistance=1):
        # Searchers ingredientNames and returns results
        # 'match' field in results indicates the Levenshtein distance between result and search string
        # L for Levenshtein
        from Levenshtein import distance
        def match(str1, str2):
            d = min([distance(w, str2) for w in re.split(' |,', str1)])
            return d
        result = self.rxnormIngr
        result['match'] = result['INGREDIENT'].apply(lambda x: match(x, substring))
        result = result.sort_values('match')
        return result[result['match'] <= maxdistance]

    # takes in rxcui (or rxcui_ing) and returns ingredient list from rxnorm
    # DEPRECTATED!!! USE findIngredientsByRxcui
    def findIngredientByRxcui(self, rxcui=None, rxcui_ing=None, verbose=False):
        queryField = 'ING_RXCUI' if rxcui_ing is not None else 'RXCUI'
        queryString = rxcui_ing if rxcui_ing is not None else rxcui
        result = self.rxnormIngr[self.rxnormIngr[queryField] == queryString].value_counts(['INGREDIENT', queryField]).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'getIngredientName: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result[queryField][0], result['INGREDIENT'][0]
            # return result
        else:
            print(f'Cannot find rxcui: {rxcui}, rxcui_ing: {rxcui_ing}' )
            return None

    def findIngredientByRxcuiIng(self, rxcui_ing=None, verbose=False):
        queryField = 'ING_RXCUI'
        queryString = rxcui_ing
        result = self.rxnormIngr[self.rxnormIngr[queryField] == queryString].value_counts(['INGREDIENT', queryField]).reset_index(name="counts")
        if (len(result) > 0):
            result_0 = result.iloc[0]
            if verbose:
                print(f'getIngredientName: {len(result)}, using first one: INGREDIENT: {result_0["INGREDIENT"]}, ING_RXCUI: {result_0["ING_RXCUI"]}, counts: {result_0["counts"]}')
            return result[queryField][0], result['INGREDIENT'][0]
            # return result
        else:
            print(f'Cannot find rxcui: rxcui_ing: {rxcui_ing}' )
            return (None, None)

    def findIngredientsByRxcui(self, rxcui=None, rxcui_ing=None, verbose=False):
        queryField = 'ING_RXCUI' if rxcui_ing is not None else 'RXCUI'
        queryString = rxcui_ing if rxcui_ing is not None else rxcui
        result = self.rxnormIngr[self.rxnormIngr[queryField] == queryString]
        if (len(result) > 0):
            return result
        else:
            if verbose: print(f'Cannot find rxcui: {rxcui}, rxcui_ing: {rxcui_ing}' )
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
            rxcui, ing_name = self.findIngredientByRxcui(rxcui_ing=i)
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
        # df_meds_mapped.rename(columns={'ING_RXCUI': 'ING_RXCUI_LIST'}, inplace=True)
        # df_meds_mapped['rxcui_ing'] = pd.to_numeric(df_meds_mapped['ING_RXCUI_LIST'])
        return df_meds_mapped
    
    def addIngredients(self, df_meds, left_rxcui="rxcui"):
        result = df_meds.merge(self.rxnormIngr, left_on=left_rxcui, right_on="RXCUI", how="left")
        return result

    def test(self, verbose=False):
        ## JUST RUNS THE TEST TO MAKE SURE RX_CUI DATABASE IS CORRECTLY LOADED
        if verbose: print(list(self.rxnormIngr))
        # rxnormIngr[rxnormIngr['INGREDIENT'].str.contains('hydrochlorothiazide', case=False)].value_counts(['INGREDIENT', 'ING_RXCUI'])

        query = 'thyroxine'
        if verbose: print(self.searchIngredientByName(query))
        if verbose: print(self.getIngredientNameByRxcui(10582))
        print('All EurekaMeds tests completed successfully!')




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

    def queryClassAPI(self, 
            queryStr = None, 
            rxcui = None, 
            includeClassType=['ATC1-4'], 
            excludeClassTypes=['DISEASE', 'PE', 'MOA', 'CHEM', 'STRUCT', 'DISPOS', 'EPC', 'PK'],
            verbose=False):
        # either use searchStr or rxcui
        result = None
        if (queryStr != None):
            result = self.searchIngredientByName(queryStr)
            print(result)
            if len(result) == 0:
                print('rxcui not found')
                return
            else:
                rxcui = result['ING_RXCUI'][0]
                print(f'Using {rxcui}')
                
        final = []
        url_s = f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={str(rxcui)}'
        json = pd.read_json(url_s)
        for item in json['rxclassDrugInfoList']['rxclassDrugInfo']:
            if (item['minConcept']['rxcui'] == str(rxcui) 
                and (includeClassType == None or item['rxclassMinConceptItem']['classType'] in includeClassType)
                and (item['rxclassMinConceptItem']['classType'] not in excludeClassTypes)):
        #         print(item['minConcept'])
                final.append(item['rxclassMinConceptItem'])
                if verbose:
                    print(item['rxclassMinConceptItem'])
        return final


    def extract_search_strings(s):
        # Utility method
        import re
        s = str(s)
        m = re.split('[\(\)\s,%\d-]+', s)
        m = [i for i in m if i]
        exclude = ['tablet', 'injection', 'capsule', 'tablet', 'tab', 'mg', 'units', 'ml', 'oral','.','ac','acids','mg/','liquid','hr','cr','sr','ec','shampoo','unit','mcg','pen','puff','hcl','weight','nasal','iv','inh','spray','misc','hr','solution','mg/ml','oil','peninjctr','find','/','er','kit','na','cap','mcg/actuation','b','d','iodine/ml','hfa','cream','plus','topical','xr']
        m = [i for i in m if i.lower() not in exclude]
        return m

    def search_ingredient_by_substring(self, s, max_distance=0, all_results=False, verbose=False):
        if verbose: print('searching', s)
        self.i = self.i+1
        if (self.i%100 == 0): print (f'{self.i} / {self.i_len}')
        return_columns = ['INGREDIENT_LIST', 'ING_RXCUI_LIST']
        search = DrugUtil.extract_search_strings(s)
        results = []
        for s in search:
            if verbose: print('looking at keyword', s)
            s = s.lower()
            r = self.findIngredientsByNameOrBrandnameL(s)
            r['searched'] = s
            results.append(r)
        
        if len(results) == 0: 
            if verbose: print('found:', s, 'not found')
            return pd.Series([np.nan, np.nan], index=return_columns)

        results = pd.concat(results, axis=0)
        # if len(results) == 0 return results
        results = results[results['match'] <= max_distance]

        if len(results) == 0: 
            if verbose: print('found:', s, 'not found')
            return pd.Series([np.nan, np.nan], index=return_columns)

        if len(results) == 1: 
            if verbose: print('found:', s, 'found results', len(results), 'specific:', results.iloc[0]['INGREDIENT_LIST'])
            return results.iloc[0][return_columns]
        else:
            length = results.searched.astype(str).map(len)
            if verbose: print('found:', s, 'found results', len(results), 'specific:', results.iloc[length.argmax()]['INGREDIENT_LIST'])
            return results.iloc[length.argmax()][return_columns]

    def add_ingredient_columns(self, df, med_name_column, new_code_column='ing_code', new_name_column='ing_name', max_distance=0):
        self.i = 0
        self.i_len = len(df)
        df[[new_name_column, new_code_column]] = df[med_name_column].apply(self.search_ingredient_by_substring, max_distance=max_distance)
        return df
