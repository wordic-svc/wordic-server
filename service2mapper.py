import os
import javalang


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
analysis_result = find_mapper_methods_called_by_service(root_folder)

for item in analysis_result:
    print(item)
