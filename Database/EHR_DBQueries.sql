create database EHR_Authentication;
use EHR_Authentication;

-- Step 3: Create the Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Step 4: Create the Fingerprints table
CREATE TABLE Fingerprints (
    user_id INT PRIMARY KEY,
    fingerprint_data LONGBLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Step 5: (Optional/Additional) Create a table for tracking login attempts or sessions
CREATE TABLE Login_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);
INSERT INTO Users (email, password) values ('ifraahmed817@gmail.com', 'BunyanulMarsoos');
select * from users;
