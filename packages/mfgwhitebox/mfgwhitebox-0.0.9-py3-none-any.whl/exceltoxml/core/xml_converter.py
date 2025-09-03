import pandas as pd
from lxml import etree

class XmlConverter:
    def __init__(self, xml_path):
        try:
            self.tree = etree.parse(xml_path)
        except (IOError, etree.XMLSyntaxError) as e:
            raise Exception(f"Error: Cannot parse XML file at {xml_path}. {e}")
        self.root = self.tree.getroot()

    def to_excel(self, excel_path):
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            entities_by_sheet = {}
            for entity in self.root.findall(".//entity"):
                sheet_name = entity.get("component")
                if sheet_name not in entities_by_sheet:
                    entities_by_sheet[sheet_name] = []
                entities_by_sheet[sheet_name].append(entity)

            for sheet_name, entities in entities_by_sheet.items():
                sheet_data = []
                for entity in entities:
                    sheet_data.append(["DataTag", entity.get("type"), entity.get("uri"), entity.get("title"), "实体类", entity.get("className")])

                    fields = ["DataField"]
                    titles = ["DataTitle"]
                    types = ["DataType"]
                    foreign_keys = ["ForeignKey"]
                    has_foreign_key = False
                    
                    attributes = entity.find("attributes")
                    if attributes is not None:
                        for attr in attributes.findall("attribute"):
                            attr_name = attr.get("name")
                            if attr_name:
                                fields.append(attr_name)
                                titles.append(attr.get("title"))
                                attr_type = attr.get("type")
                                if attr.get("isCollection") == "true":
                                    attr_type = f"List<{attr_type}>"
                                types.append(attr_type)
                                fk = attr.get("foreignKey")
                                foreign_keys.append(fk if fk is not None else "")
                                if fk is not None:
                                    has_foreign_key = True
                    
                    sheet_data.append(fields)
                    sheet_data.append(titles)
                    sheet_data.append(types)
                    if has_foreign_key:
                        sheet_data.append(foreign_keys)

                    records = entity.find("records")
                    if records is not None:
                        for record in records.findall("record"):
                            row_data = ["DataRow"]
                            for field in fields[1:]:
                                value = record.get(field)
                                row_data.append(value if value is not None else "")
                            sheet_data.append(row_data)
                    sheet_data.append([])
                
                df = pd.DataFrame(sheet_data)
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)