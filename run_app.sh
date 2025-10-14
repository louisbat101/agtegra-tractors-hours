#!/bin/bash
pip install -r requirements.txt
streamlit run app.py --server.headless=true --server.enableCORS=false