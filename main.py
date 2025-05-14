from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from GUI.gui import Ui_MainWindow
import sys
import csv

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import joblib

from EHR_system import predict_file, predict_single_record
from Database.db_connect import get_connection 
from email_utils import generate_otp, send_otp_email
from fingerprint.match_template import match_fingerprint

class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.generated_otp = None
        
        self.stackedWidget.setCurrentIndex(0)
        self.showPassword_checkbox.stateChanged.connect(self.toggle_password_visibility)

        self.signIn_button.clicked.connect(self.signIn)
        
        self.verify_otp_button.clicked.connect(self.verify_otp)
        self.resend_code_button.clicked.connect(self.send_OTP)

        self.scan_fp_button.clicked.connect(self.fingerprint_verification)

        if self.chart_widget.layout() is None:
            self.chart_widget.setLayout(QtWidgets.QVBoxLayout())

        self.progress_val = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.progress_update)   
        self.dataset_table.setStyleSheet(self.dataset_table.styleSheet())

        self.upload_dataset_button.clicked.connect(self.load_csv_to_table)
        self.upload_dataset_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.dataset_page))
        self.new_data_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.dataentry_page))

        self.show_chart_button.clicked.connect(self.show_svm_model)
        self.pushButton.clicked.connect(self.check_single_record)

        self.back_button.clicked.connect(self.back)
        self.back_button_2.clicked.connect(self.back)
        self.exit_button.clicked.connect(self.exit)
        self.exit_button_2.clicked.connect(self.exit)

    def signIn(self):
        username = self.emailaddress.text()
        password = self.password.text()
        print(f"username: {username}")
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and Password are required.")
            return

        # Connect to DB and validate credentials
        
        conn = get_connection()
        print("trying db conn")
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT * FROM Users WHERE email = %s AND password = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if result:
                    QMessageBox.information(self, "Login Success", f"Welcome {username}")
                    self.username = username  # ✅ Set username after validation
                    print("[DEBUG] User authenticated, sending OTP...")
                    self.send_OTP()
                    
                    self.stackedWidget.setCurrentWidget(self.Email_Authentication)
                else:
                    QMessageBox.critical(self, "Login Failed", "Incorrect username or password.")
            except Exception as e:
                print("[ERROR] Exception during DB login:", str(e))
                QMessageBox.critical(self, "Database Error", str(e))
        else:
            QMessageBox.critical(self, "Connection Error", "Failed to connect to the database.")

    def toggle_password_visibility(self):
        if self.showPassword_checkbox.isChecked():
            self.password.setEchoMode(QtWidgets.QLineEdit.Normal)  # Show password
        else:
            self.password.setEchoMode(QtWidgets.QLineEdit.Password)  # Hide password

    def verify_otp(self):
        try:
            entered_otp = self.OTP_here.text().replace(" ", "").strip()
            print(f"[DEBUG] Entered OTP: {entered_otp}")
            
            if len(entered_otp) == 6 and entered_otp.isdigit():
                if str(self.generated_otp) == entered_otp:
                    QMessageBox.information(self, "Verified", "OTP verified successfully!")
                    self.current_user = self.username  # So match_fingerprint has correct input
                    self.stackedWidget.setCurrentWidget(self.Fingerprint_Authentication)

                else:
                    QMessageBox.critical(self, "Invalid OTP", "Incorrect OTP. Please try again or click the resend button.")
                    self.OTP_here.clear()
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid 6-digit OTP.")
        except Exception as e:
            print("[ERROR] Exception in auto_verify_otp:", str(e))
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def send_OTP(self):
        try:
            print("[DEBUG] Generating OTP...")
            self.generated_otp = generate_otp()
            print(f"[DEBUG] Generated OTP: {self.generated_otp}")

            success = send_otp_email(self.username, self.generated_otp)
            print(f"[DEBUG] Email send success: {success}")

            if success:
                QMessageBox.information(self, "OTP Sent", f"A 6-digit OTP has been sent to {self.username}.")
            else:
                QMessageBox.critical(self, "Error", "Failed to send OTP. Please try again.")
        except Exception as e:
            print("[ERROR] Exception during OTP sending:", str(e))
            QMessageBox.critical(self, "Email Error", str(e))

    def fingerprint_verification(self):
        try:
            if match_fingerprint(self.username):
                print("AUTH_SUCCESS")
                self.fp_message_label.setStyleSheet("color: green;")
                self.fp_message_label.setText("Biometric Authentication Successful :)")

                QTimer.singleShot(1500, self.start_loading_screen)
            else:
                print("AUTH_FAIL")
                self.fp_message_label.setStyleSheet("color: red;")
                self.fp_message_label.setText("Biometric Authentication Unsuccessful :(")
        except Exception as e:
            print("ERROR during fingerprint verification:", str(e))
            self.fp_message_label.setStyleSheet("color: red;")
            self.fp_message_label.setText("Error during fingerprint verification. Please try again.")
    
    def start_loading_screen(self):
        self.stackedWidget.setCurrentWidget(self.loading_page)
        self.progress_val = 0
        self.progress_bar.setValue(0)
        self.timer.start(30)  # This starts the progress bar update every 30 ms

    def progress_update(self):
        self.progress_val += 1
        self.progress_bar.setValue(self.progress_val)

        if self.progress_val > 100:
            self.timer.stop()
            self.stackedWidget.setCurrentWidget(self.selection_page)

    def load_csv_to_table(self):
        file_name = r"data\processed_dataset.csv"
        try:
            with open(file_name, newline='', encoding='utf-8') as csvfile:
                data = list(csv.reader(csvfile))
                self.dataset_table.setStyleSheet("background: white;")
                self.dataset_table.horizontalHeader().setDefaultSectionSize(130)
                self.dataset_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

                self.dataset_table.setRowCount(len(data) - 1)
                self.dataset_table.setColumnCount(len(data[0]))
                self.dataset_table.setHorizontalHeaderLabels(data[0])

                for row_idx, row_data in enumerate(data[1:]):
                    for col_idx, cell in enumerate(row_data):
                        self.dataset_table.setItem(row_idx, col_idx, QTableWidgetItem(cell))

            self.run_prediction()
        except Exception as e:
            print(f"Failed to load file: {e}")

    def show_svm_model(self):
        df = pd.read_csv(r"data\processed_dataset.csv")

        svm_model = joblib.load("models/svm_model.pkl")
        scaler = joblib.load("models/scaler.pkl")
        le = joblib.load("models/label_encoder.pkl")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        df['routine_encoded'] = le.transform(df['routine'])

        feature_cols = ['device_id', 'user_id', 'routine_encoded', 'patient_id', 'duration', 'hour', 'dayofweek']
        X = df[feature_cols]
        X_scaled = scaler.transform(X)
        predictions = svm_model.predict(X_scaled)

        layout = self.chart_widget.layout()
        if layout is None:
            print("Error: chart_widget layout is not set.")
            return

        for i in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        fig = Figure(figsize=(5, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        colors = ['red' if label == 0 else 'green' for label in predictions]
        ax.scatter(X['user_id'], X['duration'], c=colors, alpha=0.6, edgecolors='k', s=60)

        ax.set_title('SVM Classification: user_id vs duration')
        ax.set_xlabel('user_id')
        ax.set_ylabel('duration')

        layout.addWidget(canvas)

    def run_prediction(self):
        input_csv_path = r"data\processed_dataset.csv"
        predictions = predict_file(input_csv_path)
        self.show_result_button.clicked.connect(lambda: self.display_prediction_results(predictions))

    def display_prediction_results(self, predictions):
        normal_count = sum(1 for p in predictions if p == 1)
        anomalous_count = sum(1 for p in predictions if p == 0)              
        result = f"Anomalous: {anomalous_count}, Normal: {normal_count}"
        self.result_textfield.setText(result)

    def check_single_record(self):
        try:
            device_id = int(self.device_textfield.text())
            user_id = int(self.user_textfield.text())
            routine = self.routine_combobox.currentText()
            patient_id = int(self.patient_textfield.text())
            duration = int(self.duration_textfield.text())

        # Value range checks
            if not (100 <= device_id <= 110):
                raise ValueError("Device ID must be between 100 and 110.")
            if not (1 <= user_id <= 50):
                raise ValueError("User ID must be between 1 and 50.")
            if not (1000 <= patient_id <= 1050):
                raise ValueError("Patient ID must be between 1000 and 1050.")
            if not (10 <= duration <= 150):
                raise ValueError("Duration must be between 10 and 150 minutes.")
            
            record = {
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_id': int(self.device_textfield.text()),
                'user_id': int(self.user_textfield.text()),
                'routine': self.routine_combobox.currentText(),
                'patient_id': int(self.patient_textfield.text()),
                'duration': int(self.duration_textfield.text())
            }
            is_anomalous = predict_single_record(record) # suspicious if isanomalous == 0
            result_text = "Suspicious" if is_anomalous else "Normal"
            self.new_data_result_textfield.setText(result_text)
            color = "#ff6666" if is_anomalous else "#66ff66"
            self.new_data_result_textfield.setStyleSheet(f"background: #300000; color: {color};")

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input values: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Prediction Error", f"Failed to check record: {str(e)}")

    def back(self):
        self.stackedWidget.setCurrentWidget(self.selection_page)
        self.result_textfield.clear()
        self.device_textfield.clear()
        self.user_textfield.clear()
                
        self.patient_textfield.clear()
        self.duration_textfield.clear()
        self.new_data_result_textfield.clear()

        layout = self.chart_widget.layout()
        if layout:
            for i in reversed(range(layout.count())):
                widget_to_remove = layout.itemAt(i).widget()
                if widget_to_remove is not None:
                    widget_to_remove.setParent(None)

    def exit(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
