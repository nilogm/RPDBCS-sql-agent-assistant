import json
from pydantic import Field
from typing import Annotated
from dataclasses import dataclass


@dataclass
class TableSchema:
    table_schema: Annotated[str, Field(description="Nome, descrição e colunas de uma tabela no banco de dados")]
    foreign_keys: Annotated[str, Field(description="Chaves estrangeiras da tabela")]
    samples: Annotated[list[str], Field(description="Exemplos de linhas da tabela")]


def check_schema(table: Annotated[str, Field(description="Nome de uma tabela no banco de dados")]) -> TableSchema:
    """Retorna informações sobre uma tabela específica no banco de dados."""
    with open("schema.json", "r", encoding="utf-8") as f:
        data: dict = json.load(f)

    if table not in data["tables"]:
        raise ValueError(f"Table '{table}' not in the database!")

    table_dict = data["tables"][table]

    with open("system__agent_configs.json", "r", encoding="utf-8") as f:
        configs: dict = json.load(f)
        use_comments = configs["add_schema_comments"]

    schema = []
    schema.append("Table: " + table)
    if "hint" in table and len(table["hint"]) > 0 and use_comments:
        schema.append(f"\tDescription: {table['hint']}")
    for item in table_dict["columns"]:
        if use_comments:
            hint = item["hint"] if "hint" in item and len(item["hint"]) else ""
            schema.append(f"- {item['name']}: {hint}")
        else:
            schema.append(f"- {item['name']}")
    schema = "\n".join(schema)

    fks = []
    for fk in table_dict["foreign_keys"]:
        link = f"{table}({fk['column']}) references {fk['references_table']}({fk['references_column']})"
        fks.append(link)
    fks = "\n".join(fks)

    samples = []
    for sample in data["tables"][table]["examples"]:
        items = []
        for k, v in sample.items():
            max_chars = 30
            if len(str(v)) < max_chars:
                items.append(f"{k}[{v}]")
            else:
                items.append(f"{k}[{v[:max_chars]}...]")
        samples.append(f"{table}({', '.join(items)})")

    return TableSchema(table_schema=schema, foreign_keys=fks, samples=samples)
