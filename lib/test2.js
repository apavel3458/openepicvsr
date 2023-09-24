{
    Recommendation_Strength: "STRONG"
    Patient_Text: "You have a mechanical heart valve in the aortic and/or pulmonic position. You must be on warfarin, with an INR target of <if high_risk_valve_yesno() == YES then 2.5-3.5, ELSE 2.0-3.0>. Warfarin is the only blood thinner you can be on, because other blood thinners (direct-acting oral anticoagulants (DOACs) such as dabigatran) have not been proven to be safe, and may cause damage to the valve or cause a stroke. Aspirin alone is also not adequate, but may be added to warfarin."
    Provider_Text: "Your patient has a mechanical heart valve in the aortic and/or pulmonic position.  Warfarin is the only approved anticoagulant for this type of valve as per the guidelines.  The recommended INR is <if high_risk_valve_yesno() == YES then 2.5-3.5, ELSE 2.0-3.0>. In the RE-ALIGN RCT, when dabigatran was compared to warfarin in patients with mechanical heart valves, the study concluded that 'the use of dabigatran was shown to have increased rates of thromboembolic and bleeding complications as compared with warfarin, thus showing no benefit with excess risk'"
    References: "Eikelboom et al, NEJM 2023"

    Medication_Set_1: {
        Medications: {
            Medication1: { Name: "warfarin", Dosage: x, Units: "mg", Frequency: x, AIG: 0104597xxx}
        }
        Priority: 1
        Stop_Medication: "clopidogrel" AIG: 0134440xxx, "edoxaban" AIG: 0158530xxx, "prasugrel" AIG: 0152712xxx, "rivaroxaban" AIG: 0152487xxx, "ticagrelor" AIG:0152934xxx, "edoxaban" AIG: 0158530xxx, "dabigatran" AIG:0152467xxx
        Provider_notes: "For patients with mechanical mitral or aortic valve replacement who are at low risk of bleeding, addition of low dose aspirin (75mg-100mg daily) to warfarin may be considered."
        Patient_Notes: None
        Reference: "ACC/AHA 2020 Valve Guidelines"

    Reference_Long: "(Eikelboom et al, NEJM 2023) Eikelboom JW, Connolly SJ, Brueckmann M, et al. Dabigatran versus Warfarin in Patients with Mechanical Heart Valves. N Engl J Med. 2013;369(13):1206-1214. doi:10.1056/NEJMoa1300615"
    Reference_Long: "(ACC/AHA 2020 Valve Guidelines) Otto CM, Nishimura RA, Bonow RO, et al. 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease. Journal of the American College of Cardiology. 2021;77(4):e25-e197. doi:10.1016/j.jacc.2020.11.018"
}