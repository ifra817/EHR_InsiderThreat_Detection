# 🩺 EHR Insider Threat Detection System

An advanced, multi-factor authentication-based system that detects insider threats in Electronic Health Records (EHR) using Machine Learning and Biometric Verification.

---

## 🧪 Features
- Secure Login with Multi-Factor Authentication  
- OTP-based Email Verification  
- Fingerprint Biometric Login  
- EHR Dataset Anomaly Detection via SVM  
- Custom Input Prediction Interface  
- Activity Logging and Tracking  

---

## 🧠 Project Workflow

The system enforces **multi-factor authentication** before granting access to sensitive EHR functionalities:

1. **Login**  
   The user enters their registered email and password.
   ![image](https://github.com/user-attachments/assets/b81fd762-5237-4e1f-8fd6-135a061c87ab)


3. **Email Verification**  
   A 6-digit OTP is sent to the user's email address. If valid, the process continues.
   ![image](https://github.com/user-attachments/assets/96a3368c-a845-4058-b7e7-8457dc551ff4)


5. **Fingerprint Verification**  
   The system compares the scanned fingerprint with the registered template using minutiae-based matching via SecuGen SDK.
   ![image](https://github.com/user-attachments/assets/1365486a-23fa-424a-b71f-31086d4a1690)


7. **EHR Threat Detection**  
   After successful authentication, two options are available:
   ![image](https://github.com/user-attachments/assets/baee11d2-9314-43df-ab86-83628d0d2116)

   - **Load Preprocessed Dataset**  
     View the table, SVM scatter plot, and statistics of suspicious vs. normal access.
     ![image](https://github.com/user-attachments/assets/4031ec37-cc93-44f1-9d8c-ba73a90dcdc9)

   - **Predict New Entry**  
     Input new EHR access fields to predict if the behavior is **normal** or **suspicious** using a pre-trained SVM model.
     ![image](https://github.com/user-attachments/assets/5b152bb8-de26-430f-9b08-3a445f7e2e46)


> ✳️ **Note**: New user registration is only available through `fingerprint/register_fingerprint.py`.

---

## 📂 Project Structure

```bash
EHR_InsiderThreat_Detection/
│
├── main.py # Entry point with GUI and workflow logic
├── EHR_system.py # EHR anomaly detection & ML logic
├── email_utils.py # OTP generation and email sender
│
├── data/
│ ├── EHR_dataset.csv # Original dataset
│ └── preprocessed_dataset.csv # Preprocessed for ML model
│
├── Database/
│ ├── db_config.json # DB connection credentials
│ ├── db_connect.py # DB connection handler
│ └── EHR_DBQueries.sql # SQL schema
│
├── fingerprint/
│ ├── capture/ # Fingerprint capture logic
│ ├── fingerprints/ # Stored .dat fingerprint files
│ ├── match_template.py # Template matcher
│ ├── match_utils.py # Matching helper functions
│ ├── register_fingerprint.py # Used to register new user
│ └── store_template.py # Store fingerprint in DB
│
├── GUI/
│ ├── bg_image.jpg # Background image
│ ├── gui.py # Main GUI logic
│ └── gui.ui # Qt Designer file
│
├── models/
│ ├── features.pkl
│ ├── label_encoder.pkl
│ ├── scaler.pkl
│ └── svm_model.pkl # Trained SVM model for detection

```

---

## 🛠️ Tech Stack

- **Frontend/UI**: PyQt5 + Qt Designer
- **Backend**: Python, C++
- **Database**: MySQL
- **Fingerprint Verification**: SecuGen SDK + Minutiae Matcher (Custom Logic)

---

## 🔐 Multi-Factor Authentication

- **Email + Password**
- **Email OTP**
- **Fingerprint Biometric**

Stored securely in a **MySQL** database.

### 🧬 Database Schema

```sql
CREATE DATABASE EHR_Authentication;
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Fingerprints (
    fingerprint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fingerprint_data LONGBLOB NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Login_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    ip_address VARCHAR(255),
    user_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);
```

## 💻 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/ifra817/EHR_InsiderThreat_Detection.git
cd EHR_InsiderThreat_Detection
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. [Optional] Disable Fingerprint (For Testing without Scanner)

If you do not have a fingerprint scanner:

- Open main.py
- Go to line 105 inside the verify_otp function.
  Replace:
  ```python
  self.stackedWidget.setCurrentWidget(self.Fingerprint_Authentication)
  ```
  with:
  ```python
  QTimer.singleShot(1500, self.start_loading_screen)
  ```
  
### 4. Start the Application

```bash
python main.py
```

---

## 📦 Dependencies

From requirements.txt:
```ini
PyQt5==5.15.11
matplotlib==3.9.2
pandas==2.2.2
numpy==2.1.0
scikit-learn==1.5.2
sklearn-compat==0.1.3
joblib==1.4.2
scipy==1.14.1
opencv-python==4.11.0.86
scikit-image==0.25.2
pymysql==1.1.1
cryptography
```

---

## 📸 Fingerprint Matching
- Biometric Authentication using SecuGen SDK
- Templates matched via custom Minutiae Matching Algorithm
- Fingerprints stored securely in .dat format & saved in MySQL BLOBs

---

## 🧑‍💻 Developer Notes
Project built & tested using VS Code
For demo/testing without biometric hardware, follow the fingerprint bypass instructions above

---

## 🤝 Contributing
Pull requests and issue reports are welcome!
For feature requests, bugs, or improvements, open an issue or contact the maintainer.

--- 

## 👤 Author

**Ifra Ahmed**  
[LinkedIn Profile](www.linkedin.com/in/ifra-ahmed-096423319)

