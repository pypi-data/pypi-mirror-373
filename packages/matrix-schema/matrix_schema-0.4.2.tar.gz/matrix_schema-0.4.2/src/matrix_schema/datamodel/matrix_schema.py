# Auto generated from matrix_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-08-26T11:42:20
# Schema: matrix-schema
#
# id: https://w3id.org/everycure-org/matrix-schema
# description: The collected MATRIX schemas
# license: BSD-3

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Boolean, Integer, String, Uriorcurie
from linkml_runtime.utils.metamodelcore import Bool, URIorCURIE

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
BIOLINK = CurieNamespace('biolink', 'https://w3id.org/biolink/vocab/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
MATRIX_SCHEMA = CurieNamespace('matrix_schema', 'https://w3id.org/everycure-org/matrix-schema/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = MATRIX_SCHEMA


# Types

# Class references
class MatrixNodeId(URIorCURIE):
    pass


class UnionedNodeId(MatrixNodeId):
    pass


@dataclass(repr=False)
class MatrixNode(YAMLRoot):
    """
    A node in the Biolink knowledge graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["MatrixNode"]
    class_class_curie: ClassVar[str] = "matrix_schema:MatrixNode"
    class_name: ClassVar[str] = "MatrixNode"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.MatrixNode

    id: Union[str, MatrixNodeId] = None
    category: Union[str, "NodeCategoryEnum"] = None
    name: Optional[str] = None
    description: Optional[str] = None
    equivalent_identifiers: Optional[Union[str, List[str]]] = empty_list()
    all_categories: Optional[Union[Union[str, "NodeCategoryEnum"], List[Union[str, "NodeCategoryEnum"]]]] = empty_list()
    publications: Optional[Union[str, List[str]]] = empty_list()
    labels: Optional[Union[str, List[str]]] = empty_list()
    international_resource_identifier: Optional[str] = None
    upstream_data_source: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, MatrixNodeId):
            self.id = MatrixNodeId(self.id)

        if self._is_empty(self.category):
            self.MissingRequiredField("category")
        if not isinstance(self.category, NodeCategoryEnum):
            self.category = NodeCategoryEnum(self.category)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.equivalent_identifiers, list):
            self.equivalent_identifiers = [self.equivalent_identifiers] if self.equivalent_identifiers is not None else []
        self.equivalent_identifiers = [v if isinstance(v, str) else str(v) for v in self.equivalent_identifiers]

        if not isinstance(self.all_categories, list):
            self.all_categories = [self.all_categories] if self.all_categories is not None else []
        self.all_categories = [v if isinstance(v, NodeCategoryEnum) else NodeCategoryEnum(v) for v in self.all_categories]

        if not isinstance(self.publications, list):
            self.publications = [self.publications] if self.publications is not None else []
        self.publications = [v if isinstance(v, str) else str(v) for v in self.publications]

        if not isinstance(self.labels, list):
            self.labels = [self.labels] if self.labels is not None else []
        self.labels = [v if isinstance(v, str) else str(v) for v in self.labels]

        if self.international_resource_identifier is not None and not isinstance(self.international_resource_identifier, str):
            self.international_resource_identifier = str(self.international_resource_identifier)

        if not isinstance(self.upstream_data_source, list):
            self.upstream_data_source = [self.upstream_data_source] if self.upstream_data_source is not None else []
        self.upstream_data_source = [v if isinstance(v, str) else str(v) for v in self.upstream_data_source]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MatrixEdge(YAMLRoot):
    """
    An edge representing a relationship between two nodes in the Biolink knowledge graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["MatrixEdge"]
    class_class_curie: ClassVar[str] = "matrix_schema:MatrixEdge"
    class_name: ClassVar[str] = "MatrixEdge"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.MatrixEdge

    subject: str = None
    predicate: Union[str, "PredicateEnum"] = None
    object: str = None
    knowledge_level: Optional[Union[str, "KnowledgeLevelEnum"]] = None
    agent_type: Optional[Union[str, "AgentTypeEnum"]] = None
    primary_knowledge_source: Optional[str] = None
    aggregator_knowledge_source: Optional[Union[str, List[str]]] = empty_list()
    publications: Optional[Union[str, List[str]]] = empty_list()
    subject_aspect_qualifier: Optional[str] = None
    subject_direction_qualifier: Optional[str] = None
    object_aspect_qualifier: Optional[str] = None
    object_direction_qualifier: Optional[str] = None
    upstream_data_source: Optional[Union[str, List[str]]] = empty_list()
    num_references: Optional[int] = None
    num_sentences: Optional[int] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.subject):
            self.MissingRequiredField("subject")
        if not isinstance(self.subject, str):
            self.subject = str(self.subject)

        if self._is_empty(self.predicate):
            self.MissingRequiredField("predicate")
        if not isinstance(self.predicate, PredicateEnum):
            self.predicate = PredicateEnum(self.predicate)

        if self._is_empty(self.object):
            self.MissingRequiredField("object")
        if not isinstance(self.object, str):
            self.object = str(self.object)

        if self.knowledge_level is not None and not isinstance(self.knowledge_level, KnowledgeLevelEnum):
            self.knowledge_level = KnowledgeLevelEnum(self.knowledge_level)

        if self.agent_type is not None and not isinstance(self.agent_type, AgentTypeEnum):
            self.agent_type = AgentTypeEnum(self.agent_type)

        if self.primary_knowledge_source is not None and not isinstance(self.primary_knowledge_source, str):
            self.primary_knowledge_source = str(self.primary_knowledge_source)

        if not isinstance(self.aggregator_knowledge_source, list):
            self.aggregator_knowledge_source = [self.aggregator_knowledge_source] if self.aggregator_knowledge_source is not None else []
        self.aggregator_knowledge_source = [v if isinstance(v, str) else str(v) for v in self.aggregator_knowledge_source]

        if not isinstance(self.publications, list):
            self.publications = [self.publications] if self.publications is not None else []
        self.publications = [v if isinstance(v, str) else str(v) for v in self.publications]

        if self.subject_aspect_qualifier is not None and not isinstance(self.subject_aspect_qualifier, str):
            self.subject_aspect_qualifier = str(self.subject_aspect_qualifier)

        if self.subject_direction_qualifier is not None and not isinstance(self.subject_direction_qualifier, str):
            self.subject_direction_qualifier = str(self.subject_direction_qualifier)

        if self.object_aspect_qualifier is not None and not isinstance(self.object_aspect_qualifier, str):
            self.object_aspect_qualifier = str(self.object_aspect_qualifier)

        if self.object_direction_qualifier is not None and not isinstance(self.object_direction_qualifier, str):
            self.object_direction_qualifier = str(self.object_direction_qualifier)

        if not isinstance(self.upstream_data_source, list):
            self.upstream_data_source = [self.upstream_data_source] if self.upstream_data_source is not None else []
        self.upstream_data_source = [v if isinstance(v, str) else str(v) for v in self.upstream_data_source]

        if self.num_references is not None and not isinstance(self.num_references, int):
            self.num_references = int(self.num_references)

        if self.num_sentences is not None and not isinstance(self.num_sentences, int):
            self.num_sentences = int(self.num_sentences)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class UnionedNode(MatrixNode):
    """
    A node in the unioned everycure matrix graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["UnionedNode"]
    class_class_curie: ClassVar[str] = "matrix_schema:UnionedNode"
    class_name: ClassVar[str] = "UnionedNode"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.UnionedNode

    id: Union[str, UnionedNodeId] = None
    category: Union[str, "NodeCategoryEnum"] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, UnionedNodeId):
            self.id = UnionedNodeId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class UnionedEdge(MatrixEdge):
    """
    An edge in the unioned everycure matrix graph.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["UnionedEdge"]
    class_class_curie: ClassVar[str] = "matrix_schema:UnionedEdge"
    class_name: ClassVar[str] = "UnionedEdge"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.UnionedEdge

    subject: str = None
    predicate: Union[str, "PredicateEnum"] = None
    object: str = None
    primary_knowledge_sources: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.primary_knowledge_sources, list):
            self.primary_knowledge_sources = [self.primary_knowledge_sources] if self.primary_knowledge_sources is not None else []
        self.primary_knowledge_sources = [v if isinstance(v, str) else str(v) for v in self.primary_knowledge_sources]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MatrixEdgeList(YAMLRoot):
    """
    A container for MatrixEdge objects.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["MatrixEdgeList"]
    class_class_curie: ClassVar[str] = "matrix_schema:MatrixEdgeList"
    class_name: ClassVar[str] = "MatrixEdgeList"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.MatrixEdgeList

    edges: Optional[Union[Union[dict, MatrixEdge], List[Union[dict, MatrixEdge]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.edges, list):
            self.edges = [self.edges] if self.edges is not None else []
        self.edges = [v if isinstance(v, MatrixEdge) else MatrixEdge(**as_dict(v)) for v in self.edges]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MatrixNodeList(YAMLRoot):
    """
    A container for MatrixNode objects.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["MatrixNodeList"]
    class_class_curie: ClassVar[str] = "matrix_schema:MatrixNodeList"
    class_name: ClassVar[str] = "MatrixNodeList"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.MatrixNodeList

    nodes: Optional[Union[Dict[Union[str, MatrixNodeId], Union[dict, MatrixNode]], List[Union[dict, MatrixNode]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="nodes", slot_type=MatrixNode, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DiseaseListEntry(YAMLRoot):
    """
    A disease entry in the disease list.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["DiseaseListEntry"]
    class_class_curie: ClassVar[str] = "matrix_schema:DiseaseListEntry"
    class_name: ClassVar[str] = "DiseaseListEntry"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.DiseaseListEntry

    category_class: str = None
    label: str = None
    synonyms: Union[str, List[str]] = None
    subsets: Union[str, List[str]] = None
    crossreferences: Union[str, List[str]] = None
    is_matrix_manually_excluded: Union[bool, Bool] = None
    is_matrix_manually_included: Union[bool, Bool] = None
    is_clingen: Union[bool, Bool] = None
    is_grouping_subset: Union[bool, Bool] = None
    is_grouping_subset_ancestor: Union[bool, Bool] = None
    is_orphanet_subtype: Union[bool, Bool] = None
    is_orphanet_subtype_descendant: Union[bool, Bool] = None
    is_omimps: Union[bool, Bool] = None
    is_omimps_descendant: Union[bool, Bool] = None
    is_leaf: Union[bool, Bool] = None
    is_leaf_direct_parent: Union[bool, Bool] = None
    is_orphanet_disorder: Union[bool, Bool] = None
    is_omim: Union[bool, Bool] = None
    is_icd_category: Union[bool, Bool] = None
    is_icd_chapter_code: Union[bool, Bool] = None
    is_icd_chapter_header: Union[bool, Bool] = None
    is_icd_billable: Union[bool, Bool] = None
    is_mondo_subtype: Union[bool, Bool] = None
    is_pathway_defect: Union[bool, Bool] = None
    is_susceptibility: Union[bool, Bool] = None
    is_paraphilic: Union[bool, Bool] = None
    is_acquired: Union[bool, Bool] = None
    is_andor: Union[bool, Bool] = None
    is_withorwithout: Union[bool, Bool] = None
    is_obsoletion_candidate: Union[bool, Bool] = None
    is_unclassified_hereditary: Union[bool, Bool] = None
    official_matrix_filter: Union[bool, Bool] = None
    harrisons_view: Union[str, List[str]] = None
    mondo_txgnn: Union[str, List[str]] = None
    mondo_top_grouping: Union[str, List[str]] = None
    medical_specialization: Union[str, List[str]] = None
    txgnn: Union[str, List[str]] = None
    anatomical: Union[str, List[str]] = None
    is_pathogen_caused: Union[bool, Bool] = None
    is_cancer: Union[bool, Bool] = None
    is_glucose_dysfunction: Union[bool, Bool] = None
    tag_existing_treatment: Union[bool, Bool] = None
    tag_qaly_lost: str = None
    definition: Optional[str] = None
    subset_group_id: Optional[str] = None
    subset_group_label: Optional[str] = None
    other_subsets_count: Optional[int] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.category_class):
            self.MissingRequiredField("category_class")
        if not isinstance(self.category_class, str):
            self.category_class = str(self.category_class)

        if self._is_empty(self.label):
            self.MissingRequiredField("label")
        if not isinstance(self.label, str):
            self.label = str(self.label)

        if self._is_empty(self.synonyms):
            self.MissingRequiredField("synonyms")
        if not isinstance(self.synonyms, list):
            self.synonyms = [self.synonyms] if self.synonyms is not None else []
        self.synonyms = [v if isinstance(v, str) else str(v) for v in self.synonyms]

        if self._is_empty(self.subsets):
            self.MissingRequiredField("subsets")
        if not isinstance(self.subsets, list):
            self.subsets = [self.subsets] if self.subsets is not None else []
        self.subsets = [v if isinstance(v, str) else str(v) for v in self.subsets]

        if self._is_empty(self.crossreferences):
            self.MissingRequiredField("crossreferences")
        if not isinstance(self.crossreferences, list):
            self.crossreferences = [self.crossreferences] if self.crossreferences is not None else []
        self.crossreferences = [v if isinstance(v, str) else str(v) for v in self.crossreferences]

        if self._is_empty(self.is_matrix_manually_excluded):
            self.MissingRequiredField("is_matrix_manually_excluded")
        if not isinstance(self.is_matrix_manually_excluded, Bool):
            self.is_matrix_manually_excluded = Bool(self.is_matrix_manually_excluded)

        if self._is_empty(self.is_matrix_manually_included):
            self.MissingRequiredField("is_matrix_manually_included")
        if not isinstance(self.is_matrix_manually_included, Bool):
            self.is_matrix_manually_included = Bool(self.is_matrix_manually_included)

        if self._is_empty(self.is_clingen):
            self.MissingRequiredField("is_clingen")
        if not isinstance(self.is_clingen, Bool):
            self.is_clingen = Bool(self.is_clingen)

        if self._is_empty(self.is_grouping_subset):
            self.MissingRequiredField("is_grouping_subset")
        if not isinstance(self.is_grouping_subset, Bool):
            self.is_grouping_subset = Bool(self.is_grouping_subset)

        if self._is_empty(self.is_grouping_subset_ancestor):
            self.MissingRequiredField("is_grouping_subset_ancestor")
        if not isinstance(self.is_grouping_subset_ancestor, Bool):
            self.is_grouping_subset_ancestor = Bool(self.is_grouping_subset_ancestor)

        if self._is_empty(self.is_orphanet_subtype):
            self.MissingRequiredField("is_orphanet_subtype")
        if not isinstance(self.is_orphanet_subtype, Bool):
            self.is_orphanet_subtype = Bool(self.is_orphanet_subtype)

        if self._is_empty(self.is_orphanet_subtype_descendant):
            self.MissingRequiredField("is_orphanet_subtype_descendant")
        if not isinstance(self.is_orphanet_subtype_descendant, Bool):
            self.is_orphanet_subtype_descendant = Bool(self.is_orphanet_subtype_descendant)

        if self._is_empty(self.is_omimps):
            self.MissingRequiredField("is_omimps")
        if not isinstance(self.is_omimps, Bool):
            self.is_omimps = Bool(self.is_omimps)

        if self._is_empty(self.is_omimps_descendant):
            self.MissingRequiredField("is_omimps_descendant")
        if not isinstance(self.is_omimps_descendant, Bool):
            self.is_omimps_descendant = Bool(self.is_omimps_descendant)

        if self._is_empty(self.is_leaf):
            self.MissingRequiredField("is_leaf")
        if not isinstance(self.is_leaf, Bool):
            self.is_leaf = Bool(self.is_leaf)

        if self._is_empty(self.is_leaf_direct_parent):
            self.MissingRequiredField("is_leaf_direct_parent")
        if not isinstance(self.is_leaf_direct_parent, Bool):
            self.is_leaf_direct_parent = Bool(self.is_leaf_direct_parent)

        if self._is_empty(self.is_orphanet_disorder):
            self.MissingRequiredField("is_orphanet_disorder")
        if not isinstance(self.is_orphanet_disorder, Bool):
            self.is_orphanet_disorder = Bool(self.is_orphanet_disorder)

        if self._is_empty(self.is_omim):
            self.MissingRequiredField("is_omim")
        if not isinstance(self.is_omim, Bool):
            self.is_omim = Bool(self.is_omim)

        if self._is_empty(self.is_icd_category):
            self.MissingRequiredField("is_icd_category")
        if not isinstance(self.is_icd_category, Bool):
            self.is_icd_category = Bool(self.is_icd_category)

        if self._is_empty(self.is_icd_chapter_code):
            self.MissingRequiredField("is_icd_chapter_code")
        if not isinstance(self.is_icd_chapter_code, Bool):
            self.is_icd_chapter_code = Bool(self.is_icd_chapter_code)

        if self._is_empty(self.is_icd_chapter_header):
            self.MissingRequiredField("is_icd_chapter_header")
        if not isinstance(self.is_icd_chapter_header, Bool):
            self.is_icd_chapter_header = Bool(self.is_icd_chapter_header)

        if self._is_empty(self.is_icd_billable):
            self.MissingRequiredField("is_icd_billable")
        if not isinstance(self.is_icd_billable, Bool):
            self.is_icd_billable = Bool(self.is_icd_billable)

        if self._is_empty(self.is_mondo_subtype):
            self.MissingRequiredField("is_mondo_subtype")
        if not isinstance(self.is_mondo_subtype, Bool):
            self.is_mondo_subtype = Bool(self.is_mondo_subtype)

        if self._is_empty(self.is_pathway_defect):
            self.MissingRequiredField("is_pathway_defect")
        if not isinstance(self.is_pathway_defect, Bool):
            self.is_pathway_defect = Bool(self.is_pathway_defect)

        if self._is_empty(self.is_susceptibility):
            self.MissingRequiredField("is_susceptibility")
        if not isinstance(self.is_susceptibility, Bool):
            self.is_susceptibility = Bool(self.is_susceptibility)

        if self._is_empty(self.is_paraphilic):
            self.MissingRequiredField("is_paraphilic")
        if not isinstance(self.is_paraphilic, Bool):
            self.is_paraphilic = Bool(self.is_paraphilic)

        if self._is_empty(self.is_acquired):
            self.MissingRequiredField("is_acquired")
        if not isinstance(self.is_acquired, Bool):
            self.is_acquired = Bool(self.is_acquired)

        if self._is_empty(self.is_andor):
            self.MissingRequiredField("is_andor")
        if not isinstance(self.is_andor, Bool):
            self.is_andor = Bool(self.is_andor)

        if self._is_empty(self.is_withorwithout):
            self.MissingRequiredField("is_withorwithout")
        if not isinstance(self.is_withorwithout, Bool):
            self.is_withorwithout = Bool(self.is_withorwithout)

        if self._is_empty(self.is_obsoletion_candidate):
            self.MissingRequiredField("is_obsoletion_candidate")
        if not isinstance(self.is_obsoletion_candidate, Bool):
            self.is_obsoletion_candidate = Bool(self.is_obsoletion_candidate)

        if self._is_empty(self.is_unclassified_hereditary):
            self.MissingRequiredField("is_unclassified_hereditary")
        if not isinstance(self.is_unclassified_hereditary, Bool):
            self.is_unclassified_hereditary = Bool(self.is_unclassified_hereditary)

        if self._is_empty(self.official_matrix_filter):
            self.MissingRequiredField("official_matrix_filter")
        if not isinstance(self.official_matrix_filter, Bool):
            self.official_matrix_filter = Bool(self.official_matrix_filter)

        if self._is_empty(self.harrisons_view):
            self.MissingRequiredField("harrisons_view")
        if not isinstance(self.harrisons_view, list):
            self.harrisons_view = [self.harrisons_view] if self.harrisons_view is not None else []
        self.harrisons_view = [v if isinstance(v, str) else str(v) for v in self.harrisons_view]

        if self._is_empty(self.mondo_txgnn):
            self.MissingRequiredField("mondo_txgnn")
        if not isinstance(self.mondo_txgnn, list):
            self.mondo_txgnn = [self.mondo_txgnn] if self.mondo_txgnn is not None else []
        self.mondo_txgnn = [v if isinstance(v, str) else str(v) for v in self.mondo_txgnn]

        if self._is_empty(self.mondo_top_grouping):
            self.MissingRequiredField("mondo_top_grouping")
        if not isinstance(self.mondo_top_grouping, list):
            self.mondo_top_grouping = [self.mondo_top_grouping] if self.mondo_top_grouping is not None else []
        self.mondo_top_grouping = [v if isinstance(v, str) else str(v) for v in self.mondo_top_grouping]

        if self._is_empty(self.medical_specialization):
            self.MissingRequiredField("medical_specialization")
        if not isinstance(self.medical_specialization, list):
            self.medical_specialization = [self.medical_specialization] if self.medical_specialization is not None else []
        self.medical_specialization = [v if isinstance(v, str) else str(v) for v in self.medical_specialization]

        if self._is_empty(self.txgnn):
            self.MissingRequiredField("txgnn")
        if not isinstance(self.txgnn, list):
            self.txgnn = [self.txgnn] if self.txgnn is not None else []
        self.txgnn = [v if isinstance(v, str) else str(v) for v in self.txgnn]

        if self._is_empty(self.anatomical):
            self.MissingRequiredField("anatomical")
        if not isinstance(self.anatomical, list):
            self.anatomical = [self.anatomical] if self.anatomical is not None else []
        self.anatomical = [v if isinstance(v, str) else str(v) for v in self.anatomical]

        if self._is_empty(self.is_pathogen_caused):
            self.MissingRequiredField("is_pathogen_caused")
        if not isinstance(self.is_pathogen_caused, Bool):
            self.is_pathogen_caused = Bool(self.is_pathogen_caused)

        if self._is_empty(self.is_cancer):
            self.MissingRequiredField("is_cancer")
        if not isinstance(self.is_cancer, Bool):
            self.is_cancer = Bool(self.is_cancer)

        if self._is_empty(self.is_glucose_dysfunction):
            self.MissingRequiredField("is_glucose_dysfunction")
        if not isinstance(self.is_glucose_dysfunction, Bool):
            self.is_glucose_dysfunction = Bool(self.is_glucose_dysfunction)

        if self._is_empty(self.tag_existing_treatment):
            self.MissingRequiredField("tag_existing_treatment")
        if not isinstance(self.tag_existing_treatment, Bool):
            self.tag_existing_treatment = Bool(self.tag_existing_treatment)

        if self._is_empty(self.tag_qaly_lost):
            self.MissingRequiredField("tag_qaly_lost")
        if not isinstance(self.tag_qaly_lost, str):
            self.tag_qaly_lost = str(self.tag_qaly_lost)

        if self.definition is not None and not isinstance(self.definition, str):
            self.definition = str(self.definition)

        if self.subset_group_id is not None and not isinstance(self.subset_group_id, str):
            self.subset_group_id = str(self.subset_group_id)

        if self.subset_group_label is not None and not isinstance(self.subset_group_label, str):
            self.subset_group_label = str(self.subset_group_label)

        if self.other_subsets_count is not None and not isinstance(self.other_subsets_count, int):
            self.other_subsets_count = int(self.other_subsets_count)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MatrixDiseaseList(YAMLRoot):
    """
    A list of diseases.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = MATRIX_SCHEMA["MatrixDiseaseList"]
    class_class_curie: ClassVar[str] = "matrix_schema:MatrixDiseaseList"
    class_name: ClassVar[str] = "MatrixDiseaseList"
    class_model_uri: ClassVar[URIRef] = MATRIX_SCHEMA.MatrixDiseaseList

    disease_list_entries: Optional[Union[Union[dict, DiseaseListEntry], List[Union[dict, DiseaseListEntry]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.disease_list_entries, list):
            self.disease_list_entries = [self.disease_list_entries] if self.disease_list_entries is not None else []
        self.disease_list_entries = [v if isinstance(v, DiseaseListEntry) else DiseaseListEntry(**as_dict(v)) for v in self.disease_list_entries]

        super().__post_init__(**kwargs)


# Enumerations
class PredicateEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="PredicateEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "biolink:related_to",
            PermissibleValue(text="biolink:related_to"))
        setattr(cls, "biolink:related_to_at_concept_level",
            PermissibleValue(text="biolink:related_to_at_concept_level"))
        setattr(cls, "biolink:related_to_at_instance_level",
            PermissibleValue(text="biolink:related_to_at_instance_level"))
        setattr(cls, "biolink:disease_has_location",
            PermissibleValue(text="biolink:disease_has_location"))
        setattr(cls, "biolink:location_of_disease",
            PermissibleValue(text="biolink:location_of_disease"))
        setattr(cls, "biolink:composed_primarily_of",
            PermissibleValue(text="biolink:composed_primarily_of"))
        setattr(cls, "biolink:primarily_composed_of",
            PermissibleValue(text="biolink:primarily_composed_of"))
        setattr(cls, "biolink:associated_with",
            PermissibleValue(text="biolink:associated_with"))
        setattr(cls, "biolink:opposite_of",
            PermissibleValue(text="biolink:opposite_of"))
        setattr(cls, "biolink:affects_likelihood_of",
            PermissibleValue(text="biolink:affects_likelihood_of"))
        setattr(cls, "biolink:likelihood_affected_by",
            PermissibleValue(text="biolink:likelihood_affected_by"))
        setattr(cls, "biolink:target_for",
            PermissibleValue(text="biolink:target_for"))
        setattr(cls, "biolink:has_target",
            PermissibleValue(text="biolink:has_target"))
        setattr(cls, "biolink:active_in",
            PermissibleValue(text="biolink:active_in"))
        setattr(cls, "biolink:has_active_component",
            PermissibleValue(text="biolink:has_active_component"))
        setattr(cls, "biolink:acts_upstream_of",
            PermissibleValue(text="biolink:acts_upstream_of"))
        setattr(cls, "biolink:has_upstream_actor",
            PermissibleValue(text="biolink:has_upstream_actor"))
        setattr(cls, "biolink:mentions",
            PermissibleValue(text="biolink:mentions"))
        setattr(cls, "biolink:mentioned_by",
            PermissibleValue(text="biolink:mentioned_by"))
        setattr(cls, "biolink:contributor",
            PermissibleValue(text="biolink:contributor"))
        setattr(cls, "biolink:has_contributor",
            PermissibleValue(text="biolink:has_contributor"))
        setattr(cls, "biolink:assesses",
            PermissibleValue(text="biolink:assesses"))
        setattr(cls, "biolink:is_assessed_by",
            PermissibleValue(text="biolink:is_assessed_by"))
        setattr(cls, "biolink:interacts_with",
            PermissibleValue(text="biolink:interacts_with"))
        setattr(cls, "biolink:affects",
            PermissibleValue(text="biolink:affects"))
        setattr(cls, "biolink:affected_by",
            PermissibleValue(text="biolink:affected_by"))
        setattr(cls, "biolink:diagnoses",
            PermissibleValue(text="biolink:diagnoses"))
        setattr(cls, "biolink:is_diagnosed_by",
            PermissibleValue(text="biolink:is_diagnosed_by"))
        setattr(cls, "biolink:increases_amount_or_activity_of",
            PermissibleValue(text="biolink:increases_amount_or_activity_of"))
        setattr(cls, "biolink:amount_or_activity_increased_by",
            PermissibleValue(text="biolink:amount_or_activity_increased_by"))
        setattr(cls, "biolink:decreases_amount_or_activity_of",
            PermissibleValue(text="biolink:decreases_amount_or_activity_of"))
        setattr(cls, "biolink:amount_or_activity_decreased_by",
            PermissibleValue(text="biolink:amount_or_activity_decreased_by"))
        setattr(cls, "biolink:gene_product_of",
            PermissibleValue(text="biolink:gene_product_of"))
        setattr(cls, "biolink:has_gene_product",
            PermissibleValue(text="biolink:has_gene_product"))
        setattr(cls, "biolink:transcribed_to",
            PermissibleValue(text="biolink:transcribed_to"))
        setattr(cls, "biolink:transcribed_from",
            PermissibleValue(text="biolink:transcribed_from"))
        setattr(cls, "biolink:translates_to",
            PermissibleValue(text="biolink:translates_to"))
        setattr(cls, "biolink:translation_of",
            PermissibleValue(text="biolink:translation_of"))
        setattr(cls, "biolink:coexists_with",
            PermissibleValue(text="biolink:coexists_with"))
        setattr(cls, "biolink:contributes_to",
            PermissibleValue(text="biolink:contributes_to"))
        setattr(cls, "biolink:contribution_from",
            PermissibleValue(text="biolink:contribution_from"))
        setattr(cls, "biolink:studied_to_treat",
            PermissibleValue(text="biolink:studied_to_treat"))
        setattr(cls, "biolink:applied_to_treat",
            PermissibleValue(text="biolink:applied_to_treat"))
        setattr(cls, "biolink:treatment_applications_from",
            PermissibleValue(text="biolink:treatment_applications_from"))
        setattr(cls, "biolink:treats_or_applied_or_studied_to_treat",
            PermissibleValue(text="biolink:treats_or_applied_or_studied_to_treat"))
        setattr(cls, "biolink:subject_of_treatment_application_or_study_for_treatment_by",
            PermissibleValue(text="biolink:subject_of_treatment_application_or_study_for_treatment_by"))
        setattr(cls, "biolink:has_phenotype",
            PermissibleValue(text="biolink:has_phenotype"))
        setattr(cls, "biolink:phenotype_of",
            PermissibleValue(text="biolink:phenotype_of"))
        setattr(cls, "biolink:occurs_in",
            PermissibleValue(text="biolink:occurs_in"))
        setattr(cls, "biolink:contains_process",
            PermissibleValue(text="biolink:contains_process"))
        setattr(cls, "biolink:located_in",
            PermissibleValue(text="biolink:located_in"))
        setattr(cls, "biolink:location_of",
            PermissibleValue(text="biolink:location_of"))
        setattr(cls, "biolink:similar_to",
            PermissibleValue(text="biolink:similar_to"))
        setattr(cls, "biolink:has_sequence_location",
            PermissibleValue(text="biolink:has_sequence_location"))
        setattr(cls, "biolink:sequence_location_of",
            PermissibleValue(text="biolink:sequence_location_of"))
        setattr(cls, "biolink:model_of",
            PermissibleValue(text="biolink:model_of"))
        setattr(cls, "biolink:models",
            PermissibleValue(text="biolink:models"))
        setattr(cls, "biolink:overlaps",
            PermissibleValue(text="biolink:overlaps"))
        setattr(cls, "biolink:has_participant",
            PermissibleValue(text="biolink:has_participant"))
        setattr(cls, "biolink:participates_in",
            PermissibleValue(text="biolink:participates_in"))
        setattr(cls, "biolink:derives_into",
            PermissibleValue(text="biolink:derives_into"))
        setattr(cls, "biolink:derives_from",
            PermissibleValue(text="biolink:derives_from"))
        setattr(cls, "biolink:manifestation_of",
            PermissibleValue(text="biolink:manifestation_of"))
        setattr(cls, "biolink:has_manifestation",
            PermissibleValue(text="biolink:has_manifestation"))
        setattr(cls, "biolink:produces",
            PermissibleValue(text="biolink:produces"))
        setattr(cls, "biolink:produced_by",
            PermissibleValue(text="biolink:produced_by"))
        setattr(cls, "biolink:temporally_related_to",
            PermissibleValue(text="biolink:temporally_related_to"))
        setattr(cls, "biolink:related_condition",
            PermissibleValue(text="biolink:related_condition"))
        setattr(cls, "biolink:is_sequence_variant_of",
            PermissibleValue(text="biolink:is_sequence_variant_of"))
        setattr(cls, "biolink:has_sequence_variant",
            PermissibleValue(text="biolink:has_sequence_variant"))
        setattr(cls, "biolink:disease_has_basis_in",
            PermissibleValue(text="biolink:disease_has_basis_in"))
        setattr(cls, "biolink:occurs_in_disease",
            PermissibleValue(text="biolink:occurs_in_disease"))
        setattr(cls, "biolink:contraindicated_in",
            PermissibleValue(text="biolink:contraindicated_in"))
        setattr(cls, "biolink:has_contraindication",
            PermissibleValue(text="biolink:has_contraindication"))
        setattr(cls, "biolink:has_not_completed",
            PermissibleValue(text="biolink:has_not_completed"))
        setattr(cls, "biolink:not_completed_by",
            PermissibleValue(text="biolink:not_completed_by"))
        setattr(cls, "biolink:has_completed",
            PermissibleValue(text="biolink:has_completed"))
        setattr(cls, "biolink:completed_by",
            PermissibleValue(text="biolink:completed_by"))
        setattr(cls, "biolink:in_linkage_disequilibrium_with",
            PermissibleValue(text="biolink:in_linkage_disequilibrium_with"))
        setattr(cls, "biolink:has_increased_amount",
            PermissibleValue(text="biolink:has_increased_amount"))
        setattr(cls, "biolink:increased_amount_of",
            PermissibleValue(text="biolink:increased_amount_of"))
        setattr(cls, "biolink:has_decreased_amount",
            PermissibleValue(text="biolink:has_decreased_amount"))
        setattr(cls, "biolink:decreased_amount_in",
            PermissibleValue(text="biolink:decreased_amount_in"))
        setattr(cls, "biolink:lacks_part",
            PermissibleValue(text="biolink:lacks_part"))
        setattr(cls, "biolink:missing_from",
            PermissibleValue(text="biolink:missing_from"))
        setattr(cls, "biolink:develops_from",
            PermissibleValue(text="biolink:develops_from"))
        setattr(cls, "biolink:develops_into",
            PermissibleValue(text="biolink:develops_into"))
        setattr(cls, "biolink:in_taxon",
            PermissibleValue(text="biolink:in_taxon"))
        setattr(cls, "biolink:taxon_of",
            PermissibleValue(text="biolink:taxon_of"))
        setattr(cls, "biolink:has_molecular_consequence",
            PermissibleValue(text="biolink:has_molecular_consequence"))
        setattr(cls, "biolink:is_molecular_consequence_of",
            PermissibleValue(text="biolink:is_molecular_consequence_of"))
        setattr(cls, "biolink:has_missense_variant",
            PermissibleValue(text="biolink:has_missense_variant"))
        setattr(cls, "biolink:has_synonymous_variant",
            PermissibleValue(text="biolink:has_synonymous_variant"))
        setattr(cls, "biolink:has_nonsense_variant",
            PermissibleValue(text="biolink:has_nonsense_variant"))
        setattr(cls, "biolink:has_frameshift_variant",
            PermissibleValue(text="biolink:has_frameshift_variant"))
        setattr(cls, "biolink:has_splice_site_variant",
            PermissibleValue(text="biolink:has_splice_site_variant"))
        setattr(cls, "biolink:has_nearby_variant",
            PermissibleValue(text="biolink:has_nearby_variant"))
        setattr(cls, "biolink:has_non_coding_variant",
            PermissibleValue(text="biolink:has_non_coding_variant"))
        setattr(cls, "biolink:is_missense_variant_of",
            PermissibleValue(text="biolink:is_missense_variant_of"))
        setattr(cls, "biolink:is_synonymous_variant_of",
            PermissibleValue(text="biolink:is_synonymous_variant_of"))
        setattr(cls, "biolink:is_nonsense_variant_of",
            PermissibleValue(text="biolink:is_nonsense_variant_of"))
        setattr(cls, "biolink:is_frameshift_variant_of",
            PermissibleValue(text="biolink:is_frameshift_variant_of"))
        setattr(cls, "biolink:is_splice_site_variant_of",
            PermissibleValue(text="biolink:is_splice_site_variant_of"))
        setattr(cls, "biolink:is_nearby_variant_of",
            PermissibleValue(text="biolink:is_nearby_variant_of"))
        setattr(cls, "biolink:is_non_coding_variant_of",
            PermissibleValue(text="biolink:is_non_coding_variant_of"))
        setattr(cls, "biolink:precedes",
            PermissibleValue(text="biolink:precedes"))
        setattr(cls, "biolink:preceded_by",
            PermissibleValue(text="biolink:preceded_by"))
        setattr(cls, "biolink:has_mode_of_inheritance",
            PermissibleValue(text="biolink:has_mode_of_inheritance"))
        setattr(cls, "biolink:mode_of_inheritance_of",
            PermissibleValue(text="biolink:mode_of_inheritance_of"))
        setattr(cls, "biolink:is_metabolite_of",
            PermissibleValue(text="biolink:is_metabolite_of"))
        setattr(cls, "biolink:has_metabolite",
            PermissibleValue(text="biolink:has_metabolite"))
        setattr(cls, "biolink:is_input_of",
            PermissibleValue(text="biolink:is_input_of"))
        setattr(cls, "biolink:is_output_of",
            PermissibleValue(text="biolink:is_output_of"))
        setattr(cls, "biolink:catalyzes",
            PermissibleValue(text="biolink:catalyzes"))
        setattr(cls, "biolink:is_substrate_of",
            PermissibleValue(text="biolink:is_substrate_of"))
        setattr(cls, "biolink:actively_involved_in",
            PermissibleValue(text="biolink:actively_involved_in"))
        setattr(cls, "biolink:enables",
            PermissibleValue(text="biolink:enables"))
        setattr(cls, "biolink:capable_of",
            PermissibleValue(text="biolink:capable_of"))
        setattr(cls, "biolink:consumed_by",
            PermissibleValue(text="biolink:consumed_by"))
        setattr(cls, "biolink:has_input",
            PermissibleValue(text="biolink:has_input"))
        setattr(cls, "biolink:has_output",
            PermissibleValue(text="biolink:has_output"))
        setattr(cls, "biolink:has_catalyst",
            PermissibleValue(text="biolink:has_catalyst"))
        setattr(cls, "biolink:has_substrate",
            PermissibleValue(text="biolink:has_substrate"))
        setattr(cls, "biolink:actively_involves",
            PermissibleValue(text="biolink:actively_involves"))
        setattr(cls, "biolink:enabled_by",
            PermissibleValue(text="biolink:enabled_by"))
        setattr(cls, "biolink:can_be_carried_out_by",
            PermissibleValue(text="biolink:can_be_carried_out_by"))
        setattr(cls, "biolink:consumes",
            PermissibleValue(text="biolink:consumes"))
        setattr(cls, "biolink:has_part",
            PermissibleValue(text="biolink:has_part"))
        setattr(cls, "biolink:part_of",
            PermissibleValue(text="biolink:part_of"))
        setattr(cls, "biolink:plasma_membrane_part_of",
            PermissibleValue(text="biolink:plasma_membrane_part_of"))
        setattr(cls, "biolink:food_component_of",
            PermissibleValue(text="biolink:food_component_of"))
        setattr(cls, "biolink:is_active_ingredient_of",
            PermissibleValue(text="biolink:is_active_ingredient_of"))
        setattr(cls, "biolink:is_excipient_of",
            PermissibleValue(text="biolink:is_excipient_of"))
        setattr(cls, "biolink:variant_part_of",
            PermissibleValue(text="biolink:variant_part_of"))
        setattr(cls, "biolink:nutrient_of",
            PermissibleValue(text="biolink:nutrient_of"))
        setattr(cls, "biolink:has_plasma_membrane_part",
            PermissibleValue(text="biolink:has_plasma_membrane_part"))
        setattr(cls, "biolink:has_food_component",
            PermissibleValue(text="biolink:has_food_component"))
        setattr(cls, "biolink:has_active_ingredient",
            PermissibleValue(text="biolink:has_active_ingredient"))
        setattr(cls, "biolink:has_excipient",
            PermissibleValue(text="biolink:has_excipient"))
        setattr(cls, "biolink:has_variant_part",
            PermissibleValue(text="biolink:has_variant_part"))
        setattr(cls, "biolink:has_nutrient",
            PermissibleValue(text="biolink:has_nutrient"))
        setattr(cls, "biolink:homologous_to",
            PermissibleValue(text="biolink:homologous_to"))
        setattr(cls, "biolink:chemically_similar_to",
            PermissibleValue(text="biolink:chemically_similar_to"))
        setattr(cls, "biolink:paralogous_to",
            PermissibleValue(text="biolink:paralogous_to"))
        setattr(cls, "biolink:orthologous_to",
            PermissibleValue(text="biolink:orthologous_to"))
        setattr(cls, "biolink:xenologous_to",
            PermissibleValue(text="biolink:xenologous_to"))
        setattr(cls, "biolink:expresses",
            PermissibleValue(text="biolink:expresses"))
        setattr(cls, "biolink:expressed_in",
            PermissibleValue(text="biolink:expressed_in"))
        setattr(cls, "biolink:treated_by",
            PermissibleValue(text="biolink:treated_by"))
        setattr(cls, "biolink:tested_by_clinical_trials_of",
            PermissibleValue(text="biolink:tested_by_clinical_trials_of"))
        setattr(cls, "biolink:treated_in_studies_by",
            PermissibleValue(text="biolink:treated_in_studies_by"))
        setattr(cls, "biolink:tested_by_preclinical_trials_of",
            PermissibleValue(text="biolink:tested_by_preclinical_trials_of"))
        setattr(cls, "biolink:models_demonstrating_benefits_for",
            PermissibleValue(text="biolink:models_demonstrating_benefits_for"))
        setattr(cls, "biolink:treats",
            PermissibleValue(text="biolink:treats"))
        setattr(cls, "biolink:in_clinical_trials_for",
            PermissibleValue(text="biolink:in_clinical_trials_for"))
        setattr(cls, "biolink:in_preclinical_trials_for",
            PermissibleValue(text="biolink:in_preclinical_trials_for"))
        setattr(cls, "biolink:beneficial_in_models_for",
            PermissibleValue(text="biolink:beneficial_in_models_for"))
        setattr(cls, "biolink:ameliorates_condition",
            PermissibleValue(text="biolink:ameliorates_condition"))
        setattr(cls, "biolink:preventative_for_condition",
            PermissibleValue(text="biolink:preventative_for_condition"))
        setattr(cls, "biolink:caused_by",
            PermissibleValue(text="biolink:caused_by"))
        setattr(cls, "biolink:causes",
            PermissibleValue(text="biolink:causes"))
        setattr(cls, "biolink:in_pathway_with",
            PermissibleValue(text="biolink:in_pathway_with"))
        setattr(cls, "biolink:in_complex_with",
            PermissibleValue(text="biolink:in_complex_with"))
        setattr(cls, "biolink:in_cell_population_with",
            PermissibleValue(text="biolink:in_cell_population_with"))
        setattr(cls, "biolink:colocalizes_with",
            PermissibleValue(text="biolink:colocalizes_with"))
        setattr(cls, "biolink:response_affected_by",
            PermissibleValue(text="biolink:response_affected_by"))
        setattr(cls, "biolink:regulated_by",
            PermissibleValue(text="biolink:regulated_by"))
        setattr(cls, "biolink:disrupted_by",
            PermissibleValue(text="biolink:disrupted_by"))
        setattr(cls, "biolink:condition_ameliorated_by",
            PermissibleValue(text="biolink:condition_ameliorated_by"))
        setattr(cls, "biolink:condition_prevented_by",
            PermissibleValue(text="biolink:condition_prevented_by"))
        setattr(cls, "biolink:condition_exacerbated_by",
            PermissibleValue(text="biolink:condition_exacerbated_by"))
        setattr(cls, "biolink:adverse_event_of",
            PermissibleValue(text="biolink:adverse_event_of"))
        setattr(cls, "biolink:is_side_effect_of",
            PermissibleValue(text="biolink:is_side_effect_of"))
        setattr(cls, "biolink:response_increased_by",
            PermissibleValue(text="biolink:response_increased_by"))
        setattr(cls, "biolink:response_decreased_by",
            PermissibleValue(text="biolink:response_decreased_by"))
        setattr(cls, "biolink:affects_response_to",
            PermissibleValue(text="biolink:affects_response_to"))
        setattr(cls, "biolink:regulates",
            PermissibleValue(text="biolink:regulates"))
        setattr(cls, "biolink:disrupts",
            PermissibleValue(text="biolink:disrupts"))
        setattr(cls, "biolink:exacerbates_condition",
            PermissibleValue(text="biolink:exacerbates_condition"))
        setattr(cls, "biolink:has_adverse_event",
            PermissibleValue(text="biolink:has_adverse_event"))
        setattr(cls, "biolink:has_side_effect",
            PermissibleValue(text="biolink:has_side_effect"))
        setattr(cls, "biolink:increases_response_to",
            PermissibleValue(text="biolink:increases_response_to"))
        setattr(cls, "biolink:decreases_response_to",
            PermissibleValue(text="biolink:decreases_response_to"))
        setattr(cls, "biolink:physically_interacts_with",
            PermissibleValue(text="biolink:physically_interacts_with"))
        setattr(cls, "biolink:genetically_interacts_with",
            PermissibleValue(text="biolink:genetically_interacts_with"))
        setattr(cls, "biolink:gene_fusion_with",
            PermissibleValue(text="biolink:gene_fusion_with"))
        setattr(cls, "biolink:genetic_neighborhood_of",
            PermissibleValue(text="biolink:genetic_neighborhood_of"))
        setattr(cls, "biolink:directly_physically_interacts_with",
            PermissibleValue(text="biolink:directly_physically_interacts_with"))
        setattr(cls, "biolink:indirectly_physically_interacts_with",
            PermissibleValue(text="biolink:indirectly_physically_interacts_with"))
        setattr(cls, "biolink:binds",
            PermissibleValue(text="biolink:binds"))
        setattr(cls, "biolink:has_provider",
            PermissibleValue(text="biolink:has_provider"))
        setattr(cls, "biolink:has_publisher",
            PermissibleValue(text="biolink:has_publisher"))
        setattr(cls, "biolink:has_editor",
            PermissibleValue(text="biolink:has_editor"))
        setattr(cls, "biolink:has_author",
            PermissibleValue(text="biolink:has_author"))
        setattr(cls, "biolink:provider",
            PermissibleValue(text="biolink:provider"))
        setattr(cls, "biolink:publisher",
            PermissibleValue(text="biolink:publisher"))
        setattr(cls, "biolink:editor",
            PermissibleValue(text="biolink:editor"))
        setattr(cls, "biolink:author",
            PermissibleValue(text="biolink:author"))
        setattr(cls, "biolink:has_positive_upstream_actor",
            PermissibleValue(text="biolink:has_positive_upstream_actor"))
        setattr(cls, "biolink:has_negative_upstream_actor",
            PermissibleValue(text="biolink:has_negative_upstream_actor"))
        setattr(cls, "biolink:has_upstream_or_within_actor",
            PermissibleValue(text="biolink:has_upstream_or_within_actor"))
        setattr(cls, "biolink:has_positive_upstream_or_within_actor",
            PermissibleValue(text="biolink:has_positive_upstream_or_within_actor"))
        setattr(cls, "biolink:has_negative_upstream_or_within_actor",
            PermissibleValue(text="biolink:has_negative_upstream_or_within_actor"))
        setattr(cls, "biolink:acts_upstream_of_positive_effect",
            PermissibleValue(text="biolink:acts_upstream_of_positive_effect"))
        setattr(cls, "biolink:acts_upstream_of_negative_effect",
            PermissibleValue(text="biolink:acts_upstream_of_negative_effect"))
        setattr(cls, "biolink:acts_upstream_of_or_within",
            PermissibleValue(text="biolink:acts_upstream_of_or_within"))
        setattr(cls, "biolink:acts_upstream_of_or_within_positive_effect",
            PermissibleValue(text="biolink:acts_upstream_of_or_within_positive_effect"))
        setattr(cls, "biolink:acts_upstream_of_or_within_negative_effect",
            PermissibleValue(text="biolink:acts_upstream_of_or_within_negative_effect"))
        setattr(cls, "biolink:condition_promoted_by",
            PermissibleValue(text="biolink:condition_promoted_by"))
        setattr(cls, "biolink:condition_predisposed_by",
            PermissibleValue(text="biolink:condition_predisposed_by"))
        setattr(cls, "biolink:promotes_condition",
            PermissibleValue(text="biolink:promotes_condition"))
        setattr(cls, "biolink:predisposes_to_condition",
            PermissibleValue(text="biolink:predisposes_to_condition"))
        setattr(cls, "biolink:associated_with_likelihood_of",
            PermissibleValue(text="biolink:associated_with_likelihood_of"))
        setattr(cls, "biolink:likelihood_associated_with",
            PermissibleValue(text="biolink:likelihood_associated_with"))
        setattr(cls, "biolink:associated_with_sensitivity_to",
            PermissibleValue(text="biolink:associated_with_sensitivity_to"))
        setattr(cls, "biolink:sensitivity_associated_with",
            PermissibleValue(text="biolink:sensitivity_associated_with"))
        setattr(cls, "biolink:associated_with_resistance_to",
            PermissibleValue(text="biolink:associated_with_resistance_to"))
        setattr(cls, "biolink:resistance_associated_with",
            PermissibleValue(text="biolink:resistance_associated_with"))
        setattr(cls, "biolink:genetic_association",
            PermissibleValue(text="biolink:genetic_association"))
        setattr(cls, "biolink:genetically_associated_with",
            PermissibleValue(text="biolink:genetically_associated_with"))
        setattr(cls, "biolink:correlated_with",
            PermissibleValue(text="biolink:correlated_with"))
        setattr(cls, "biolink:positively_correlated_with",
            PermissibleValue(text="biolink:positively_correlated_with"))
        setattr(cls, "biolink:negatively_correlated_with",
            PermissibleValue(text="biolink:negatively_correlated_with"))
        setattr(cls, "biolink:occurs_together_in_literature_with",
            PermissibleValue(text="biolink:occurs_together_in_literature_with"))
        setattr(cls, "biolink:coexpressed_with",
            PermissibleValue(text="biolink:coexpressed_with"))
        setattr(cls, "biolink:has_biomarker",
            PermissibleValue(text="biolink:has_biomarker"))
        setattr(cls, "biolink:biomarker_for",
            PermissibleValue(text="biolink:biomarker_for"))
        setattr(cls, "biolink:gene_associated_with_condition",
            PermissibleValue(text="biolink:gene_associated_with_condition"))
        setattr(cls, "biolink:condition_associated_with_gene",
            PermissibleValue(text="biolink:condition_associated_with_gene"))
        setattr(cls, "biolink:increased_likelihood_associated_with",
            PermissibleValue(text="biolink:increased_likelihood_associated_with"))
        setattr(cls, "biolink:decreased_likelihood_associated_with",
            PermissibleValue(text="biolink:decreased_likelihood_associated_with"))
        setattr(cls, "biolink:associated_with_increased_likelihood_of",
            PermissibleValue(text="biolink:associated_with_increased_likelihood_of"))
        setattr(cls, "biolink:associated_with_decreased_likelihood_of",
            PermissibleValue(text="biolink:associated_with_decreased_likelihood_of"))
        setattr(cls, "biolink:has_chemical_role",
            PermissibleValue(text="biolink:has_chemical_role"))
        setattr(cls, "biolink:superclass_of",
            PermissibleValue(text="biolink:superclass_of"))
        setattr(cls, "biolink:subclass_of",
            PermissibleValue(text="biolink:subclass_of"))
        setattr(cls, "biolink:close_match",
            PermissibleValue(text="biolink:close_match"))
        setattr(cls, "biolink:broad_match",
            PermissibleValue(text="biolink:broad_match"))
        setattr(cls, "biolink:narrow_match",
            PermissibleValue(text="biolink:narrow_match"))
        setattr(cls, "biolink:member_of",
            PermissibleValue(text="biolink:member_of"))
        setattr(cls, "biolink:has_member",
            PermissibleValue(text="biolink:has_member"))
        setattr(cls, "biolink:exact_match",
            PermissibleValue(text="biolink:exact_match"))
        setattr(cls, "biolink:same_as",
            PermissibleValue(text="biolink:same_as"))

class NodeCategoryEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="NodeCategoryEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "biolink:NamedThing",
            PermissibleValue(text="biolink:NamedThing"))
        setattr(cls, "biolink:Attribute",
            PermissibleValue(text="biolink:Attribute"))
        setattr(cls, "biolink:OrganismTaxon",
            PermissibleValue(text="biolink:OrganismTaxon"))
        setattr(cls, "biolink:Event",
            PermissibleValue(text="biolink:Event"))
        setattr(cls, "biolink:AdministrativeEntity",
            PermissibleValue(text="biolink:AdministrativeEntity"))
        setattr(cls, "biolink:InformationContentEntity",
            PermissibleValue(text="biolink:InformationContentEntity"))
        setattr(cls, "biolink:PhysicalEntity",
            PermissibleValue(text="biolink:PhysicalEntity"))
        setattr(cls, "biolink:Activity",
            PermissibleValue(text="biolink:Activity"))
        setattr(cls, "biolink:Procedure",
            PermissibleValue(text="biolink:Procedure"))
        setattr(cls, "biolink:Phenomenon",
            PermissibleValue(text="biolink:Phenomenon"))
        setattr(cls, "biolink:Device",
            PermissibleValue(text="biolink:Device"))
        setattr(cls, "biolink:DiagnosticAid",
            PermissibleValue(text="biolink:DiagnosticAid"))
        setattr(cls, "biolink:PlanetaryEntity",
            PermissibleValue(text="biolink:PlanetaryEntity"))
        setattr(cls, "biolink:BiologicalEntity",
            PermissibleValue(text="biolink:BiologicalEntity"))
        setattr(cls, "biolink:ChemicalEntity",
            PermissibleValue(text="biolink:ChemicalEntity"))
        setattr(cls, "biolink:ClinicalEntity",
            PermissibleValue(text="biolink:ClinicalEntity"))
        setattr(cls, "biolink:Treatment",
            PermissibleValue(text="biolink:Treatment"))
        setattr(cls, "biolink:ClinicalTrial",
            PermissibleValue(text="biolink:ClinicalTrial"))
        setattr(cls, "biolink:ClinicalIntervention",
            PermissibleValue(text="biolink:ClinicalIntervention"))
        setattr(cls, "biolink:Hospitalization",
            PermissibleValue(text="biolink:Hospitalization"))
        setattr(cls, "biolink:MolecularEntity",
            PermissibleValue(text="biolink:MolecularEntity"))
        setattr(cls, "biolink:ChemicalMixture",
            PermissibleValue(text="biolink:ChemicalMixture"))
        setattr(cls, "biolink:EnvironmentalFoodContaminant",
            PermissibleValue(text="biolink:EnvironmentalFoodContaminant"))
        setattr(cls, "biolink:FoodAdditive",
            PermissibleValue(text="biolink:FoodAdditive"))
        setattr(cls, "biolink:MolecularMixture",
            PermissibleValue(text="biolink:MolecularMixture"))
        setattr(cls, "biolink:ComplexMolecularMixture",
            PermissibleValue(text="biolink:ComplexMolecularMixture"))
        setattr(cls, "biolink:ProcessedMaterial",
            PermissibleValue(text="biolink:ProcessedMaterial"))
        setattr(cls, "biolink:Food",
            PermissibleValue(text="biolink:Food"))
        setattr(cls, "biolink:Drug",
            PermissibleValue(text="biolink:Drug"))
        setattr(cls, "biolink:SmallMolecule",
            PermissibleValue(text="biolink:SmallMolecule"))
        setattr(cls, "biolink:NucleicAcidEntity",
            PermissibleValue(text="biolink:NucleicAcidEntity"))
        setattr(cls, "biolink:RegulatoryRegion",
            PermissibleValue(text="biolink:RegulatoryRegion"))
        setattr(cls, "biolink:BiologicalProcessOrActivity",
            PermissibleValue(text="biolink:BiologicalProcessOrActivity"))
        setattr(cls, "biolink:GeneticInheritance",
            PermissibleValue(text="biolink:GeneticInheritance"))
        setattr(cls, "biolink:OrganismalEntity",
            PermissibleValue(text="biolink:OrganismalEntity"))
        setattr(cls, "biolink:DiseaseOrPhenotypicFeature",
            PermissibleValue(text="biolink:DiseaseOrPhenotypicFeature"))
        setattr(cls, "biolink:Gene",
            PermissibleValue(text="biolink:Gene"))
        setattr(cls, "biolink:MacromolecularComplex",
            PermissibleValue(text="biolink:MacromolecularComplex"))
        setattr(cls, "biolink:NucleosomeModification",
            PermissibleValue(text="biolink:NucleosomeModification"))
        setattr(cls, "biolink:Genome",
            PermissibleValue(text="biolink:Genome"))
        setattr(cls, "biolink:Exon",
            PermissibleValue(text="biolink:Exon"))
        setattr(cls, "biolink:Transcript",
            PermissibleValue(text="biolink:Transcript"))
        setattr(cls, "biolink:CodingSequence",
            PermissibleValue(text="biolink:CodingSequence"))
        setattr(cls, "biolink:Polypeptide",
            PermissibleValue(text="biolink:Polypeptide"))
        setattr(cls, "biolink:ProteinDomain",
            PermissibleValue(text="biolink:ProteinDomain"))
        setattr(cls, "biolink:PosttranslationalModification",
            PermissibleValue(text="biolink:PosttranslationalModification"))
        setattr(cls, "biolink:ProteinFamily",
            PermissibleValue(text="biolink:ProteinFamily"))
        setattr(cls, "biolink:NucleicAcidSequenceMotif",
            PermissibleValue(text="biolink:NucleicAcidSequenceMotif"))
        setattr(cls, "biolink:GeneFamily",
            PermissibleValue(text="biolink:GeneFamily"))
        setattr(cls, "biolink:Genotype",
            PermissibleValue(text="biolink:Genotype"))
        setattr(cls, "biolink:Haplotype",
            PermissibleValue(text="biolink:Haplotype"))
        setattr(cls, "biolink:SequenceVariant",
            PermissibleValue(text="biolink:SequenceVariant"))
        setattr(cls, "biolink:ReagentTargetedGene",
            PermissibleValue(text="biolink:ReagentTargetedGene"))
        setattr(cls, "biolink:Snv",
            PermissibleValue(text="biolink:Snv"))
        setattr(cls, "biolink:Protein",
            PermissibleValue(text="biolink:Protein"))
        setattr(cls, "biolink:ProteinIsoform",
            PermissibleValue(text="biolink:ProteinIsoform"))
        setattr(cls, "biolink:RNAProduct",
            PermissibleValue(text="biolink:RNAProduct"))
        setattr(cls, "biolink:RNAProductIsoform",
            PermissibleValue(text="biolink:RNAProductIsoform"))
        setattr(cls, "biolink:NoncodingRNAProduct",
            PermissibleValue(text="biolink:NoncodingRNAProduct"))
        setattr(cls, "biolink:MicroRNA",
            PermissibleValue(text="biolink:MicroRNA"))
        setattr(cls, "biolink:SiRNA",
            PermissibleValue(text="biolink:SiRNA"))
        setattr(cls, "biolink:Disease",
            PermissibleValue(text="biolink:Disease"))
        setattr(cls, "biolink:PhenotypicFeature",
            PermissibleValue(text="biolink:PhenotypicFeature"))
        setattr(cls, "biolink:BehavioralFeature",
            PermissibleValue(text="biolink:BehavioralFeature"))
        setattr(cls, "biolink:ClinicalFinding",
            PermissibleValue(text="biolink:ClinicalFinding"))
        setattr(cls, "biolink:Bacterium",
            PermissibleValue(text="biolink:Bacterium"))
        setattr(cls, "biolink:Virus",
            PermissibleValue(text="biolink:Virus"))
        setattr(cls, "biolink:CellularOrganism",
            PermissibleValue(text="biolink:CellularOrganism"))
        setattr(cls, "biolink:LifeStage",
            PermissibleValue(text="biolink:LifeStage"))
        setattr(cls, "biolink:IndividualOrganism",
            PermissibleValue(text="biolink:IndividualOrganism"))
        setattr(cls, "biolink:PopulationOfIndividualOrganisms",
            PermissibleValue(text="biolink:PopulationOfIndividualOrganisms"))
        setattr(cls, "biolink:AnatomicalEntity",
            PermissibleValue(text="biolink:AnatomicalEntity"))
        setattr(cls, "biolink:CellLine",
            PermissibleValue(text="biolink:CellLine"))
        setattr(cls, "biolink:CellularComponent",
            PermissibleValue(text="biolink:CellularComponent"))
        setattr(cls, "biolink:Cell",
            PermissibleValue(text="biolink:Cell"))
        setattr(cls, "biolink:GrossAnatomicalStructure",
            PermissibleValue(text="biolink:GrossAnatomicalStructure"))
        setattr(cls, "biolink:PathologicalAnatomicalStructure",
            PermissibleValue(text="biolink:PathologicalAnatomicalStructure"))
        setattr(cls, "biolink:StudyPopulation",
            PermissibleValue(text="biolink:StudyPopulation"))
        setattr(cls, "biolink:Cohort",
            PermissibleValue(text="biolink:Cohort"))
        setattr(cls, "biolink:Case",
            PermissibleValue(text="biolink:Case"))
        setattr(cls, "biolink:Mammal",
            PermissibleValue(text="biolink:Mammal"))
        setattr(cls, "biolink:Plant",
            PermissibleValue(text="biolink:Plant"))
        setattr(cls, "biolink:Invertebrate",
            PermissibleValue(text="biolink:Invertebrate"))
        setattr(cls, "biolink:Vertebrate",
            PermissibleValue(text="biolink:Vertebrate"))
        setattr(cls, "biolink:Fungus",
            PermissibleValue(text="biolink:Fungus"))
        setattr(cls, "biolink:Human",
            PermissibleValue(text="biolink:Human"))
        setattr(cls, "biolink:MolecularActivity",
            PermissibleValue(text="biolink:MolecularActivity"))
        setattr(cls, "biolink:BiologicalProcess",
            PermissibleValue(text="biolink:BiologicalProcess"))
        setattr(cls, "biolink:Pathway",
            PermissibleValue(text="biolink:Pathway"))
        setattr(cls, "biolink:PhysiologicalProcess",
            PermissibleValue(text="biolink:PhysiologicalProcess"))
        setattr(cls, "biolink:Behavior",
            PermissibleValue(text="biolink:Behavior"))
        setattr(cls, "biolink:PathologicalProcess",
            PermissibleValue(text="biolink:PathologicalProcess"))
        setattr(cls, "biolink:AccessibleDnaRegion",
            PermissibleValue(text="biolink:AccessibleDnaRegion"))
        setattr(cls, "biolink:TranscriptionFactorBindingSite",
            PermissibleValue(text="biolink:TranscriptionFactorBindingSite"))
        setattr(cls, "biolink:EnvironmentalProcess",
            PermissibleValue(text="biolink:EnvironmentalProcess"))
        setattr(cls, "biolink:EnvironmentalFeature",
            PermissibleValue(text="biolink:EnvironmentalFeature"))
        setattr(cls, "biolink:GeographicLocation",
            PermissibleValue(text="biolink:GeographicLocation"))
        setattr(cls, "biolink:GeographicLocationAtTime",
            PermissibleValue(text="biolink:GeographicLocationAtTime"))
        setattr(cls, "biolink:Study",
            PermissibleValue(text="biolink:Study"))
        setattr(cls, "biolink:MaterialSample",
            PermissibleValue(text="biolink:MaterialSample"))
        setattr(cls, "biolink:StudyResult",
            PermissibleValue(text="biolink:StudyResult"))
        setattr(cls, "biolink:StudyVariable",
            PermissibleValue(text="biolink:StudyVariable"))
        setattr(cls, "biolink:CommonDataElement",
            PermissibleValue(text="biolink:CommonDataElement"))
        setattr(cls, "biolink:Dataset",
            PermissibleValue(text="biolink:Dataset"))
        setattr(cls, "biolink:DatasetDistribution",
            PermissibleValue(text="biolink:DatasetDistribution"))
        setattr(cls, "biolink:DatasetVersion",
            PermissibleValue(text="biolink:DatasetVersion"))
        setattr(cls, "biolink:DatasetSummary",
            PermissibleValue(text="biolink:DatasetSummary"))
        setattr(cls, "biolink:ConfidenceLevel",
            PermissibleValue(text="biolink:ConfidenceLevel"))
        setattr(cls, "biolink:EvidenceType",
            PermissibleValue(text="biolink:EvidenceType"))
        setattr(cls, "biolink:Publication",
            PermissibleValue(text="biolink:Publication"))
        setattr(cls, "biolink:RetrievalSource",
            PermissibleValue(text="biolink:RetrievalSource"))
        setattr(cls, "biolink:Book",
            PermissibleValue(text="biolink:Book"))
        setattr(cls, "biolink:BookChapter",
            PermissibleValue(text="biolink:BookChapter"))
        setattr(cls, "biolink:Serial",
            PermissibleValue(text="biolink:Serial"))
        setattr(cls, "biolink:Article",
            PermissibleValue(text="biolink:Article"))
        setattr(cls, "biolink:Patent",
            PermissibleValue(text="biolink:Patent"))
        setattr(cls, "biolink:WebPage",
            PermissibleValue(text="biolink:WebPage"))
        setattr(cls, "biolink:PreprintPublication",
            PermissibleValue(text="biolink:PreprintPublication"))
        setattr(cls, "biolink:DrugLabel",
            PermissibleValue(text="biolink:DrugLabel"))
        setattr(cls, "biolink:JournalArticle",
            PermissibleValue(text="biolink:JournalArticle"))
        setattr(cls, "biolink:ConceptCountAnalysisResult",
            PermissibleValue(text="biolink:ConceptCountAnalysisResult"))
        setattr(cls, "biolink:ObservedExpectedFrequencyAnalysisResult",
            PermissibleValue(text="biolink:ObservedExpectedFrequencyAnalysisResult"))
        setattr(cls, "biolink:RelativeFrequencyAnalysisResult",
            PermissibleValue(text="biolink:RelativeFrequencyAnalysisResult"))
        setattr(cls, "biolink:TextMiningResult",
            PermissibleValue(text="biolink:TextMiningResult"))
        setattr(cls, "biolink:ChiSquaredAnalysisResult",
            PermissibleValue(text="biolink:ChiSquaredAnalysisResult"))
        setattr(cls, "biolink:LogOddsAnalysisResult",
            PermissibleValue(text="biolink:LogOddsAnalysisResult"))
        setattr(cls, "biolink:Agent",
            PermissibleValue(text="biolink:Agent"))
        setattr(cls, "biolink:ChemicalRole",
            PermissibleValue(text="biolink:ChemicalRole"))
        setattr(cls, "biolink:BiologicalSex",
            PermissibleValue(text="biolink:BiologicalSex"))
        setattr(cls, "biolink:SeverityValue",
            PermissibleValue(text="biolink:SeverityValue"))
        setattr(cls, "biolink:OrganismAttribute",
            PermissibleValue(text="biolink:OrganismAttribute"))
        setattr(cls, "biolink:Zygosity",
            PermissibleValue(text="biolink:Zygosity"))
        setattr(cls, "biolink:ClinicalAttribute",
            PermissibleValue(text="biolink:ClinicalAttribute"))
        setattr(cls, "biolink:SocioeconomicAttribute",
            PermissibleValue(text="biolink:SocioeconomicAttribute"))
        setattr(cls, "biolink:GenomicBackgroundExposure",
            PermissibleValue(text="biolink:GenomicBackgroundExposure"))
        setattr(cls, "biolink:PathologicalProcessExposure",
            PermissibleValue(text="biolink:PathologicalProcessExposure"))
        setattr(cls, "biolink:PathologicalAnatomicalExposure",
            PermissibleValue(text="biolink:PathologicalAnatomicalExposure"))
        setattr(cls, "biolink:DiseaseOrPhenotypicFeatureExposure",
            PermissibleValue(text="biolink:DiseaseOrPhenotypicFeatureExposure"))
        setattr(cls, "biolink:ChemicalExposure",
            PermissibleValue(text="biolink:ChemicalExposure"))
        setattr(cls, "biolink:ComplexChemicalExposure",
            PermissibleValue(text="biolink:ComplexChemicalExposure"))
        setattr(cls, "biolink:BioticExposure",
            PermissibleValue(text="biolink:BioticExposure"))
        setattr(cls, "biolink:EnvironmentalExposure",
            PermissibleValue(text="biolink:EnvironmentalExposure"))
        setattr(cls, "biolink:BehavioralExposure",
            PermissibleValue(text="biolink:BehavioralExposure"))
        setattr(cls, "biolink:SocioeconomicExposure",
            PermissibleValue(text="biolink:SocioeconomicExposure"))
        setattr(cls, "biolink:GeographicExposure",
            PermissibleValue(text="biolink:GeographicExposure"))
        setattr(cls, "biolink:DrugExposure",
            PermissibleValue(text="biolink:DrugExposure"))
        setattr(cls, "biolink:DrugToGeneInteractionExposure",
            PermissibleValue(text="biolink:DrugToGeneInteractionExposure"))
        setattr(cls, "biolink:ClinicalMeasurement",
            PermissibleValue(text="biolink:ClinicalMeasurement"))
        setattr(cls, "biolink:ClinicalModifier",
            PermissibleValue(text="biolink:ClinicalModifier"))
        setattr(cls, "biolink:ClinicalCourse",
            PermissibleValue(text="biolink:ClinicalCourse"))
        setattr(cls, "biolink:Onset",
            PermissibleValue(text="biolink:Onset"))
        setattr(cls, "biolink:PhenotypicQuality",
            PermissibleValue(text="biolink:PhenotypicQuality"))
        setattr(cls, "biolink:PhenotypicSex",
            PermissibleValue(text="biolink:PhenotypicSex"))
        setattr(cls, "biolink:GenotypicSex",
            PermissibleValue(text="biolink:GenotypicSex"))

class KnowledgeLevelEnum(EnumDefinitionImpl):

    knowledge_assertion = PermissibleValue(
        text="knowledge_assertion",
        description="""A statement of purported fact that is put forth by an agent as true, based on assessment of direct evidence. Assertions are likely but not  definitively true.""")
    logical_entailment = PermissibleValue(
        text="logical_entailment",
        description="""A statement reporting a conclusion that follows logically from premises representing established facts or knowledge assertions (e.g. fingernail part of finger, finger part of hand --> fingernail part of hand).""")
    prediction = PermissibleValue(
        text="prediction",
        description="""A statement of a possible fact based on probabilistic forms of reasoning over more indirect forms of evidence, that lead to more speculative conclusions.""")
    statistical_association = PermissibleValue(
        text="statistical_association",
        description="""A statement that reports concepts representing variables in a dataset to be statistically associated with each other in a particular cohort (e.g. 'Metformin Treatment (variable 1) is correlated with Diabetes Diagnosis (variable 2) in EHR dataset X').""")
    observation = PermissibleValue(
        text="observation",
        description="""A statement reporting (and possibly quantifying) a phenomenon that was observed to occur -  absent any analysis or interpretation that generates a statistical association or supports a broader conclusion or inference.""")
    not_provided = PermissibleValue(
        text="not_provided",
        description="""The knowledge level is not provided, typically because it cannot be determined from available. information.""")

    _defn = EnumDefinition(
        name="KnowledgeLevelEnum",
    )

class AgentTypeEnum(EnumDefinitionImpl):

    manual_agent = PermissibleValue(
        text="manual_agent",
        description="""A human agent who is responsible for generating a statement of knowledge. The human may utilize computationally generated information as evidence for the resulting knowledge,  but the human is the one who ultimately interprets/reasons with  this evidence to produce a statement of knowledge.""")
    automated_agent = PermissibleValue(
        text="automated_agent",
        description="""An automated agent, typically a software program or tool, that is  responsible for generating a statement of knowledge. Human contribution  to the knowledge creation process ends with the definition and coding of algorithms or analysis pipelines that get executed by the automated agent.""")
    data_analysis_pipeline = PermissibleValue(
        text="data_analysis_pipeline",
        description="""An automated agent that executes an analysis workflow over data and  reports the direct results of the analysis. These typically report  statistical associations/correlations between variables in the input dataset, and do not interpret/infer broader conclusions from associations the analysis reveals in the data.""")
    computational_model = PermissibleValue(
        text="computational_model",
        description="""An automated agent that generates knowledge statements (typically predictions) based on rules/logic explicitly encoded in an algorithm (e.g. heuristic models, supervised classifiers), or learned from patterns  observed in data (e.g. ML models, unsupervised classifiers).""")
    text_mining_agent = PermissibleValue(
        text="text_mining_agent",
        description="""An automated agent that uses Natural Language Processing to recognize concepts and/or relationships in text, and report them using formally encoded semantics (e.g. as an edge in a knowledge graph).""")
    image_processing_agent = PermissibleValue(
        text="image_processing_agent",
        description="""An automated agent that processes images to generate textual statements of  knowledge derived from the image and/or expressed in text the image  depicts (e.g. via OCR).""")
    manual_validation_of_automated_agent = PermissibleValue(
        text="manual_validation_of_automated_agent",
        description="""A human agent reviews and validates/approves the veracity of knowledge  that is initially generated by an automated agent.""")
    not_provided = PermissibleValue(
        text="not_provided",
        description="""The agent type is not provided, typically because it cannot be determined from available information if the agent that generated the knowledge is  manual or automated.""")

    _defn = EnumDefinition(
        name="AgentTypeEnum",
    )

class AttributeTypeEnum(EnumDefinitionImpl):
    """
    Code used to describe the nature of a slot, for documentative purposes.
    """
    filter = PermissibleValue(
        text="filter",
        description="Attribute used as a boolean filter for the disease list.")
    grouping = PermissibleValue(
        text="grouping",
        description="Attribute used as a grouping/tagging attribute for the disease list.")

    _defn = EnumDefinition(
        name="AttributeTypeEnum",
        description="Code used to describe the nature of a slot, for documentative purposes.",
    )

class CurationTypeEnum(EnumDefinitionImpl):
    """
    Code used to describe how a slot / attribute was curated.
    """
    manual_everycure = PermissibleValue(
        text="manual_everycure",
        description="Manually curated by a Matrix medical expert.")
    manual_mondo = PermissibleValue(
        text="manual_mondo",
        description="Manually curated by the Mondo team.")
    llm = PermissibleValue(
        text="llm",
        description="Automatically curated by a script or algorithm.")
    ontology_hierarchy = PermissibleValue(
        text="ontology_hierarchy",
        description="Automatically extracted from the ontology hierarchy.")
    external_source = PermissibleValue(
        text="external_source",
        description="Automatically extracted from an external source.")
    lexical_matching = PermissibleValue(
        text="lexical_matching",
        description="Automatically curated from a lexical matching algorithm.")

    _defn = EnumDefinition(
        name="CurationTypeEnum",
        description="Code used to describe how a slot / attribute was curated.",
    )

# Slots
class slots:
    pass

slots.id = Slot(uri=SCHEMA.identifier, name="id", curie=SCHEMA.curie('identifier'),
                   model_uri=MATRIX_SCHEMA.id, domain=None, range=URIRef)

slots.name = Slot(uri=MATRIX_SCHEMA.name, name="name", curie=MATRIX_SCHEMA.curie('name'),
                   model_uri=MATRIX_SCHEMA.name, domain=None, range=Optional[str])

slots.category = Slot(uri=MATRIX_SCHEMA.category, name="category", curie=MATRIX_SCHEMA.curie('category'),
                   model_uri=MATRIX_SCHEMA.category, domain=None, range=Optional[Union[str, "NodeCategoryEnum"]])

slots.description = Slot(uri=MATRIX_SCHEMA.description, name="description", curie=MATRIX_SCHEMA.curie('description'),
                   model_uri=MATRIX_SCHEMA.description, domain=None, range=Optional[str])

slots.equivalent_identifiers = Slot(uri=MATRIX_SCHEMA.equivalent_identifiers, name="equivalent_identifiers", curie=MATRIX_SCHEMA.curie('equivalent_identifiers'),
                   model_uri=MATRIX_SCHEMA.equivalent_identifiers, domain=None, range=Optional[Union[str, List[str]]])

slots.all_categories = Slot(uri=MATRIX_SCHEMA.all_categories, name="all_categories", curie=MATRIX_SCHEMA.curie('all_categories'),
                   model_uri=MATRIX_SCHEMA.all_categories, domain=None, range=Optional[Union[Union[str, "NodeCategoryEnum"], List[Union[str, "NodeCategoryEnum"]]]])

slots.publications = Slot(uri=MATRIX_SCHEMA.publications, name="publications", curie=MATRIX_SCHEMA.curie('publications'),
                   model_uri=MATRIX_SCHEMA.publications, domain=None, range=Optional[Union[str, List[str]]])

slots.labels = Slot(uri=MATRIX_SCHEMA.labels, name="labels", curie=MATRIX_SCHEMA.curie('labels'),
                   model_uri=MATRIX_SCHEMA.labels, domain=None, range=Optional[Union[str, List[str]]])

slots.international_resource_identifier = Slot(uri=MATRIX_SCHEMA.international_resource_identifier, name="international_resource_identifier", curie=MATRIX_SCHEMA.curie('international_resource_identifier'),
                   model_uri=MATRIX_SCHEMA.international_resource_identifier, domain=None, range=Optional[str])

slots.upstream_data_source = Slot(uri=MATRIX_SCHEMA.upstream_data_source, name="upstream_data_source", curie=MATRIX_SCHEMA.curie('upstream_data_source'),
                   model_uri=MATRIX_SCHEMA.upstream_data_source, domain=None, range=Optional[Union[str, List[str]]])

slots.num_references = Slot(uri=MATRIX_SCHEMA.num_references, name="num_references", curie=MATRIX_SCHEMA.curie('num_references'),
                   model_uri=MATRIX_SCHEMA.num_references, domain=None, range=Optional[int])

slots.num_sentences = Slot(uri=MATRIX_SCHEMA.num_sentences, name="num_sentences", curie=MATRIX_SCHEMA.curie('num_sentences'),
                   model_uri=MATRIX_SCHEMA.num_sentences, domain=None, range=Optional[int])

slots.subject = Slot(uri=MATRIX_SCHEMA.subject, name="subject", curie=MATRIX_SCHEMA.curie('subject'),
                   model_uri=MATRIX_SCHEMA.subject, domain=None, range=Optional[str])

slots.predicate = Slot(uri=MATRIX_SCHEMA.predicate, name="predicate", curie=MATRIX_SCHEMA.curie('predicate'),
                   model_uri=MATRIX_SCHEMA.predicate, domain=None, range=Optional[Union[str, "PredicateEnum"]])

slots.object = Slot(uri=MATRIX_SCHEMA.object, name="object", curie=MATRIX_SCHEMA.curie('object'),
                   model_uri=MATRIX_SCHEMA.object, domain=None, range=Optional[str])

slots.knowledge_level = Slot(uri=MATRIX_SCHEMA.knowledge_level, name="knowledge_level", curie=MATRIX_SCHEMA.curie('knowledge_level'),
                   model_uri=MATRIX_SCHEMA.knowledge_level, domain=None, range=Optional[Union[str, "KnowledgeLevelEnum"]])

slots.agent_type = Slot(uri=MATRIX_SCHEMA.agent_type, name="agent_type", curie=MATRIX_SCHEMA.curie('agent_type'),
                   model_uri=MATRIX_SCHEMA.agent_type, domain=None, range=Optional[Union[str, "AgentTypeEnum"]])

slots.primary_knowledge_source = Slot(uri=MATRIX_SCHEMA.primary_knowledge_source, name="primary_knowledge_source", curie=MATRIX_SCHEMA.curie('primary_knowledge_source'),
                   model_uri=MATRIX_SCHEMA.primary_knowledge_source, domain=None, range=Optional[str])

slots.primary_knowledge_sources = Slot(uri=MATRIX_SCHEMA.primary_knowledge_sources, name="primary_knowledge_sources", curie=MATRIX_SCHEMA.curie('primary_knowledge_sources'),
                   model_uri=MATRIX_SCHEMA.primary_knowledge_sources, domain=None, range=Optional[Union[str, List[str]]])

slots.aggregator_knowledge_source = Slot(uri=MATRIX_SCHEMA.aggregator_knowledge_source, name="aggregator_knowledge_source", curie=MATRIX_SCHEMA.curie('aggregator_knowledge_source'),
                   model_uri=MATRIX_SCHEMA.aggregator_knowledge_source, domain=None, range=Optional[Union[str, List[str]]])

slots.subject_aspect_qualifier = Slot(uri=MATRIX_SCHEMA.subject_aspect_qualifier, name="subject_aspect_qualifier", curie=MATRIX_SCHEMA.curie('subject_aspect_qualifier'),
                   model_uri=MATRIX_SCHEMA.subject_aspect_qualifier, domain=None, range=Optional[str])

slots.subject_direction_qualifier = Slot(uri=MATRIX_SCHEMA.subject_direction_qualifier, name="subject_direction_qualifier", curie=MATRIX_SCHEMA.curie('subject_direction_qualifier'),
                   model_uri=MATRIX_SCHEMA.subject_direction_qualifier, domain=None, range=Optional[str])

slots.object_aspect_qualifier = Slot(uri=MATRIX_SCHEMA.object_aspect_qualifier, name="object_aspect_qualifier", curie=MATRIX_SCHEMA.curie('object_aspect_qualifier'),
                   model_uri=MATRIX_SCHEMA.object_aspect_qualifier, domain=None, range=Optional[str])

slots.object_direction_qualifier = Slot(uri=MATRIX_SCHEMA.object_direction_qualifier, name="object_direction_qualifier", curie=MATRIX_SCHEMA.curie('object_direction_qualifier'),
                   model_uri=MATRIX_SCHEMA.object_direction_qualifier, domain=None, range=Optional[str])

slots.category_class = Slot(uri=MATRIX_SCHEMA.category_class, name="category_class", curie=MATRIX_SCHEMA.curie('category_class'),
                   model_uri=MATRIX_SCHEMA.category_class, domain=None, range=Optional[str])

slots.label = Slot(uri=MATRIX_SCHEMA.label, name="label", curie=MATRIX_SCHEMA.curie('label'),
                   model_uri=MATRIX_SCHEMA.label, domain=None, range=Optional[str])

slots.definition = Slot(uri=MATRIX_SCHEMA.definition, name="definition", curie=MATRIX_SCHEMA.curie('definition'),
                   model_uri=MATRIX_SCHEMA.definition, domain=None, range=Optional[str])

slots.synonyms = Slot(uri=MATRIX_SCHEMA.synonyms, name="synonyms", curie=MATRIX_SCHEMA.curie('synonyms'),
                   model_uri=MATRIX_SCHEMA.synonyms, domain=None, range=Optional[Union[str, List[str]]])

slots.subsets = Slot(uri=MATRIX_SCHEMA.subsets, name="subsets", curie=MATRIX_SCHEMA.curie('subsets'),
                   model_uri=MATRIX_SCHEMA.subsets, domain=None, range=Optional[Union[str, List[str]]])

slots.crossreferences = Slot(uri=MATRIX_SCHEMA.crossreferences, name="crossreferences", curie=MATRIX_SCHEMA.curie('crossreferences'),
                   model_uri=MATRIX_SCHEMA.crossreferences, domain=None, range=Optional[Union[str, List[str]]])

slots.subset_group_id = Slot(uri=MATRIX_SCHEMA.subset_group_id, name="subset_group_id", curie=MATRIX_SCHEMA.curie('subset_group_id'),
                   model_uri=MATRIX_SCHEMA.subset_group_id, domain=None, range=Optional[str])

slots.subset_group_label = Slot(uri=MATRIX_SCHEMA.subset_group_label, name="subset_group_label", curie=MATRIX_SCHEMA.curie('subset_group_label'),
                   model_uri=MATRIX_SCHEMA.subset_group_label, domain=None, range=Optional[str])

slots.other_subsets_count = Slot(uri=MATRIX_SCHEMA.other_subsets_count, name="other_subsets_count", curie=MATRIX_SCHEMA.curie('other_subsets_count'),
                   model_uri=MATRIX_SCHEMA.other_subsets_count, domain=None, range=Optional[int])

slots.edges = Slot(uri=MATRIX_SCHEMA.edges, name="edges", curie=MATRIX_SCHEMA.curie('edges'),
                   model_uri=MATRIX_SCHEMA.edges, domain=None, range=Optional[Union[str, List[str]]])

slots.nodes = Slot(uri=MATRIX_SCHEMA.nodes, name="nodes", curie=MATRIX_SCHEMA.curie('nodes'),
                   model_uri=MATRIX_SCHEMA.nodes, domain=None, range=Optional[Union[str, List[str]]])

slots.disease_list_entries = Slot(uri=MATRIX_SCHEMA.disease_list_entries, name="disease_list_entries", curie=MATRIX_SCHEMA.curie('disease_list_entries'),
                   model_uri=MATRIX_SCHEMA.disease_list_entries, domain=None, range=Optional[Union[Union[dict, DiseaseListEntry], List[Union[dict, DiseaseListEntry]]]])

slots.attribute_type = Slot(uri=MATRIX_SCHEMA.attribute_type, name="attribute_type", curie=MATRIX_SCHEMA.curie('attribute_type'),
                   model_uri=MATRIX_SCHEMA.attribute_type, domain=None, range=Optional[Union[str, "AttributeTypeEnum"]])

slots.curation_type = Slot(uri=MATRIX_SCHEMA.curation_type, name="curation_type", curie=MATRIX_SCHEMA.curie('curation_type'),
                   model_uri=MATRIX_SCHEMA.curation_type, domain=None, range=Optional[Union[str, "CurationTypeEnum"]])

slots.is_matrix_manually_excluded = Slot(uri=MATRIX_SCHEMA.is_matrix_manually_excluded, name="is_matrix_manually_excluded", curie=MATRIX_SCHEMA.curie('is_matrix_manually_excluded'),
                   model_uri=MATRIX_SCHEMA.is_matrix_manually_excluded, domain=None, range=Optional[Union[bool, Bool]])

slots.is_matrix_manually_included = Slot(uri=MATRIX_SCHEMA.is_matrix_manually_included, name="is_matrix_manually_included", curie=MATRIX_SCHEMA.curie('is_matrix_manually_included'),
                   model_uri=MATRIX_SCHEMA.is_matrix_manually_included, domain=None, range=Optional[Union[bool, Bool]])

slots.is_clingen = Slot(uri=MATRIX_SCHEMA.is_clingen, name="is_clingen", curie=MATRIX_SCHEMA.curie('is_clingen'),
                   model_uri=MATRIX_SCHEMA.is_clingen, domain=None, range=Optional[Union[bool, Bool]])

slots.is_grouping_subset = Slot(uri=MATRIX_SCHEMA.is_grouping_subset, name="is_grouping_subset", curie=MATRIX_SCHEMA.curie('is_grouping_subset'),
                   model_uri=MATRIX_SCHEMA.is_grouping_subset, domain=None, range=Optional[Union[bool, Bool]])

slots.is_grouping_subset_ancestor = Slot(uri=MATRIX_SCHEMA.is_grouping_subset_ancestor, name="is_grouping_subset_ancestor", curie=MATRIX_SCHEMA.curie('is_grouping_subset_ancestor'),
                   model_uri=MATRIX_SCHEMA.is_grouping_subset_ancestor, domain=None, range=Optional[Union[bool, Bool]])

slots.is_orphanet_subtype = Slot(uri=MATRIX_SCHEMA.is_orphanet_subtype, name="is_orphanet_subtype", curie=MATRIX_SCHEMA.curie('is_orphanet_subtype'),
                   model_uri=MATRIX_SCHEMA.is_orphanet_subtype, domain=None, range=Optional[Union[bool, Bool]])

slots.is_orphanet_subtype_descendant = Slot(uri=MATRIX_SCHEMA.is_orphanet_subtype_descendant, name="is_orphanet_subtype_descendant", curie=MATRIX_SCHEMA.curie('is_orphanet_subtype_descendant'),
                   model_uri=MATRIX_SCHEMA.is_orphanet_subtype_descendant, domain=None, range=Optional[Union[bool, Bool]])

slots.is_omimps = Slot(uri=MATRIX_SCHEMA.is_omimps, name="is_omimps", curie=MATRIX_SCHEMA.curie('is_omimps'),
                   model_uri=MATRIX_SCHEMA.is_omimps, domain=None, range=Optional[Union[bool, Bool]])

slots.is_omimps_descendant = Slot(uri=MATRIX_SCHEMA.is_omimps_descendant, name="is_omimps_descendant", curie=MATRIX_SCHEMA.curie('is_omimps_descendant'),
                   model_uri=MATRIX_SCHEMA.is_omimps_descendant, domain=None, range=Optional[Union[bool, Bool]])

slots.is_leaf = Slot(uri=MATRIX_SCHEMA.is_leaf, name="is_leaf", curie=MATRIX_SCHEMA.curie('is_leaf'),
                   model_uri=MATRIX_SCHEMA.is_leaf, domain=None, range=Optional[Union[bool, Bool]])

slots.is_leaf_direct_parent = Slot(uri=MATRIX_SCHEMA.is_leaf_direct_parent, name="is_leaf_direct_parent", curie=MATRIX_SCHEMA.curie('is_leaf_direct_parent'),
                   model_uri=MATRIX_SCHEMA.is_leaf_direct_parent, domain=None, range=Optional[Union[bool, Bool]])

slots.is_orphanet_disorder = Slot(uri=MATRIX_SCHEMA.is_orphanet_disorder, name="is_orphanet_disorder", curie=MATRIX_SCHEMA.curie('is_orphanet_disorder'),
                   model_uri=MATRIX_SCHEMA.is_orphanet_disorder, domain=None, range=Optional[Union[bool, Bool]])

slots.is_omim = Slot(uri=MATRIX_SCHEMA.is_omim, name="is_omim", curie=MATRIX_SCHEMA.curie('is_omim'),
                   model_uri=MATRIX_SCHEMA.is_omim, domain=None, range=Optional[Union[bool, Bool]])

slots.is_icd_category = Slot(uri=MATRIX_SCHEMA.is_icd_category, name="is_icd_category", curie=MATRIX_SCHEMA.curie('is_icd_category'),
                   model_uri=MATRIX_SCHEMA.is_icd_category, domain=None, range=Optional[Union[bool, Bool]])

slots.is_icd_chapter_code = Slot(uri=MATRIX_SCHEMA.is_icd_chapter_code, name="is_icd_chapter_code", curie=MATRIX_SCHEMA.curie('is_icd_chapter_code'),
                   model_uri=MATRIX_SCHEMA.is_icd_chapter_code, domain=None, range=Optional[Union[bool, Bool]])

slots.is_icd_chapter_header = Slot(uri=MATRIX_SCHEMA.is_icd_chapter_header, name="is_icd_chapter_header", curie=MATRIX_SCHEMA.curie('is_icd_chapter_header'),
                   model_uri=MATRIX_SCHEMA.is_icd_chapter_header, domain=None, range=Optional[Union[bool, Bool]])

slots.is_icd_billable = Slot(uri=MATRIX_SCHEMA.is_icd_billable, name="is_icd_billable", curie=MATRIX_SCHEMA.curie('is_icd_billable'),
                   model_uri=MATRIX_SCHEMA.is_icd_billable, domain=None, range=Optional[Union[bool, Bool]])

slots.is_mondo_subtype = Slot(uri=MATRIX_SCHEMA.is_mondo_subtype, name="is_mondo_subtype", curie=MATRIX_SCHEMA.curie('is_mondo_subtype'),
                   model_uri=MATRIX_SCHEMA.is_mondo_subtype, domain=None, range=Optional[Union[bool, Bool]])

slots.is_pathway_defect = Slot(uri=MATRIX_SCHEMA.is_pathway_defect, name="is_pathway_defect", curie=MATRIX_SCHEMA.curie('is_pathway_defect'),
                   model_uri=MATRIX_SCHEMA.is_pathway_defect, domain=None, range=Optional[Union[bool, Bool]])

slots.is_susceptibility = Slot(uri=MATRIX_SCHEMA.is_susceptibility, name="is_susceptibility", curie=MATRIX_SCHEMA.curie('is_susceptibility'),
                   model_uri=MATRIX_SCHEMA.is_susceptibility, domain=None, range=Optional[Union[bool, Bool]])

slots.is_paraphilic = Slot(uri=MATRIX_SCHEMA.is_paraphilic, name="is_paraphilic", curie=MATRIX_SCHEMA.curie('is_paraphilic'),
                   model_uri=MATRIX_SCHEMA.is_paraphilic, domain=None, range=Optional[Union[bool, Bool]])

slots.is_acquired = Slot(uri=MATRIX_SCHEMA.is_acquired, name="is_acquired", curie=MATRIX_SCHEMA.curie('is_acquired'),
                   model_uri=MATRIX_SCHEMA.is_acquired, domain=None, range=Optional[Union[bool, Bool]])

slots.is_andor = Slot(uri=MATRIX_SCHEMA.is_andor, name="is_andor", curie=MATRIX_SCHEMA.curie('is_andor'),
                   model_uri=MATRIX_SCHEMA.is_andor, domain=None, range=Optional[Union[bool, Bool]])

slots.is_withorwithout = Slot(uri=MATRIX_SCHEMA.is_withorwithout, name="is_withorwithout", curie=MATRIX_SCHEMA.curie('is_withorwithout'),
                   model_uri=MATRIX_SCHEMA.is_withorwithout, domain=None, range=Optional[Union[bool, Bool]])

slots.is_obsoletion_candidate = Slot(uri=MATRIX_SCHEMA.is_obsoletion_candidate, name="is_obsoletion_candidate", curie=MATRIX_SCHEMA.curie('is_obsoletion_candidate'),
                   model_uri=MATRIX_SCHEMA.is_obsoletion_candidate, domain=None, range=Optional[Union[bool, Bool]])

slots.is_unclassified_hereditary = Slot(uri=MATRIX_SCHEMA.is_unclassified_hereditary, name="is_unclassified_hereditary", curie=MATRIX_SCHEMA.curie('is_unclassified_hereditary'),
                   model_uri=MATRIX_SCHEMA.is_unclassified_hereditary, domain=None, range=Optional[Union[bool, Bool]])

slots.official_matrix_filter = Slot(uri=MATRIX_SCHEMA.official_matrix_filter, name="official_matrix_filter", curie=MATRIX_SCHEMA.curie('official_matrix_filter'),
                   model_uri=MATRIX_SCHEMA.official_matrix_filter, domain=None, range=Optional[Union[bool, Bool]])

slots.is_pathogen_caused = Slot(uri=MATRIX_SCHEMA.is_pathogen_caused, name="is_pathogen_caused", curie=MATRIX_SCHEMA.curie('is_pathogen_caused'),
                   model_uri=MATRIX_SCHEMA.is_pathogen_caused, domain=None, range=Optional[Union[bool, Bool]])

slots.is_cancer = Slot(uri=MATRIX_SCHEMA.is_cancer, name="is_cancer", curie=MATRIX_SCHEMA.curie('is_cancer'),
                   model_uri=MATRIX_SCHEMA.is_cancer, domain=None, range=Optional[Union[bool, Bool]])

slots.is_glucose_dysfunction = Slot(uri=MATRIX_SCHEMA.is_glucose_dysfunction, name="is_glucose_dysfunction", curie=MATRIX_SCHEMA.curie('is_glucose_dysfunction'),
                   model_uri=MATRIX_SCHEMA.is_glucose_dysfunction, domain=None, range=Optional[Union[bool, Bool]])

slots.tag_existing_treatment = Slot(uri=MATRIX_SCHEMA.tag_existing_treatment, name="tag_existing_treatment", curie=MATRIX_SCHEMA.curie('tag_existing_treatment'),
                   model_uri=MATRIX_SCHEMA.tag_existing_treatment, domain=None, range=Optional[Union[bool, Bool]])

slots.harrisons_view = Slot(uri=MATRIX_SCHEMA.harrisons_view, name="harrisons_view", curie=MATRIX_SCHEMA.curie('harrisons_view'),
                   model_uri=MATRIX_SCHEMA.harrisons_view, domain=None, range=Optional[Union[str, List[str]]])

slots.mondo_txgnn = Slot(uri=MATRIX_SCHEMA.mondo_txgnn, name="mondo_txgnn", curie=MATRIX_SCHEMA.curie('mondo_txgnn'),
                   model_uri=MATRIX_SCHEMA.mondo_txgnn, domain=None, range=Optional[Union[str, List[str]]])

slots.mondo_top_grouping = Slot(uri=MATRIX_SCHEMA.mondo_top_grouping, name="mondo_top_grouping", curie=MATRIX_SCHEMA.curie('mondo_top_grouping'),
                   model_uri=MATRIX_SCHEMA.mondo_top_grouping, domain=None, range=Optional[Union[str, List[str]]])

slots.medical_specialization = Slot(uri=MATRIX_SCHEMA.medical_specialization, name="medical_specialization", curie=MATRIX_SCHEMA.curie('medical_specialization'),
                   model_uri=MATRIX_SCHEMA.medical_specialization, domain=None, range=Optional[Union[str, List[str]]])

slots.txgnn = Slot(uri=MATRIX_SCHEMA.txgnn, name="txgnn", curie=MATRIX_SCHEMA.curie('txgnn'),
                   model_uri=MATRIX_SCHEMA.txgnn, domain=None, range=Optional[Union[str, List[str]]])

slots.anatomical = Slot(uri=MATRIX_SCHEMA.anatomical, name="anatomical", curie=MATRIX_SCHEMA.curie('anatomical'),
                   model_uri=MATRIX_SCHEMA.anatomical, domain=None, range=Optional[Union[str, List[str]]])

slots.tag_qaly_lost = Slot(uri=MATRIX_SCHEMA.tag_qaly_lost, name="tag_qaly_lost", curie=MATRIX_SCHEMA.curie('tag_qaly_lost'),
                   model_uri=MATRIX_SCHEMA.tag_qaly_lost, domain=None, range=str,
                   pattern=re.compile(r'^(low|medium|high|very_high|none)$'))

slots.MatrixNode_category = Slot(uri=MATRIX_SCHEMA.category, name="MatrixNode_category", curie=MATRIX_SCHEMA.curie('category'),
                   model_uri=MATRIX_SCHEMA.MatrixNode_category, domain=MatrixNode, range=Union[str, "NodeCategoryEnum"])

slots.MatrixNode_id = Slot(uri=SCHEMA.identifier, name="MatrixNode_id", curie=SCHEMA.curie('identifier'),
                   model_uri=MATRIX_SCHEMA.MatrixNode_id, domain=MatrixNode, range=Union[str, MatrixNodeId])

slots.MatrixEdge_subject = Slot(uri=MATRIX_SCHEMA.subject, name="MatrixEdge_subject", curie=MATRIX_SCHEMA.curie('subject'),
                   model_uri=MATRIX_SCHEMA.MatrixEdge_subject, domain=MatrixEdge, range=str)

slots.MatrixEdge_predicate = Slot(uri=MATRIX_SCHEMA.predicate, name="MatrixEdge_predicate", curie=MATRIX_SCHEMA.curie('predicate'),
                   model_uri=MATRIX_SCHEMA.MatrixEdge_predicate, domain=MatrixEdge, range=Union[str, "PredicateEnum"])

slots.MatrixEdge_object = Slot(uri=MATRIX_SCHEMA.object, name="MatrixEdge_object", curie=MATRIX_SCHEMA.curie('object'),
                   model_uri=MATRIX_SCHEMA.MatrixEdge_object, domain=MatrixEdge, range=str)

slots.MatrixEdgeList_edges = Slot(uri=MATRIX_SCHEMA.edges, name="MatrixEdgeList_edges", curie=MATRIX_SCHEMA.curie('edges'),
                   model_uri=MATRIX_SCHEMA.MatrixEdgeList_edges, domain=MatrixEdgeList, range=Optional[Union[Union[dict, MatrixEdge], List[Union[dict, MatrixEdge]]]])

slots.MatrixNodeList_nodes = Slot(uri=MATRIX_SCHEMA.nodes, name="MatrixNodeList_nodes", curie=MATRIX_SCHEMA.curie('nodes'),
                   model_uri=MATRIX_SCHEMA.MatrixNodeList_nodes, domain=MatrixNodeList, range=Optional[Union[Dict[Union[str, MatrixNodeId], Union[dict, MatrixNode]], List[Union[dict, MatrixNode]]]])

slots.DiseaseListEntry_category_class = Slot(uri=MATRIX_SCHEMA.category_class, name="DiseaseListEntry_category_class", curie=MATRIX_SCHEMA.curie('category_class'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_category_class, domain=DiseaseListEntry, range=str)

slots.DiseaseListEntry_label = Slot(uri=MATRIX_SCHEMA.label, name="DiseaseListEntry_label", curie=MATRIX_SCHEMA.curie('label'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_label, domain=DiseaseListEntry, range=str)

slots.DiseaseListEntry_definition = Slot(uri=MATRIX_SCHEMA.definition, name="DiseaseListEntry_definition", curie=MATRIX_SCHEMA.curie('definition'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_definition, domain=DiseaseListEntry, range=Optional[str])

slots.DiseaseListEntry_synonyms = Slot(uri=MATRIX_SCHEMA.synonyms, name="DiseaseListEntry_synonyms", curie=MATRIX_SCHEMA.curie('synonyms'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_synonyms, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_subsets = Slot(uri=MATRIX_SCHEMA.subsets, name="DiseaseListEntry_subsets", curie=MATRIX_SCHEMA.curie('subsets'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_subsets, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_crossreferences = Slot(uri=MATRIX_SCHEMA.crossreferences, name="DiseaseListEntry_crossreferences", curie=MATRIX_SCHEMA.curie('crossreferences'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_crossreferences, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_is_matrix_manually_excluded = Slot(uri=MATRIX_SCHEMA.is_matrix_manually_excluded, name="DiseaseListEntry_is_matrix_manually_excluded", curie=MATRIX_SCHEMA.curie('is_matrix_manually_excluded'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_matrix_manually_excluded, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_matrix_manually_included = Slot(uri=MATRIX_SCHEMA.is_matrix_manually_included, name="DiseaseListEntry_is_matrix_manually_included", curie=MATRIX_SCHEMA.curie('is_matrix_manually_included'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_matrix_manually_included, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_clingen = Slot(uri=MATRIX_SCHEMA.is_clingen, name="DiseaseListEntry_is_clingen", curie=MATRIX_SCHEMA.curie('is_clingen'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_clingen, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_grouping_subset = Slot(uri=MATRIX_SCHEMA.is_grouping_subset, name="DiseaseListEntry_is_grouping_subset", curie=MATRIX_SCHEMA.curie('is_grouping_subset'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_grouping_subset, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_grouping_subset_ancestor = Slot(uri=MATRIX_SCHEMA.is_grouping_subset_ancestor, name="DiseaseListEntry_is_grouping_subset_ancestor", curie=MATRIX_SCHEMA.curie('is_grouping_subset_ancestor'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_grouping_subset_ancestor, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_orphanet_subtype = Slot(uri=MATRIX_SCHEMA.is_orphanet_subtype, name="DiseaseListEntry_is_orphanet_subtype", curie=MATRIX_SCHEMA.curie('is_orphanet_subtype'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_orphanet_subtype, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_orphanet_subtype_descendant = Slot(uri=MATRIX_SCHEMA.is_orphanet_subtype_descendant, name="DiseaseListEntry_is_orphanet_subtype_descendant", curie=MATRIX_SCHEMA.curie('is_orphanet_subtype_descendant'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_orphanet_subtype_descendant, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_omimps = Slot(uri=MATRIX_SCHEMA.is_omimps, name="DiseaseListEntry_is_omimps", curie=MATRIX_SCHEMA.curie('is_omimps'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_omimps, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_omimps_descendant = Slot(uri=MATRIX_SCHEMA.is_omimps_descendant, name="DiseaseListEntry_is_omimps_descendant", curie=MATRIX_SCHEMA.curie('is_omimps_descendant'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_omimps_descendant, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_leaf = Slot(uri=MATRIX_SCHEMA.is_leaf, name="DiseaseListEntry_is_leaf", curie=MATRIX_SCHEMA.curie('is_leaf'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_leaf, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_leaf_direct_parent = Slot(uri=MATRIX_SCHEMA.is_leaf_direct_parent, name="DiseaseListEntry_is_leaf_direct_parent", curie=MATRIX_SCHEMA.curie('is_leaf_direct_parent'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_leaf_direct_parent, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_orphanet_disorder = Slot(uri=MATRIX_SCHEMA.is_orphanet_disorder, name="DiseaseListEntry_is_orphanet_disorder", curie=MATRIX_SCHEMA.curie('is_orphanet_disorder'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_orphanet_disorder, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_omim = Slot(uri=MATRIX_SCHEMA.is_omim, name="DiseaseListEntry_is_omim", curie=MATRIX_SCHEMA.curie('is_omim'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_omim, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_icd_category = Slot(uri=MATRIX_SCHEMA.is_icd_category, name="DiseaseListEntry_is_icd_category", curie=MATRIX_SCHEMA.curie('is_icd_category'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_icd_category, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_icd_chapter_code = Slot(uri=MATRIX_SCHEMA.is_icd_chapter_code, name="DiseaseListEntry_is_icd_chapter_code", curie=MATRIX_SCHEMA.curie('is_icd_chapter_code'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_icd_chapter_code, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_icd_chapter_header = Slot(uri=MATRIX_SCHEMA.is_icd_chapter_header, name="DiseaseListEntry_is_icd_chapter_header", curie=MATRIX_SCHEMA.curie('is_icd_chapter_header'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_icd_chapter_header, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_icd_billable = Slot(uri=MATRIX_SCHEMA.is_icd_billable, name="DiseaseListEntry_is_icd_billable", curie=MATRIX_SCHEMA.curie('is_icd_billable'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_icd_billable, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_mondo_subtype = Slot(uri=MATRIX_SCHEMA.is_mondo_subtype, name="DiseaseListEntry_is_mondo_subtype", curie=MATRIX_SCHEMA.curie('is_mondo_subtype'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_mondo_subtype, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_pathway_defect = Slot(uri=MATRIX_SCHEMA.is_pathway_defect, name="DiseaseListEntry_is_pathway_defect", curie=MATRIX_SCHEMA.curie('is_pathway_defect'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_pathway_defect, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_susceptibility = Slot(uri=MATRIX_SCHEMA.is_susceptibility, name="DiseaseListEntry_is_susceptibility", curie=MATRIX_SCHEMA.curie('is_susceptibility'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_susceptibility, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_paraphilic = Slot(uri=MATRIX_SCHEMA.is_paraphilic, name="DiseaseListEntry_is_paraphilic", curie=MATRIX_SCHEMA.curie('is_paraphilic'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_paraphilic, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_acquired = Slot(uri=MATRIX_SCHEMA.is_acquired, name="DiseaseListEntry_is_acquired", curie=MATRIX_SCHEMA.curie('is_acquired'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_acquired, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_andor = Slot(uri=MATRIX_SCHEMA.is_andor, name="DiseaseListEntry_is_andor", curie=MATRIX_SCHEMA.curie('is_andor'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_andor, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_withorwithout = Slot(uri=MATRIX_SCHEMA.is_withorwithout, name="DiseaseListEntry_is_withorwithout", curie=MATRIX_SCHEMA.curie('is_withorwithout'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_withorwithout, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_obsoletion_candidate = Slot(uri=MATRIX_SCHEMA.is_obsoletion_candidate, name="DiseaseListEntry_is_obsoletion_candidate", curie=MATRIX_SCHEMA.curie('is_obsoletion_candidate'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_obsoletion_candidate, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_unclassified_hereditary = Slot(uri=MATRIX_SCHEMA.is_unclassified_hereditary, name="DiseaseListEntry_is_unclassified_hereditary", curie=MATRIX_SCHEMA.curie('is_unclassified_hereditary'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_unclassified_hereditary, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_official_matrix_filter = Slot(uri=MATRIX_SCHEMA.official_matrix_filter, name="DiseaseListEntry_official_matrix_filter", curie=MATRIX_SCHEMA.curie('official_matrix_filter'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_official_matrix_filter, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_harrisons_view = Slot(uri=MATRIX_SCHEMA.harrisons_view, name="DiseaseListEntry_harrisons_view", curie=MATRIX_SCHEMA.curie('harrisons_view'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_harrisons_view, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_mondo_txgnn = Slot(uri=MATRIX_SCHEMA.mondo_txgnn, name="DiseaseListEntry_mondo_txgnn", curie=MATRIX_SCHEMA.curie('mondo_txgnn'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_mondo_txgnn, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_mondo_top_grouping = Slot(uri=MATRIX_SCHEMA.mondo_top_grouping, name="DiseaseListEntry_mondo_top_grouping", curie=MATRIX_SCHEMA.curie('mondo_top_grouping'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_mondo_top_grouping, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_medical_specialization = Slot(uri=MATRIX_SCHEMA.medical_specialization, name="DiseaseListEntry_medical_specialization", curie=MATRIX_SCHEMA.curie('medical_specialization'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_medical_specialization, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_txgnn = Slot(uri=MATRIX_SCHEMA.txgnn, name="DiseaseListEntry_txgnn", curie=MATRIX_SCHEMA.curie('txgnn'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_txgnn, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_anatomical = Slot(uri=MATRIX_SCHEMA.anatomical, name="DiseaseListEntry_anatomical", curie=MATRIX_SCHEMA.curie('anatomical'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_anatomical, domain=DiseaseListEntry, range=Union[str, List[str]])

slots.DiseaseListEntry_is_pathogen_caused = Slot(uri=MATRIX_SCHEMA.is_pathogen_caused, name="DiseaseListEntry_is_pathogen_caused", curie=MATRIX_SCHEMA.curie('is_pathogen_caused'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_pathogen_caused, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_cancer = Slot(uri=MATRIX_SCHEMA.is_cancer, name="DiseaseListEntry_is_cancer", curie=MATRIX_SCHEMA.curie('is_cancer'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_cancer, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_is_glucose_dysfunction = Slot(uri=MATRIX_SCHEMA.is_glucose_dysfunction, name="DiseaseListEntry_is_glucose_dysfunction", curie=MATRIX_SCHEMA.curie('is_glucose_dysfunction'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_is_glucose_dysfunction, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_tag_existing_treatment = Slot(uri=MATRIX_SCHEMA.tag_existing_treatment, name="DiseaseListEntry_tag_existing_treatment", curie=MATRIX_SCHEMA.curie('tag_existing_treatment'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_tag_existing_treatment, domain=DiseaseListEntry, range=Union[bool, Bool])

slots.DiseaseListEntry_tag_qaly_lost = Slot(uri=MATRIX_SCHEMA.tag_qaly_lost, name="DiseaseListEntry_tag_qaly_lost", curie=MATRIX_SCHEMA.curie('tag_qaly_lost'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_tag_qaly_lost, domain=DiseaseListEntry, range=str,
                   pattern=re.compile(r'^(low|medium|high|very_high|none)$'))

slots.DiseaseListEntry_subset_group_id = Slot(uri=MATRIX_SCHEMA.subset_group_id, name="DiseaseListEntry_subset_group_id", curie=MATRIX_SCHEMA.curie('subset_group_id'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_subset_group_id, domain=DiseaseListEntry, range=Optional[str])

slots.DiseaseListEntry_subset_group_label = Slot(uri=MATRIX_SCHEMA.subset_group_label, name="DiseaseListEntry_subset_group_label", curie=MATRIX_SCHEMA.curie('subset_group_label'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_subset_group_label, domain=DiseaseListEntry, range=Optional[str])

slots.DiseaseListEntry_other_subsets_count = Slot(uri=MATRIX_SCHEMA.other_subsets_count, name="DiseaseListEntry_other_subsets_count", curie=MATRIX_SCHEMA.curie('other_subsets_count'),
                   model_uri=MATRIX_SCHEMA.DiseaseListEntry_other_subsets_count, domain=DiseaseListEntry, range=Optional[int])

slots.MatrixDiseaseList_disease_list_entries = Slot(uri=MATRIX_SCHEMA.disease_list_entries, name="MatrixDiseaseList_disease_list_entries", curie=MATRIX_SCHEMA.curie('disease_list_entries'),
                   model_uri=MATRIX_SCHEMA.MatrixDiseaseList_disease_list_entries, domain=MatrixDiseaseList, range=Optional[Union[Union[dict, DiseaseListEntry], List[Union[dict, DiseaseListEntry]]]])