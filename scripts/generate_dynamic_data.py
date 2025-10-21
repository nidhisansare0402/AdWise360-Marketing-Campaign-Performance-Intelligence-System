'''
AdWise360 Project: Marketing Campaign Database Schema
Author: Nidhi Yugesh Sansare
Date: 22-10-2025
'''
import pandas as pd
import random
from datetime import datetime, timedelta
import os

os.makedirs('database', exist_ok=True)

platforms = [1,2,3]  # assume platforms table already has ids 1,2,3
objectives = ['Sales','Traffic','Awareness','Engagement']
regions = ['India','USA','UK']

# Campaigns (10 campaigns)
campaign_rows=[]
start_base = datetime(2025,9,1)
for i, cid in enumerate(range(101,111)):
    pname = f"Campaign_{cid}"
    platform = random.choice(platforms)
    objective = random.choice(objectives)
    start = start_base + timedelta(days=random.randint(0,9))
    end = start + timedelta(days=random.randint(10,25))
    region = random.choice(regions)
    budget = float(random.randint(5000,20000))
    campaign_rows.append([cid, pname, platform, objective, start.date().isoformat(), end.date().isoformat(), region, f"{budget:.2f}"])

df_c = pd.DataFrame(campaign_rows, columns=['campaign_id','campaign_name','platform_id','objective','start_date','end_date','region','budget'])
df_c.to_csv('database/campaigns.csv', index=False)

# Metrics — 20 days per campaign 
metric_rows=[]
mid=1
for row in campaign_rows:
    cid = row[0]
    s = datetime.fromisoformat(row[4])
    days = (datetime.fromisoformat(row[5]) - s).days
    days = max(days,10)
    for d in range(days):
        date = (s + timedelta(days=d)).date().isoformat()
        impressions = random.randint(2000,50000)
        ctr = random.uniform(0.01,0.12)
        clicks = int(impressions * ctr)
        conversions = max(0, int(clicks * random.uniform(0.02,0.25)))
        spend = round(clicks * random.uniform(0.3,3.0),2)
        revenue = round(conversions * random.uniform(5,100),2)
        metric_rows.append([mid, cid, date, impressions, clicks, conversions, f"{spend:.2f}", f"{revenue:.2f}"])
        mid += 1

df_m = pd.DataFrame(metric_rows, columns=['metric_id','campaign_id','date','impressions','clicks','conversions','spend','revenue'])
df_m.to_csv('database/metrics.csv', index=False)

print("Created database/campaigns.csv and database/metrics.csv")

