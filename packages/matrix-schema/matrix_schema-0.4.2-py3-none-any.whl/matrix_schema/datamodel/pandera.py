try:
    import pyspark.sql.types as T
    import pandera.pandas as pa
    from ..utils.pandera_utils import Column, DataFrameSchema
    # Import the enums from the pydantic model
    from .matrix_schema_pydantic import (
        PredicateEnum,
        NodeCategoryEnum,
        KnowledgeLevelEnum,
        AgentTypeEnum
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    T = None
    pa = None
    Column = None
    DataFrameSchema = None
    PredicateEnum = None
    NodeCategoryEnum = None
    KnowledgeLevelEnum = None
    AgentTypeEnum = None
    DEPENDENCIES_AVAILABLE = False
    IMPORT_ERROR = str(e)


def get_matrix_node_schema(validate_enumeration_values: bool = True):
    """Get the Pandera schema for MatrixNode validation.
    
    Returns a universal schema that works with both pandas and PySpark DataFrames.
    The actual schema type is determined at validation time based on the DataFrame type.
    """
    if not DEPENDENCIES_AVAILABLE:
        error_msg = f"Dependencies not available for Pandera schema. Original error: {IMPORT_ERROR if 'IMPORT_ERROR' in globals() else 'Unknown'}. Install with: pip install 'pandera[pyspark]' pyspark"
        raise ImportError(error_msg)

    if validate_enumeration_values:
        category_checks = [pa.Check.isin([category.value for category in NodeCategoryEnum])]
    else:
        category_checks = []

    return DataFrameSchema(
        columns={
            "id": Column(T.StringType(), nullable=False),
            "name": Column(T.StringType(), nullable=True),
            "category": Column(T.StringType(), nullable=False, 
                             checks=category_checks),
            "description": Column(T.StringType(), nullable=True),
            "equivalent_identifiers": Column(T.ArrayType(T.StringType()), nullable=True),
            "all_categories": Column(T.ArrayType(T.StringType()), nullable=True),
            "publications": Column(T.ArrayType(T.StringType()), nullable=True),
            "labels": Column(T.ArrayType(T.StringType()), nullable=True),
            "international_resource_identifier": Column(T.StringType(), nullable=True),
            "upstream_data_source": Column(T.ArrayType(T.StringType()), nullable=True),
        },
        unique=["id"],
        strict=True,
    )


def get_matrix_edge_schema(validate_enumeration_values: bool = True):
    """Get the Pandera schema for MatrixEdge validation.
    
    Returns a universal schema that works with both pandas and PySpark DataFrames.
    The actual schema type is determined at validation time based on the DataFrame type.
    """
    if not DEPENDENCIES_AVAILABLE:
        error_msg = f"Dependencies not available for Pandera schema. Original error: {IMPORT_ERROR if 'IMPORT_ERROR' in globals() else 'Unknown'}. Install with: pip install 'pandera[pyspark]' pyspark"
        raise ImportError(error_msg)
    
    if validate_enumeration_values:
        predicate_checks = [pa.Check.isin([predicate.value for predicate in PredicateEnum])]
        knowledge_level_checks = [pa.Check.isin([level.value for level in KnowledgeLevelEnum])]
        agent_type_checks = [pa.Check.isin([agent.value for agent in AgentTypeEnum])]
    else:
        predicate_checks = []
        knowledge_level_checks = []
        agent_type_checks = []

    return DataFrameSchema(
        columns={
            "subject": Column(T.StringType(), nullable=False),
            "predicate": Column(T.StringType(), nullable=False,
                              checks=predicate_checks),
            "object": Column(T.StringType(), nullable=False),
            "knowledge_level": Column(T.StringType(), nullable=True,
                                    checks=knowledge_level_checks),
            "agent_type": Column(T.StringType(), nullable=True,
                               checks=agent_type_checks),
            "primary_knowledge_source": Column(T.StringType(), nullable=True),
            "aggregator_knowledge_source": Column(T.ArrayType(T.StringType()), nullable=True),
            "publications": Column(T.ArrayType(T.StringType()), nullable=True),
            "subject_aspect_qualifier": Column(T.StringType(), nullable=True),
            "subject_direction_qualifier": Column(T.StringType(), nullable=True),
            "object_aspect_qualifier": Column(T.StringType(), nullable=True),
            "object_direction_qualifier": Column(T.StringType(), nullable=True),
            "upstream_data_source": Column(T.ArrayType(T.StringType()), nullable=True),
            # Additional fields from original pandera schema
            "num_references": Column(T.IntegerType(), nullable=True),
            "num_sentences": Column(T.IntegerType(), nullable=True),
        },
        unique=["subject", "predicate", "object"],
        strict=True,
    )


def get_unioned_node_schema(validate_enumeration_values: bool = True):
    """Get the Pandera schema for UnionedNode validation.
    
    Returns a universal schema that works with both pandas and PySpark DataFrames.
    The actual schema type is determined at validation time based on the DataFrame type.
    """
    if not DEPENDENCIES_AVAILABLE:
        error_msg = f"Dependencies not available for Pandera schema. Original error: {IMPORT_ERROR if 'IMPORT_ERROR' in globals() else 'Unknown'}. Install with: pip install 'pandera[pyspark]' pyspark"
        raise ImportError(error_msg)

    if validate_enumeration_values:
        category_checks = [pa.Check.isin([category.value for category in NodeCategoryEnum])]
    else:
        category_checks = []

    return DataFrameSchema(
        columns={
            "id": Column(T.StringType(), nullable=False),
            "name": Column(T.StringType(), nullable=True),
            "category": Column(T.StringType(), nullable=False, 
                             checks=category_checks),
            "description": Column(T.StringType(), nullable=True),
            "equivalent_identifiers": Column(T.ArrayType(T.StringType()), nullable=True),
            "all_categories": Column(T.ArrayType(T.StringType()), nullable=True),
            "publications": Column(T.ArrayType(T.StringType()), nullable=True),
            "labels": Column(T.ArrayType(T.StringType()), nullable=True),
            "international_resource_identifier": Column(T.StringType(), nullable=True),
            "upstream_data_source": Column(T.ArrayType(T.StringType()), nullable=True),
        },
        unique=["id"],
        strict=True,
    )


def get_unioned_edge_schema(validate_enumeration_values: bool = True):
    """Get the Pandera schema for UnionedEdge validation.
    
    Returns a universal schema that works with both pandas and PySpark DataFrames.
    The actual schema type is determined at validation time based on the DataFrame type.
    """
    if not DEPENDENCIES_AVAILABLE:
        error_msg = f"Dependencies not available for Pandera schema. Original error: {IMPORT_ERROR if 'IMPORT_ERROR' in globals() else 'Unknown'}. Install with: pip install 'pandera[pyspark]' pyspark"
        raise ImportError(error_msg)
    
    if validate_enumeration_values:
        predicate_checks = [pa.Check.isin([predicate.value for predicate in PredicateEnum])]
        knowledge_level_checks = [pa.Check.isin([level.value for level in KnowledgeLevelEnum])]
        agent_type_checks = [pa.Check.isin([agent.value for agent in AgentTypeEnum])]
    else:
        predicate_checks = []
        knowledge_level_checks = []
        agent_type_checks = []

    return DataFrameSchema(
        columns={
            "primary_knowledge_sources": Column(T.ArrayType(T.StringType()), nullable=False),
            "subject": Column(T.StringType(), nullable=False),
            "predicate": Column(T.StringType(), nullable=False,
                              checks=predicate_checks),
            "object": Column(T.StringType(), nullable=False),
            "knowledge_level": Column(T.StringType(), nullable=True,
                                    checks=knowledge_level_checks),
            "agent_type": Column(T.StringType(), nullable=True,
                               checks=agent_type_checks),
            "primary_knowledge_source": Column(T.StringType(), nullable=True),
            "aggregator_knowledge_source": Column(T.ArrayType(T.StringType()), nullable=True),
            "publications": Column(T.ArrayType(T.StringType()), nullable=True),
            "subject_aspect_qualifier": Column(T.StringType(), nullable=True),
            "subject_direction_qualifier": Column(T.StringType(), nullable=True),
            "object_aspect_qualifier": Column(T.StringType(), nullable=True),
            "object_direction_qualifier": Column(T.StringType(), nullable=True),
            "upstream_data_source": Column(T.ArrayType(T.StringType()), nullable=True),
            "num_references": Column(T.IntegerType(), nullable=True),
            "num_sentences": Column(T.IntegerType(), nullable=True),
        },
        unique=["subject", "predicate", "object"],
        strict=True,
    )