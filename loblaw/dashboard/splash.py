import streamlit as st

SPLASH_MD = """
# Loblaw Bio Clinical Trial Dashboard
Interactive dashboard for exploring immune cell population frequencies and treatment-response patterns.

## Key Questions:
- What is the frequency of each immune cell population in each sample?
- Do melanoma PBMC responders and non-responders differ under miraclib?
- What does the baseline miraclib melanoma PBMC subset look like?

## Navigation:
- [Data Overview](data_overview)
- [Miraclib Treatment Responder](treatment_response)
"""

st.markdown(SPLASH_MD)
