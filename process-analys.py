import os
import javalang
import os
import xml.etree.ElementTree as ET
import mybatis_mapper2sql
from sql_metadata import Parser
from concurrent.futures import ThreadPoolExecutor


def find_rest_methods_referencing_service(root_folder):
    result_list = []

    rest_annotations = ["GetMapping", "PostMapping", "PutMapping", "DeleteMapping", "PatchMapping", "RequestMapping"]

    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.java'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                    if 'enum' in content:
                        continue

                    try:
                        tree = javalang.parse.parse(content)
                        for type_declaration in tree.types:
                            if type_declaration.annotations:
                                is_controller_or_restcontroller = any(
                                    annotation.name in ['Controller', 'RestController'] for annotation in
                                    type_declaration.annotations)
                                if is_controller_or_restcontroller:
                                    class_name = type_declaration.name

                                    # 클래스 레벨에서 @RequestMapping 값을 추출합니다.
                                    class_base_url = ''
                                    for annotation in type_declaration.annotations:
                                        if annotation.name == "RequestMapping":
                                            class_base_url = annotation.element.value.strip('"')
                                            if not class_base_url.endswith('/'):
                                                class_base_url += '/'


                                    service_var_to_class = {}
                                    for field in type_declaration.fields:
                                        if field.type and field.type.name.endswith("Service"):
                                            for declarator in field.declarators:
                                                service_var_to_class[declarator.name] = field.type.name

                                    api_info_list = []
                                    for method in type_declaration.methods:
                                        is_rest_method = any(
                                            annotation.name in rest_annotations for annotation in method.annotations)

                                        if is_rest_method:
                                            api_url = None
                                            for annotation in method.annotations:
                                                if annotation.name in rest_annotations:
                                                    if isinstance(annotation.element, list):
                                                        for elem in annotation.element:
                                                            if elem.name == 'value':
                                                                api_url = elem.value.value  # Literal 객체의 value 속성에서 실제 값을 가져옴
                                                                break
                                                    elif annotation.element:
                                                        api_url = annotation.element.value
                                                    break

                                            method_url = (annotation.element.value if annotation.element else "").strip('"')
                                            if method_url.startswith('/'):
                                                method_url = method_url[1:]
                                            api_url = class_base_url + method_url

                                            services_list = []
                                            for path, node in method.filter(javalang.tree.MethodInvocation):
                                                qualifier = node.qualifier
                                                if qualifier in service_var_to_class:
                                                    services_list.append({'name': service_var_to_class[qualifier]})
                                            if api_url:
                                                api_info_list.append({
                                                    'url': api_url,
                                                    'service': services_list
                                                })
                                    if api_info_list:
                                        result_list.append({
                                            'ControllerName': class_name,
                                            'ApiInfo': api_info_list
                                        })
                    except Exception as e:
                        print(f"Error parsing file {file_path}: {e}")

    return result_list

def find_mapper_methods_called_by_service(root_folder):
    result_list = []

    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.java'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                    try:
                        tree = javalang.parse.parse(content)
                        for type_declaration in tree.types:
                            if isinstance(type_declaration, javalang.tree.ClassDeclaration) and 'Service' in type_declaration.name:
                                service_name = type_declaration.name

                                # Collect all autowired mappers by their names and types
                                mapper_dict = {}
                                for field in type_declaration.fields:
                                    if 'Mapper' in field.type.name and any(anno.name == 'Autowired' for anno in field.annotations):
                                        for declarator in field.declarators:
                                            mapper_dict[declarator.name] = field.type.name

                                methods_details = []
                                for method in type_declaration.methods:
                                    mappers_called = set()
                                    for _, node in method.filter(javalang.tree.MethodInvocation):
                                        if node.qualifier in mapper_dict:
                                            mappers_called.add(mapper_dict[node.qualifier])
                                    if mappers_called:
                                        methods_details.append({
                                            'name': method.name,
                                            'mapper': list(mappers_called)
                                        })
                                if methods_details:
                                    result_list.append({
                                        'serviceName': service_name.replace('Impl', ''),
                                        'serviceMethod': methods_details
                                    })
                    except Exception as e:
                        print(f"Error parsing file {file_path}: {e}")

    return result_list
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
                    methods['table'] = table_names
                    methods['name'] = method_name

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
controller_2_service = find_rest_methods_referencing_service(root_folder)

print("===== Controller to Service Result =====")
for item in controller_2_service:
    print(item)

service_2_mapper = find_mapper_methods_called_by_service(root_folder)
print("===== Service to Mapper Result =====")
for item in service_2_mapper:
    print(item)

mapper_2_table = find_mybatis_xml_files_and_parse_namespace(root_folder)
print("===== Mapper to Table Result =====")
for info in mapper_2_table:
    print(info)

final_result = []

for controller in controller_2_service:
    for api_info in controller['ApiInfo']:
        rest_api_url = api_info['url'].strip('"')  # URL에서 따옴표 제거
        target_tables = set()  # 중복 테이블을 방지하기 위한 set

        for service in api_info['service']:
            service_name = service['name']
            # 해당 서비스와 연결된 매퍼를 찾습니다.
            for service_item in service_2_mapper:
                if service_item['serviceName'] == service_name:
                    for method_info in service_item['serviceMethod']:
                        mapper_names = method_info['mapper']

                        # 모든 연관된 매퍼에 대해서 처리
                        for mapper_name in mapper_names:
                            # 해당 매퍼와 연결된 테이블을 찾습니다.
                            for mapper_info in mapper_2_table:
                                if mapper_info['interface'] == mapper_name:
                                    target_tables.update(mapper_info['method']['table'])  # 테이블 리스트 추가

        final_result.append({
            'restApiUrl': rest_api_url,
            'targetTable': list(target_tables)  # set를 list로 변환
        })

for item in final_result:
    print(item)
