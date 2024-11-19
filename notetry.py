import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QListWidget, QVBoxLayout,
    QHBoxLayout, QWidget, QSplitter, QFileDialog, QToolBar, QAction,
    QLineEdit, QMessageBox, QColorDialog, QFontDialog, QListWidgetItem,QDialog, QPushButton, QInputDialog,
     QLabel, QComboBox, QPushButton
)
import re
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextImageFormat, QTextCursor, QIcon
from PyQt5.QtCore import Qt
import os
from AITOOL import getAI
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QGuiApplication

class FileTextEditor(QMainWindow):
    def adjust_to_screen_resolution(self):
        """根据系统屏幕分辨率调整窗口大小"""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

    # 设置窗口为屏幕的 80% 大小，转换为整数
        self.setGeometry(
            int(screen_width * 0.25),  # 距离左侧 25% 的位置
            int(screen_height * 0.25),  
            int(screen_width * 0.5),  # 宽度占 50%
            int(screen_height * 0.5)  
        )

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件选择与富文本编辑器")
        self.adjust_to_screen_resolution()  # 调整窗口大小
        self.current_file = None

        # 初始化布局和菜单
        self.init_ui()
        
        # 当前打开的文件路径
        self.current_file = None
        
        self.updatefile()
        

    def init_ui(self):
        """初始化界面布局"""
        # 创建左侧文件列表
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.open_selected_file)

        # 添加搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索文件...")
        self.search_box.textChanged.connect(self.filter_files)

        # 将搜索框和文件列表放在一个垂直布局中
        file_list_layout = QVBoxLayout()
        file_list_layout.addWidget(self.search_box)
        file_list_layout.addWidget(self.file_list)

        file_list_widget = QWidget()
        file_list_widget.setLayout(file_list_layout)

        # 创建右侧文本编辑区域，分为康奈尔笔记布局
        # 上半部分，左侧为提示，右侧为笔记
        self.cues_section = QTextEdit()  # 提示部分
        self.cues_section.setPlaceholderText("提示部分")
        self.notes_section = QTextEdit() # 笔记部分
        self.notes_section.setPlaceholderText("笔记部分")
        # 下半部分，总结
        self.summary_section = QTextEdit()  # 总结部分
        self.summary_section.setPlaceholderText("总结部分")
        # 上半部分的布局（左右结构），设置占比
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.cues_section, 1)  # 左侧提示，占 30% 的空间
        top_layout.addWidget(self.notes_section, 3) # 右侧笔记，占 70% 的空间

        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # 下半部分的布局（总结）
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.summary_section)  # 总结

        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        # 创建主布局，右侧部分
        right_layout = QVBoxLayout()
        right_layout.addWidget(top_widget)      # 上半部分（提示和笔记）
        right_layout.addWidget(bottom_widget)   # 下半部分（总结）

        # 设置上下部分之间的间距
        right_layout.setSpacing(0)  # 设置为较小的间距，避免过大的空隙

        # 通过 stretch factor 调整上下部分的比例
        right_layout.setStretch(0, 3)  # 上半部分占 75% 的空间
        right_layout.setStretch(1, 1)  # 下半部分占 25% 的空间

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # 创建分割器，确保文件列表和右侧区域正确显示
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(file_list_widget)  # 左侧文件列表
        splitter.addWidget(right_widget)      # 右侧编辑区
        splitter.setStretchFactor(0, 2)       # 左侧占比
        splitter.setStretchFactor(1, 4)       # 右侧占比

        # 设置中心控件
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        self.create_toolbar()
   
    def show_find_dialog(self):
        """显示查找对话框"""
        find_text, ok = QInputDialog.getText(self, "查找", "输入查找内容:")
        if ok and find_text:
            self.find_text(find_text)

    def find_text(self, text):
        """在文本区域中查找指定内容，若找到则高亮显示否则弹出警告框"""
        found_items = []
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("yellow"))

        case_sensitive = True  
        delimiters = r'[\s,.;，。；！!?？：、“”"'']' 

        for section in [self.cues_section, self.notes_section, self.summary_section]:
            cursor = section.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)
            clear_format = QTextCharFormat()
            clear_format.setBackground(QColor("transparent"))
            cursor.mergeCharFormat(clear_format)
            cursor.setPosition(0)
            text_content = section.toPlainText()
            segments = [seg.strip() for seg in re.split(delimiters, text_content) if seg]
            
            for seg in segments:
                if text in seg:
                    start_index = text_content.find(seg)
                    cursor.setPosition(start_index)
                    cursor.setPosition(start_index + len(seg), QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(highlight_format)
                    found_items.append(seg)

            cursor.endEditBlock()

        if found_items:
            response = QMessageBox.information(self, "找到的内容", f"找到 {len(found_items)} 个相关内容:\n" + "\n".join(found_items), QMessageBox.Ok)
            if response == QMessageBox.Ok:
                for section in [self.cues_section, self.notes_section, self.summary_section]:
                    cursor = section.textCursor()
                    cursor.select(QTextCursor.Document)
                    clear_format = QTextCharFormat()
                    clear_format.setBackground(QColor("transparent"))
                    cursor.mergeCharFormat(clear_format)
        else:
            QMessageBox.warning(self, "未查找到内容", "没有找到相关内容")
        
    def create_toolbar(self):
        """创建工具栏并添加功能项"""
        toolbar = self.menuBar()
        
        # 文件菜单
        file_menu = toolbar.addMenu("文件")
        open_dir_action = QAction("打开", self)
        open_dir_action.setShortcut("Ctrl+O")  # 设置快捷键
        open_dir_action.triggered.connect(self.open_directory)
        file_menu.addAction(open_dir_action)

        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")  # 设置快捷键
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为", self)
        save_as_action.setShortcut("Ctrl+Shift+S")  # 设置快捷键
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        # 选项菜单
        options_menu = toolbar.addMenu("选项")
        font_action = QAction(QIcon("icon.png"),"字体", self)
        font_action.setShortcut("Ctrl+T")  # 设置快捷键
        font_action.triggered.connect(self.set_font)
        options_menu.addAction(font_action)
        
        # 添加粗体按钮
        bold_action = QAction("粗体(B)", self)
        bold_action.setShortcut("Ctrl+B")  # 设置快捷键
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        options_menu.addAction(bold_action)

        # 添加斜体按钮
        italic_action = QAction("斜体(I)", self)
        italic_action.setShortcut("Ctrl+I")  # 设置快捷键
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        options_menu.addAction(italic_action)

        # 添加图片插入按钮
        image_action = QAction("图片(P)", self)
        image_action.setShortcut("Ctrl+P")  # 设置快捷键
        image_action.triggered.connect(self.insert_image)
        options_menu.addAction(image_action)

        color_action = QAction("颜色(C)", self)
        color_action.setShortcut("Ctrl+Shift+C")  # 设置快捷键
        color_action.triggered.connect(self.set_color)
        options_menu.addAction(color_action)

        mark_action = QAction("标记(M)", self)
        mark_action.setShortcut("Ctrl+M")  # 设置快捷键
        mark_action.triggered.connect(self.mark_text)
        options_menu.addAction(mark_action)

        add_review_action = QAction("添加心得(R)", self)
        add_review_action.setShortcut("Ctrl+R")  # 设置快捷键
        add_review_action.triggered.connect(self.add_review)
        options_menu.addAction(add_review_action)

        # 设置菜单（占位）
        settings_menu = toolbar.addMenu("设置")

        # 帮助菜单（占位）
        help_menu = toolbar.addMenu("帮助")
        
        AI_respond_action = QAction("问问AI", self)     # 添加问问AI按钮
        AI_respond_action.setShortcut("Ctrl+Q")  # 设置快捷键
        AI_respond_action.triggered.connect(self.AI_respond)
        help_menu.addAction(AI_respond_action)
          
        # 添加查找按钮
        find_action = QAction("查找", self)
        find_action.setShortcut("Ctrl+F")  # 设置快捷键
        find_action.triggered.connect(self.show_find_dialog)
        help_menu.addAction(find_action)

        # 关于我们菜单（占位）
        about_menu = toolbar.addMenu("关于我们")
        

    def set_font(self):
        """设置字体"""
        font, ok = QFontDialog.getFont(self.notes_section.font(), self, "选择字体")
        if ok:
            self.notes_section.setCurrentFont(font)

    def set_color(self):
        """设置字体颜色"""
        color = QColorDialog.getColor(self.notes_section.textColor(), self, "选择颜色")
        if color.isValid():
            self.notes_section.setTextColor(color)

    
    def AI_respond(self):
        # 获取 QTextCursor 对象
        cursor = self.notes_section.textCursor()
        # 获取选中的文本
        selected_text = cursor.selectedText()
        
        if selected_text:  # 确保有选中文本
            # 获取 AI 回答
            # 创建一个自定义的对话框
            ai_response = getAI(selected_text)

            # 创建一个自定义的对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("AI回答")
            
            # 创建垂直布局
            layout = QVBoxLayout(dialog)

            # 创建一个 QTextEdit 用于显示 AI 的回答，且可复制
            text_edit = QTextEdit(dialog)
            text_edit.setText(ai_response)
            text_edit.setReadOnly(True)  # 设置为只读，防止修改
            layout.addWidget(text_edit)

            # 设置对话框的样式
            dialog.setLayout(layout)
            dialog.setFixedSize(400, 300)  # 设置对话框固定大小
            dialog.exec_()


    def toggle_bold(self):
        """切换粗体"""
        if self.notes_section.fontWeight() == QFont.Bold:
            self.notes_section.setFontWeight(QFont.Normal)
        else:
            self.notes_section.setFontWeight(QFont.Bold)

    def toggle_italic(self):
        """切换斜体"""
        # 切换斜体状态
        self.notes_section.setFontItalic(not self.notes_section.fontItalic())  
        
    def get_current_editor(self):
        """获取当前选中的文本编辑区域"""
        # 你可以通过其他方式来决定当前使用的是哪个编辑区
        # 例如，可以通过点击或焦点设置一个全局变量来跟踪当前的编辑区域
        # 在此示例中假设使用 `notes_section`（或者你可以使用一个标志位）
        return self.notes_section  # 或者返回如 `self.cues_section` 或 `self.summary_section`

    
    def insert_image(self):
        """插入图片并设置初始大小"""
        image_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图像文件 (*.png *.jpg *.bmp *.gif)")
        if image_path:
            cursor = self.notes_section.textCursor()
            image_format = QTextImageFormat()
            image_format.setName(image_path)
            image_format.setWidth(300)
            image_format.setHeight(300)
            cursor.insertImage(image_format)

    def new_directory(self):
        file_base_path = "E:"  # 保存的目录路径
        # 打开保存文件对话框，允许用户指定文件名
        file_name, ok = QInputDialog.getText(self, "输入文件名", "请输入文件名（不包括扩展名）:")
        if not ok or not file_name:
            # 如果用户没有输入文件名，则退出
            return

        # 构建文件路径（使用用户输入的文件名）
        file_path = os.path.join(file_base_path, f"{file_name}.html")
        
        # 获取文件的基础名称并构建其他保存路径
        file_base_name = file_name  # 使用用户输入的文件名作为基本名称
        if not file_path:
            # 如果用户取消了保存对话框，则退出
            return

        # 获取文件的基础名称并构建其他保存路径
        file_base_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            # 保存 HTML 文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.notes_section.toHtml())
                self.current_file = file_path  # 更新当前文件路径
                QMessageBox.information(self, "成功", f"文件已保存到:\n{file_path}")

            # 保存self.cues_section的内容为 .cues 文件
            cues_file_path = os.path.join(file_base_path, f"{file_base_name}.cues")
            with open(cues_file_path, 'w', encoding='utf-8') as cues_file:
                cues_file.write(self.cues_section.toHtml())

            # 保存self.summary_section的内容为 .summary 文件
            summary_file_path = os.path.join(file_base_path, f"{file_base_name}.summary")
            with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                summary_file.write(self.summary_section.toHtml())
            self.updatefile()
            
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"发生错误: {str(e)}")



    def open_directory(self):
        """打开目录并加载文件到左侧列表"""
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        print(directory)
        if directory:
            self.file_list.clear()
            for file_name in os.listdir(directory):
                if file_name.endswith((".html")):
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, os.path.join(directory, file_name))
                    self.file_list.addItem(item)

    def updatefile(self):
        directory = "E:\\"
        if directory:
            self.file_list.clear()
            for file_name in os.listdir(directory):
                if file_name.endswith((".html")):
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, os.path.join(directory, file_name))
                    self.file_list.addItem(item)

    def filter_files(self, text):
        """过滤文件列表"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())


    def load_file_content(self, file_path, target_widget):
        """加载文件内容到目标小部件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                target_widget.setHtml(content)
        except Exception as e:
            QMessageBox.warning(self, "加载文件失败", f"无法加载文件内容: {e}")


    def open_selected_file(self, item):
        """打开左侧选择的文件"""
        file_path = item.data(Qt.UserRole)
        file_base_name, _ = os.path.splitext(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.notes_section.setHtml(content)
                self.current_file = file_path
            cues_file_path = f"{file_base_name}.cues"
            with open(cues_file_path, 'r', encoding='utf-8') as cues_file:
                content = cues_file.read()
                self.cues_section.setHtml(content)
            cues_file_path = f"{file_base_name}.summary"
            with open(cues_file_path, 'r', encoding='utf-8') as summary_file:
                content = summary_file.read()
                self.summary_section.setHtml(content)

        except Exception as e:
            a=1
            #QMessageBox.critical(self, "错误", f"无法打开文件:\n{e}")

    def save_file(self):
        """保存当前编辑内容到文件"""
        if not self.current_file:
            self.save_file_as()
        else:
            try:
                file_base_name, _ = os.path.splitext(self.current_file)

                # 保存self.notes_section的内容为 HTML 文件
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.notes_section.toHtml())
                    QMessageBox.information(self, "成功", f"文件已保存到:\n{self.current_file}")

                # 保存self.cues_section的内容为 .cues 文件
                cues_file_path = f"{file_base_name}.cues"
                with open(cues_file_path, 'w', encoding='utf-8') as cues_file:
                    cues_file.write(self.cues_section.toHtml())

                # 保存self.summary_section的内容为 .summary 文件
                summary_file_path = f"{file_base_name}.summary"
                with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                    summary_file.write(self.summary_section.toHtml())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件:\n{e}")

    def save_file_as(self):
        """另存为文件"""
        file_base_path = "E:"  # 保存的目录路径
        # 打开保存文件对话框，允许用户指定文件名
        file_name, ok = QInputDialog.getText(self, "输入文件名", "请输入文件名（不包括扩展名）:")
        if not ok or not file_name:
            # 如果用户没有输入文件名，则退出
            return

        # 构建文件路径（使用用户输入的文件名）
        file_path = os.path.join(file_base_path, f"{file_name}.html")
        
        # 获取文件的基础名称并构建其他保存路径
        file_base_name = file_name  # 使用用户输入的文件名作为基本名称
        if not file_path:
            # 如果用户取消了保存对话框，则退出
            return

        # 获取文件的基础名称并构建其他保存路径
        file_base_name = os.path.splitext(os.path.basename(file_path))[0]
        if file_path:
            try:
                # 获取文件名的基础部分（不带扩展名）
                file_base_name, _ = os.path.splitext(file_path)

                # 保存self.notes_section的内容为 HTML 文件
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.notes_section.toHtml())
                    self.current_file = file_path  # 更新当前文件路径
                    QMessageBox.information(self, "成功", f"文件已保存到:\n{file_path}")

                # 保存self.cues_section的内容为 .cues 文件
                cues_file_path = f"{file_base_name}.cues"
                with open(cues_file_path, 'w', encoding='utf-8') as cues_file:
                    cues_file.write(self.cues_section.toHtml())

                # 保存self.summary_section的内容为 .summary 文件
                summary_file_path = f"{file_base_name}.summary"
                with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                    summary_file.write(self.summary_section.toHtml())
                self.updatefile()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件:\n{e}")

    def add_review(self):
        """添加心得体会"""
        review_dialog = QDialog(self)
        review_dialog.setWindowTitle("添加心得体会")
        layout = QVBoxLayout()

        review_text_edit = QTextEdit()
        review_text_edit.setPlaceholderText("请输入心得体会...")

        save_button = QPushButton("保存")
        save_button.clicked.connect(lambda: self.save_review(review_text_edit.toPlainText(), review_dialog))

        layout.addWidget(review_text_edit)
        layout.addWidget(save_button)

        review_dialog.setLayout(layout)
        review_dialog.exec_()

    def save_review(self, review_text, dialog):
        """保存心得体会"""
        if review_text.strip():
            self.summary_section.append(f"<b>心得体会：</b><br>{review_text}<br><br>")
            dialog.accept()
            QMessageBox.information(self, "保存成功", "心得体会已保存到笔记中")
        else:
            QMessageBox.warning(self, "输入为空", "请输入心得体会内容")

    def mark_text(self):
        """标记选中的文本"""
        cursor = self.notes_section.textCursor()
        if not cursor.hasSelection():
            QMessageBox.warning(self, "无选中文本", "请先选择一段文本进行标记")
            return

        mark_dialog = QDialog(self)
        mark_dialog.setWindowTitle("选择标记类型")
        layout = QVBoxLayout()

        mark_label = QLabel("选择标记类型：")
        mark_combobox = QComboBox()
        mark_combobox.addItems(["重点", "难点", "注意", "取消标记"])

        mark_button = QPushButton("应用标记")
        mark_button.clicked.connect(lambda: self.apply_mark(cursor, mark_combobox.currentText(), mark_dialog))

        layout.addWidget(mark_label)
        layout.addWidget(mark_combobox)
        layout.addWidget(mark_button)

        mark_dialog.setLayout(layout)
        mark_dialog.exec_()

    def apply_mark(self, cursor, mark_type, dialog):
        """应用标记到选中的文本"""
        if mark_type == "取消标记":
            cursor.setCharFormat(QTextCharFormat())  # 取消标记
        else:
            cursor.mergeCharFormat(self.create_mark_format(mark_type))
        dialog.accept()

    def create_mark_format(self, mark_type):
        """根据标记类型创建相应的格式"""
        mark_format = QTextCharFormat()
        if mark_type == "重点":
            mark_format.setBackground(QColor("yellow"))
            mark_format.setFontWeight(QFont.Bold)
        elif mark_type == "难点":
            mark_format.setBackground(QColor("lightcoral"))
            mark_format.setFontItalic(True)
        elif mark_type == "注意":
            mark_format.setBackground(QColor("lightgreen"))
        return mark_format

    def apply_styles(self):
        """应用统一样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
            QToolBar {
                background-color: #f0f0f0;
                border: none;
            }
            QToolButton {
                background-color: #e6e6e6;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #d9d9d9;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = FileTextEditor()
    editor.show()
    sys.exit(app.exec_())