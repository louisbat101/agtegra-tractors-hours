import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.file_uploader import FileUploader
from components.data_processor import DataProcessor
from components.visualizations import Visualizations
from utils.data_utils import DataUtils
import io

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
        st.session_state.processed_data = pd.DataFrame()

    # Sidebar for controls
    with st.sidebar:
        st.header("📁 File Upload")
        file_uploader = FileUploader()
        uploaded_files = file_uploader.render()
        
        if uploaded_files:
            processor = DataProcessor()
            new_data = processor.process_files(uploaded_files)
            
            if not new_data.empty:
                st.session_state.uploaded_data.append(new_data)
                st.session_state.processed_data = pd.concat(
                    st.session_state.uploaded_data, 
                    ignore_index=True
                ).drop_duplicates()
                st.success(f"✅ Processed {len(uploaded_files)} file(s)")

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
            st.plotly_chart(fig_milestone, use_container_width=True)
        
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
                st.plotly_chart(fig_closest, use_container_width=True)
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