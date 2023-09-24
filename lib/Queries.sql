-- These are the queries that are available to pull data from redshift. 
-- MEDICATION references


unload 
(
$$
SELECT DISTINCT f.resourceType
	, f.id
    , f.code.text
    , f.form.text
    , code_coding."system" as "coding_system"
    , code_coding.code as "coding_code"
--    , ingredient.itemCodeableConcept.text
--    , ing_coding."system" as "ing_coding_system"
--    , ing_coding.code as "ing_coding_code"
--    , form_coding."system"
 
FROM "glue-fhir"."r4_medication_references" f
	, f.code.coding code_coding
    , f.form.coding form_coding
    , f.ingredient ingredient
    , ingredient.itemCodeableConcept.coding ing_coding
WHERE
    coding_system = 'http://www.nlm.nih.gov/research/umls/rxnorm'
--    AND
--    ing_coding_system = 'http://www.nlm.nih.gov/research/umls/rxnorm'
--    AND
--    f.id = 'eQG0kOzZw4Tom3..tFxYW6nQQf4mgeUsk78ramRlmUVDv5-0hA0fiiPG2DTMGvgxEcw.w5xWhH1MY8IPkI7404Y1oyEhnCTPe5qCHDFkrKSo3'
$$)
to 's3://eurekatechteam-analysis/fhir/medications-references.csv'
iam_role 'arn:aws:iam::312752447322:role/production-redshift-RedshiftRole-1X54CSFEKND4'
parallel off
ALLOWOVERWRITE
HEADER
CSV DELIMITER AS ',';

----------------------------------------------------------------------------------------------
- MEDICATION REQUEST

unload ($$
  SELECT f.user_id
	, f.uploaded_date
    , f.provider
    , e.resource.id
    , e.resource.status
    , e.resource.intent
    , e.resource.medicationReference.reference as "medication_reference"
    , e.resource.medicationReference.display as "text"
    , e.resource.authoredOn
    , e.resource.requester.display as "requester_display"
    , e.resource.recorder.display as "recorder_display"
    , e.resource.courseofTherapyType.text as "course_of_therapy"
    , dosageInstruction.text as "dosage_text"
    , dosageInstruction.patientInstruction as "dosage_patientInstruction"
    , dosageInstruction.asNeededBoolean as "dosage_as_needed"
    , dosageInstruction.route.text as "dosage_route"
    , dosageInstruction.method.text as "dosage_method"
    , doseAndRate.type.text as "dose_text"
    , doseAndRate.doseQuantity.value as "dose_quantity_value"
    , doseAndRate.doseQuantity.unit as "dose_quantity_unit"
    , e.resource.dispenseRequest.validityPeriod.start as "start"
    , e.resource.dispenseRequest.numberOfRepeatsAllowed as "repeats"
    , e.resource.dispenseRequest.quantity.value as "quantity"
    , e.resource.dispenseRequest.quantity.unit as "quantity_unit"
    , e.resource.dispenseRequest.expectedSupplyDuration.value as "supply"
    , e.resource.dispenseRequest.expectedSupplyDuration.value as "supply_unit"
FROM "glue-fhir"."r4_medicationrequest" f
	, f.entries e
    , e.resource.dosageInstruction dosageInstruction
    , dosageInstruction.doseAndRate doseAndRate;
$$)
to 's3://eurekatechteam-analysis/fhir/medications.csv'
iam_role 'arn:aws:iam::312752447322:role/production-redshift-RedshiftRole-1X54CSFEKND4'
parallel off
ALLOWOVERWRITE
HEADER
CSV DELIMITER AS ',';


-------------------------------------
- CONDITIONS

unload 
(
$$SELECT DISTINCT f.user_id
	, e.resource.resourceType
    , f.provider
    , f.uploaded_date
	, f.fhir_version
    -- , e.resource.subject.display AS patient_name
    , e.resource.code.text AS condition_text
    , codeCoding."system" AS coding_system
    , codeCoding.code AS coding_code
    , category.text AS category
    , e.resource.id AS resource_id
    , e.resource.onsetPeriod.start
    , e.resource.onsetPeriod.end
    , e.resource.recordedDate
    , e.resource.verificationStatus.text AS verification_text
    , e.resource.clinicalStatus.text AS status
FROM "glue-fhir"."r4_condition" f
	, f.entries e
    , e.resource.code.coding codeCoding
    , e.resource.category category
--WHERE
--	f.uploaded_date >= '2000-04-03'
--    AND 
--    	codeCoding."system" = 'urn:oid:2.16.840.1.113883.6.96'      -- SNOMED
--          OR codeCoding."system" = 'urn:oid:2.16.840.1.113883.6.90' -- ICD10cm
ORDER BY
	f.user_id;$$)
to 's3://eurekatechteam-analysis/fhir/conditions_allcoding.csv'
iam_role 'arn:aws:iam::312752447322:role/production-redshift-RedshiftRole-1X54CSFEKND4'
parallel off
ALLOWOVERWRITE
HEADER
CSV DELIMITER AS ',';






-------------------------------------
- ENCOUNTERS

SELECT DISTINCT f.user_id
    , f.resource
    , f.provider
    , e.resource.resourceType
    , e.resource.id
    , f.uploaded_date
    , e.resource.subject.reference
    , e.resource.subject.display
    -- , link.relation
    -- , link.url
    , identifier.use
    , identifier."system" as id_system
    , identifier.value
    , e.resource.status
    -- , e.resource.class."system" as class_system
    -- , e.resource.class.code as class_code
    , e.resource.class.display as class_display
    -- , coding."system" as coding_system
    -- , coding.code as coding_code
    -- , coding.display as coding_display
    , type.text as type_text
    , e.resource.period.start
    , e.resource.period.end
    , location.location.reference
    , location.location.display
FROM "glue-fhir"."r4_encounter" f
	, f.entries e
    , e.resource.identifier identifier
    -- , e.link link
    , e.resource.location location
    , e.resource.type as type
    , type.coding as coding


 ------------------------------------------------
- ENCOUNTERS ULOAD

    unload 
(
$$SELECT DISTINCT f.user_id
    , f.resource
    , f.provider
    , e.resource.resourceType
    , e.resource.id
    , f.uploaded_date
    , e.resource.subject.reference
    , e.resource.subject.display
    -- , link.relation
    -- , link.url
    , identifier.use
    , identifier."system" as id_system
    , identifier.value
    , e.resource.status
    -- , e.resource.class."system" as class_system
    -- , e.resource.class.code as class_code
    , e.resource.class.display as class_display
    -- , coding."system" as coding_system
    -- , coding.code as coding_code
    -- , coding.display as coding_display
    , type.text as type_text
    , e.resource.period.start
    , e.resource.period.end
    , location.location.reference
    , location.location.display
FROM "glue-fhir"."r4_encounter" f
	, f.entries e
    , e.resource.identifier identifier
    -- , e.link link
    , e.resource.location location
    , e.resource.type as type
    , type.coding as coding
$$)
to 's3://eurekatechteam-analysis/fhir/encounters.csv'
iam_role 'arn:aws:iam::312752447322:role/production-redshift-RedshiftRole-1X54CSFEKND4'
parallel off
ALLOWOVERWRITE
HEADER
CSV DELIMITER AS ',';