import streamlit as st
import pandas as pd
import io
from typing import List, Optional

class DataProcessor:
    """Processes uploaded CSV and Excel files"""
    
    def __init__(self):
        self.nickname_columns = ['nickname', 'name', 'tractor_name', 'id', 'identifier']
        self.engine_hours_columns = [
            'last_known_engine_hrs', 'engine_hours', 'hours', 
            'last_engine_hours', 'engine_hrs', 'total_hours'
        ]
    
    def process_files(self, uploaded_files: List) -> pd.DataFrame:
        """Process multiple uploaded files and return combined DataFrame"""
        
        all_data = []
        
        for file in uploaded_files:
            try:
                # Read the file based on its extension
                file_extension = file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df = pd.read_csv(file)
                elif file_extension in ['xlsx', 'xls']:
                    df = pd.read_excel(file)
                else:
                    st.warning(f"Unsupported file format: {file.name}")
                    continue
                
                # Process the DataFrame
                processed_df = self._process_dataframe(df, file.name)
                
                if not processed_df.empty:
                    all_data.append(processed_df)
                    st.success(f"✅ Successfully processed: {file.name}")
                else:
                    st.warning(f"⚠️ No valid data found in: {file.name}")
                
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
    
    def _process_dataframe(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Process individual DataFrame to standardize column names"""
        
        # Make column names lowercase for easier matching
        df_lower = df.copy()
        df_lower.columns = df_lower.columns.str.lower().str.strip()
        
        # Find nickname column
        nickname_col = self._find_column(df_lower.columns, self.nickname_columns)
        if not nickname_col:
            st.warning(f"No nickname column found in {filename}")
            return pd.DataFrame()
        
        # Find engine hours column
        hours_col = self._find_column(df_lower.columns, self.engine_hours_columns)
        if not hours_col:
            st.warning(f"No engine hours column found in {filename}")
            return pd.DataFrame()
        
        # Create standardized DataFrame
        processed_df = pd.DataFrame({
            'nickname': df_lower[nickname_col],
            'engine_hours': pd.to_numeric(df_lower[hours_col], errors='coerce'),
            'source_file': filename
        })
        
        # Add hours to 900 column
        processed_df['hours_to_900'] = 900 - processed_df['engine_hours']
        processed_df['hours_to_900'] = processed_df['hours_to_900'].apply(
            lambda x: max(0, x) if pd.notna(x) else 0
        )
        
        # Add additional columns if they exist
        date_columns = ['date', 'timestamp', 'created_date', 'last_updated']
        date_col = self._find_column(df_lower.columns, date_columns)
        if date_col:
            processed_df['date'] = pd.to_datetime(df_lower[date_col], errors='coerce')
        
        location_columns = ['location', 'field', 'site', 'area']
        location_col = self._find_column(df_lower.columns, location_columns)
        if location_col:
            processed_df['location'] = df_lower[location_col]
        
        # Remove rows with invalid engine hours
        processed_df = processed_df.dropna(subset=['engine_hours'])
        processed_df = processed_df[processed_df['engine_hours'] >= 0]
        
        return processed_df
    
    def _find_column(self, columns, possible_names: List[str]) -> Optional[str]:
        """Find the best matching column name"""
        column_list = list(columns)
        for col in column_list:
            if col in possible_names:
                return col
        
        # Try partial matching
        for col in column_list:
            for name in possible_names:
                if name in col or col in name:
                    return col
        
        return None
    
    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """Get summary statistics for the processed data"""
        if df.empty:
            return {}
        
        return {
            'total_records': len(df),
            'unique_tractors': df['nickname'].nunique(),
            'avg_engine_hours': df['engine_hours'].mean(),
            'max_engine_hours': df['engine_hours'].max(),
            'min_engine_hours': df['engine_hours'].min(),
            'files_processed': df['source_file'].nunique()
        }