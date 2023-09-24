{
    Recommendation_Strength: "REASONABLE"
    
    Patient_Text: "You have <List if patient has: atrial fibrillation [AF_DX] AND/OR atrial flutter [AFLUTTER_DX]> and are at increased risk of organ damage from blood clots, e.g. stroke. Your yearly risk of blood clot leading to organ damage is <get_thromboembolic_risk_number()>% , which means that in one year, one in <get_one_in_blank_number(get_thromboembolic_risk_number())> patients with your medical history will have a stroke. A blood thinner will significantly reduce your stroke risk. In addition, You have indicated that you have a [SURGERY_CAROTID_DX] that was placed within the past 90 days, which means you need to be on an addtional antiplatelet drug to protect you from stroke. After 90 days from the stent insertion, the antiplatelet drug is typically discontinued"
    Provider_Text: "Your patient has <List if patient has: atrial fibrillation [AF_DX] AND/OR atrial flutter [AFLUTTER_DX]> and is at an increased risk of stroke. Patient's CHADS2-65 score is <get_chads65_score_number()> and yearly thromboembolic risk is <get_thromboembolic_risk_number()>%. Lifelong anticoagulation is recommended to reduce stroke risk. Since your patient also has had a [SURGERY_CAROTID_DX] within the past 90 days, additional antiplatelet therapy is recommended.  However, no randomized controlled data is available, this recommendation is based on expert consensus."
    Medication_Set_1: {
        Medications: {
          Medication1: { Name: "clopidogrel", Dosage: 75, Units: "mg", Frequency: "daily", AIG: 0134440001}
          Medication2: { Name: "apixaban", Dosage: "get_apixaban_dose(STRATEGY=DUAL)", Units: "mg", Frequency: "twice daily", AIG:0153051001 }
          }
          Priority: 1
          Stop_Medication: "ASA" AIG:0101169013, "prasugrel" AIG: 0152712001 , "rivaroxaban" AIG: 0152487004, "ticagrelor" AIG:0152934002, "edoxaban" AIG: 0158530002, "dabigatran" AIG:0152467001, "warfarin" AIG: 0104597007
          Provider_notes: "Apixaban is a twice daily medication."
          Patient_Notes: "Apixaban is a twice daily medication."
          Reference: "", 
        }
      
      Medication_Set_2: {
          Medications: {
            Medication1: { Name: "clopidogrel", Dosage: 75, Units: "mg", Frequency: "once daily", AIG: 0134440001}
            Medication2: { Name: "edoxaban", Dosage: "get_edoxaban_dose(STRATEGY=DUAL)", Units: "mg", Frequency: "once daily", AIG: 0158530002}
          }
            
          Priority: 1
          Stop_Medication: "ASA" AIG:0101169013, "prasugrel" AIG: 0152712001 , "rivaroxaban" AIG: 0152487004, "ticagrelor" AIG:0152934002, "apixaban" AIG: 0153051001, "dabigatran" AIG:0152467001, "warfarin" AIG: 0104597007
          Provder_Notes: ""
          Patient_Notes: ""
          References: ""
      }
      Medication_Set_3: {
        Medications: {
          Medication1: { Name: "clopidogrel", Dosage: 75, Units: "mg", Frequency: "once daily", AIG: 0134440001}
          Medication2: { Name: "dabigatran", Dosage: "get_dabigatran_dose(STRATEGY=DUAL)", Units: "mg", Frequency: "once daily", AIG:0152467001 }
        }
          
        Priority: 1
        Stop_Medication: "ASA" AIG:0101169013, "prasugrel" AIG: 0152712001 , "rivaroxaban" AIG: 0152487004, "ticagrelor" AIG:0152934002, "apixaban" AIG: 0153051001, "warfarin" AIG: 0104597007, "edoxaban" AIG:0158530002�Provider_Notes: ""
        Patient_Notes: ""
        References: ""
       }
      
       Medication_Set_4: {
      Medications: {
          Medication1: { Name: "clopidogrel", Dosage: 75, Units: "mg", Frequency: "once daily", AIG: 0134440001}
          Medication2: { Name: "rivaroxaban", Dosage: "get_rivaroxaban_dose(STRATEGY=DUAL)", Units: "mg", Frequency: "once daily", AIG: 0152487004}
      }
        
      Priority: 1
      Stop_Medication: "ASA" AIG:0101169013, "prasugrel" AIG: 0152712001, "ticagrelor" AIG:0152934002, "apixaban" AIG: 0153051001, "warfarin" AIG: 0104597007, "edoxaban" AIG:0158530002, "dabigatran" AIG:0152467001
      Provider_Notes: "<if patient over 78 years old, put this statement:> Rivaroxaban is less preferred for patients 80 years of age or older. Patients taking Rivaroxaban may have a higher risk of major bleeding and gastrointestinal bleeding compared with other direct oral anticoagulants (DOACs), particularly apixaban."
      Reference: "American Geriatrics Society 2019 Updated AGS Beers Criteria:registered: JAGS 2019"
      Provider_Notes: "Rivaroxaban should be taken with food."
      References: "Andrade et al. CJC 2020"
      Patient_Notes: "Rivaroxaban should be taken with food."
      }

      Medication_Set_5: {
        Medications: {
            Medication1: { Name: "clopidogrel", Dosage: 75, Units: "mg", Frequency: "once daily", AIG: 0134440001}
            Medication2: { Name: "Warfarin", Dosage: "", Units: "", Frequency: "", AIG: 0104597007}
        }
        
        Priority: 2
        Stop_Medication: "ASA" AIG:0101169013, "prasugrel" AIG: 0152712001, "ticagrelor" AIG:0152934002, "apixaban" AIG: 0153051001, "edoxaban" AIG:0158530002, "dabigatran" AIG:0152467001, "rivaroxaban" AIG: 0152487004
        Provider_Notes: "DOACs are generally preferred over warfarin because they are associated with less serious bleeding, and in some cases are more effective at preventing stroke. Current CCS 2020 Atrial Fibrillation Guidelines place high value on the results of several large randomized controlled trials that have shown that DOACs are either equivalent or superior to warfarin in preventing atrial fibrillation-related thromboembolic events.  Patients already on warfarin may be offered the option to switch to a DOAC. "
            References: "Andrade et al. CJC 2020"
        Provider_Notes: “DOACs are more expensive than warfarin.  Drug coverage for DOACs varies based on provincial guidelines. “
        Provider_Notes: “Warfarin requires regular INR testing (every 1-4 weeks), and must be titrated to an INR target of 2-3.  This may be less preferred or not feasible for some patients.”
            Provider_Notes: ""
            Patient_Notes: "Warfarin is known to have food and drug interactions, and requires regular monitoring with a blood test.  Please review this with your healthcare provider."
        }
        

   
   Scheduled_Actions: "RERUN ALGORITHM AT 90 DAYS POST STENT"
   
   "Reference_Long: ""
   }