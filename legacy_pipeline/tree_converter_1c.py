import json

def create_node(title: str, val: str = None, equality: str = None, children: list = None):
    node = {
        "title": title,
        "technicalName": title
    }
    if val is not None:
        node["val"] = val
    if equality is not None:
        node["equality"] = equality
    if children is not None:
        node["children"] = children
    return node

def flat_1c_to_tree_format(flat_1c_schemas: list) -> list:
    """
    Converts a list of flat 1C dictionaries into the nested UI Tree format.
    Focuses exclusively on Class-level properties.
    """
    schema_class_children = []
    
    for i, schema in enumerate(flat_1c_schemas):
        class_idx = i + 1
        
        # 1. Base Class Properties (1C)
        class_props = [
            create_node("SchemaName", val=schema.get("class_name", "")),
            create_node("DataSource", val=schema.get("data_source", "")),
            create_node("DateAggregationOn", val=schema.get("date_aggregation_on", "")),
            create_node("SettlementType", val=schema.get("settlement_type", "")),
            create_node("OutputProcessCode", val=schema.get("output_process_code", ""))
        ]
        
        schema_class_children.append(
            create_node(f"#SchemaClass#{class_idx}", children=class_props)
        )

    # Wrap in the Root structure
    root_structure = [
        create_node("Root", children=[
            create_node("SchemaGroupName", val=flat_1c_schemas[0].get("source_schema", "Generated Process") if flat_1c_schemas else "Generated Process"),
            create_node("SourceSchema", val=flat_1c_schemas[0].get("source_schema", "Generated Process") if flat_1c_schemas else "Generated Process"),
            create_node("SchemaClasses", children=schema_class_children)
        ])
    ]
    
    return root_structure
