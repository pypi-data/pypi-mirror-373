import sys
import os
from exceltoxml.core.excel_converter import ExcelConverter
from exceltoxml.core.xml_converter import XmlConverter
from exceltoxml.core.json_converter import JsonConverter

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python -m exceltoxml.converter <input_file> [output_file]")
        print("If output_file is not provided, it will be inferred based on the input file type.")
        sys.exit(1)

    input_file = sys.argv[1]
    base, input_ext = os.path.splitext(input_file)

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        if input_ext == '.xlsx':
            output_file = base + '.json'
        elif input_ext == '.xml':
            output_file = base + '.xlsx'
        elif input_ext == '.json':
            output_file = base + '.xlsx'
        else:
            print(f"Unsupported input file extension for automatic output file generation: {input_ext}")
            sys.exit(1)

    _, output_ext = os.path.splitext(output_file)

    try:
        if input_ext == '.xlsx' and output_ext == '.xml':
            print(f"Converting {input_file} to {output_file}...")
            converter = ExcelConverter(input_file)
            converter.to_xml(output_file)
            print("Conversion to XML complete.")
        elif input_ext == '.xlsx' and output_ext == '.json':
            print(f"Converting {input_file} to {output_file}...")
            converter = ExcelConverter(input_file)
            converter.to_json(output_file)
            print("Conversion to JSON complete.")
        elif input_ext == '.xml' and output_ext == '.xlsx':
            print(f"Converting {input_file} to {output_file}...")
            converter = XmlConverter(input_file)
            converter.to_excel(output_file)
            print("Conversion to Excel complete.")
        elif input_ext == '.json' and output_ext == '.xlsx':
            print(f"Converting {input_file} to {output_file}...")
            converter = JsonConverter(input_file)
            converter.to_excel(output_file)
            print("Conversion to Excel complete.")
        else:
            print(f"Unsupported conversion from {input_ext} to {output_ext}")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def maintest():
    excel_file = "D:\\hedaima\\mfgwhitebox\\src\\test\\cmp.common.datasource.entity.xlsx"
    json_file ="D:\\hedaima\\mfgwhitebox\\src\\test\\cmp.common.datasource.entity.json"
    xml_file ="D:\\hedaima\\mfgwhitebox\\src\\test\\cmp.common.datasource.entity.xml"
    excel_file_xml = "D:\\hedaima\\mfgwhitebox\\src\\test\\cmp.common.datasource.entity_xml.xlsx"
    excel_file_json = "D:\\hedaima\\mfgwhitebox\\src\\test\\cmp.common.datasource.entity_json.xlsx"
    print(f"Converting {excel_file} to {xml_file}...")
    converter = ExcelConverter(excel_file)
    converter.to_xml(xml_file)
    print("Conversion to XML complete.")

    print(f"Converting {xml_file} to {excel_file_xml}...")
    converter = XmlConverter(xml_file)
    converter.to_excel(excel_file_xml)
    print("Conversion to Excel complete.")

    print(f"Converting {excel_file} to {json_file}...")
    converter = ExcelConverter(excel_file)
    converter.to_json(json_file)
    print("Conversion to JSON complete.")

    print(f"Converting {json_file} to {excel_file_json}...")
    converter = JsonConverter(json_file)
    converter.to_excel(excel_file_json)
    print("Conversion to Excel complete.")


if __name__ == "__main__":
    maintest()