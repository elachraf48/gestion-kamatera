import sys
import json
import requests
import webbrowser
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
                             QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QHeaderView,
                             QMessageBox, QAbstractItemView, QLabel, QLineEdit, QDialog,
                             QDialogButtonBox, QFormLayout, QComboBox, QProgressBar, QTextEdit,
                             QSplitter, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kamatera Login")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QFormLayout(self)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your Kamatera API key")
        layout.addRow("API Key:", self.api_key_edit)
        
        self.api_secret_edit = QLineEdit()
        self.api_secret_edit.setPlaceholderText("Enter your Kamatera API secret")
        self.api_secret_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("API Secret:", self.api_secret_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def get_credentials(self):
        return self.api_key_edit.text(), self.api_secret_edit.text()

class NetworkWorkflowDialog(QDialog):
    def __init__(self, servers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Network Switching Workflow")
        self.setModal(True)
        self.setGeometry(200, 200, 800, 600)
        self.servers = servers
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🚀 Smart Network Switching Assistant")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; background-color: #3498db; color: white; border-radius: 5px;")
        layout.addWidget(title)
        
        # Tab widget for different approaches
        tabs = QTabWidget()
        
        # Tab 1: Automated Workflow
        auto_tab = QWidget()
        auto_layout = QVBoxLayout(auto_tab)
        
        auto_info = QLabel("""
<h3>🔄 Automated Power Management + Manual Network Switch</h3>
<p>This workflow automates the tedious parts and guides you through the network change:</p>
<ol>
<li><b>Automatic:</b> Power off all selected servers</li>
<li><b>Manual:</b> Change network in Kamatera console (we'll open it for you)</li>
<li><b>Automatic:</b> Power on all servers</li>
<li><b>Automatic:</b> Verify network changes</li>
</ol>
        """)
        auto_info.setWordWrap(True)
        auto_layout.addWidget(auto_info)
        
        # Server list
        auto_layout.addWidget(QLabel("Selected Servers:"))
        server_text = QTextEdit()
        server_list = "\n".join([f"• {s['name']} ({s['id']}) - Current: {s.get('network', 'Unknown')}" for s in servers])
        server_text.setPlainText(server_list)
        server_text.setMaximumHeight(100)
        auto_layout.addWidget(server_text)
        
        # Network selection
        auto_layout.addWidget(QLabel("Target Network Type:"))
        self.network_combo = QComboBox()
        self.network_combo.addItems(["Public", "Private"])
        
        # Auto-detect best option
        current_networks = [s.get('network', '').lower() for s in servers]
        if 'private' in current_networks:
            self.network_combo.setCurrentText("Public")
        else:
            self.network_combo.setCurrentText("Private")
            
        auto_layout.addWidget(self.network_combo)
        
        # Buttons for automated workflow
        auto_buttons = QHBoxLayout()
        self.start_workflow_btn = QPushButton("🚀 Start Smart Workflow")
        self.start_workflow_btn.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 10px; }")
        self.start_workflow_btn.clicked.connect(self.start_automated_workflow)
        auto_buttons.addWidget(self.start_workflow_btn)
        auto_layout.addLayout(auto_buttons)
        
        tabs.addTab(auto_tab, "🔄 Smart Workflow")
        
        # Tab 2: Manual Instructions
        manual_tab = QWidget()
        manual_layout = QVBoxLayout(manual_tab)
        
        manual_info = QLabel("<h3>📋 Complete Manual Instructions</h3>")
        manual_layout.addWidget(manual_info)
        
        instructions = QTextEdit()
        instructions.setPlainText(self.get_manual_instructions())
        instructions.setReadOnly(True)
        manual_layout.addWidget(instructions)
        
        manual_buttons = QHBoxLayout()
        open_console_btn = QPushButton("🌐 Open Kamatera Console")
        open_console_btn.clicked.connect(self.open_console)
        manual_buttons.addWidget(open_console_btn)
        manual_layout.addLayout(manual_buttons)
        
        tabs.addTab(manual_tab, "📋 Manual Instructions")
        
        # Tab 3: CLI Method (if available)
        cli_tab = QWidget()
        cli_layout = QVBoxLayout(cli_tab)
        
        cli_info = QLabel("""
<h3>⚡ CLI Method (Advanced)</h3>
<p>If you have Kamatera CLI tools installed, you can use these commands:</p>
        """)
        cli_layout.addWidget(cli_info)
        
        cli_commands = QTextEdit()
        cli_commands.setPlainText(self.get_cli_commands())
        cli_commands.setReadOnly(True)
        cli_layout.addWidget(cli_commands)
        
        cli_buttons = QHBoxLayout()
        try_cli_btn = QPushButton("🔍 Check CLI Availability")
        try_cli_btn.clicked.connect(self.check_cli)
        cli_buttons.addWidget(try_cli_btn)
        cli_layout.addLayout(cli_buttons)
        
        tabs.addTab(cli_tab, "⚡ CLI Method")
        
        layout.addWidget(tabs)
        
        # Main dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.workflow_active = False
    
    def get_manual_instructions(self):
        target_network = "Public" if any(s.get('network', '').lower() == 'private' for s in self.servers) else "Private"
        
        instructions = f"""COMPLETE MANUAL NETWORK SWITCHING GUIDE

TARGET: Switch to {target_network} Network
SERVERS: {len(self.servers)} server(s)

STEP-BY-STEP PROCESS:

1. PREPARE SERVERS
   • Stop any critical applications running on the servers
   • Note current IP addresses for DNS/firewall updates
   • Ensure you have console access credentials

2. POWER OFF SERVERS (do this first!)
"""
        
        for server in self.servers:
            instructions += f"   • {server['name']} ({server['id']})\n"
        
        instructions += f"""
3. NETWORK CONFIGURATION IN CONSOLE
   a) Go to: https://console.kamatera.com/
   b) Navigate to "Server Management" or "My Servers"
   c) For each server:
      • Click on the server name or "Manage" button
      • Look for "Network" or "Networking" section
      • Click "Edit" or "Modify Network"
      • Change from current network to {target_network}
      • Save changes

4. POWER ON SERVERS
   • Start each server after network changes are saved
   • Wait for each server to fully boot before starting the next

5. VERIFY CHANGES
   • Check new IP addresses
   • Update DNS records if IPs changed
   • Update firewall rules if needed
   • Test connectivity to all services

6. POST-CHANGE TASKS
   • Update monitoring systems with new IPs
   • Notify team members of IP changes
   • Update documentation

IMPORTANT WARNINGS:
⚠️ Servers will be unreachable during this process
⚠️ IP addresses will likely change
⚠️ Plan for 15-30 minutes of downtime per server
⚠️ Have a rollback plan ready

TROUBLESHOOTING:
• If server won't start: Check console for error messages
• If network config is missing: Contact Kamatera support
• If IPs don't change: Verify network was actually switched
"""
        return instructions
    
    def get_cli_commands(self):
        target_network = "public" if any(s.get('network', '').lower() == 'private' for s in self.servers) else "private"
        
        commands = f"""KAMATERA CLI COMMANDS (if CLI tools are available)

# Install Kamatera CLI (if not installed)
pip install kamatera-cli

# Configure credentials
export KAMATERA_API_CLIENT_ID="your_api_key"
export KAMATERA_API_SECRET="your_api_secret"

# Power off servers
"""
        
        for server in self.servers:
            commands += f'kamatera server power --server-id "{server["id"]}" --power off\n'
        
        commands += f"""
# Wait for servers to shut down (check status)
"""
        for server in self.servers:
            commands += f'kamatera server info --server-id "{server["id"]}"\n'
            
        commands += f"""
# Modify network (if supported by CLI)
"""
        for server in self.servers:
            commands += f'# kamatera server modify --server-id "{server["id"]}" --network {target_network}\n'
            
        commands += f"""
# Power on servers
"""
        for server in self.servers:
            commands += f'kamatera server power --server-id "{server["id"]}" --power on\n'
            
        commands += f"""
# Verify changes
"""
        for server in self.servers:
            commands += f'kamatera server info --server-id "{server["id"]}"\n'
            
        commands += """
NOTE: CLI network modification commands may not be available.
If 'kamatera server modify --network' fails, use the manual console method.
"""
        return commands
    
    def start_automated_workflow(self):
        """Start the automated workflow"""
        if self.workflow_active:
            return
            
        reply = QMessageBox.question(
            self, "Start Automated Workflow", 
            f"This will:\n"
            f"1. Power OFF all {len(self.servers)} selected servers\n"
            f"2. Open Kamatera console for manual network changes\n"
            f"3. Guide you through powering servers back ON\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.workflow_active = True
            self.start_workflow_btn.setText("🔄 Workflow Running...")
            self.start_workflow_btn.setEnabled(False)
            
            # Signal parent to start workflow
            self.accept()  # Close dialog and return success
    
    def open_console(self):
        """Open Kamatera console in browser"""
        webbrowser.open("https://console.kamatera.com/")
        QMessageBox.information(self, "Console Opened", 
                              "Kamatera console opened in your browser.\n"
                              "Navigate to Server Management to modify network settings.")
    
    def check_cli(self):
        """Check if Kamatera CLI is available"""
        try:
            result = subprocess.run(['kamatera', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                QMessageBox.information(self, "CLI Available", 
                                      f"Kamatera CLI is installed!\n\nVersion info:\n{result.stdout}")
            else:
                raise subprocess.CalledProcessError(result.returncode, 'kamatera')
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            QMessageBox.information(self, "CLI Not Available", 
                                  "Kamatera CLI is not installed.\n\n"
                                  "To install:\npip install kamatera-cli\n\n"
                                  "Or use the Smart Workflow tab for automated assistance.")
    
    def get_target_network(self):
        return self.network_combo.currentText().lower()

class KamateraManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Kamatera Server Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize variables
        self.api_key = None
        self.api_secret = None
        self.base_url = "https://console.kamatera.com/service"
        self.servers = []
        self.workflow_state = None
        
        # Set up the UI
        self.init_ui()
        
        # Try to load credentials from config
        self.load_config()
        
        # If no config, show login dialog
        if not self.api_key or not self.api_secret:
            self.show_login_dialog()
        else:
            self.load_servers()
    
    def init_ui(self):
        # Central widget with splitter
        splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(splitter)
        
        # Top widget for controls and table
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Title
        title = QLabel("🚀 Smart Kamatera Server Manager")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 15px; background-color: #2c3e50; color: white; border-radius: 8px;")
        top_layout.addWidget(title)
        
        # Info banner
        info_banner = QLabel("💡 Network switching made easy with automated workflows and smart guidance!")
        info_banner.setStyleSheet("padding: 8px; background-color: #f39c12; color: white; border-radius: 4px;")
        info_banner.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(info_banner)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        # Selection buttons
        self.select_all_btn = QPushButton("Select All")
        self.deselect_all_btn = QPushButton("Deselect All")
        self.select_all_btn.clicked.connect(self.select_all_servers)
        self.deselect_all_btn.clicked.connect(self.deselect_all_servers)
        
        # Action buttons
        self.power_on_btn = QPushButton("⚡ Power On")
        self.power_off_btn = QPushButton("🛑 Power Off")
        self.reboot_btn = QPushButton("🔄 Reboot")
        self.smart_network_btn = QPushButton("🧠 Smart Network Switch")
        self.info_btn = QPushButton("ℹ️ Server Info")
        
        # Style the smart network button
        self.smart_network_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.power_on_btn.clicked.connect(lambda: self.perform_power_action("on"))
        self.power_off_btn.clicked.connect(lambda: self.perform_power_action("off"))
        self.reboot_btn.clicked.connect(lambda: self.perform_power_action("reboot"))
        self.smart_network_btn.clicked.connect(self.smart_network_switch)
        self.info_btn.clicked.connect(self.show_server_info)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_servers)
        
        # Add buttons to layout
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.power_on_btn)
        button_layout.addWidget(self.power_off_btn)
        button_layout.addWidget(self.reboot_btn)
        button_layout.addWidget(self.smart_network_btn)
        button_layout.addWidget(self.info_btn)
        button_layout.addWidget(self.refresh_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Server table
        self.server_table = QTableWidget()
        self.server_table.setColumnCount(7)
        self.server_table.setHorizontalHeaderLabels(["Select", "ID", "Name", "Status", "IP", "Power", "Network"])
        self.server_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.server_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.server_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Add to top layout
        top_layout.addLayout(button_layout)
        top_layout.addWidget(self.progress_bar)
        top_layout.addWidget(self.server_table)
        
        # Bottom widget for workflow log
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        log_label = QLabel("📋 Workflow Log")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        bottom_layout.addWidget(log_label)
        
        self.workflow_log = QTextEdit()
        self.workflow_log.setMaximumHeight(150)
        self.workflow_log.setPlainText("Ready to help with network switching! Select servers and click 'Smart Network Switch' to begin.")
        bottom_layout.addWidget(self.workflow_log)
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([600, 200])  # Give more space to the top
        
        # Status bar
        self.status_label = QLabel("Ready - Smart network switching available!")
        self.statusBar().addWidget(self.status_label)
        
        # Set style
        self.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
            QTableWidget {
                gridline-color: #bdc3c7;
                font-size: 12px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
    
    def log_message(self, message):
        """Add message to workflow log"""
        self.workflow_log.append(f"[{QTimer().remainingTime()}] {message}")
        QApplication.processEvents()
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                self.api_secret = config.get('api_secret')
        except FileNotFoundError:
            self.status_label.setText("Config file not found. Please login.")
        except json.JSONDecodeError:
            self.status_label.setText("Invalid config file. Please login.")
    
    def save_config(self):
        config = {
            'api_key': self.api_key,
            'api_secret': self.api_secret
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)
    
    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.api_key, self.api_secret = dialog.get_credentials()
            if self.api_key and self.api_secret:
                self.save_config()
                self.load_servers()
            else:
                QMessageBox.warning(self, "Error", "API key and secret are required.")
    
    def make_api_request(self, endpoint, method="GET", data=None):
        """Make authenticated API request to Kamatera"""
        if not self.api_key or not self.api_secret:
            self.show_login_dialog()
            return None
            
        headers = {
            "AuthClientId": self.api_key,
            "AuthSecret": self.api_secret,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                return None
            
            response.raise_for_status()
            
            # Try to parse as JSON, if fails return text
            try:
                return response.json()
            except:
                return response.text
                
        except requests.exceptions.RequestException as e:
            self.log_message(f"API Error: {str(e)}")
            return None

    # Add this new method to change network configuration
    def change_server_network(self, server_id, network_type):
        """Change server network configuration"""
        self.log_message(f"Changing network for server {server_id} to {network_type}")
        
        # First get current server configuration
        server_info = self.make_api_request(f"/server/{server_id}", "GET")
        if not server_info:
            self.log_message(f"❌ Failed to get server info for {server_id}")
            return False
            
        # Prepare network change data
        network_data = {
            "networks": []
        }
        
        # Add the appropriate network based on type
        if network_type.lower() == "public":
            network_data["networks"].append({"name": "internet"})
        elif network_type.lower() == "private":
            network_data["networks"].append({"name": "local"})
        
        # Make the API call to change network
        result = self.make_api_request(f"/server/{server_id}", "PUT", network_data)
        
        if result:
            self.log_message(f"✅ Successfully changed network for server {server_id}")
            return True
        else:
            self.log_message(f"❌ Failed to change network for server {server_id}")
            return False

    # Update the workflow_step_2 method to include automatic network change
    def workflow_step_2(self, servers, target_network):
        """Step 2: Network switching (automatic or manual)"""
        self.log_message("Step 2: Network configuration")
        
        # Try automatic network change first
        auto_success = True
        self.log_message("Attempting automatic network change via API...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(servers))
        
        for i, server in enumerate(servers):
            server_id = server.get('id')
            server_name = server.get('name', 'Unknown')
            
            self.log_message(f"Changing network for: {server_name}")
            self.status_label.setText(f"Changing network: {server_name}")
            
            success = self.change_server_network(server_id, target_network)
            if not success:
                auto_success = False
                self.log_message(f"❌ Automatic network change failed for {server_name}")
            
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()
        
        self.progress_bar.setVisible(False)
        
        if auto_success:
            self.log_message("✅ All network changes completed successfully!")
            # Proceed to power on step
            self.workflow_step_3(servers)
        else:
            self.log_message("⚠️ Automatic network change partially failed, switching to manual method")
            # Fall back to manual method
            self.workflow_step_2_manual(servers, target_network)

    def workflow_step_2_manual(self, servers, target_network):
        """Manual network switching fallback"""
        self.log_message("Step 2: Manual network switching required")
        
        # Open Kamatera console
        webbrowser.open("https://console.kamatera.com/")
        self.log_message("🌐 Opened Kamatera console in browser")
        
        # Show guided instructions
        server_list = "\n".join([f"• {s.get('name', 'Unknown')} ({s.get('id', 'Unknown')})" for s in servers])
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🔧 Manual Network Configuration")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Console opened! Now configure networks for {len(servers)} servers.")
        msg.setInformativeText(f"Switch each server to: {target_network.title()} Network")
        msg.setDetailedText(f"""SERVERS TO CONFIGURE:
{server_list}

STEPS IN KAMATERA CONSOLE:
1. Go to "Server Management" or "My Servers"
2. For each server above:
   • Click server name or "Manage"
   • Find "Network" or "Networking" section  
   • Click "Edit" or "Modify Network"
   • Change to: {target_network.title()} Network
   • Save changes

3. When ALL servers are configured, click "Yes" below
4. We'll automatically power them back on!

IMPORTANT: Configure ALL servers before proceeding to power-on step.""")
        
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("✅ All Networks Configured - Power On Servers")
        msg.button(QMessageBox.Cancel).setText("❌ Cancel Workflow")
        
        reply = msg.exec_()
        
        if reply == QMessageBox.Yes:
            self.log_message("✅ User confirmed network configuration complete")
            self.workflow_step_3(servers)
        else:
            self.log_message("❌ Workflow cancelled by user")
            self.status_label.setText("Workflow cancelled")

    # Update the start_automated_workflow method
    def start_automated_workflow(self, servers, target_network):
        """Execute the automated workflow"""
        self.log_message(f"🔄 Starting automated workflow: {len(servers)} servers → {target_network}")
        
        # Step 1: Power off servers
        self.log_message("Step 1: Powering off servers...")
        self.power_off_servers_for_workflow(servers)
        
        # Step 2: Network change (automatic with manual fallback)
        self.workflow_step_2(servers, target_network)
    def extract_ip_and_network_info(self, detailed_info):
        """Extract IP address and network type from detailed server information"""
        ip_address = 'N/A'
        network_type = 'Unknown'
        
        try:
            if 'networks' in detailed_info and isinstance(detailed_info['networks'], list) and detailed_info['networks']:
                for network in detailed_info['networks']:
                    if isinstance(network, dict) and 'ips' in network:
                        if isinstance(network['ips'], list) and network['ips']:
                            ip_address = network['ips'][0]
                            
                            if 'name' in network:
                                network_name = network['name'].lower()
                                if 'private' in network_name or 'local' in network_name:
                                    network_type = 'Private'
                                elif 'public' in network_name or 'internet' in network_name:
                                    network_type = 'Public'
                            
                            if network_type == 'Unknown' and ip_address != 'N/A':
                                if (ip_address.startswith('10.') or 
                                    ip_address.startswith('172.') or 
                                    ip_address.startswith('192.168.')):
                                    network_type = 'Private'
                                else:
                                    network_type = 'Public'
                            break
            
            if ip_address == 'N/A':
                ip_fields = ['ip', 'ipAddress', 'primaryIP', 'publicIP', 'privateIP']
                for field in ip_fields:
                    if field in detailed_info and detailed_info[field]:
                        ip_address = detailed_info[field]
                        if 'private' in field.lower():
                            network_type = 'Private'
                        elif 'public' in field.lower():
                            network_type = 'Public'
                        break
                        
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            self.log_message(f"Error extracting IP and network info: {e}")
        
        return ip_address, network_type

    def load_servers(self):
        """Load servers from Kamatera API"""
        self.log_message("Loading servers...")
        self.status_label.setText("Loading servers...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        QApplication.processEvents()
        
        servers = self.make_api_request("/servers", "GET")
        
        if servers is None:
            self.progress_bar.setVisible(False)
            self.status_label.setText("Failed to load servers")
            self.log_message("❌ Failed to load servers")
            return
            
        if isinstance(servers, dict):
            if 'servers' in servers:
                servers = servers['servers']
            elif 'items' in servers:
                servers = servers['items']
            elif 'data' in servers:
                servers = servers['data']
        
        if not servers:
            self.progress_bar.setVisible(False)
            self.status_label.setText("No servers found")
            self.log_message("ℹ️ No servers found")
            return
            
        self.servers = servers
        self.server_table.setRowCount(len(servers))
        
        # Load server information
        self.progress_bar.setRange(0, len(servers))
        for row, server in enumerate(servers):
            server_id = server.get('id') or 'N/A'
            server_name = server.get('name') or 'Unnamed'
            server_status = server.get('status') or 'unknown'
            server_power = server.get('power') or 'unknown'
            
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QVBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.server_table.setCellWidget(row, 0, checkbox_widget)
            
            # Server details
            self.server_table.setItem(row, 1, QTableWidgetItem(str(server_id)))
            self.server_table.setItem(row, 2, QTableWidgetItem(server_name))
            
            # Status with color coding
            status_item = QTableWidgetItem(server_status)
            status = server_status.lower()
            if 'run' in status or 'on' in status:
                status_item.setBackground(QColor(220, 255, 220))
            elif 'stop' in status or 'off' in status:
                status_item.setBackground(QColor(255, 220, 220))
            elif 'pend' in status:
                status_item.setBackground(QColor(255, 255, 200))
            self.server_table.setItem(row, 3, status_item)
            
            # Get detailed info for IP and network
            if server_id != 'N/A':
                detailed_info = self.make_api_request(f"/server/{server_id}", "GET")
                if detailed_info and isinstance(detailed_info, dict):
                    server_ip, network_type = self.extract_ip_and_network_info(detailed_info)
                    self.server_table.setItem(row, 4, QTableWidgetItem(server_ip))
                    
                    # Store network info in server dict for workflow
                    server['network'] = network_type
                    server['ip'] = server_ip
                    
                    # Network type with color coding
                    network_item = QTableWidgetItem(network_type)
                    if network_type.lower() == 'public':
                        network_item.setBackground(QColor(220, 220, 255))
                    elif network_type.lower() == 'private':
                        network_item.setBackground(QColor(255, 220, 255))
                    self.server_table.setItem(row, 6, network_item)
                else:
                    self.server_table.setItem(row, 4, QTableWidgetItem("Error"))
                    self.server_table.setItem(row, 6, QTableWidgetItem("Error"))
                    server['network'] = 'Error'
                    server['ip'] = 'Error'
            else:
                self.server_table.setItem(row, 4, QTableWidgetItem("N/A"))
                self.server_table.setItem(row, 6, QTableWidgetItem("N/A"))
                server['network'] = 'N/A'
                server['ip'] = 'N/A'
            
            # Power status
            power_item = QTableWidgetItem(server_power)
            power = server_power.lower()
            if 'on' in power:
                power_item.setBackground(QColor(220, 255, 220))
            elif 'off' in power:
                power_item.setBackground(QColor(255, 220, 220))
            self.server_table.setItem(row, 5, power_item)
            
            # Update progress
            self.progress_bar.setValue(row + 1)
            QApplication.processEvents()
        
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✅ Loaded {len(servers)} servers - Ready for smart network switching!")
        self.log_message(f"✅ Loaded {len(servers)} servers successfully")
    
    def get_selected_servers(self):
        """Get list of selected server data"""
        selected_servers = []
        for row in range(self.server_table.rowCount()):
            checkbox_widget = self.server_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox and checkbox.isChecked():
                # Find the server data by ID
                server_id = self.server_table.item(row, 1).text()
                for server in self.servers:
                    if server.get('id') == server_id:
                        # Enhance with current table data
                        server['name'] = self.server_table.item(row, 2).text()
                        server['current_status'] = self.server_table.item(row, 3).text()
                        server['current_power'] = self.server_table.item(row, 5).text()
                        selected_servers.append(server)
                        break
        return selected_servers
    
    def select_all_servers(self):
        """Select all servers in the table"""
        for row in range(self.server_table.rowCount()):
            checkbox_widget = self.server_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(True)
    
    def deselect_all_servers(self):
        """Deselect all servers in the table"""
        for row in range(self.server_table.rowCount()):
            checkbox_widget = self.server_table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(False)
    
    def smart_network_switch(self):
        """Launch smart network switching workflow"""
        selected_servers = self.get_selected_servers()
        
        if not selected_servers:
            QMessageBox.warning(self, "No Selection", "Please select at least one server for network switching.")
            return
        
        self.log_message(f"🚀 Starting smart network switch for {len(selected_servers)} servers")
        
        # Launch the workflow dialog
        dialog = NetworkWorkflowDialog(selected_servers, self)
        if dialog.exec_() == QDialog.Accepted:
            # User chose to start automated workflow
            target_network = dialog.get_target_network()
            self.start_automated_workflow(selected_servers, target_network)
    
    def start_automated_workflow(self, servers, target_network):
        """Execute the automated workflow"""
        self.log_message(f"🔄 Starting automated workflow: {len(servers)} servers → {target_network}")
        
        # Step 1: Power off servers
        self.log_message("Step 1: Powering off servers...")
        self.power_off_servers_for_workflow(servers)
        
        # Step 2: Wait a moment, then open console and show manual instructions
        QTimer.singleShot(5000, lambda: self.workflow_step_2(servers, target_network))
    
    def power_off_servers_for_workflow(self, servers):
        """Power off servers as part of workflow"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(servers))
        
        success_count = 0
        for i, server in enumerate(servers):
            server_id = server.get('id')
            server_name = server.get('name', 'Unknown')
            
            self.log_message(f"Powering off: {server_name}")
            self.status_label.setText(f"Powering off: {server_name}")
            
            result = self.make_api_request(f"/server/{server_id}/power", "PUT", {"power": "off"})
            
            if result:
                success_count += 1
                self.log_message(f"✅ {server_name} power off initiated")
            else:
                self.log_message(f"❌ Failed to power off {server_name}")
            
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()
        
        self.progress_bar.setVisible(False)
        self.log_message(f"Power off completed: {success_count}/{len(servers)} servers")
    
    def workflow_step_2(self, servers, target_network):
        """Step 2: Manual network switching with guidance"""
        self.log_message("Step 2: Manual network switching required")
        
        # Open Kamatera console
        webbrowser.open("https://console.kamatera.com/")
        self.log_message("🌐 Opened Kamatera console in browser")
        
        # Show guided instructions
        server_list = "\n".join([f"• {s.get('name', 'Unknown')} ({s.get('id', 'Unknown')})" for s in servers])
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🔧 Manual Network Configuration")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Console opened! Now configure networks for {len(servers)} servers.")
        msg.setInformativeText(f"Switch each server to: {target_network.title()} Network")
        msg.setDetailedText(f"""SERVERS TO CONFIGURE:
{server_list}

STEPS IN KAMATERA CONSOLE:
1. Go to "Server Management" or "My Servers"
2. For each server above:
   • Click server name or "Manage"
   • Find "Network" or "Networking" section  
   • Click "Edit" or "Modify Network"
   • Change to: {target_network.title()} Network
   • Save changes

3. When ALL servers are configured, click "Yes" below
4. We'll automatically power them back on!

IMPORTANT: Configure ALL servers before proceeding to power-on step.""")
        
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("✅ All Networks Configured - Power On Servers")
        msg.button(QMessageBox.Cancel).setText("❌ Cancel Workflow")
        
        reply = msg.exec_()
        
        if reply == QMessageBox.Yes:
            self.log_message("✅ User confirmed network configuration complete")
            self.workflow_step_3(servers)
        else:
            self.log_message("❌ Workflow cancelled by user")
            self.status_label.setText("Workflow cancelled")
    
    def workflow_step_3(self, servers):
        """Step 3: Power on servers"""
        self.log_message("Step 3: Powering on servers...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(servers))
        
        success_count = 0
        for i, server in enumerate(servers):
            server_id = server.get('id')
            server_name = server.get('name', 'Unknown')
            
            self.log_message(f"Powering on: {server_name}")
            self.status_label.setText(f"Powering on: {server_name}")
            
            result = self.make_api_request(f"/server/{server_id}/power", "PUT", {"power": "on"})
            
            if result:
                success_count += 1
                self.log_message(f"✅ {server_name} power on initiated")
            else:
                self.log_message(f"❌ Failed to power on {server_name}")
            
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()
        
        self.progress_bar.setVisible(False)
        self.log_message(f"Power on completed: {success_count}/{len(servers)} servers")
        
        # Step 4: Final verification
        QTimer.singleShot(10000, lambda: self.workflow_step_4(servers))
    
    def workflow_step_4(self, servers):
        """Step 4: Verify changes and refresh"""
        self.log_message("Step 4: Verifying network changes...")
        self.status_label.setText("Verifying network changes...")
        
        # Refresh server data
        self.load_servers()
        
        # Show completion dialog
        QMessageBox.information(
            self, "🎉 Workflow Complete!", 
            f"Smart network switching workflow completed!\n\n"
            f"✅ Powered off {len(servers)} servers\n"
            f"✅ Guided manual network configuration\n"
            f"✅ Powered on {len(servers)} servers\n"
            f"✅ Refreshed server data\n\n"
            f"Please verify the network changes in the server table.\n"
            f"IP addresses may have changed - update DNS/firewall rules as needed."
        )
        
        self.log_message("🎉 Smart network switching workflow completed successfully!")
        self.status_label.setText("✅ Network switching workflow completed!")
    
    def perform_power_action(self, action):
        """Perform power action on selected servers"""
        selected_servers = self.get_selected_servers()
        
        if not selected_servers:
            QMessageBox.warning(self, "No Selection", "Please select at least one server.")
            return
        
        action_names = {"on": "Power On", "off": "Power Off", "reboot": "Reboot"}
        reply = QMessageBox.question(
            self, "Confirm Action", 
            f"Are you sure you want to {action_names.get(action, action)} {len(selected_servers)} server(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.log_message(f"🔄 {action_names.get(action, action)} initiated for {len(selected_servers)} servers")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(selected_servers))
        
        success_count = 0
        for i, server in enumerate(selected_servers):
            server_id = server.get('id')
            server_name = server.get('name', 'Unknown')
            
            self.status_label.setText(f"{action_names.get(action, action)}: {server_name}")
            
            result = self.make_api_request(f"/server/{server_id}/power", "PUT", {"power": action})
            
            if result:
                success_count += 1
                self.log_message(f"✅ {server_name}: {action} successful")
            else:
                self.log_message(f"❌ {server_name}: {action} failed")
            
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()
        
        self.progress_bar.setVisible(False)
        
        if success_count > 0:
            self.log_message(f"✅ {action_names.get(action, action)} completed: {success_count}/{len(selected_servers)} servers")
            QTimer.singleShot(3000, self.load_servers)
        
        self.status_label.setText(f"{action_names.get(action, action)} completed")
    
    def show_server_info(self):
        """Show information about selected server"""
        selected_servers = self.get_selected_servers()
        
        if not selected_servers:
            QMessageBox.warning(self, "No Selection", "Please select a server.")
            return
        
        if len(selected_servers) > 1:
            QMessageBox.warning(self, "Multiple Selection", "Please select only one server.")
            return
        
        server = selected_servers[0]
        server_id = server.get('id')
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        QApplication.processEvents()
        
        result = self.make_api_request(f"/server/{server_id}", "GET")
        
        self.progress_bar.setVisible(False)
        
        if result:
            info_text = f"Server {server_id} Information:\n\n"
            
            if isinstance(result, dict):
                important_fields = ['id', 'name', 'status', 'power', 'cpu', 'ram', 'disk', 'datacenter', 'os', 'networks']
                
                for field in important_fields:
                    if field in result:
                        value = result[field]
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value, indent=2)
                        info_text += f"{field.upper()}: {value}\n"
                
                for key, value in result.items():
                    if key not in important_fields:
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, indent=2)
                        info_text += f"{key.upper()}: {value}\n"
            else:
                info_text += str(result)
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Server Information")
            msg.setText(f"Detailed information for server {server.get('name', 'Unknown')}")
            msg.setDetailedText(info_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
            self.log_message(f"ℹ️ Showed info for server: {server.get('name', 'Unknown')}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to get information for server {server_id}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Show welcome message
    msg = QMessageBox()
    msg.setWindowTitle("🚀 Smart Kamatera Manager")
    msg.setIcon(QMessageBox.Information)
    msg.setText("Welcome to Smart Kamatera Server Manager!")
    msg.setInformativeText("Network switching made easy with automated workflows")
    msg.setDetailedText("""
FEATURES:
🔄 Automated power management
🧠 Smart network switching workflows  
📋 Step-by-step guidance
🌐 Automatic console opening
📊 Real-time workflow logging
✅ Verification and validation

WORKFLOW PROCESS:
1. Select servers to switch networks
2. Click "Smart Network Switch"  
3. Choose automated workflow
4. We handle power off automatically
5. Console opens for manual network config
6. We handle power on automatically
7. Verification and completion

This approach combines automation where possible with guided manual steps where needed,
giving you the best of both worlds for reliable network switching!
    """)
    msg.exec_()
    
    window = KamateraManager()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()