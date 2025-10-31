/*
AdWise360 Project: Marketing Campaign Database Schema
Author: Nidhi Yugesh Sansare
Date: 31-10-2025
*/
Use adwise360;

# verify imported data
SELECT COUNT(*) FROM campaigns;
SELECT COUNT(*) FROM metrics;

SELECT * FROM campaigns;
SELECT * FROM metrics LIMIT 5;

#analytical queries
#connect campaigns with their platforms and metrics:
SELECT 
	c.campaign_id,
    c.campaign_name,
    p.name,
    c.objective,
    c.region,
    m.date,
    m.impressions,
    m.conversions,
    m.spend,
    m.revenue
FROM campaigns c
JOIN platforms p ON c.platform_id = p.platform_id
JOIN metrics m ON c.campaign_id = m.campaign_id
LIMIT 10;

#Calculate CTR, CPC, ROI for Each Campaign - shows which campaigns are most profitable and on which platform.
SELECT 
	c.campaign_id,
    c.campaign_name,
    p.name,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND(SUM(m.spend)/SUM(m.clicks),2) AS CPC,
    ROUND(SUM(m.spend)/SUM(m.conversions),2) AS CPA,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS Avg_ROI
FROM campaigns c
JOIN platforms p ON c.platform_id = p.platform_id
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.campaign_id, p.name
ORDER BY Avg_ROI DESC;

#Platform-Wise Performance - identify the best performing platform
SELECT 
    p.name,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS Avg_CTR,
    ROUND(SUM(m.spend)/SUM(m.clicks),2) AS Avg_CPC,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS Avg_ROI
FROM campaigns c
JOIN platforms p ON c.platform_id = p.platform_id
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY p.name
ORDER BY Avg_ROI DESC;

# advanced analytical queries
# Region-wise Performance Analysis - which region gives the best ROI and lowest CPA
SELECT 
    c.region,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND(SUM(m.spend)/SUM(m.clicks),2) AS CPC,
    ROUND(SUM(m.spend)/SUM(m.conversions),2) AS CPA,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI
FROM campaigns c
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.region
ORDER BY ROI DESC;

# Objective wise Campaign Effectiveness - which marketing objective drives more conversions or ROI
SELECT 
    c.objective,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND(SUM(m.conversions)/SUM(m.clicks)*100,2) AS Conversion_Rate,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI
FROM campaigns c
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.objective
ORDER BY ROI DESC;

# Daily Performance Trend - shows how spend, revenue, and engagement change day-by-day, helping identify peak performance days.
SELECT 
    m.date,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS Avg_CTR,
    ROUND(SUM(m.spend),2) AS Total_Spend,
    ROUND(SUM(m.revenue),2) AS Total_Revenue,
    ROUND((SUM(m.revenue)-SUM(m.spend)),2) AS Net_Profit
FROM metrics m
GROUP BY m.date
ORDER BY m.date ASC;

# Top Performing Campaigns by ROI - Top 5 campaigns
SELECT 
    c.campaign_name,
    p.name,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI,
    ROUND(SUM(m.revenue),2) AS Total_Revenue,
    ROUND(SUM(m.spend),2) AS Total_Spend
FROM campaigns c
JOIN metrics m ON c.campaign_id = m.campaign_id
JOIN platforms p ON c.platform_id = p.platform_id
GROUP BY c.campaign_id, p.name
ORDER BY ROI DESC
LIMIT 5;

# Top Performing Platforms by ROI - which ad platform gives best ROI
SELECT 
    p.name,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND(SUM(m.spend)/SUM(m.clicks),2) AS CPC,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI
FROM platforms p
JOIN campaigns c ON c.platform_id = p.platform_id
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY p.name
ORDER BY ROI DESC;

# High CTR but Low ROI Campaigns - campaigns are getting attention (high CTR) but not conversions
SELECT 
    c.campaign_name,
    p.name,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI
FROM campaigns c
JOIN metrics m ON c.campaign_id = m.campaign_id
JOIN platforms p ON c.platform_id = p.platform_id
GROUP BY c.campaign_id, p.name
HAVING CTR > 5 AND ROI < 300
ORDER BY CTR DESC;

# Campaign Performance Summary - Combine all KPIs and group by platform and region
SELECT 
    p.name,
    c.region,
    ROUND(SUM(m.impressions)/1000,2) AS Total_Impressions_K,
    ROUND(SUM(m.clicks)/SUM(m.impressions)*100,2) AS CTR,
    ROUND(SUM(m.conversions)/SUM(m.clicks)*100,2) AS Conversion_Rate,
    ROUND(SUM(m.spend)/SUM(m.clicks),2) AS CPC,
    ROUND(SUM(m.spend)/SUM(m.conversions),2) AS CPA,
    ROUND((SUM(m.revenue)-SUM(m.spend))/SUM(m.spend)*100,2) AS ROI
FROM platforms p
JOIN campaigns c ON c.platform_id = p.platform_id
JOIN metrics m ON c.campaign_id = m.campaign_id
GROUP BY p.name, c.region
ORDER BY ROI DESC;




