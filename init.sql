CREATE DATABASE IF NOT EXISTS notifications_db;

USE notifications_db;

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    push_id VARCHAR(255) NOT NULL,
    proc_name VARCHAR(255) DEFAULT NULL,
    client_id VARCHAR(255) DEFAULT NULL,
    response JSON DEFAULT NULL,
    message JSON DEFAULT NULL,
    status ENUM('pending', 'processing', 'notified', 'error') DEFAULT 'pending',
    is_push_sent ENUM('no', 'yes') DEFAULT 'no',
    is_email_sent ENUM('no', 'yes') DEFAULT 'no',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON clients (status);

-- Insert 50 dummy clients
INSERT INTO clients (email, phone, push_id, proc_name, client_id, response, message, status, is_push_sent, is_email_sent)
VALUES 
('client1@example.com', '+12345678901', 'push_id_1', 'worker_1', 1, NULL, NULL, 'pending', 'no', 'no'),
('client2@example.com', '+12345678902', 'push_id_2', 'worker_1', 2, NULL, NULL, 'pending', 'no', 'no'),
('client3@example.com', '+12345678903', 'push_id_3', 'worker_1', 3, NULL, NULL, 'pending', 'no', 'no'),
('client49@example.com', '+12345678949', 'push_id_49', 'worker_1', 4, NULL, NULL, 'pending', 'no', 'no'),
('client50@example.com', '+12345678950', 'push_id_50', 'worker_1', 5, NULL, NULL, 'pending', 'no', 'no');