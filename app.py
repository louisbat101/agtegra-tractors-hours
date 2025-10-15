import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from typing import List, Optional, Dict, Tuple
import numpy as np
import re
import json
import os
from datetime import datetime

# ================================
# DATA PERSISTENCE FUNCTIONS
# ================================
def save_data_to_file(data: pd.DataFrame, filename: str = "cached_data.json"):
    """Save DataFrame to JSON file"""
    try:
        if not data.empty:
            # Convert DataFrame to JSON
            data_dict = {
                'data': data.to_dict('records'),
                'timestamp': datetime.now().isoformat(),
                'columns': list(data.columns)
            }
            
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Save to file
            filepath = os.path.join('data', filename)
            with open(filepath, 'w') as f:
                json.dump(data_dict, f, default=str)
            
            return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_data_from_file(filename: str = "cached_data.json") -> pd.DataFrame:
    """Load DataFrame from JSON file"""
    try:
        filepath = os.path.join('data', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data_dict = json.load(f)
            
            # Convert back to DataFrame
            df = pd.DataFrame(data_dict['data'])
            
            # Convert date columns back to datetime if they exist
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Remove duplicates keeping highest engine hours
            df = remove_duplicates_keep_highest(df)
            
            return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
    
    return pd.DataFrame()

def remove_duplicates_keep_highest(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate nicknames, keeping only the record with highest engine hours"""
    if df.empty or 'nickname' not in df.columns or 'engine_hours' not in df.columns:
        return df
    
    original_count = len(df)
    duplicate_count = df.duplicated(subset=['nickname']).sum()
    
    # Sort by engine_hours in descending order and drop duplicates by nickname
    # This keeps the first occurrence which will be the highest engine hours
    cleaned_df = df.sort_values('engine_hours', ascending=False).drop_duplicates(
        subset=['nickname'], keep='first'
    )
    
    # Sort back by nickname for consistent display
    cleaned_df = cleaned_df.sort_values('nickname').reset_index(drop=True)
    
    # Show info about removed duplicates
    if duplicate_count > 0:
        st.info(f"🔧 Removed {duplicate_count} duplicate entries, keeping highest engine hours for each nickname")
    
    return cleaned_df

def list_saved_data_files() -> List[str]:
    """List all saved data files"""
    try:
        data_dir = 'data'
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            return files
    except:
        pass
    return []

# ================================
# FILE UPLOADER CLASS
# ================================
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

# ================================
# DATA PROCESSOR CLASS
# ================================
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

# ================================
# VISUALIZATIONS CLASS
# ================================
class Visualizations:
    """Creates various visualizations for tractor engine hours data"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create a bar chart of engine hours by tractor nickname"""
        
        # Sort by engine hours for better visualization
        df_sorted = df.sort_values('engine_hours', ascending=True)
        
        fig = px.bar(
            df_sorted,
            x='engine_hours',
            y='nickname',
            orientation='h',
            title='Engine Hours by Tractor',
            labels={'engine_hours': 'Engine Hours', 'nickname': 'Tractor Nickname'},
            color='engine_hours',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=max(400, len(df) * 25),
            showlegend=False,
            xaxis_title="Engine Hours",
            yaxis_title="Tractor Nickname"
        )
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame) -> go.Figure:
        """Create a scatter plot of engine hours distribution"""
        
        # Create index for x-axis if no date column
        df_plot = df.copy()
        df_plot['index'] = range(len(df_plot))
        
        fig = px.scatter(
            df_plot,
            x='index',
            y='engine_hours',
            color='nickname',
            title='Engine Hours Distribution',
            labels={'index': 'Tractor Index', 'engine_hours': 'Engine Hours'},
            hover_data=['nickname', 'engine_hours']
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Tractor Index",
            yaxis_title="Engine Hours"
        )
        
        return fig
    
    def create_line_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Create a line chart showing engine hours over time"""
        
        if 'date' not in df.columns:
            return None
        
        # Sort by date
        df_sorted = df.sort_values('date')
        
        fig = px.line(
            df_sorted,
            x='date',
            y='engine_hours',
            color='nickname',
            title='Engine Hours Over Time',
            labels={'date': 'Date', 'engine_hours': 'Engine Hours'},
            markers=True
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Engine Hours"
        )
        
        return fig
    
    def create_box_plot(self, df: pd.DataFrame) -> go.Figure:
        """Create a box plot for engine hours distribution analysis"""
        
        fig = px.box(
            df,
            y='engine_hours',
            title='Engine Hours Distribution Analysis',
            labels={'engine_hours': 'Engine Hours'}
        )
        
        # Add individual points
        fig.add_trace(
            go.Scatter(
                x=[0] * len(df),
                y=df['engine_hours'],
                mode='markers',
                marker=dict(color='red', size=4, opacity=0.6),
                text=df['nickname'],
                hovertemplate='<b>%{text}</b><br>Engine Hours: %{y}<extra></extra>',
                name='Individual Tractors'
            )
        )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            yaxis_title="Engine Hours"
        )
        
        return fig

# ================================
# MAIN APPLICATION
# ================================
def main():
    st.set_page_config(
        page_title="Agtegra Tractors Hours",
        page_icon="🚜",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🚜 Agtegra Tractors Hours")
    st.markdown("Upload multiple CSV files to compare tractor nicknames and engine hours")

    # Initialize session state
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = []
    if 'processed_data' not in st.session_state:
        # Try to load cached data on startup
        cached_data = load_data_from_file()
        st.session_state.processed_data = cached_data
    
    # Try to load data from uploaded file in session
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = None

    # Sidebar for controls
    with st.sidebar:
        st.header("📁 File Upload")
        
        # Show data persistence options
        st.subheader("💾 Data Persistence")
        
        # Show current data status
        if not st.session_state.processed_data.empty:
            st.success(f"📊 {len(st.session_state.processed_data)} tractors loaded")
            
            # Save current data
            if st.button("💾 Save Data"):
                if save_data_to_file(st.session_state.processed_data):
                    st.success("✅ Data saved successfully!")
            
            # Clear current data
            if st.button("🗑️ Clear Data"):
                st.session_state.processed_data = pd.DataFrame()
                st.session_state.uploaded_data = []
                st.session_state.data_cache = None
                st.rerun()
        
        # Load saved data files
        saved_files = list_saved_data_files()
        if saved_files:
            st.subheader("📂 Load Saved Data")
            selected_file = st.selectbox("Choose saved data:", [""] + saved_files)
            if selected_file and st.button("� Load Selected"):
                loaded_data = load_data_from_file(selected_file)
                if not loaded_data.empty:
                    st.session_state.processed_data = loaded_data
                    st.session_state.data_cache = loaded_data.copy()
                    st.success(f"✅ Loaded {len(loaded_data)} tractors from {selected_file}")
                    st.rerun()
        
        st.header("📁 Upload New Files")
        file_uploader = FileUploader()
        uploaded_files = file_uploader.render()
        
        if uploaded_files:
            processor = DataProcessor()
            new_data = processor.process_files(uploaded_files)
            
            if not new_data.empty:
                # Add new data to existing data
                if not st.session_state.processed_data.empty:
                    combined_data = pd.concat([
                        st.session_state.processed_data, 
                        new_data
                    ], ignore_index=True)
                    
                    # Remove duplicates by keeping the highest engine hours for each nickname
                    st.session_state.processed_data = remove_duplicates_keep_highest(combined_data)
                else:
                    st.session_state.processed_data = remove_duplicates_keep_highest(new_data)
                
                # Auto-save the updated data
                save_data_to_file(st.session_state.processed_data)
                
                st.success(f"✅ Processed {len(uploaded_files)} file(s)")
                st.info("💾 Data automatically saved!")
                st.rerun()

        st.header("📊 Visualization Options")
        viz_options = st.multiselect(
            "Select chart types:",
            ["Bar Chart", "Scatter Plot", "Line Chart", "Box Plot"],
            default=["Bar Chart", "Scatter Plot"]
        )

    # Main content area
    if not st.session_state.processed_data.empty:
        data = st.session_state.processed_data
        
        # Data overview
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Tractors", len(data))
        with col2:
            st.metric("Average Engine Hours", f"{data['engine_hours'].mean():.1f}")
        with col3:
            st.metric("Max Engine Hours", f"{data['engine_hours'].max():.1f}")
        with col4:
            st.metric("Min Engine Hours", f"{data['engine_hours'].min():.1f}")
        with col5:
            tractors_under_900 = len(data[data['engine_hours'] < 900])
            st.metric("Tractors Under 900 hrs", tractors_under_900)

        # Visualizations
        viz = Visualizations()
        
        if "Bar Chart" in viz_options:
            st.subheader("📊 Engine Hours by Tractor")
            fig_bar = viz.create_bar_chart(data)
            st.plotly_chart(fig_bar, width='stretch')

        if "Scatter Plot" in viz_options:
            st.subheader("🔍 Engine Hours Distribution")
            fig_scatter = viz.create_scatter_plot(data)
            st.plotly_chart(fig_scatter, width='stretch')

        if "Line Chart" in viz_options:
            st.subheader("📈 Engine Hours Trend")
            if 'date' in data.columns:
                fig_line = viz.create_line_chart(data)
                st.plotly_chart(fig_line, width='stretch')
            else:
                st.info("Date column not found. Line chart requires date information.")

        if "Box Plot" in viz_options:
            st.subheader("📦 Engine Hours Distribution Analysis")
            fig_box = viz.create_box_plot(data)
            st.plotly_chart(fig_box, width='stretch')

        # Additional visualization for 900 hour milestone
        st.subheader("🎯 900 Hour Milestone Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Chart showing tractors by their proximity to 900 hours
            tractors_over_900 = len(data[data['engine_hours'] >= 900])
            tractors_under_900 = len(data[data['engine_hours'] < 900])
            
            milestone_data = pd.DataFrame({
                'Status': ['Under 900 hrs', 'Over 900 hrs'],
                'Count': [tractors_under_900, tractors_over_900]
            })
            
            fig_milestone = px.pie(
                milestone_data, 
                values='Count', 
                names='Status',
                title='Tractors by 900 Hour Milestone',
                color_discrete_map={
                    'Under 900 hrs': '#90EE90',
                    'Over 900 hrs': '#FFB6C1'
                }
            )
            st.plotly_chart(fig_milestone, width='stretch')
        
        with col2:
            # Show tractors closest to 900 hours
            under_900 = data[data['engine_hours'] < 900].copy()
            if not under_900.empty:
                under_900_sorted = under_900.sort_values('hours_to_900').head(10)
                
                fig_closest = px.bar(
                    under_900_sorted,
                    x='hours_to_900',
                    y='nickname',
                    orientation='h',
                    title='Tractors Closest to 900 Hours',
                    labels={'hours_to_900': 'Hours Remaining to 900', 'nickname': 'Tractor'},
                    color='hours_to_900',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_closest.update_layout(height=400)
                st.plotly_chart(fig_closest, width='stretch')
            else:
                st.info("All tractors have exceeded 900 hours!")

        # Data table
        st.subheader("📋 Data Table")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            min_hours = st.number_input("Min Engine Hours", value=0)
        with col2:
            max_hours = st.number_input("Max Engine Hours", value=int(data['engine_hours'].max()))

        filtered_data = data[
            (data['engine_hours'] >= min_hours) & 
            (data['engine_hours'] <= max_hours)
        ]

        # Format the data for display
        display_data = filtered_data.copy()
        display_data['Engine Hours'] = display_data['engine_hours'].round(1)
        display_data['Hours to 900'] = display_data['hours_to_900'].round(1)
        display_data['Nickname'] = display_data['nickname']
        display_data['Source File'] = display_data['source_file']
        
        # Add status column
        display_data['Status'] = display_data['engine_hours'].apply(
            lambda x: "🔴 Over 900 hrs" if x >= 900 else f"🟢 Under 900 hrs"
        )
        
        # Select columns for display
        columns_to_show = ['Nickname', 'Engine Hours', 'Hours to 900', 'Status', 'Source File']
        if 'date' in filtered_data.columns:
            display_data['Date'] = filtered_data['date']
            columns_to_show.insert(-1, 'Date')
        if 'location' in filtered_data.columns:
            display_data['Location'] = filtered_data['location']
            columns_to_show.insert(-1, 'Location')

        st.dataframe(
            display_data[columns_to_show],
            width='stretch',
            hide_index=True
        )

        # Export functionality
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name="agtegra_tractor_hours.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_data.to_excel(writer, sheet_name='Tractor Data', index=False)
            
            st.download_button(
                label="📗 Download as Excel",
                data=buffer.getvalue(),
                file_name="agtegra_tractor_hours.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        # Welcome message and sample data
        st.info("👆 Upload CSV files using the sidebar to get started!")
        
        # Show data persistence explanation
        st.subheader("💾 Data Persistence")
        st.markdown("""
        **Your data now persists across devices and sessions!**
        
        🔄 **Automatic Saving**: Data is automatically saved when you upload files
        
        📱 **Cross-Device Access**: Open this app on any device to access your saved data
        
        💾 **Manual Save/Load**: Use the sidebar to save current data or load previously saved datasets
        
        🗑️ **Data Management**: Clear data when you want to start fresh
        """)
        
        st.subheader("📋 Expected CSV Format")
        sample_data = pd.DataFrame({
            'nickname': ['Tractor_A', 'Tractor_B', 'Tractor_C'],
            'last_known_engine_hrs': [1250.5, 890.2, 2100.0],
            'date': ['2025-10-14', '2025-10-14', '2025-10-14'],
            'location': ['Field_1', 'Field_2', 'Field_3']
        })
        
        # Add the calculated column for display
        sample_data['hours_to_900'] = 900 - sample_data['last_known_engine_hrs']
        sample_data['hours_to_900'] = sample_data['hours_to_900'].apply(lambda x: max(0, x))
        
        # Format for display
        display_sample = pd.DataFrame({
            'Nickname': sample_data['nickname'],
            'Engine Hours': sample_data['last_known_engine_hrs'],
            'Hours to 900': sample_data['hours_to_900'],
            'Date': sample_data['date'],
            'Location': sample_data['location']
        })
        
        st.dataframe(display_sample, width='stretch', hide_index=True)
        
        # Sample data download
        csv_sample = sample_data.to_csv(index=False)
        st.download_button(
            label="📄 Download Sample CSV",
            data=csv_sample,
            file_name="sample_agtegra_tractor_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()