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

INSERT INTO Users (email, password) values ('ifraahmed817@gmail.com', 'BunyanulMarsoos');
SELECT * FROM Users;

