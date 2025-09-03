import pandas as pd
from lxml import etree
from datetime import datetime
import json
import re

class ExcelConverter:
    def __init__(self, excel_path):
        try:
            # Using pandas to read the excel file
            self.xls = pd.ExcelFile(excel_path)
        except FileNotFoundError:
            raise Exception(f"Error: Excel file not found at {excel_path}")
        self.sheets_data = self._parse_sheets()

    def _parse_sheets(self):
        sheets_data = {}
        for sheet_name in self.xls.sheet_names:
            # Reading each sheet into a DataFrame
            df = pd.read_excel(self.xls, sheet_name=sheet_name, header=None)
            df = df.where(pd.notna(df), None) # replace NaN with None
            sheets_data[sheet_name] = []
            current_entity_data = None

            for _, row_series in df.iterrows():
                row = list(row_series)
                tag = row[0]
                if tag == "DataTag":
                    if len(row) < 6:
                        row.extend([None] * (6 - len(row)))
                    uri_value = row[2].strip() if row[2] else ""
                    class_name = row[5].strip() if row[5] else ""
                    
                    entity_data = {
                        "type": row[1],
                        "uri": uri_value,
                        "title": row[3],
                        "className": class_name,
                        "component": sheet_name,
                        "fields": [], "titles": [], "types": [], "records": [], "foreign_keys": []
                    }
                    sheets_data[sheet_name].append(entity_data)
                    current_entity_data = entity_data
                elif tag == "DataField" and current_entity_data:
                    current_entity_data["fields"] = row[1:]
                elif tag == "DataTitle" and current_entity_data:
                    current_entity_data["titles"] = row[1:]
                elif tag == "DataType" and current_entity_data:
                    current_entity_data["types"] = row[1:]
                elif tag == "ForeignKey" and current_entity_data:
                    current_entity_data["foreign_keys"] = row[1:]
                elif tag == "DataRow" and current_entity_data:
                    current_entity_data["records"].append(row[1:])
        return sheets_data

    def to_xml(self, xml_path):
        datasource = etree.Element("datasource")
        entities_node = etree.SubElement(datasource, "entities")

        for sheet_name, entities_data in self.sheets_data.items():
            for entity_data in entities_data:
                self._process_entity_to_xml(entities_node, entity_data)

        with open(xml_path, 'wb') as f:
            f.write(etree.tostring(datasource, pretty_print=True, xml_declaration=True, encoding='utf-8'))

    def to_json(self, json_path):
        datasource = {"datasource": {"entities": []}}

        for sheet_name, entities_data in self.sheets_data.items():
            for entity_data in entities_data:
                entity_node = self._process_entity_to_dict(entity_data)
                datasource["datasource"]["entities"].append(entity_node)

        pretty_json_str = json.dumps(datasource, indent=4, ensure_ascii=False)

        def reformat_attributes(match):
            indentation = match.group(1)
            attributes_list_str = match.group(2)
            try:
                attributes_list = json.loads(attributes_list_str)
            except json.JSONDecodeError:
                return match.group(0)

            if not attributes_list:
                return f'{indentation}"attributes": []'

            attr_indent = indentation + '    '
            formatted_attributes = [attr_indent + json.dumps(r, ensure_ascii=False) for r in attributes_list]
            return f'{indentation}"attributes": [\n' + ',\n'.join(formatted_attributes) + f'\n{indentation}]'

        def reformat_records(match):
            indentation = match.group(1)
            records_list_str = match.group(2)
            try:
                records_list = json.loads(records_list_str)
            except json.JSONDecodeError:
                return match.group(0)

            if not records_list:
                return f'{indentation}"records": []'

            record_indent = indentation + '    '
            formatted_records = [record_indent + json.dumps(r, ensure_ascii=False) for r in records_list]
            return f'{indentation}"records": [\n' + ',\n'.join(formatted_records) + f'\n{indentation}]'

        attributes_pattern = re.compile(r'^(\s*)"attributes":\s*(\[.*?\])', re.DOTALL | re.MULTILINE)
        records_pattern = re.compile(r'^(\s*)"records":\s*(\[.*?\])', re.DOTALL | re.MULTILINE)
        
        interim_json_str = attributes_pattern.sub(reformat_attributes, pretty_json_str)
        final_json_str = records_pattern.sub(reformat_records, interim_json_str)

        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(final_json_str)

    def _process_entity_to_xml(self, entities_node, entity_data):
        entity_node = etree.SubElement(entities_node, "entity",
                                    uri=str(entity_data.get("uri", "")),
                                    title=str(entity_data.get("title", "")),
                                    type=str(entity_data.get("type", "")),
                                    className=str(entity_data.get("className", "")),
                                    component=str(entity_data.get("component", "")))

        attributes_node = etree.SubElement(entity_node, "attributes")
        original_fields = entity_data.get("fields", [])
        fields = [str(f).replace('$key', '_key') if f is not None else None for f in original_fields]
        titles = entity_data.get("titles", [])
        types = entity_data.get("types", [])
        foreign_keys = entity_data.get("foreign_keys", [])

        for i, field in enumerate(fields):
            if not field or field=='None':
                continue

            title = titles[i] if i < len(titles) and titles[i] is not None else ""
            field_type = types[i] if i < len(types) and types[i] is not None else ""
            is_collection = "false"
            
            if isinstance(field_type, str) and field_type.startswith("List<"):
                is_collection = "true"
                field_type = field_type[5:-1]

            attribute_props = {
                "name": str(field),
                "title": str(title),
                "type": str(field_type)
            }
            if is_collection == "true":
                attribute_props["isCollection"] = is_collection
            
            if i < len(foreign_keys) and foreign_keys[i]:
                attribute_props["foreignKey"] = str(foreign_keys[i])

            etree.SubElement(attributes_node, "attribute", **attribute_props)

        records_node = etree.SubElement(entity_node, "records")
        
        for record_data in entity_data.get("records", []):
            record_node = etree.SubElement(records_node, "record")
            for i, field in enumerate(fields):
                if not field or i >= len(record_data):
                    continue
                value = record_data[i]
                record_node.set(str(field), self._format_date_value(value) if value is not None else "")

    def _process_entity_to_dict(self, entity_data):
        entity_dict = {
            "uri": str(entity_data.get("uri", "")),
            "title": str(entity_data.get("title", "")),
            "type": str(entity_data.get("type", "")),
            "className": str(entity_data.get("className", "")),
            "component": str(entity_data.get("component", "")),
            "attributes": [],
            "records": []
        }

        original_fields = entity_data.get("fields", [])
        fields = [str(f).replace('$key', '_key') if f is not None else None for f in original_fields]
        titles = entity_data.get("titles", [])
        types = entity_data.get("types", [])
        foreign_keys = entity_data.get("foreign_keys", [])

        for i, field in enumerate(fields):
            if not field or field=='None':
                continue

            title = titles[i] if i < len(titles) and titles[i] is not None else ""
            field_type = types[i] if i < len(types) and types[i] is not None else ""
            is_collection = False
            
            if isinstance(field_type, str) and field_type.startswith("List<"):
                is_collection = True
                field_type = field_type[5:-1]

            attribute_props = {
                "name": str(field),
                "title": str(title),
                "type": str(field_type)
            }
            if is_collection:
                attribute_props["isCollection"] = True
            
            if i < len(foreign_keys) and foreign_keys[i]:
                attribute_props["foreignKey"] = str(foreign_keys[i])

            entity_dict["attributes"].append(attribute_props)

        for record_data in entity_data.get("records", []):
            record_dict = {}
            for i, field in enumerate(fields):
                if not field or i >= len(record_data):
                    continue
                value = record_data[i]
                record_dict[str(field)] = self._format_date_value(value) if value is not None else None
            entity_dict["records"].append(record_dict)
            
        return entity_dict

    def _format_date_value(self, value):
        if isinstance(value, datetime):
            if value.hour == 0 and value.minute == 0 and value.second == 0 and value.microsecond == 0:
                return value.strftime("%Y-%m-%d")
            else:
                return value.strftime("%Y-%m-%d %H:%M:%S")
        # Handle pandas NaT
        if pd.isna(value):
            return ""
        return str(value)
