from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = None

class PredicateEnum(str, Enum):
    RELATED_TO = "biolink:related_to"
    RELATED_TO_AT_CONCEPT_LEVEL = "biolink:related_to_at_concept_level"
    RELATED_TO_AT_INSTANCE_LEVEL = "biolink:related_to_at_instance_level"
    DISEASE_HAS_LOCATION = "biolink:disease_has_location"
    LOCATION_OF_DISEASE = "biolink:location_of_disease"
    COMPOSED_PRIMARILY_OF = "biolink:composed_primarily_of"
    PRIMARILY_COMPOSED_OF = "biolink:primarily_composed_of"
    ASSOCIATED_WITH = "biolink:associated_with"
    OPPOSITE_OF = "biolink:opposite_of"
    AFFECTS_LIKELIHOOD_OF = "biolink:affects_likelihood_of"
    LIKELIHOOD_AFFECTED_BY = "biolink:likelihood_affected_by"
    TARGET_FOR = "biolink:target_for"
    HAS_TARGET = "biolink:has_target"
    ACTIVE_IN = "biolink:active_in"
    HAS_ACTIVE_COMPONENT = "biolink:has_active_component"
    ACTS_UPSTREAM_OF = "biolink:acts_upstream_of"
    HAS_UPSTREAM_ACTOR = "biolink:has_upstream_actor"
    MENTIONS = "biolink:mentions"
    MENTIONED_BY = "biolink:mentioned_by"
    CONTRIBUTOR = "biolink:contributor"
    HAS_CONTRIBUTOR = "biolink:has_contributor"
    ASSESSES = "biolink:assesses"
    IS_ASSESSED_BY = "biolink:is_assessed_by"
    INTERACTS_WITH = "biolink:interacts_with"
    AFFECTS = "biolink:affects"
    AFFECTED_BY = "biolink:affected_by"
    DIAGNOSES = "biolink:diagnoses"
    IS_DIAGNOSED_BY = "biolink:is_diagnosed_by"
    INCREASES_AMOUNT_OR_ACTIVITY_OF = "biolink:increases_amount_or_activity_of"
    AMOUNT_OR_ACTIVITY_INCREASED_BY = "biolink:amount_or_activity_increased_by"
    DECREASES_AMOUNT_OR_ACTIVITY_OF = "biolink:decreases_amount_or_activity_of"
    AMOUNT_OR_ACTIVITY_DECREASED_BY = "biolink:amount_or_activity_decreased_by"
    GENE_PRODUCT_OF = "biolink:gene_product_of"
    HAS_GENE_PRODUCT = "biolink:has_gene_product"
    TRANSCRIBED_TO = "biolink:transcribed_to"
    TRANSCRIBED_FROM = "biolink:transcribed_from"
    TRANSLATES_TO = "biolink:translates_to"
    TRANSLATION_OF = "biolink:translation_of"
    COEXISTS_WITH = "biolink:coexists_with"
    CONTRIBUTES_TO = "biolink:contributes_to"
    CONTRIBUTION_FROM = "biolink:contribution_from"
    STUDIED_TO_TREAT = "biolink:studied_to_treat"
    APPLIED_TO_TREAT = "biolink:applied_to_treat"
    TREATMENT_APPLICATIONS_FROM = "biolink:treatment_applications_from"
    TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT = "biolink:treats_or_applied_or_studied_to_treat"
    SUBJECT_OF_TREATMENT_APPLICATION_OR_STUDY_FOR_TREATMENT_BY = "biolink:subject_of_treatment_application_or_study_for_treatment_by"
    HAS_PHENOTYPE = "biolink:has_phenotype"
    PHENOTYPE_OF = "biolink:phenotype_of"
    OCCURS_IN = "biolink:occurs_in"
    CONTAINS_PROCESS = "biolink:contains_process"
    LOCATED_IN = "biolink:located_in"
    LOCATION_OF = "biolink:location_of"
    SIMILAR_TO = "biolink:similar_to"
    HAS_SEQUENCE_LOCATION = "biolink:has_sequence_location"
    SEQUENCE_LOCATION_OF = "biolink:sequence_location_of"
    MODEL_OF = "biolink:model_of"
    MODELS = "biolink:models"
    OVERLAPS = "biolink:overlaps"
    HAS_PARTICIPANT = "biolink:has_participant"
    PARTICIPATES_IN = "biolink:participates_in"
    DERIVES_INTO = "biolink:derives_into"
    DERIVES_FROM = "biolink:derives_from"
    MANIFESTATION_OF = "biolink:manifestation_of"
    HAS_MANIFESTATION = "biolink:has_manifestation"
    PRODUCES = "biolink:produces"
    PRODUCED_BY = "biolink:produced_by"
    TEMPORALLY_RELATED_TO = "biolink:temporally_related_to"
    RELATED_CONDITION = "biolink:related_condition"
    IS_SEQUENCE_VARIANT_OF = "biolink:is_sequence_variant_of"
    HAS_SEQUENCE_VARIANT = "biolink:has_sequence_variant"
    DISEASE_HAS_BASIS_IN = "biolink:disease_has_basis_in"
    OCCURS_IN_DISEASE = "biolink:occurs_in_disease"
    CONTRAINDICATED_IN = "biolink:contraindicated_in"
    HAS_CONTRAINDICATION = "biolink:has_contraindication"
    HAS_NOT_COMPLETED = "biolink:has_not_completed"
    NOT_COMPLETED_BY = "biolink:not_completed_by"
    HAS_COMPLETED = "biolink:has_completed"
    COMPLETED_BY = "biolink:completed_by"
    IN_LINKAGE_DISEQUILIBRIUM_WITH = "biolink:in_linkage_disequilibrium_with"
    HAS_INCREASED_AMOUNT = "biolink:has_increased_amount"
    INCREASED_AMOUNT_OF = "biolink:increased_amount_of"
    HAS_DECREASED_AMOUNT = "biolink:has_decreased_amount"
    DECREASED_AMOUNT_IN = "biolink:decreased_amount_in"
    LACKS_PART = "biolink:lacks_part"
    MISSING_FROM = "biolink:missing_from"
    DEVELOPS_FROM = "biolink:develops_from"
    DEVELOPS_INTO = "biolink:develops_into"
    IN_TAXON = "biolink:in_taxon"
    TAXON_OF = "biolink:taxon_of"
    HAS_MOLECULAR_CONSEQUENCE = "biolink:has_molecular_consequence"
    IS_MOLECULAR_CONSEQUENCE_OF = "biolink:is_molecular_consequence_of"
    HAS_MISSENSE_VARIANT = "biolink:has_missense_variant"
    HAS_SYNONYMOUS_VARIANT = "biolink:has_synonymous_variant"
    HAS_NONSENSE_VARIANT = "biolink:has_nonsense_variant"
    HAS_FRAMESHIFT_VARIANT = "biolink:has_frameshift_variant"
    HAS_SPLICE_SITE_VARIANT = "biolink:has_splice_site_variant"
    HAS_NEARBY_VARIANT = "biolink:has_nearby_variant"
    HAS_NON_CODING_VARIANT = "biolink:has_non_coding_variant"
    IS_MISSENSE_VARIANT_OF = "biolink:is_missense_variant_of"
    IS_SYNONYMOUS_VARIANT_OF = "biolink:is_synonymous_variant_of"
    IS_NONSENSE_VARIANT_OF = "biolink:is_nonsense_variant_of"
    IS_FRAMESHIFT_VARIANT_OF = "biolink:is_frameshift_variant_of"
    IS_SPLICE_SITE_VARIANT_OF = "biolink:is_splice_site_variant_of"
    IS_NEARBY_VARIANT_OF = "biolink:is_nearby_variant_of"
    IS_NON_CODING_VARIANT_OF = "biolink:is_non_coding_variant_of"
    PRECEDES = "biolink:precedes"
    PRECEDED_BY = "biolink:preceded_by"
    HAS_MODE_OF_INHERITANCE = "biolink:has_mode_of_inheritance"
    MODE_OF_INHERITANCE_OF = "biolink:mode_of_inheritance_of"
    IS_METABOLITE_OF = "biolink:is_metabolite_of"
    HAS_METABOLITE = "biolink:has_metabolite"
    IS_INPUT_OF = "biolink:is_input_of"
    IS_OUTPUT_OF = "biolink:is_output_of"
    CATALYZES = "biolink:catalyzes"
    IS_SUBSTRATE_OF = "biolink:is_substrate_of"
    ACTIVELY_INVOLVED_IN = "biolink:actively_involved_in"
    ENABLES = "biolink:enables"
    CAPABLE_OF = "biolink:capable_of"
    CONSUMED_BY = "biolink:consumed_by"
    HAS_INPUT = "biolink:has_input"
    HAS_OUTPUT = "biolink:has_output"
    HAS_CATALYST = "biolink:has_catalyst"
    HAS_SUBSTRATE = "biolink:has_substrate"
    ACTIVELY_INVOLVES = "biolink:actively_involves"
    ENABLED_BY = "biolink:enabled_by"
    CAN_BE_CARRIED_OUT_BY = "biolink:can_be_carried_out_by"
    CONSUMES = "biolink:consumes"
    HAS_PART = "biolink:has_part"
    PART_OF = "biolink:part_of"
    PLASMA_MEMBRANE_PART_OF = "biolink:plasma_membrane_part_of"
    FOOD_COMPONENT_OF = "biolink:food_component_of"
    IS_ACTIVE_INGREDIENT_OF = "biolink:is_active_ingredient_of"
    IS_EXCIPIENT_OF = "biolink:is_excipient_of"
    VARIANT_PART_OF = "biolink:variant_part_of"
    NUTRIENT_OF = "biolink:nutrient_of"
    HAS_PLASMA_MEMBRANE_PART = "biolink:has_plasma_membrane_part"
    HAS_FOOD_COMPONENT = "biolink:has_food_component"
    HAS_ACTIVE_INGREDIENT = "biolink:has_active_ingredient"
    HAS_EXCIPIENT = "biolink:has_excipient"
    HAS_VARIANT_PART = "biolink:has_variant_part"
    HAS_NUTRIENT = "biolink:has_nutrient"
    HOMOLOGOUS_TO = "biolink:homologous_to"
    CHEMICALLY_SIMILAR_TO = "biolink:chemically_similar_to"
    PARALOGOUS_TO = "biolink:paralogous_to"
    ORTHOLOGOUS_TO = "biolink:orthologous_to"
    XENOLOGOUS_TO = "biolink:xenologous_to"
    EXPRESSES = "biolink:expresses"
    EXPRESSED_IN = "biolink:expressed_in"
    TREATED_BY = "biolink:treated_by"
    TESTED_BY_CLINICAL_TRIALS_OF = "biolink:tested_by_clinical_trials_of"
    TREATED_IN_STUDIES_BY = "biolink:treated_in_studies_by"
    TESTED_BY_PRECLINICAL_TRIALS_OF = "biolink:tested_by_preclinical_trials_of"
    MODELS_DEMONSTRATING_BENEFITS_FOR = "biolink:models_demonstrating_benefits_for"
    TREATS = "biolink:treats"
    IN_CLINICAL_TRIALS_FOR = "biolink:in_clinical_trials_for"
    IN_PRECLINICAL_TRIALS_FOR = "biolink:in_preclinical_trials_for"
    BENEFICIAL_IN_MODELS_FOR = "biolink:beneficial_in_models_for"
    AMELIORATES_CONDITION = "biolink:ameliorates_condition"
    PREVENTATIVE_FOR_CONDITION = "biolink:preventative_for_condition"
    CAUSED_BY = "biolink:caused_by"
    CAUSES = "biolink:causes"
    IN_PATHWAY_WITH = "biolink:in_pathway_with"
    IN_COMPLEX_WITH = "biolink:in_complex_with"
    IN_CELL_POPULATION_WITH = "biolink:in_cell_population_with"
    COLOCALIZES_WITH = "biolink:colocalizes_with"
    RESPONSE_AFFECTED_BY = "biolink:response_affected_by"
    REGULATED_BY = "biolink:regulated_by"
    DISRUPTED_BY = "biolink:disrupted_by"
    CONDITION_AMELIORATED_BY = "biolink:condition_ameliorated_by"
    CONDITION_PREVENTED_BY = "biolink:condition_prevented_by"
    CONDITION_EXACERBATED_BY = "biolink:condition_exacerbated_by"
    ADVERSE_EVENT_OF = "biolink:adverse_event_of"
    IS_SIDE_EFFECT_OF = "biolink:is_side_effect_of"
    RESPONSE_INCREASED_BY = "biolink:response_increased_by"
    RESPONSE_DECREASED_BY = "biolink:response_decreased_by"
    AFFECTS_RESPONSE_TO = "biolink:affects_response_to"
    REGULATES = "biolink:regulates"
    DISRUPTS = "biolink:disrupts"
    EXACERBATES_CONDITION = "biolink:exacerbates_condition"
    HAS_ADVERSE_EVENT = "biolink:has_adverse_event"
    HAS_SIDE_EFFECT = "biolink:has_side_effect"
    INCREASES_RESPONSE_TO = "biolink:increases_response_to"
    DECREASES_RESPONSE_TO = "biolink:decreases_response_to"
    PHYSICALLY_INTERACTS_WITH = "biolink:physically_interacts_with"
    GENETICALLY_INTERACTS_WITH = "biolink:genetically_interacts_with"
    GENE_FUSION_WITH = "biolink:gene_fusion_with"
    GENETIC_NEIGHBORHOOD_OF = "biolink:genetic_neighborhood_of"
    DIRECTLY_PHYSICALLY_INTERACTS_WITH = "biolink:directly_physically_interacts_with"
    INDIRECTLY_PHYSICALLY_INTERACTS_WITH = "biolink:indirectly_physically_interacts_with"
    BINDS = "biolink:binds"
    HAS_PROVIDER = "biolink:has_provider"
    HAS_PUBLISHER = "biolink:has_publisher"
    HAS_EDITOR = "biolink:has_editor"
    HAS_AUTHOR = "biolink:has_author"
    PROVIDER = "biolink:provider"
    PUBLISHER = "biolink:publisher"
    EDITOR = "biolink:editor"
    AUTHOR = "biolink:author"
    HAS_POSITIVE_UPSTREAM_ACTOR = "biolink:has_positive_upstream_actor"
    HAS_NEGATIVE_UPSTREAM_ACTOR = "biolink:has_negative_upstream_actor"
    HAS_UPSTREAM_OR_WITHIN_ACTOR = "biolink:has_upstream_or_within_actor"
    HAS_POSITIVE_UPSTREAM_OR_WITHIN_ACTOR = "biolink:has_positive_upstream_or_within_actor"
    HAS_NEGATIVE_UPSTREAM_OR_WITHIN_ACTOR = "biolink:has_negative_upstream_or_within_actor"
    ACTS_UPSTREAM_OF_POSITIVE_EFFECT = "biolink:acts_upstream_of_positive_effect"
    ACTS_UPSTREAM_OF_NEGATIVE_EFFECT = "biolink:acts_upstream_of_negative_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN = "biolink:acts_upstream_of_or_within"
    ACTS_UPSTREAM_OF_OR_WITHIN_POSITIVE_EFFECT = "biolink:acts_upstream_of_or_within_positive_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_NEGATIVE_EFFECT = "biolink:acts_upstream_of_or_within_negative_effect"
    CONDITION_PROMOTED_BY = "biolink:condition_promoted_by"
    CONDITION_PREDISPOSED_BY = "biolink:condition_predisposed_by"
    PROMOTES_CONDITION = "biolink:promotes_condition"
    PREDISPOSES_TO_CONDITION = "biolink:predisposes_to_condition"
    ASSOCIATED_WITH_LIKELIHOOD_OF = "biolink:associated_with_likelihood_of"
    LIKELIHOOD_ASSOCIATED_WITH = "biolink:likelihood_associated_with"
    ASSOCIATED_WITH_SENSITIVITY_TO = "biolink:associated_with_sensitivity_to"
    SENSITIVITY_ASSOCIATED_WITH = "biolink:sensitivity_associated_with"
    ASSOCIATED_WITH_RESISTANCE_TO = "biolink:associated_with_resistance_to"
    RESISTANCE_ASSOCIATED_WITH = "biolink:resistance_associated_with"
    GENETIC_ASSOCIATION = "biolink:genetic_association"
    GENETICALLY_ASSOCIATED_WITH = "biolink:genetically_associated_with"
    CORRELATED_WITH = "biolink:correlated_with"
    POSITIVELY_CORRELATED_WITH = "biolink:positively_correlated_with"
    NEGATIVELY_CORRELATED_WITH = "biolink:negatively_correlated_with"
    OCCURS_TOGETHER_IN_LITERATURE_WITH = "biolink:occurs_together_in_literature_with"
    COEXPRESSED_WITH = "biolink:coexpressed_with"
    HAS_BIOMARKER = "biolink:has_biomarker"
    BIOMARKER_FOR = "biolink:biomarker_for"
    GENE_ASSOCIATED_WITH_CONDITION = "biolink:gene_associated_with_condition"
    CONDITION_ASSOCIATED_WITH_GENE = "biolink:condition_associated_with_gene"
    INCREASED_LIKELIHOOD_ASSOCIATED_WITH = "biolink:increased_likelihood_associated_with"
    DECREASED_LIKELIHOOD_ASSOCIATED_WITH = "biolink:decreased_likelihood_associated_with"
    ASSOCIATED_WITH_INCREASED_LIKELIHOOD_OF = "biolink:associated_with_increased_likelihood_of"
    ASSOCIATED_WITH_DECREASED_LIKELIHOOD_OF = "biolink:associated_with_decreased_likelihood_of"
    HAS_CHEMICAL_ROLE = "biolink:has_chemical_role"
    SUPERCLASS_OF = "biolink:superclass_of"
    SUBCLASS_OF = "biolink:subclass_of"
    CLOSE_MATCH = "biolink:close_match"
    BROAD_MATCH = "biolink:broad_match"
    NARROW_MATCH = "biolink:narrow_match"
    MEMBER_OF = "biolink:member_of"
    HAS_MEMBER = "biolink:has_member"
    EXACT_MATCH = "biolink:exact_match"
    SAME_AS = "biolink:same_as"


class NodeCategoryEnum(str, Enum):
    NAMED_THING = "biolink:NamedThing"
    ATTRIBUTE = "biolink:Attribute"
    ORGANISM_TAXON = "biolink:OrganismTaxon"
    EVENT = "biolink:Event"
    ADMINISTRATIVE_ENTITY = "biolink:AdministrativeEntity"
    INFORMATION_CONTENT_ENTITY = "biolink:InformationContentEntity"
    PHYSICAL_ENTITY = "biolink:PhysicalEntity"
    ACTIVITY = "biolink:Activity"
    PROCEDURE = "biolink:Procedure"
    PHENOMENON = "biolink:Phenomenon"
    DEVICE = "biolink:Device"
    DIAGNOSTIC_AID = "biolink:DiagnosticAid"
    PLANETARY_ENTITY = "biolink:PlanetaryEntity"
    BIOLOGICAL_ENTITY = "biolink:BiologicalEntity"
    CHEMICAL_ENTITY = "biolink:ChemicalEntity"
    CLINICAL_ENTITY = "biolink:ClinicalEntity"
    TREATMENT = "biolink:Treatment"
    CLINICAL_TRIAL = "biolink:ClinicalTrial"
    CLINICAL_INTERVENTION = "biolink:ClinicalIntervention"
    HOSPITALIZATION = "biolink:Hospitalization"
    MOLECULAR_ENTITY = "biolink:MolecularEntity"
    CHEMICAL_MIXTURE = "biolink:ChemicalMixture"
    ENVIRONMENTAL_FOOD_CONTAMINANT = "biolink:EnvironmentalFoodContaminant"
    FOOD_ADDITIVE = "biolink:FoodAdditive"
    MOLECULAR_MIXTURE = "biolink:MolecularMixture"
    COMPLEX_MOLECULAR_MIXTURE = "biolink:ComplexMolecularMixture"
    PROCESSED_MATERIAL = "biolink:ProcessedMaterial"
    FOOD = "biolink:Food"
    DRUG = "biolink:Drug"
    SMALL_MOLECULE = "biolink:SmallMolecule"
    NUCLEIC_ACID_ENTITY = "biolink:NucleicAcidEntity"
    REGULATORY_REGION = "biolink:RegulatoryRegion"
    BIOLOGICAL_PROCESS_OR_ACTIVITY = "biolink:BiologicalProcessOrActivity"
    GENETIC_INHERITANCE = "biolink:GeneticInheritance"
    ORGANISMAL_ENTITY = "biolink:OrganismalEntity"
    DISEASE_OR_PHENOTYPIC_FEATURE = "biolink:DiseaseOrPhenotypicFeature"
    GENE = "biolink:Gene"
    MACROMOLECULAR_COMPLEX = "biolink:MacromolecularComplex"
    NUCLEOSOME_MODIFICATION = "biolink:NucleosomeModification"
    GENOME = "biolink:Genome"
    EXON = "biolink:Exon"
    TRANSCRIPT = "biolink:Transcript"
    CODING_SEQUENCE = "biolink:CodingSequence"
    POLYPEPTIDE = "biolink:Polypeptide"
    PROTEIN_DOMAIN = "biolink:ProteinDomain"
    POSTTRANSLATIONAL_MODIFICATION = "biolink:PosttranslationalModification"
    PROTEIN_FAMILY = "biolink:ProteinFamily"
    NUCLEIC_ACID_SEQUENCE_MOTIF = "biolink:NucleicAcidSequenceMotif"
    GENE_FAMILY = "biolink:GeneFamily"
    GENOTYPE = "biolink:Genotype"
    HAPLOTYPE = "biolink:Haplotype"
    SEQUENCE_VARIANT = "biolink:SequenceVariant"
    REAGENT_TARGETED_GENE = "biolink:ReagentTargetedGene"
    SNV = "biolink:Snv"
    PROTEIN = "biolink:Protein"
    PROTEIN_ISOFORM = "biolink:ProteinIsoform"
    RNA_PRODUCT = "biolink:RNAProduct"
    RNA_PRODUCT_ISOFORM = "biolink:RNAProductIsoform"
    NONCODING_RNA_PRODUCT = "biolink:NoncodingRNAProduct"
    MICRORNA = "biolink:MicroRNA"
    SIRNA = "biolink:SiRNA"
    DISEASE = "biolink:Disease"
    PHENOTYPIC_FEATURE = "biolink:PhenotypicFeature"
    BEHAVIORAL_FEATURE = "biolink:BehavioralFeature"
    CLINICAL_FINDING = "biolink:ClinicalFinding"
    BACTERIUM = "biolink:Bacterium"
    VIRUS = "biolink:Virus"
    CELLULAR_ORGANISM = "biolink:CellularOrganism"
    LIFE_STAGE = "biolink:LifeStage"
    INDIVIDUAL_ORGANISM = "biolink:IndividualOrganism"
    POPULATION_OF_INDIVIDUAL_ORGANISMS = "biolink:PopulationOfIndividualOrganisms"
    ANATOMICAL_ENTITY = "biolink:AnatomicalEntity"
    CELL_LINE = "biolink:CellLine"
    CELLULAR_COMPONENT = "biolink:CellularComponent"
    CELL = "biolink:Cell"
    GROSS_ANATOMICAL_STRUCTURE = "biolink:GrossAnatomicalStructure"
    PATHOLOGICAL_ANATOMICAL_STRUCTURE = "biolink:PathologicalAnatomicalStructure"
    STUDY_POPULATION = "biolink:StudyPopulation"
    COHORT = "biolink:Cohort"
    CASE = "biolink:Case"
    MAMMAL = "biolink:Mammal"
    PLANT = "biolink:Plant"
    INVERTEBRATE = "biolink:Invertebrate"
    VERTEBRATE = "biolink:Vertebrate"
    FUNGUS = "biolink:Fungus"
    HUMAN = "biolink:Human"
    MOLECULAR_ACTIVITY = "biolink:MolecularActivity"
    BIOLOGICAL_PROCESS = "biolink:BiologicalProcess"
    PATHWAY = "biolink:Pathway"
    PHYSIOLOGICAL_PROCESS = "biolink:PhysiologicalProcess"
    BEHAVIOR = "biolink:Behavior"
    PATHOLOGICAL_PROCESS = "biolink:PathologicalProcess"
    ACCESSIBLE_DNA_REGION = "biolink:AccessibleDnaRegion"
    TRANSCRIPTION_FACTOR_BINDING_SITE = "biolink:TranscriptionFactorBindingSite"
    ENVIRONMENTAL_PROCESS = "biolink:EnvironmentalProcess"
    ENVIRONMENTAL_FEATURE = "biolink:EnvironmentalFeature"
    GEOGRAPHIC_LOCATION = "biolink:GeographicLocation"
    GEOGRAPHIC_LOCATION_AT_TIME = "biolink:GeographicLocationAtTime"
    STUDY = "biolink:Study"
    MATERIAL_SAMPLE = "biolink:MaterialSample"
    STUDY_RESULT = "biolink:StudyResult"
    STUDY_VARIABLE = "biolink:StudyVariable"
    COMMON_DATA_ELEMENT = "biolink:CommonDataElement"
    DATASET = "biolink:Dataset"
    DATASET_DISTRIBUTION = "biolink:DatasetDistribution"
    DATASET_VERSION = "biolink:DatasetVersion"
    DATASET_SUMMARY = "biolink:DatasetSummary"
    CONFIDENCE_LEVEL = "biolink:ConfidenceLevel"
    EVIDENCE_TYPE = "biolink:EvidenceType"
    PUBLICATION = "biolink:Publication"
    RETRIEVAL_SOURCE = "biolink:RetrievalSource"
    BOOK = "biolink:Book"
    BOOK_CHAPTER = "biolink:BookChapter"
    SERIAL = "biolink:Serial"
    ARTICLE = "biolink:Article"
    PATENT = "biolink:Patent"
    WEB_PAGE = "biolink:WebPage"
    PREPRINT_PUBLICATION = "biolink:PreprintPublication"
    DRUG_LABEL = "biolink:DrugLabel"
    JOURNAL_ARTICLE = "biolink:JournalArticle"
    CONCEPT_COUNT_ANALYSIS_RESULT = "biolink:ConceptCountAnalysisResult"
    OBSERVED_EXPECTED_FREQUENCY_ANALYSIS_RESULT = "biolink:ObservedExpectedFrequencyAnalysisResult"
    RELATIVE_FREQUENCY_ANALYSIS_RESULT = "biolink:RelativeFrequencyAnalysisResult"
    TEXT_MINING_RESULT = "biolink:TextMiningResult"
    CHI_SQUARED_ANALYSIS_RESULT = "biolink:ChiSquaredAnalysisResult"
    LOG_ODDS_ANALYSIS_RESULT = "biolink:LogOddsAnalysisResult"
    AGENT = "biolink:Agent"
    CHEMICAL_ROLE = "biolink:ChemicalRole"
    BIOLOGICAL_SEX = "biolink:BiologicalSex"
    SEVERITY_VALUE = "biolink:SeverityValue"
    ORGANISM_ATTRIBUTE = "biolink:OrganismAttribute"
    ZYGOSITY = "biolink:Zygosity"
    CLINICAL_ATTRIBUTE = "biolink:ClinicalAttribute"
    SOCIOECONOMIC_ATTRIBUTE = "biolink:SocioeconomicAttribute"
    GENOMIC_BACKGROUND_EXPOSURE = "biolink:GenomicBackgroundExposure"
    PATHOLOGICAL_PROCESS_EXPOSURE = "biolink:PathologicalProcessExposure"
    PATHOLOGICAL_ANATOMICAL_EXPOSURE = "biolink:PathologicalAnatomicalExposure"
    DISEASE_OR_PHENOTYPIC_FEATURE_EXPOSURE = "biolink:DiseaseOrPhenotypicFeatureExposure"
    CHEMICAL_EXPOSURE = "biolink:ChemicalExposure"
    COMPLEX_CHEMICAL_EXPOSURE = "biolink:ComplexChemicalExposure"
    BIOTIC_EXPOSURE = "biolink:BioticExposure"
    ENVIRONMENTAL_EXPOSURE = "biolink:EnvironmentalExposure"
    BEHAVIORAL_EXPOSURE = "biolink:BehavioralExposure"
    SOCIOECONOMIC_EXPOSURE = "biolink:SocioeconomicExposure"
    GEOGRAPHIC_EXPOSURE = "biolink:GeographicExposure"
    DRUG_EXPOSURE = "biolink:DrugExposure"
    DRUG_TO_GENE_INTERACTION_EXPOSURE = "biolink:DrugToGeneInteractionExposure"
    CLINICAL_MEASUREMENT = "biolink:ClinicalMeasurement"
    CLINICAL_MODIFIER = "biolink:ClinicalModifier"
    CLINICAL_COURSE = "biolink:ClinicalCourse"
    ONSET = "biolink:Onset"
    PHENOTYPIC_QUALITY = "biolink:PhenotypicQuality"
    PHENOTYPIC_SEX = "biolink:PhenotypicSex"
    GENOTYPIC_SEX = "biolink:GenotypicSex"


class KnowledgeLevelEnum(str, Enum):
    # A statement of purported fact that is put forth by an agent as true, based on assessment of direct evidence. Assertions are likely but not  definitively true.
    knowledge_assertion = "knowledge_assertion"
    # A statement reporting a conclusion that follows logically from premises representing established facts or knowledge assertions (e.g. fingernail part of finger, finger part of hand --> fingernail part of hand).
    logical_entailment = "logical_entailment"
    # A statement of a possible fact based on probabilistic forms of reasoning over more indirect forms of evidence, that lead to more speculative conclusions.
    prediction = "prediction"
    # A statement that reports concepts representing variables in a dataset to be statistically associated with each other in a particular cohort (e.g. 'Metformin Treatment (variable 1) is correlated with Diabetes Diagnosis (variable 2) in EHR dataset X').
    statistical_association = "statistical_association"
    # A statement reporting (and possibly quantifying) a phenomenon that was observed to occur -  absent any analysis or interpretation that generates a statistical association or supports a broader conclusion or inference.
    observation = "observation"
    # The knowledge level is not provided, typically because it cannot be determined from available. information.
    not_provided = "not_provided"


class AgentTypeEnum(str, Enum):
    # A human agent who is responsible for generating a statement of knowledge. The human may utilize computationally generated information as evidence for the resulting knowledge,  but the human is the one who ultimately interprets/reasons with  this evidence to produce a statement of knowledge.
    manual_agent = "manual_agent"
    # An automated agent, typically a software program or tool, that is  responsible for generating a statement of knowledge. Human contribution  to the knowledge creation process ends with the definition and coding of algorithms or analysis pipelines that get executed by the automated agent.
    automated_agent = "automated_agent"
    # An automated agent that executes an analysis workflow over data and  reports the direct results of the analysis. These typically report  statistical associations/correlations between variables in the input dataset, and do not interpret/infer broader conclusions from associations the analysis reveals in the data.
    data_analysis_pipeline = "data_analysis_pipeline"
    # An automated agent that generates knowledge statements (typically predictions) based on rules/logic explicitly encoded in an algorithm (e.g. heuristic models, supervised classifiers), or learned from patterns  observed in data (e.g. ML models, unsupervised classifiers).
    computational_model = "computational_model"
    # An automated agent that uses Natural Language Processing to recognize concepts and/or relationships in text, and report them using formally encoded semantics (e.g. as an edge in a knowledge graph).
    text_mining_agent = "text_mining_agent"
    # An automated agent that processes images to generate textual statements of  knowledge derived from the image and/or expressed in text the image  depicts (e.g. via OCR).
    image_processing_agent = "image_processing_agent"
    # A human agent reviews and validates/approves the veracity of knowledge  that is initially generated by an automated agent.
    manual_validation_of_automated_agent = "manual_validation_of_automated_agent"
    # The agent type is not provided, typically because it cannot be determined from available information if the agent that generated the knowledge is  manual or automated.
    not_provided = "not_provided"


class AttributeTypeEnum(str, Enum):
    """
    Code used to describe the nature of a slot, for documentative purposes.
    """
    # Attribute used as a boolean filter for the disease list.
    filter = "filter"
    # Attribute used as a grouping/tagging attribute for the disease list.
    grouping = "grouping"


class CurationTypeEnum(str, Enum):
    """
    Code used to describe how a slot / attribute was curated.
    """
    # Manually curated by a Matrix medical expert.
    manual_everycure = "manual_everycure"
    # Manually curated by the Mondo team.
    manual_mondo = "manual_mondo"
    # Automatically curated by a script or algorithm.
    llm = "llm"
    # Automatically extracted from the ontology hierarchy.
    ontology_hierarchy = "ontology_hierarchy"
    # Automatically extracted from an external source.
    external_source = "external_source"
    # Automatically curated from a lexical matching algorithm.
    lexical_matching = "lexical_matching"



class MatrixNode(ConfiguredBaseModel):
    """
    A node in the Biolink knowledge graph.
    """
    id: str = Field(default=..., description="""A unique identifier for a thing""")
    name: Optional[str] = Field(default=None, description="""Human-readable name of the entity.""")
    category: NodeCategoryEnum = Field(default=..., description="""Biolink category of the entity.""")
    description: Optional[str] = Field(default=None, description="""Detailed description of the entity.""")
    equivalent_identifiers: Optional[List[str]] = Field(default=None, description="""List of equivalent identifiers for the entity.""")
    all_categories: Optional[List[NodeCategoryEnum]] = Field(default=None, description="""All categories associated with the entity.""")
    publications: Optional[List[str]] = Field(default=None, description="""Publications associated with the entity.""")
    labels: Optional[List[str]] = Field(default=None, description="""Alternative labels for the entity.""")
    international_resource_identifier: Optional[str] = Field(default=None, description="""IRI of the entity.""")
    upstream_data_source: Optional[List[str]] = Field(default=None, description="""Sources from which this entity's data originates.""")


class MatrixEdge(ConfiguredBaseModel):
    """
    An edge representing a relationship between two nodes in the Biolink knowledge graph.
    """
    subject: str = Field(default=..., description="""The subject entity in the edge.""")
    predicate: PredicateEnum = Field(default=..., description="""The predicate defining the relationship.""")
    object: str = Field(default=..., description="""The object entity in the edge.""")
    knowledge_level: Optional[KnowledgeLevelEnum] = Field(default=None, description="""Knowledge level of the relationship""")
    agent_type: Optional[AgentTypeEnum] = Field(default=None, description="""Type of agent involved in the relationship.""")
    primary_knowledge_source: Optional[str] = Field(default=None, description="""Primary source of the knowledge in the edge.""")
    aggregator_knowledge_source: Optional[List[str]] = Field(default=None, description="""Aggregators of the knowledge.""")
    publications: Optional[List[str]] = Field(default=None, description="""Publications associated with the entity.""")
    subject_aspect_qualifier: Optional[str] = Field(default=None, description="""Aspect qualifier for the subject.""")
    subject_direction_qualifier: Optional[str] = Field(default=None, description="""Direction qualifier for the subject.""")
    object_aspect_qualifier: Optional[str] = Field(default=None, description="""Aspect qualifier for the object.""")
    object_direction_qualifier: Optional[str] = Field(default=None, description="""Direction qualifier for the object.""")
    upstream_data_source: Optional[List[str]] = Field(default=None, description="""Sources from which this entity's data originates.""")
    num_references: Optional[int] = Field(default=None, description="""Number of references supporting this edge.""")
    num_sentences: Optional[int] = Field(default=None, description="""Number of sentences supporting this edge.""")


class UnionedNode(MatrixNode):
    """
    A node in the unioned everycure matrix graph.
    """
    id: str = Field(default=..., description="""A unique identifier for a thing""")
    name: Optional[str] = Field(default=None, description="""Human-readable name of the entity.""")
    category: NodeCategoryEnum = Field(default=..., description="""Biolink category of the entity.""")
    description: Optional[str] = Field(default=None, description="""Detailed description of the entity.""")
    equivalent_identifiers: Optional[List[str]] = Field(default=None, description="""List of equivalent identifiers for the entity.""")
    all_categories: Optional[List[NodeCategoryEnum]] = Field(default=None, description="""All categories associated with the entity.""")
    publications: Optional[List[str]] = Field(default=None, description="""Publications associated with the entity.""")
    labels: Optional[List[str]] = Field(default=None, description="""Alternative labels for the entity.""")
    international_resource_identifier: Optional[str] = Field(default=None, description="""IRI of the entity.""")
    upstream_data_source: Optional[List[str]] = Field(default=None, description="""Sources from which this entity's data originates.""")


class UnionedEdge(MatrixEdge):
    """
    An edge in the unioned everycure matrix graph.
    """
    primary_knowledge_sources: Optional[List[str]] = Field(default=None, description="""Primary sources from edges merged into this edge.""")
    subject: str = Field(default=..., description="""The subject entity in the edge.""")
    predicate: PredicateEnum = Field(default=..., description="""The predicate defining the relationship.""")
    object: str = Field(default=..., description="""The object entity in the edge.""")
    knowledge_level: Optional[KnowledgeLevelEnum] = Field(default=None, description="""Knowledge level of the relationship""")
    agent_type: Optional[AgentTypeEnum] = Field(default=None, description="""Type of agent involved in the relationship.""")
    primary_knowledge_source: Optional[str] = Field(default=None, description="""Primary source of the knowledge in the edge.""")
    aggregator_knowledge_source: Optional[List[str]] = Field(default=None, description="""Aggregators of the knowledge.""")
    publications: Optional[List[str]] = Field(default=None, description="""Publications associated with the entity.""")
    subject_aspect_qualifier: Optional[str] = Field(default=None, description="""Aspect qualifier for the subject.""")
    subject_direction_qualifier: Optional[str] = Field(default=None, description="""Direction qualifier for the subject.""")
    object_aspect_qualifier: Optional[str] = Field(default=None, description="""Aspect qualifier for the object.""")
    object_direction_qualifier: Optional[str] = Field(default=None, description="""Direction qualifier for the object.""")
    upstream_data_source: Optional[List[str]] = Field(default=None, description="""Sources from which this entity's data originates.""")
    num_references: Optional[int] = Field(default=None, description="""Number of references supporting this edge.""")
    num_sentences: Optional[int] = Field(default=None, description="""Number of sentences supporting this edge.""")


class MatrixEdgeList(ConfiguredBaseModel):
    """
    A container for MatrixEdge objects.
    """
    edges: Optional[List[MatrixEdge]] = Field(default=None, description="""A list of edges.""")


class MatrixNodeList(ConfiguredBaseModel):
    """
    A container for MatrixNode objects.
    """
    nodes: Optional[List[MatrixNode]] = Field(default=None, description="""A list of edges.""")


class DiseaseListEntry(ConfiguredBaseModel):
    """
    A disease entry in the disease list.
    """
    category_class: str = Field(default=..., description="""The disase identifier. Slot name should probably be renamed?""")
    label: str = Field(default=..., description="""The name of the disease.""")
    definition: Optional[str] = Field(default=None, description="""The definition of the disease.""")
    synonyms: List[str] = Field(default=..., description="""Any exact synonyms of the disease.""")
    subsets: List[str] = Field(default=..., description="""The subsets of the disease in which it is part.""")
    crossreferences: List[str] = Field(default=..., description="""Cross-references to other databases and ontologies.""")
    is_matrix_manually_excluded: bool = Field(default=..., description="""Flag to denote this disease was manually excluded from the disease list by a Matrix medical expert.""")
    is_matrix_manually_included: bool = Field(default=..., description="""Flag to denote this disease was manually included from the disease list by a Matrix medical expert.""")
    is_clingen: bool = Field(default=..., description="""Flag to denote that this disease term is used directly by https://clinicalgenome.org/ (a major authority on genetic diseases), which is a strong indication that it corresponds to a real disease entity.""")
    is_grouping_subset: bool = Field(default=..., description="""Flag to denote this disease is manually curated to be a grouping term.""")
    is_grouping_subset_ancestor: bool = Field(default=..., description="""Flag to denote this disease is a parent of a disease that was manually curated to be a grouping term.""")
    is_orphanet_subtype: bool = Field(default=..., description="""Flag to denote this disease is manually curated to be a disease subtype according to Orphanet (https://www.orpha.net/), one of the most important rare disease authorities in the world.""")
    is_orphanet_subtype_descendant: bool = Field(default=..., description="""Flag to denote this disease is a child/descendant of a disease that is manually curated  to be a disease subtype according to Orphanet (https://www.orpha.net/), one of the most  important rare disease authorities in the world. If it is a descendant of a subtype, it most likely is a subtype itself.
""")
    is_omimps: bool = Field(default=..., description="""Flag to denote this disease is manually curated to be a phenotypic series according to OMIM (https://www.omim.org/),  one of the most important genetic disease authorities in the world.  A Phenotypic Series is a grouping of genetic heterogeneity of similar phenotypes across the genome.
""")
    is_omimps_descendant: bool = Field(default=..., description="""Flag to denote this disease is a child/descendant of a disease that is manually curated  to be a phenotypic series according to OMIM (https://www.omim.org/), one of the most  important genetic disease authorities in the world. If it is a descendant of a phenotypic series, it most likely is a proper genetic disease entity (or subtype).
""")
    is_leaf: bool = Field(default=..., description="""Flag to denote this disease is a leaf node in the disease hierarchy.  A leaf node is a node that has no children in the hierarchy.
""")
    is_leaf_direct_parent: bool = Field(default=..., description="""Flag to denote this disease is a direct parent of a leaf node in the disease hierarchy.  A direct parent of a leaf rarely corresponds to a grouping, and often is a proper disease entity.
""")
    is_orphanet_disorder: bool = Field(default=..., description="""Flag to denote this disease is manually curated to be a disease according to Orphanet (https://www.orpha.net/),  one of the most important rare disease authorities in the world.  A disorder according to Orphanet usually corresponds to a proper disease entity, not a grouping or a subtype.
""")
    is_omim: bool = Field(default=..., description="""Flag to denote this disease is manually curated to be a disease according to OMIM (https://www.omim.org/),  one of the most important genetic disease authorities in the world.  A disease according to OMIM usually corresponds to a proper disease entity or a subtype, not a disease grouping.
""")
    is_icd_category: bool = Field(default=..., description="""Flag to denote this disease was corresponds to an ICD category. Category codes (or subcategory codes), for example A01.1 (Paratyphoid fever A),  can be recognised by containing a period (.) character and usually represent specific  diagnosable diseases.
""")
    is_icd_chapter_code: bool = Field(default=..., description="""Flag to denote this disease was corresponds to an ICD chapter code. Chapter codes (or block codes), for example A00-B99 (Certain infectious and parasitic diseases).  These codes can be recognised by containing a dash (-) character, and usually represent broad categories of diseases.
""")
    is_icd_chapter_header: bool = Field(default=..., description="""Flag to denote this disease was corresponds to an ICD chapter header. Chapter headers (or chapter titles), for example A00 (Cholera) can be identified by codes without dashes or periods and are usually the top-level categories within each chapter. Most of the time, these are not proper diseases, but groupings of diseases.
""")
    is_icd_billable: bool = Field(default=..., description="""Flag to denote this disease was corresponds to an ICD code that is billable. Billable codes are usually the most specific codes that can be used for billing purposes, and are most of the time diagnosable diseases.
""")
    is_mondo_subtype: bool = Field(default=..., description="""Flag to denote this disease was identified to be a subtype through lexical matching. This method is maintained by the Every Cure medical team and the Disease List team.
""")
    is_pathway_defect: bool = Field(default=..., description="""Flag to denote this disease corresponds to a pathway defect rather than a proper disease.
""")
    is_susceptibility: bool = Field(default=..., description="""Flag to denote this disease corresponds to a susceptibility rather than a proper disease.
""")
    is_paraphilic: bool = Field(default=..., description="""Flag to denote this disease corresponds to a paraphilic disorder rather than a proper disease.
""")
    is_acquired: bool = Field(default=..., description="""Flag to denote this disease corresponds to an acquired form of a disease.
""")
    is_andor: bool = Field(default=..., description="""Flag to denote this disease corresponds to a disease that is a combination of two or more diseases.
""")
    is_withorwithout: bool = Field(default=..., description="""Flag to denote this disease corresponds to a disease that can be present with or without some other pathological condition.
""")
    is_obsoletion_candidate: bool = Field(default=..., description="""Flag to denote that this disease is marked for obsoletion in the (near) future. This status does not guarantee that the disease will be obsoleted, but it is a strong indication.
""")
    is_unclassified_hereditary: bool = Field(default=..., description="""Flag to denote that this disease has no descendants (is a leaf) and  is classified broadly as an hereditary disease, but lacks any further classification.
""")
    official_matrix_filter: bool = Field(default=..., description="""Flag to denote this disease corresponds to a disease that can be treated with small molecules or biologics. This flag is maintained as a combination of default filters by the Matrix team. Changes to this filter should be discussed on the Matrix disease list issue tracker (https://github.com/everycure-org/matrix-disease-list/issues). **Warning**. This flag is in early alpha state, and its use in production systems is not recommended.
""")
    harrisons_view: List[str] = Field(default=..., description="""Tag to denote this disease to be part of a grouping according to the Harrison's textbook. Top-level classes in Mondo are manually curated by the Mondo team to \"belong\" to a Harrison's textbook chapter. Disagreements should be reported on the Mondo issue tracker (https://github.com/monarch-initiative/mondo/issues).
""")
    mondo_txgnn: List[str] = Field(default=..., description="""Tag to denote this disease to be part of a grouping as defined by the txgnn paper. Disease classes in Mondo are manually curated by the Mondo team to \"belong\" to a txgnn category. Disagreements should be reported on the Mondo issue  tracker (https://github.com/monarch-initiative/mondo/issues).
""")
    mondo_top_grouping: List[str] = Field(default=..., description="""Tag to denote this disease to be a . Disease classes in Mondo are manually curated by the Mondo team to \"belong\" to a txgnn category. Disagreements should be reported on the Mondo issue  tracker (https://github.com/monarch-initiative/mondo/issues).
""")
    medical_specialization: List[str] = Field(default=..., description="""Tag this disease with a medical specialisation. Disease classes are automatically tagged by an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    txgnn: List[str] = Field(default=..., description="""Tag this disease to be part of a grouping as defined by the txgnn paper. Disease classes in Mondo are automatically assigned to a txgnn category using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    anatomical: List[str] = Field(default=..., description="""Tag to denote this disease to be part of a grouping according to the anatomical location. Disease terms are automatically tagged using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    is_pathogen_caused: bool = Field(default=..., description="""Flag to denote if this disease is caused by a pathogen. Disease classes are automatically flagged using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    is_cancer: bool = Field(default=..., description="""Flag to denote if this disease corresponds to a cancer type. Disease classes are automatically flagged using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    is_glucose_dysfunction: bool = Field(default=..., description="""Flag to denote if this disease corresponds to a glucose dysfunction. Disease classes are automatically flagged using an LLM. tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    tag_existing_treatment: bool = Field(default=..., description="""Flag to denote if this disease has some existing treatment. Disease classes are automatically flagged using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    tag_qaly_lost: str = Field(default=..., description="""Tag denoting the degree to which Quality-Adjusted Life Year (QALY) lost. Disease terms are automatically tagged using an LLM. Problems/issues should be reported on the Matrix disease list issue  tracker (https://github.com/everycure-org/matrix-disease-list/issues).
""")
    subset_group_id: Optional[str] = Field(default=None, description="""The identifier of a disease representing the subtype series this disease belongs to.""")
    subset_group_label: Optional[str] = Field(default=None, description="""The name (label) of a disease representing the subtype series this disease belongs to.""")
    other_subsets_count: Optional[int] = Field(default=None, description="""The number of other subtypes in the subset this disease belongs to.""")

    @field_validator('tag_qaly_lost')
    def pattern_tag_qaly_lost(cls, v):
        pattern=re.compile(r"^(low|medium|high|very_high|none)$")
        if isinstance(v,list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid tag_qaly_lost format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid tag_qaly_lost format: {v}")
        return v


class MatrixDiseaseList(ConfiguredBaseModel):
    """
    A list of diseases.
    """
    disease_list_entries: Optional[List[DiseaseListEntry]] = Field(default=None, description="""A list of disease list entries.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
MatrixNode.model_rebuild()
MatrixEdge.model_rebuild()
UnionedNode.model_rebuild()
UnionedEdge.model_rebuild()
MatrixEdgeList.model_rebuild()
MatrixNodeList.model_rebuild()
DiseaseListEntry.model_rebuild()
MatrixDiseaseList.model_rebuild()

