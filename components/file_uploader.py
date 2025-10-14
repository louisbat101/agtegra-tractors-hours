import streamlit as st
import pandas as pd
from typing import List, Optional

class FileUploader:
    """Handles file upload functionality with drag-and-drop support"""
    
    def __init__(self):
        self.accepted_formats = ['csv', 'xlsx', 'xls']
    
    def render(self) -> Optional[List]:
        """Render the file upload widget"""
        
        st.markdown("### Drag and Drop CSV Files")
        st.markdown("Supported formats: CSV, Excel (.xlsx, .xls)")
        
        uploaded_files = st.file_uploader(
            "Choose CSV files",
            type=self.accepted_formats,
            accept_multiple_files=True,
            help="Upload one or more CSV or Excel files containing tractor data"
        )
        
        if uploaded_files:
            st.write(f"📁 {len(uploaded_files)} file(s) uploaded:")
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024  # Size in KB
                st.write(f"- {file.name} ({file_size:.1f} KB)")
        
        return uploaded_files
    
    def validate_file(self, file) -> bool:
        """Validate uploaded file format"""
        file_extension = file.name.split('.')[-1].lower()
        return file_extension in self.accepted_formats