CREATE DATABASE voiceform CHARACTER SET utf8mb4;
CREATE USER 'voiceform'@'%' IDENTIFIED BY 'voiceform';
GRANT ALL PRIVILEGES ON voiceform.* TO 'voiceform'@'%';