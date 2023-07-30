import os
import javalang


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

                                    class_base_url = ''
                                    for annotation in type_declaration.annotations:
                                        if annotation.name == "RequestMapping":
                                            class_base_url = annotation.element.value.strip('"')

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
                                                        api_url = class_base_url + annotation.element.value
                                                    break

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
                            if isinstance(type_declaration,
                                          javalang.tree.ClassDeclaration) and 'Service' in type_declaration.name:
                                service_name = type_declaration.name

                                # Collect all autowired mappers
                                mapper_fields = []
                                for field in type_declaration.fields:
                                    for declarator in field.declarators:
                                        if 'Mapper' in field.type.name and any(
                                                anno.name == 'Autowired' for anno in field.annotations):
                                            mapper_fields.append(declarator.name)

                                methods_details = []
                                for method in type_declaration.methods:
                                    mappers_called = set()
                                    for _, node in method.filter(javalang.tree.MethodInvocation):
                                        if node.qualifier in mapper_fields:
                                            mappers_called.add(node.qualifier)
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



root_folder = '/Users/doheyonkim/Depot/if-api'
analysis_result = find_rest_methods_referencing_service(root_folder)

for item in analysis_result:
    print(item)
