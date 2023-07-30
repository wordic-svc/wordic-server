import os
import xml.etree.ElementTree as ET
import mybatis_mapper2sql
from sql_metadata import Parser
from concurrent.futures import ThreadPoolExecutor

def extract_table_names_from_sql(sql):
    return Parser(sql).tables

def parse_xml_file(xml_file_path):
    result = []

    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        namespace = root.get('namespace')
        if namespace:
            interface_name = namespace.split('.')[-1]

            # mybatis-mapper2sql 라이브러리를 사용하여 SQL 문을 파싱
            mapper, _ = mybatis_mapper2sql.create_mapper(xml=xml_file_path)
            methods = {}

            try:
                for method_name, element in mapper.items():
                    if element.text.strip() == '':
                        continue
                    statement = mybatis_mapper2sql.get_statement(mapper, result_type='raw', reindent=True, strip_comments=True)
                    table_names = extract_table_names_from_sql(statement)
                    methods[method_name] = table_names

                result.append({
                    'name': xml_file_path,
                    'interface': interface_name,
                    'method': methods
                })
            except Exception as e:
                print(f"Error parsing XML file: {xml_file_path}: {e}")
    except ET.ParseError:
        print(f"Error parsing XML file: {xml_file_path}")

    return result

def parse_xml_files_subset(xml_files_subset):
    results = []
    for xml_file_path in xml_files_subset:
        results.extend(parse_xml_file(xml_file_path))
    return results

# 기존의 parse_xml_file 함수는 동일하게 유지합니다.

def find_mybatis_xml_files_and_parse_namespace(root_folder):
    xml_files_info = []

    xml_files = []
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.xml') and ('mapper' in foldername or 'mybatis' in foldername):
                xml_files.append(os.path.join(foldername, filename))

    # XML 파일 리스트를 10개의 부분으로 나눕니다.
    num_threads = 5
    chunk_size = len(xml_files) // num_threads
    chunks = [xml_files[i:i + chunk_size] for i in range(0, len(xml_files), chunk_size)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(parse_xml_files_subset, chunks))

    # 결과를 결합합니다.
    for res in results:
        xml_files_info.extend(res)

    return xml_files_info

root_folder = '/Users/doheyonkim/Depot/if-api'
xml_files_info = find_mybatis_xml_files_and_parse_namespace(root_folder)

print("Parsed MyBatis XML files:")
for info in xml_files_info:
    print(info)
