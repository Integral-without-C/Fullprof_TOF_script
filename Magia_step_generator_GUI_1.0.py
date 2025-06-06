class StepConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magia_Step_Generator_v1.0")
        self.resize(1200, 700)
        self.param_lib = []
        self.steps = []
        self.instrument_params = []
        self.bg_params = []
        self.phase_param_dict = defaultdict(list)
        self.phase_group_dict = defaultdict(lambda: defaultdict(list))
        self.current_step_length = 1.00
        self.param_id_map = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        self.load_param_btn = QPushButton("加载参数库")
        self.load_param_btn.clicked.connect(self.load_param_json)
        top_layout.addWidget(self.load_param_btn)
        self.load_step_btn = QPushButton("导入步骤")
        self.load_step_btn.clicked.connect(self.import_steps)
        top_layout.addWidget(self.load_step_btn)
        self.save_step_btn = QPushButton("导出步骤")
        self.save_step_btn.clicked.connect(self.export_steps)
        top_layout.addWidget(self.save_step_btn)
        self.export_table_btn = QPushButton("导出步骤表格内容")
        self.export_table_btn.clicked.connect(self.export_step_table_to_txt)
        top_layout.addWidget(self.export_table_btn)        
        top_layout.addStretch()
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.clicked.connect(self.batch_delete_steps)
        top_layout.addWidget(self.batch_delete_btn)
        self.batch_copy_btn = QPushButton("批量复制")
        self.batch_copy_btn.clicked.connect(self.batch_copy_steps)
        top_layout.addWidget(self.batch_copy_btn)
        top_layout.addWidget(QLabel("统一步长:"))
        self.step_length_box = QDoubleSpinBox()
        self.step_length_box.setDecimals(2)
        self.step_length_box.setRange(0.01, 99.99)
        self.step_length_box.setValue(self.current_step_length)
        self.step_length_box.valueChanged.connect(self.on_step_length_changed)
        top_layout.addWidget(self.step_length_box)
        self.batch_step_length_btn = QPushButton("批量应用步长")
        self.batch_step_length_btn.clicked.connect(self.batch_apply_step_length)
        top_layout.addWidget(self.batch_step_length_btn)
        self.add_step_btn = QPushButton("添加步骤")
        self.add_step_btn.clicked.connect(self.add_step)
        top_layout.addWidget(self.add_step_btn)
        self.reset_all_btn = QPushButton("重置所有参数")
        self.reset_all_btn.clicked.connect(self.reset_all_params)
        top_layout.addWidget(self.reset_all_btn)
        main_layout.addLayout(top_layout)
        self.inst_bg_scroll = QScrollArea()
        self.inst_bg_scroll.setWidgetResizable(True)
        self.inst_bg_scroll.setFixedHeight(200)
        self.inst_bg_widget = QWidget()
        self.inst_bg_layout = QHBoxLayout(self.inst_bg_widget)
        self.inst_bg_layout.setContentsMargins(0, 0, 0, 0)
        self.inst_bg_scroll.setWidget(self.inst_bg_widget)
        main_layout.addWidget(self.inst_bg_scroll)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, stretch=2)
        self.step_table = QTableWidget()
        self.step_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.step_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.step_table.setWordWrap(True)
        self.step_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.step_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.step_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        main_layout.addWidget(self.step_table, stretch=3)
    def export_step_table_to_txt(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出表格内容", "", "Text Files (*.txt)")
        if not file_path:
            return
        lines = []
        headers = ["步骤名称", "  参数名称序列  ", "value序列"]
        lines.append("\t".join(headers))
        for step in self.steps:
            name = step["name"]
            param_names = [self.get_param_name(param["id"]) for param in step["active_params"]]
            param_names_str = "             \n".join(param_names)
            value_str = "\n".join([f"                  {param['value']:.2f}" for param in step["active_params"]])
            lines.append(f"{name}\t{param_names_str}\t{value_str}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        QMessageBox.information(self, "导出成功", f"表格内容已保存到 {file_path}")    
    def load_param_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择参数库JSON", "", "JSON Files (*.json)")
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.param_lib = data.get("parameters_library", [])
        self.instrument_params = []
        self.bg_params = []
        self.phase_param_dict.clear()
        self.phase_group_dict.clear()
        self.param_id_map.clear()
        is_xrd = any(p.get("name", "").startswith("d_") for p in self.param_lib)
        for p in self.param_lib:
            pname = p.get("name", "")
            if "phase" not in p and "group" not in p:
                if is_xrd:
                    if pname.startswith("d_"):
                        self.bg_params.append(p)
                    else:
                        self.instrument_params.append(p)
                else:
                    if pname.startswith("BG"):
                        self.bg_params.append(p)
                    else:
                        self.instrument_params.append(p)
            elif "phase" in p and "group" in p:
                if p["group"] != "原子参数":
                    p["name"] = f"{p['name']}_{p['phase']}"
                self.phase_param_dict[p["phase"]].append(p)
                self.phase_group_dict[p["phase"]][p["group"]].append(p)
            if "id" in p:
                self.param_id_map[p["id"]] = p
        self.refresh_inst_bg_checkboxes()
        self.refresh_param_tabs()
        self.refresh_step_table()
    def refresh_inst_bg_checkboxes(self):
        for i in reversed(range(self.inst_bg_layout.count())):
            widget = self.inst_bg_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.inst_checkboxes = {}
        inst_group = QGroupBox("仪器参数")
        inst_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("全选")
        select_btn.clicked.connect(lambda: self.select_group_checkboxes(self.inst_checkboxes))
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(lambda: self.reset_group_checkboxes(self.inst_checkboxes))
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        inst_layout.addLayout(btn_layout)
        for p in self.instrument_params:
            cb = QCheckBox(p.get("name", ""))
            cb.param_id = p.get("id", None)
            self.inst_checkboxes[p.get("id", None)] = cb
            inst_layout.addWidget(cb)
        inst_group.setLayout(inst_layout)
        self.inst_bg_layout.addWidget(inst_group)
        self.bg_checkboxes = {}
        bg_group = QGroupBox("背底参数")
        bg_layout = QVBoxLayout()
        btn_layout2 = QHBoxLayout()
        select_btn2 = QPushButton("全选")
        select_btn2.clicked.connect(lambda: self.select_group_checkboxes(self.bg_checkboxes))
        reset_btn2 = QPushButton("重置")
        reset_btn2.clicked.connect(lambda: self.reset_group_checkboxes(self.bg_checkboxes))
        btn_layout2.addWidget(select_btn2)
        btn_layout2.addWidget(reset_btn2)
        btn_layout2.addStretch()
        bg_layout.addLayout(btn_layout2)
        for p in self.bg_params:
            cb = QCheckBox(p.get("name", ""))
            cb.param_id = p.get("id", None)
            self.bg_checkboxes[p.get("id", None)] = cb
            bg_layout.addWidget(cb)
        bg_group.setLayout(bg_layout)
        self.inst_bg_layout.addWidget(bg_group)
    def refresh_param_tabs(self):
        self.tab_widget.clear()
        self.phase_checkboxes = defaultdict(lambda: defaultdict(dict))  # phase -> group -> param_id -> checkbox
        for phase in sorted(self.phase_group_dict.keys()):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            group_dict = self.phase_group_dict[phase]
            for group in ["全局参数", "峰型参数", "晶胞参数", "不对称与择优参数", "吸收矫正参数", "原子参数"]:
                if group not in group_dict:
                    continue
                group_box = QGroupBox(group)
                group_layout = QVBoxLayout()
                btn_layout = QHBoxLayout()
                select_btn = QPushButton("全选")
                select_btn.setMaximumWidth(60)
                select_btn.clicked.connect(lambda _, ph=phase, gr=group: self.select_phase_group_checkboxes(ph, gr))
                reset_btn = QPushButton("重置")
                reset_btn.setMaximumWidth(60)
                reset_btn.clicked.connect(lambda _, ph=phase, gr=group: self.reset_phase_group_checkboxes(ph, gr))
                btn_layout.addWidget(select_btn)
                btn_layout.addWidget(reset_btn)
                btn_layout.addStretch()
                group_layout.addLayout(btn_layout)
                for param in group_dict[group]:
                    cb = QCheckBox(param.get("name", ""))
                    cb.param_id = param.get("id", None)
                    self.phase_checkboxes[phase][group][param.get("id", None)] = cb
                    group_layout.addWidget(cb)
                group_box.setLayout(group_layout)
                tab_layout.addWidget(group_box)
            tab_layout.addStretch()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            tab_content = QWidget()
            tab_content.setLayout(tab_layout)
            scroll.setWidget(tab_content)
            self.tab_widget.addTab(scroll, f"phase{phase}")
    def select_group_checkboxes(self, checkbox_dict):
        for cb in checkbox_dict.values():
            cb.setChecked(True)
    def reset_group_checkboxes(self, checkbox_dict):
        for cb in checkbox_dict.values():
            if cb.isChecked():
                cb.setChecked(False)
    def select_phase_group_checkboxes(self, phase, group):
        for cb in self.phase_checkboxes[phase][group].values():
            cb.setChecked(True)
    def reset_phase_group_checkboxes(self, phase, group):
        for cb in self.phase_checkboxes[phase][group].values():
            if cb.isChecked():
                cb.setChecked(False)
    def reset_all_params(self):
        for cb in self.inst_checkboxes.values():
            if cb.isChecked():
                cb.setChecked(False)
        for cb in self.bg_checkboxes.values():
            if cb.isChecked():
                cb.setChecked(False)
        for phase in self.phase_checkboxes:
            for group in self.phase_checkboxes[phase]:
                for cb in self.phase_checkboxes[phase][group].values():
                    if cb.isChecked():
                        cb.setChecked(False)
    def get_checked_param_ids(self):
        checked_ids = []
        for pid, cb in self.inst_checkboxes.items():
            if cb.isChecked():
                checked_ids.append(pid)
        for pid, cb in self.bg_checkboxes.items():
            if cb.isChecked():
                checked_ids.append(pid)
        for phase in self.phase_checkboxes:
            for group in self.phase_checkboxes[phase]:
                for pid, cb in self.phase_checkboxes[phase][group].items():
                    if cb.isChecked():
                        checked_ids.append(pid)
        return checked_ids
    def add_step(self):
        checked_ids = self.get_checked_param_ids()
        if not checked_ids:
            QMessageBox.warning(self, "提示", "请先勾选参数")
            return
        step_idx = len(self.steps) + 1
        step_name = f"Step{step_idx}"
        step_length = self.current_step_length
        step_params = []
        for i, pid in enumerate(checked_ids):
            value = self.generate_value(i, step_length)
            step_params.append({"id": pid, "value": value})
        self.steps.append({"name": step_name, "active_params": step_params})
        self.refresh_step_table()

    def generate_value(self, order, step_length):
        int_part = (order + 1) * 10
        value = float(f"{int_part + step_length:.2f}")
        return value

    def on_step_length_changed(self, val):
        self.current_step_length = float(val)
    def batch_apply_step_length(self):
        selected_rows = self.get_selected_step_rows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先勾选要批量修改步长的步骤")
            return
        for row in selected_rows:
            step = self.steps[row]
            for i, param in enumerate(step["active_params"]):
                int_part = int(float(param["value"]) // 10 * 10)
                param["value"] = float(f"{int_part + self.current_step_length:.2f}")
        self.refresh_step_table()

    def refresh_step_table(self):
        self.step_table.blockSignals(True)
        self.step_table.setColumnCount(4)
        self.step_table.setHorizontalHeaderLabels(["选择", "步骤名称", "参数名称序列", "value序列"])
        self.step_table.setRowCount(len(self.steps))
        for row, step in enumerate(self.steps):
            cb = QCheckBox()
            cb.setChecked(False)
            self.step_table.setCellWidget(row, 0, cb)
            # 步骤名称（可编辑）
            name_item = QTableWidgetItem(step["name"])
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.step_table.setItem(row, 1, name_item)
            # 参数名称序列（纵向排列）
            param_names = []
            for param in step["active_params"]:
                pid = param["id"]
                pname = self.get_param_name(pid)
                param_names.append(pname)
            param_names_str = "\n".join(param_names)
            param_item = QTableWidgetItem(param_names_str)
            param_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            param_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.step_table.setItem(row, 2, param_item)
            value_str = "\n".join([f"{param['value']:.2f}" for param in step["active_params"]])
            value_item = QTableWidgetItem(value_str)
            value_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            value_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.step_table.setItem(row, 3, value_item)
        self.step_table.resizeRowsToContents()
        self.step_table.blockSignals(False)
        self.step_table.cellChanged.connect(self.on_step_table_cell_changed)

    def on_step_checkbox_changed(self):
        pass

    def get_selected_step_rows(self):
        selected = []
        for row in range(self.step_table.rowCount()):
            cb = self.step_table.cellWidget(row, 0)
            if cb and cb.isChecked():
                selected.append(row)
        return selected

    def batch_delete_steps(self):
        rows = sorted(self.get_selected_step_rows(), reverse=True)
        if not rows:
            QMessageBox.warning(self, "提示", "请先勾选要删除的步骤")
            return
        for row in rows:
            if 0 <= row < len(self.steps):
                del self.steps[row]
        self.refresh_step_table()

    def batch_copy_steps(self):
        rows = self.get_selected_step_rows()
        if not rows:
            QMessageBox.warning(self, "提示", "请先勾选要复制的步骤")
            return
        import copy
        offset = 0
        for row in rows:
            idx = row + 1 + offset
            new_step = copy.deepcopy(self.steps[row])
            new_step["name"] = f"{new_step['name']}_copy"
            self.steps.insert(idx, new_step)
            offset += 1
        self.refresh_step_table()

    def on_step_table_cell_changed(self, row, col):
        if col == 1:
            new_name = self.step_table.item(row, 1).text()
            self.steps[row]["name"] = new_name
        elif col == 3:
            value_str = self.step_table.item(row, 3).text()
            value_list = [v.strip() for v in value_str.split("\n")]
            for i, v in enumerate(value_list):
                try:
                    self.steps[row]["active_params"][i]["value"] = float(v)
                except Exception:
                    pass
    def delete_step(self):
        btn = self.sender()
        row = btn.property("row")
        if row is not None and 0 <= row < len(self.steps):
            del self.steps[row]
            self.refresh_step_table()

    def copy_step(self):
        btn = self.sender()
        row = btn.property("row")
        if row is not None and 0 <= row < len(self.steps):
            import copy
            new_step = copy.deepcopy(self.steps[row])
            new_step["name"] = f"{new_step['name']}_copy"
            self.steps.insert(row+1, new_step)
            self.refresh_step_table()

    def get_param_name(self, pid):
        param = self.param_id_map.get(pid, {})
        return param.get("name", f"ID{pid}")

    def import_steps(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入步骤JSON", "", "JSON Files (*.json)")
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.steps = data.get("steps", [])
        self.refresh_step_table()

    def export_steps(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出步骤JSON", "", "JSON Files (*.json)")
        if not file_path:
            return
        out = {"steps": self.steps}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "导出成功", f"已保存到 {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StepConfigGUI()
    win.show()
    sys.exit(app.exec_())
