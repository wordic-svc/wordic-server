import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Java Analysis Tool')

        # Layout and Widgets
        vbox = QVBoxLayout()
        self.text_edit = QTextEdit()
        btn_controller = QPushButton('Show Controller to Service Result')
        btn_service = QPushButton('Show Service to Mapper Result')
        btn_mapper = QPushButton('Show Mapper to Table Result')
        btn_final = QPushButton('Show Final Result')

        # Connect buttons to functions
        btn_controller.clicked.connect(self.show_controller_to_service)
        btn_service.clicked.connect(self.show_service_to_mapper)
        btn_mapper.clicked.connect(self.show_mapper_to_table)
        btn_final.clicked.connect(self.show_final_result)

        # Add widgets to layout
        vbox.addWidget(self.text_edit)
        vbox.addWidget(btn_controller)
        vbox.addWidget(btn_service)
        vbox.addWidget(btn_mapper)
        vbox.addWidget(btn_final)

        self.setLayout(vbox)
        self.resize(600, 400)
        self.show()

    def show_controller_to_service(self):
        result = find_rest_methods_referencing_service(root_folder)
        self.text_edit.clear()
        self.text_edit.append("===== Controller to Service Result =====")
        for item in result:
            self.text_edit.append(str(item))

    def show_service_to_mapper(self):
        result = find_mapper_methods_called_by_service(root_folder)
        self.text_edit.clear()
        self.text_edit.append("===== Service to Mapper Result =====")
        for item in result:
            self.text_edit.append(str(item))

    def show_mapper_to_table(self):
        result = find_mybatis_xml_files_and_parse_namespace(root_folder)
        self.text_edit.clear()
        self.text_edit.append("===== Mapper to Table Result =====")
        for item in result:
            self.text_edit.append(str(item))

    def show_final_result(self):
        # 여기서는 위에서 정의한 final_result 변수를 사용합니다.
        global final_result
        self.text_edit.clear()
        for item in final_result:
            self.text_edit.append(str(item))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
