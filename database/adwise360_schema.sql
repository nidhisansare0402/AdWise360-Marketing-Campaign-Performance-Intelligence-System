/*
AdWise360 Project: Marketing Campaign Database Schema
Author: Nidhi Yugesh Sansare
Date: 18-10-2025
*/
CREATE DATABASE adwise360;
USE adwise360;

-- Table 1 : Platforms
CREATE TABLE platforms(
platform_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(50) NOT NULL
);

-- Table 2 : Campaigns
CREATE TABLE campaigns(
campaign_id INT AUTO_INCREMENT PRIMARY KEY,
platform_id INT NOT NULL,
campaign_name VARCHAR(100) NOT NULL,
objective VARCHAR(50),
start_date DATE,
end_date DATE,
region VARCHAR(50),
budget DECIMAL(12,2),
FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
);

-- Table 3 : Metrics
CREATE TABLE metrics(
metric_id INT AUTO_INCREMENT PRIMARY KEY,
campaign_id INT NOT NULL,
date DATE NOT NULL,
impressions INT DEFAULT 0,
clicks INT DEFAULT 0,
conversions INT DEFAULT 0,
spend DECIMAL(12,2) DEFAULT 0.00,
revenue DECIMAL(12,2) DEFAULT 0.00,
FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Table 4 : Predicitions
CREATE TABLE predictions(
prediction_id INT AUTO_INCREMENT PRIMARY KEY,
campaign_id INT NOT NULL,
model_version VARCHAR(20),
performace_category VARCHAR(20),
probability_score DECIMAL(5,2),
prediction_date DATE,
FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);


SHOW DATABASES;
USE adwise360;
SHOW TABLES;
