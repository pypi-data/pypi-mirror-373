import csv
import io
from typing import Any, Dict, List

import jsonpickle  # type: ignore
import yaml
from pydantic import BaseModel


# Checks if a field is a non-complex field using the value
def Is_Non_Complex_Field_Check_By_Value(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool, type(None)))


# Checks if a field is a non-complex field using the type.. note this is not a foolproof method and is based on the assumption that the field is a complex type with RootModel in the name
def Is_Non_Complex_Field_Check_By_Type(
    field_type: Any, root_model_name: str = "RootModel"
) -> bool:
    if root_model_name in str(field_type):
        return False
    else:
        return True


class FieldData(BaseModel):
    FieldName: str
    FieldType: str


def Get_Model_Properties(model: Any) -> List[FieldData]:
    properties: List[FieldData] = list()
    for field_name, field in model.model_fields.items():
        f: FieldData = FieldData(FieldName=field_name, FieldType=str(field.annotation))
        properties.append(f)
    return properties


def Dict_To_Csv(obj: Dict[str, Any], row_header_columns: List[str], name: str) -> str:
    output: str = "``` csv\n"
    csv_output: io.StringIO = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(row_header_columns)
    for row in obj.values():
        writer.writerow([row[key] for key in row_header_columns])
    output += csv_output.getvalue() + "\n```"
    return output


def List_To_Csv(obj: List[Any], row_header_columns: List[str], name: str) -> str:
    output: str = "``` csv\n"
    csv_output: io.StringIO = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(row_header_columns)
    for row in obj:
        if not isinstance(row, dict):
            try:
                row = row.__dict__
            except Exception:
                print(f"Could not convert {row} to dictionary")
        writer.writerow([row[key] for key in row_header_columns])
    output += csv_output.getvalue() + "\n```"
    return output


def Listable_Object_To_Csv(obj: List[Any], row_type: Any) -> str:
    output: str = "``` csv\n"
    csv_output: io.StringIO = io.StringIO()
    writer = csv.writer(csv_output)
    headers: List[str] = [
        prop.FieldName
        for prop in Get_Model_Properties(row_type)
        if Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
    ]
    writer.writerow(headers)
    for row in obj:
        writer.writerow([getattr(row, header, None) for header in headers])
    output += csv_output.getvalue() + "\n```"
    return output


def Object_To_Yaml(obj: Any, strip_complex_fields: bool = False) -> str:
    obj_dict: Dict[str, Any] = obj.__dict__
    output: str = "``` yaml\n"
    if strip_complex_fields:
        obj_dict = {
            k: v
            for k, v in obj.__dict__.items()
            if Is_Non_Complex_Field_Check_By_Value(v)
        }
    yaml_output: str = yaml.dump(obj_dict, default_flow_style=False)
    return output + yaml_output + "\n```"


def Object_To_Markdown(obj: Any, name: str) -> str:
    val: str = jsonpickle.dumps(obj)
    return val
