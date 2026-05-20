import streamlit as st
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. ENTERPRISE DATA MODELS & SCHEMAS
# ==========================================
class AdCopySchema(BaseModel):
    headlines: List[str] = Field(description="Generate exactly 15 distinct headlines. Max 30 characters each. Focus on hooks, brand authority, and CTAs.")
    descriptions: List[str] = Field(description="Generate exactly 4 comprehensive descriptions. Max 90 characters each.")

class AdGroupSchema(BaseModel):
    ad_group_name: str = Field(description="Granular ad group name focusing on a tight semantic sub-category, service pillar, or brand variation bucket.")
    seed_keywords: List[str] = Field(description="Generate 15 to 25 highly relevant seed keywords for this specific intent bucket. No match type punctuation.")
    ad_copy: AdCopySchema

class CampaignSchema(BaseModel):
    campaign_name: str = Field(description="Campaign name formatted exactly as '[Client Brand] | Search | Brand' or '[Client Brand] | Search | Non-Brand'")
    campaign_type: str = Field(description="Must be exactly either 'Brand' or 'Non-Brand'")
    ad_groups: List[AdGroupSchema] = Field(description="List of granular ad groups built to live inside this specific campaign.")

# Updated to support campaign-level and account-level negative keywords
class AccountBuildSchema(BaseModel):
    client_detected_name: str = Field(description="The clean, standardized brand name extracted from the URL or text context.")
    suggested_brand_variations: List[str] = Field(description="Core clean brand terms and structural combinations to use for the Brand Campaign.")
    campaigns: List[CampaignSchema] = Field(description="Comprehensive list of multiple distinct campaigns (1 Brand Campaign and 1 consolidated Non-Brand Campaign).")
    account_level_negatives: List[str] = Field(description="Generate a list of 30-50 highly critical negative keywords tailored specifically to this business context (e.g., jobs, cheap, templates, courses, free, DIY, unrelated niches).")

# ==========================================
# 2. ADVANCED AI ENGINE FUNCTION
# ==========================================
def generate_marketing_plan(website_url: str, onboarding_notes: str, api_key: str):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    You are an Elite Enterprise Search Engine Marketing Architect. Your task is to completely reverse-engineer a full Google Ads search account structure based on this URL context: '{website_url}' and these unstructured discovery notes: '{onboarding_notes}'.
    
    CRITICAL BUILDING PROTOCOLS:
    1. EXTRACT BRAND: Figure out the clean brand name from the URL and use it to form the naming conventions.
    2. BRAND CAMPAIGN STRUCTURE & ZERO MISSPELLINGS: 
       - Title it '[Brand Name] | Search | Brand'. Under it, create multiple clean brand ad groups (e.g., 'Brand Core', 'Brand + Services', 'Brand + Intent').
       - CRITICAL RULE: Do NOT misspell the brand name under any circumstances. Keep the brand name spelled 100% correctly across all keywords. Focus instead on structural intent variations (e.g., if brand is 'Acadia', generate 'Acadia marketing', 'Acadia agency', 'Acadia performance', 'Acadia company').
    3. NON-BRAND CAMPAIGN STRUCTURE:
       - Title it '[Brand Name] | Search | Non-Brand'. Under it, analyze the website offerings and break them out into deeply granular, highly distinct sub-category Ad Groups. Do not group unrelated service pillars.
    4. KEYWORD EXPANSION: Provide a massive list of 15 to 25 seed keywords PER ad group. 
    5. RESPONSIVE SEARCH ADS (RSAs): For every single ad group, provide exactly 15 headlines (<30 chars) and 4 descriptions (<90 chars). Ensure high semantic variation.
    6. NEGATIVE KEYWORD EXTRACTION: Scrutinize the onboarding notes and website context to generate a robust list of highly relevant negative keywords to prevent budget waste (e.g., filter out careers, low-intent information seekers, or adjacent industries).
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an advanced programmatic campaign architect who outputs flawless, exhaustive multi-campaign digital marketing arrays with strict structural rules."},
            {"role": "user", "content": prompt}
        ],
        response_format=AccountBuildSchema, 
    )
    return completion.choices[0].message.parsed

# ==========================================
# 3. BULKSHEET FORMATTING ENGINE
# ==========================================
def build_google_ads_csv(account_data: AccountBuildSchema, final_url: str):
    rows = []
    
    # Process regular campaigns, ad groups, keywords, and ads
    for campaign in account_data.campaigns:
        camp_name = campaign.campaign_name
        
        for ad_group in campaign.ad_groups:
            ag_name = ad_group.ad_group_name
            
            # A. Process Keywords (Generates Broad & Exact duplicates in the same ad group)
            for kw in ad_group.seed_keywords:
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
                
            # B. Process Complete RSA Ad Copy Row mapped to this group
            ads = ad_group.ad_copy
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
# 4. SIMPLIFIED USER INTERFACE
# ==========================================
st.set_page_config(page_title="AI Bulksheet Generator", layout="wide")
st.title("🚀 Enterprise Google Ads Setup Engine")
st.subheader("Wipe out manual building. Drop a URL and map an entire account structural bulk file.")

with st.sidebar:
    st.header("Authorization")
    api_key = st.text_input("OpenAI API Key", type="password")

col1, col2 = st.columns([1, 2])
with col1:
    website_url = st.text_input("Client Website URL", placeholder="https://acadia.io")
    st.info("""The algorithm will auto-detect the Brand Name, build clean Brand ad groups, and systematically slice up Non-Brand service/product categories based on the business offerings.""")

with col2:
    onboarding_notes = st.text_area("Optional Discovery Notes / Core Guidelines", placeholder="Paste any optional discovery documentation, target audiences, or value propositions here to refine the output...", height=175)

if st.button("Execute Deep Account Mapping", type="primary"):
    if not api_key or not website_url:
        st.error("Please provide both your OpenAI API Key and the target Client Website URL.")
    else:
        with st.spinner("Analyzing target ecosystem, engineering keyword arrays, and writing copy structures..."):
            try:
                # Core processing pass
                ai_output = generate_marketing_plan(website_url, onboarding_notes, api_key)
                df_output = build_google_ads_csv(ai_output, website_url)
                
                # Interface updates
                st.success(f"🎉 Architecture mapped for brand: **{ai_output.client_detected_name.upper()}**")
                
                # Layout split for display
                disp_col1, disp_col2 = st.columns(2)
                
                with disp_col1:
                    st.subheader("Core Brand Combinations")
                    st.write(", ".join(ai_output.suggested_brand_variations))
                
                with disp_col2:
                    st.subheader("🛑 Recommended Account Negative Keywords")
                    # Display negatives in a clean text area for quick copying
                    negatives_text = "\n".join(ai_output.account_level_negatives)
                    st.text_area("Copy and paste directly into Google Ads Negative Lists:", value=negatives_text, height=150)
                
                st.subheader("Generated Google Ads Bulksheet Preview")
                st.dataframe(df_output)
                
                csv_bytes = df_output.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Ready-to-Import Google Ads Editor CSV",
                    data=csv_bytes,
                    file_name=f"{ai_output.client_detected_name.lower().replace(' ', '_')}_google_ads_import.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"An error occurred during matrix compilation: {e}")
