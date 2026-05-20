import streamlit as st
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. DEFINE DATA SCHEMAS (Pydantic models)
# ==========================================
class AdCopySchema(BaseModel):
    headlines: List[str] = Field(description="Generate exactly 15 distinct, high-converting headlines. Max 30 characters each. Must include brand name, keywords, and strong CTAs.")
    descriptions: List[str] = Field(description="Generate exactly 4 comprehensive descriptions. Max 90 characters each. Highlight value props and CTAs.")

class AdGroupSchema(BaseModel):
    ad_group_name: str = Field(description="Descriptive ad group name focusing on a tight semantic sub-category or specific service feature.")
    seed_keywords: List[str] = Field(description="Generate 15 to 25 highly relevant, high-intent seed keywords for this specific sub-category. Mix short-tail and long-tail. Do not include match type punctuation.")
    ad_copy: AdCopySchema

class CampaignSchema(BaseModel):
    campaign_name: str = Field(description="Campaign name formatted as '[Client] | Search | [Brand/Non-Brand]'")
    campaign_type: str = Field(description="Either 'Brand' or 'Non-Brand'")
    ad_groups: List[AdGroupSchema] = Field(description="A comprehensive list of every possible sub-category ad group implied by the client's services.")

# ==========================================
# 2. AI ENGINE FUNCTION
# ==========================================
def generate_marketing_plan(client_name: str, brand_terms: str, website_context: str, onboarding_notes: str, api_key: str):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    You are a Master Performance Marketing Architect. Your goal is to build an exhaustive, enterprise-grade Google Ads search account structure for '{client_name}'.
    
    Core Brand Terms to use for the Brand Campaign:
    {brand_terms}
    
    Website & Core Service Framework:
    {website_context}
    
    Granular Onboarding & Discovery Data:
    {onboarding_notes}
    
    STRICT COMPREHENSIVE BUILDING RULES:
    1. CAMPAIGN SPLIT: You must generate ONE Brand Campaign AND ONE Non-Brand Campaign.
    
    2. BRAND CAMPAIGN STRUCTURE: 
       - Build a Campaign named '{client_name} | Search | Brand'.
       - Create granular Brand Ad Groups (e.g., 'Brand Core', 'Brand + Services', 'Brand + Agency/Company').
       - Populate them with 10-15 high-intent keyword variations strictly combining the provided brand terms ({brand_terms}) with intent words (e.g., '{client_name} agency', '{client_name} performance marketing', etc.).
       - Ad copy for this campaign must heavily emphasize the official site, brand heritage, and core value props.

    3. NON-BRAND CAMPAIGN STRUCTURE:
       - Build a Campaign named '{client_name} | Search | Non-Brand'.
       - Create highly granular, distinct Ad Groups for every sub-service, specific platform capability, or niche angle mentioned in the context. For Acadia, break it down into 'Paid Search Agency', 'Paid Social Specialists', 'Programmatic Advertising', 'Retail Media Services', etc.
       - Provide 15 to 25 seed keywords PER ad group. Include high-intent commercial variations (e.g., 'agency', 'services', 'company'). Do not include brand names here.

    4. MAX OUT AD COPY: For every single ad group (Brand and Non-Brand), you must provide exactly 15 headlines (<30 chars) and 4 descriptions (<90 chars). Ensure dynamic variation.
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an advanced programmatic campaign architect who outputs flawless, exhaustive digital marketing matrices."},
            {"role": "user", "content": prompt}
        ],
        response_format=CampaignSchema, 
    )
    return completion.choices[0].message.parsed

# ==========================================
# 3. BULKSHEET FORMATTING ENGINE
# ==========================================
def build_google_ads_csv(parsed_data: CampaignSchema, final_url: str):
    rows = []
    
    for campaign in parsed_data.ad_groups:
        camp_name = parsed_data.campaign_name
        ag_name = campaign.ad_group_name
        
        # A. Process Keywords (Broad & Exact duplication)
        for kw in campaign.seed_keywords:
            clean_kw = kw.strip().lower().replace("[", "").replace("]", "")
            rows.append({
                "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "Exact", "Keyword": f"[{clean_kw}]",
                "Headline 1": "", "Headline 2": "", "Headline 3": "", "Headline 4": "", "Headline 5": "", "Headline 6": "", "Headline 7": "", "Headline 8": "", "Headline 9": "", "Headline 10": "", "Headline 11": "", "Headline 12": "", "Headline 13": "", "Headline 14": "", "Headline 15": "",
                "Description 1": "", "Description 2": "", "Description 3": "", "Description 4": "", "Final URL": ""
            })
            rows.append({
                "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "Broad", "Keyword": clean_kw,
                "Headline 1": "", "Headline 2": "", "Headline 3": "", "Headline 4": "", "Headline 5": "", "Headline 6": "", "Headline 7": "", "Headline 8": "", "Headline 9": "", "Headline 10": "", "Headline 11": "", "Headline 12": "", "Headline 13": "", "Headline 14": "", "Headline 15": "",
                "Description 1": "", "Description 2": "", "Description 3": "", "Description 4": "", "Final URL": ""
            })
            
        # B. Process Complete RSA Ad Copy Row
        ads = campaign.ad_copy
        ad_row = {
            "Campaign": camp_name, "Ad Group": ag_name, "Criterion Type": "", "Keyword": "",
            "Final URL": final_url
        }
        
        for i in range(1, 16):
            ad_row[f"Headline {i}"] = ads.headlines[i-1] if len(ads.headlines) >= i else ""
            
        for j in range(1, 5):
            ad_row[f"Description {j}"] = ads.descriptions[j-1] if len(ads.descriptions) >= j else ""
            
        rows.append(ad_row)
        
    return pd.DataFrame(rows)

# ==========================================
# 4. WEB INTERFACE LAYOUT & RUN BUTTON CODE
# ==========================================
st.set_page_config(page_title="AI Bulksheet Generator", layout="wide")
st.title("🚀 Google Ads Automation Tool")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Brand Name", placeholder="e.g., Acadia")
    brand_terms = st.text_input("Brand Name Variations / Core Brand Terms", placeholder="e.g., Acadia, Acadia.io, Team Acadia")
    website_url = st.text_input("Client Website URL", placeholder="https://acadia.io")
with col2:
    onboarding_notes = st.text_area("Onboarding & Discovery Notes", placeholder="Paste questionnaire data here...", height=150)

# THIS IS THE RUN BUTTON CODE BLOCK AT THE VERY BOTTOM
if st.button("Generate Bulksheet Architecture", type="primary"):
    if not api_key or not client_name or not website_url or not brand_terms:
        st.error("Please fill in all fields, including Brand Terms.")
    else:
        with st.spinner("Analyzing data and constructing campaign matrices..."):
            try:
                mock_scraped_data = f"Domain: {website_url}. Main category mapping based on brand values."
                
                # Triggers the AI logic
                ai_output = generate_marketing_plan(client_name, brand_terms, mock_scraped_data, onboarding_notes, api_key)
                # Triggers the CSV math logic
                df_output = build_google_ads_csv(ai_output, website_url)
                
                st.success("🎉 Account Structure Created!")
                st.dataframe(df_output)
                
                # Allows your team to download the final CSV
                csv_bytes = df_output.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Google Ads Editor CSV",
                    data=csv_bytes,
                    file_name=f"{client_name.lower().replace(' ', '_')}_google_ads_import.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
