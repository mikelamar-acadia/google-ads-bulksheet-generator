import streamlit as st
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# 1. Define Data Schemas
class AdCopySchema(BaseModel):
    headlines: List[str] = Field(description="List of 5 to 15 headlines, max 30 characters each.")
    descriptions: List[str] = Field(description="List of 2 to 4 descriptions, max 90 characters each.")

class AdGroupSchema(BaseModel):
    ad_group_name: str = Field(description="Name of the ad group (e.g., 'Brand Core' or 'Category - Blue Widgets')")
    seed_keywords: List[str] = Field(description="List of 5-10 highly relevant core keywords without match types.")
    ad_copy: AdCopySchema

class CampaignSchema(BaseModel):
    campaign_name: str = Field(description="Campaign name following '[Client] | Search | [Brand/Non-Brand]'")
    campaign_type: str = Field(description="Either 'Brand' or 'Non-Brand'")
    ad_groups: List[AdGroupSchema]

# 2. AI Engine Function
def generate_marketing_plan(client_name: str, website_context: str, onboarding_notes: str, api_key: str):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    You are an expert Google Ads Media Planner. Generate a consolidated Search campaign structure for a client named '{client_name}'.
    Website Context: {website_context}
    Onboarding Notes: {onboarding_notes}
    Rules: Minimize campaigns. Create ONE Brand Campaign and ONE consolidated Non-Brand Campaign.
    Divide Non-Brand into relevant categories. Provide compliant Google Ads copy (Headlines < 30 chars, Descriptions < 90).
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a programmatic Google Ads bulksheet generator."},
            {"role": "user", "content": prompt}
        ],
        response_format=CampaignSchema, 
    )
    return completion.choices[0].message.parsed

# 3. Bulksheet Formatting Engine
def build_google_ads_csv(parsed_data: CampaignSchema, final_url: str):
    rows = []
    for campaign in parsed_data.ad_groups:
        camp_name = parsed_data.campaign_name
        ag_name = campaign.ad_group_name
        
        for kw in campaign.seed_keywords:
            clean_kw = kw.strip().lower().replace("[", "").replace("]", "")
            rows.append({
                "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "Exact",
                "Keyword": f"[{clean_kw}]", "Headline 1": "", "Headline 2": "", "Description 1": ""
            })
            rows.append({
                "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "Broad",
                "Keyword": clean_kw, "Headline 1": "", "Headline 2": "", "Description 1": ""
            })
            
        ads = campaign.ad_copy
        rows.append({
            "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "", "Keyword": "",
            "Headline 1": ads.headlines[0] if len(ads.headlines) > 0 else "Official Site",
            "Headline 2": ads.headlines[1] if len(ads.headlines) > 1 else "Shop Now",
            "Description 1": ads.descriptions[0] if len(ads.descriptions) > 0 else "Explore our selection today.",
            "Final URL": final_url
        })
    return pd.DataFrame(rows)

# 4. Web Interface Layout
st.set_page_config(page_title="AI Bulksheet Generator", layout="wide")
st.title("🚀 Google Ads Automation Tool")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Brand Name", placeholder="e.g., Acme Corp")
    website_url = st.text_input("Client Website URL", placeholder="https://www.acme.com")
with col2:
    onboarding_notes = st.text_area("Onboarding & Discovery Notes", placeholder="Paste questionnaire data here...", height=150)

if st.button("Generate Bulksheet Architecture", type="primary"):
    if not api_key or not client_name or not website_url:
        st.error("Please fill in all fields.")
    else:
        with st.spinner("Analyzing data..."):
            try:
                mock_scraped_data = f"Domain: {website_url}. Main category mapping based on brand values."
                ai_output = generate_marketing_plan(client_name, mock_scraped_data, onboarding_notes, api_key)
                df_output = build_google_ads_csv(ai_output, website_url)
                st.success("🎉 Account Structure Created!")
                st.dataframe(df_output)
                
                csv_bytes = df_output.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Google Ads Editor CSV",
                    data=csv_bytes,
                    file_name=f"{client_name.lower().replace(' ', '_')}_google_ads_import.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
