/*
AdWise360 Project: Marketing Campaign Database Schema
Author: Nidhi Yugesh Sansare
Date: 18-10-2025
*/

USE adwise360;
INSERT INTO platforms (name)
VALUES ('Google Ads'), ('Facebook Ads'), ('YouTube');

INSERT INTO campaigns (platform_id, campaign_name, objective, start_date, end_date, region, budget)
VALUES 
(1, 'Diwali Sale 2025', 'Sales', '2025-10-01', '2025-10-15', 'India', 15000),
(2, 'Winter Offers', 'Traffic', '2025-10-05', '2025-10-25', 'USA', 12000);

SELECT * FROM platforms;
SELECT * FROM campaigns;