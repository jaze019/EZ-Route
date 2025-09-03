import sys
import re
import time
import qtawesome as qta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QStackedWidget,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

DARK_STYLE = """
/* ---- Global Styles ---- */
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: Arial, sans-serif;
    font-size: 14px;
}
QLabel {
    color: #d0d0d0;
}
QLineEdit {
    background-color: #3c3f41;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
}
QLineEdit:focus {
    border: 1px solid #4a90e2;
}
QLineEdit:read-only {
    background-color: #333333;
    border: 1px solid #444444;
}
QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #5aa1f2;
}
QPushButton:pressed {
    background-color: #3a80d2;
}
QPushButton:disabled {
    background-color: #555555;
    color: #999999;
}
QComboBox {
    background-color: #3c3f41;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #3c3f41;
    border: 1px solid #555555;
    selection-background-color: #4a90e2;
}
QTextEdit {
    background-color: #212121;
    border: 1px solid #555555;
    border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
}
QTableWidget {
    gridline-color: #555555;
    border: 1px solid #555555;
}

QHeaderView::section {
    background-color: #3c3f41;
    color: #d0d0d0; /* <-- ADD THIS LINE */
    border: 1px solid #555555;
    padding: 4px;
    font-weight: bold;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #4a90e2;
}
QStackedWidget {
    border: none;
}
"""

COMMAND_MAP = {
    'cisco_ios': {
        'version': 'show version',
        'interfaces': 'show ip interface brief',
        'use_genie': True
    },
    'juniper_junos': {
        'version': 'show version',
        'interfaces': 'show interfaces terse',
        'use_genie': False
    },
    'default': {
        'version': 'show version',
        'interfaces': 'show ip interface brief',
        'use_genie': False
    }
}


class RouterTool(QWidget):
    def __init__(self):
        super().__init__()
        self.net_connect = None
        self.is_in_config_mode = False

        self.global_commands = {
            "Show Running Config": "show running-config",
            "Show Startup Config": "show startup-config",
            "Show IP Route": "show ip route",
            "Show IP Interface Brief": "show ip interface brief",
            "Show CDP Neighbors Detail": "show cdp neighbors detail",
            "Show Version": "show version",
            "Show Inventory": "show inventory",
            "Show Spanning-Tree": "show spanning-tree",
            "Show Logging": "show logging",
            "Save Configuration": "write memory"
        }

        self.config_commands = {
            "Enable Password Encryption": "service password-encryption",
            "Disable IP Domain-Lookup": "no ip domain-lookup",
            "Enable CEF": "ip cef",
            "Set Spanning-Tree to Rapid-PVST": "spanning-tree mode rapid-pvst",
            "Set MOTD Banner": "banner motd # Unauthorized access is prohibited! #",
            "Enter VTY Line Config": "line vty 0 4",
            "Use Local Login": "login local",
            "Allow Only SSH": "transport input ssh",
            "Set Exec Timeout to 15min": "exec-timeout 15 0",
            "Disable PAD Service": "no service pad"
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('EZ Route')
        self.stacked_widget = QStackedWidget()
        self.login_page = self.create_login_page()
        self.dashboard_page = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 50)  # Add padding

        title_label = QLabel("EZ Route")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding-bottom: 20px;")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Router IP Address")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        connect_icon = qta.icon('fa5s.plug', color='white')
        connect_button = QPushButton(connect_icon, " Connect")
        connect_button.clicked.connect(self.connect_to_device)

        self.login_status_label = QLabel("")
        self.login_status_label.setStyleSheet("color: #E57373;")

        layout.addWidget(title_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(connect_button)
        layout.addWidget(self.login_status_label)
        layout.addStretch()
        return page

    def create_dashboard_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_bar_layout = QHBoxLayout()
        disconnect_icon = qta.icon('fa5s.power-off', color='white')
        disconnect_button = QPushButton(disconnect_icon, " Disconnect")
        disconnect_button.clicked.connect(self.disconnect_from_device)

        self.device_type_label = QLabel("Device Type: N/A")
        top_bar_layout.addWidget(self.device_type_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(disconnect_button)
        main_layout.addLayout(top_bar_layout)

        details_layout = QFormLayout()
        details_layout.setContentsMargins(0, 15, 0, 15)
        self.hostname_label = QLabel("N/A")
        self.version_label = QLabel("N/A")
        self.uptime_label = QLabel("N/A")
        self.serial_label = QLabel("N/A")
        details_layout.addRow("Hostname:", self.hostname_label)
        details_layout.addRow("OS Version:", self.version_label)
        details_layout.addRow("Uptime:", self.uptime_label)
        details_layout.addRow("Serial Number:", self.serial_label)
        main_layout.addLayout(details_layout)

        main_layout.addWidget(QLabel("Interfaces:"))
        self.interface_table = QTableWidget()
        self.interface_table.setColumnCount(5)
        self.interface_table.setHorizontalHeaderLabels(["Sr. No", "Interface", "IP Address", "Status", "Protocol"])
        self.interface_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.interface_table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.interface_table)


        command_section_layout = QHBoxLayout()
        command_section_layout.setContentsMargins(0, 15, 0, 0)
        self.toggle_config_button = QPushButton("Enter Config Mode")
        self.toggle_config_button.clicked.connect(self.toggle_config_mode)

        self.command_dropdown = QComboBox()
        self.update_command_dropdown()

        execute_button = QPushButton('Run Command')
        execute_button.clicked.connect(self.run_manual_command)

        command_section_layout.addWidget(QLabel("Manual Command:"))
        command_section_layout.addWidget(self.command_dropdown)
        command_section_layout.addWidget(execute_button)
        command_section_layout.addStretch()
        command_section_layout.addWidget(self.toggle_config_button)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Output of manual commands will appear here...")

        main_layout.addLayout(command_section_layout)
        main_layout.addWidget(self.output_area)

        return page

    def connect_to_device(self):
        device_creds = {
            'device_type': 'autodetect',
            'host': self.ip_input.text(),
            'username': self.user_input.text(),
            'password': self.pass_input.text(),
        }
        try:
            self.login_status_label.setText("Connecting...")
            QApplication.processEvents()
            self.net_connect = ConnectHandler(**device_creds)

            detected_os = self.net_connect.device_type

            if detected_os == 'autodetect':
                self.device_type_label.setText("Device Type: Unknown")
                cmd_set = COMMAND_MAP['default']
            else:
                self.device_type_label.setText(f"Device Type: {detected_os}")
                cmd_set = COMMAND_MAP.get(detected_os, COMMAND_MAP['default'])

            hostname = self.net_connect.find_prompt().strip(' >#')
            self.login_status_label.setText("Fetching dashboard data...")
            QApplication.processEvents()

            ver_output = self.net_connect.send_command(cmd_set['version'], use_genie=cmd_set['use_genie'])
            if not isinstance(ver_output, dict):
                ver_output = self.parse_iou_version(ver_output)

            int_output = self.net_connect.send_command(cmd_set['interfaces'], use_genie=cmd_set['use_genie'])
            if not isinstance(int_output, dict):
                int_output = self.parse_iou_interfaces(int_output)

            self.populate_dashboard(hostname, ver_output, int_output)
            self.stacked_widget.setCurrentIndex(1)
            self.login_status_label.setText("")

        except Exception as e:
            self.login_status_label.setText(f"Error: {e}")
            if self.net_connect:
                self.net_connect.disconnect()
            self.net_connect = None

    def populate_dashboard(self, hostname, ver_data, int_data):
        self.hostname_label.setText(hostname)
        self.output_area.clear()
        self.interface_table.setRowCount(0)

        if isinstance(ver_data, dict):
            version_info = ver_data.get('version', {})
            self.version_label.setText(version_info.get('version_short', 'N/A'))
            self.uptime_label.setText(version_info.get('uptime', 'N/A'))
            self.serial_label.setText(version_info.get('chassis_sn', 'N/A'))
        else:
            self.version_label.setText("N/A (Parse Failed)")
            self.uptime_label.setText("N/A (Parse Failed)")
            self.serial_label.setText("N/A (Parse Failed)")
            self.output_area.setText(
                "--- DASHBOARD PARSE FAILURE ---\nCould not parse 'version' output:\n\n" + str(ver_data))

        if isinstance(int_data, dict):
            interfaces = int_data.get('interface', {})
            for i, (name, details) in enumerate(interfaces.items()):  # Use enumerate to easily get an index
                row_position = self.interface_table.rowCount()
                self.interface_table.insertRow(row_position)

                # Add the serial number (i+1) to the new first column (index 0)
                self.interface_table.setItem(row_position, 0, QTableWidgetItem(str(i + 1)))

                # Shift all other data one column to the right (indices are now 1, 2, 3, 4)
                self.interface_table.setItem(row_position, 1, QTableWidgetItem(name))
                self.interface_table.setItem(row_position, 2, QTableWidgetItem(details.get('ip_address', 'N/A')))
                self.interface_table.setItem(row_position, 3, QTableWidgetItem(details.get('status', 'N/A')))
                self.interface_table.setItem(row_position, 4, QTableWidgetItem(details.get('protocol', 'N/A')))
        else:
            self.output_area.append(
                "\n\n--- DASHBOARD PARSE FAILURE ---\nCould not parse 'interfaces' output:\n\n" + str(int_data))

    def toggle_config_mode(self):
        if not self.net_connect:
            QMessageBox.warning(self, "Error", "Not connected to any device.")
            return
        try:
            if not self.is_in_config_mode:
                self.net_connect.write_channel("configure terminal\r\n")
                time.sleep(1)
                output = self.net_connect.read_channel()
                self.is_in_config_mode = True
                self.toggle_config_button.setText("Exit Config Mode")
                self.output_area.setText("Entered configuration mode.\n" + output)
            else:
                self.net_connect.write_channel("end\r\n")
                time.sleep(1)
                output = self.net_connect.read_channel()
                self.is_in_config_mode = False
                self.toggle_config_button.setText("Enter Config Mode")
                self.output_area.setText("Exited configuration mode.\n" + output)
            self.update_command_dropdown()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not change mode: {e}")

    def update_command_dropdown(self):
        self.command_dropdown.clear()
        if self.is_in_config_mode:
            self.command_dropdown.addItems(self.config_commands.keys())
        else:
            self.command_dropdown.addItems(self.global_commands.keys())

    def run_manual_command(self):
        if not self.net_connect:
            QMessageBox.warning(self, "Error", "Not connected to any device.")
            return
        try:
            if self.is_in_config_mode:
                selected_key = self.command_dropdown.currentText()
                command_to_run = self.config_commands.get(selected_key)
                if command_to_run:
                    self.output_area.setText(f"Sending command: {command_to_run}...")
                    QApplication.processEvents()
                    self.net_connect.write_channel(command_to_run + "\r\n")
                    time.sleep(1)
                    output = self.net_connect.read_channel()
                    self.output_area.setText(output)
            else:
                selected_key = self.command_dropdown.currentText()
                command_to_run = self.global_commands.get(selected_key)
                if command_to_run:
                    self.output_area.setText(f"Executing: {command_to_run}...")
                    QApplication.processEvents()
                    output = self.net_connect.send_command(command_to_run, read_timeout=60)
                    self.output_area.setText(output)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    def disconnect_from_device(self):
        if self.net_connect:
            if self.is_in_config_mode:
                try:
                    self.net_connect.write_channel("end\r\n")
                    time.sleep(1)
                except Exception as e:
                    print(f"Could not gracefully exit config mode: {e}")
            self.net_connect.disconnect()

        self.net_connect = None
        self.is_in_config_mode = False
        self.toggle_config_button.setText("Enter Config Mode")
        self.update_command_dropdown()
        self.stacked_widget.setCurrentIndex(0)

    def parse_iou_version(self, text_output):
        parsed_data = {'version': {}}
        match = re.search(r"Version (\S+),", text_output)
        if match:
            parsed_data['version']['version_short'] = match.group(1)
        match = re.search(r"uptime is (.*)", text_output)
        if match:
            parsed_data['version']['uptime'] = match.group(1).strip()
        parsed_data['version']['chassis_sn'] = 'N/A (IOU)'
        return parsed_data

    def parse_iou_interfaces(self, text_output):
        parsed_data = {'interface': {}}
        lines = text_output.strip().split('\n')
        for line in lines[1:]:
            match = re.match(r"^(\S+)\s+([\d.]+|unassigned)\s+\w+\s+\w+\s+(up|down|administratively down)\s+(up|down)",
                             line)
            if match:
                intf_name = match.group(1)
                parsed_data['interface'][intf_name] = {
                    'ip_address': match.group(2),
                    'status': match.group(3),
                    'protocol': match.group(4)
                }
        return parsed_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    tool = RouterTool()
    tool.resize(900, 700)
    tool.show()
    sys.exit(app.exec())