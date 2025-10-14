from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import base64
from typing import List, Optional
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

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
                file_extension = file.filename.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    df = pd.read_csv(file)
                elif file_extension in ['xlsx', 'xls']:
                    df = pd.read_excel(file)
                else:
                    continue
                
                # Process the DataFrame
                processed_df = self._process_dataframe(df, file.filename)
                
                if not processed_df.empty:
                    all_data.append(processed_df)
                
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
        
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
            return pd.DataFrame()
        
        # Find engine hours column
        hours_col = self._find_column(df_lower.columns, self.engine_hours_columns)
        if not hours_col:
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

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and return processed data"""
    
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    processor = DataProcessor()
    data = processor.process_files(files)
    
    if data.empty:
        return jsonify({'error': 'No valid data found in uploaded files'}), 400
    
    # Convert to JSON for frontend
    return jsonify({
        'success': True,
        'data': data.to_dict('records'),
        'summary': {
            'total_tractors': len(data),
            'avg_hours': float(data['engine_hours'].mean()),
            'max_hours': float(data['engine_hours'].max()),
            'min_hours': float(data['engine_hours'].min()),
            'tractors_under_900': int(len(data[data['engine_hours'] < 900]))
        }
    })

@app.route('/visualize', methods=['POST'])
def create_visualizations():
    """Create visualizations from data"""
    
    data_json = request.json.get('data')
    chart_type = request.json.get('chart_type', 'bar')
    
    if not data_json:
        return jsonify({'error': 'No data provided'}), 400
    
    df = pd.DataFrame(data_json)
    
    try:
        if chart_type == 'bar':
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
            
        elif chart_type == 'scatter':
            df['index'] = range(len(df))
            fig = px.scatter(
                df,
                x='index',
                y='engine_hours',
                color='nickname',
                title='Engine Hours Distribution',
                labels={'index': 'Tractor Index', 'engine_hours': 'Engine Hours'}
            )
            
        elif chart_type == 'pie':
            tractors_over_900 = len(df[df['engine_hours'] >= 900])
            tractors_under_900 = len(df[df['engine_hours'] < 900])
            
            milestone_data = pd.DataFrame({
                'Status': ['Under 900 hrs', 'Over 900 hrs'],
                'Count': [tractors_under_900, tractors_over_900]
            })
            
            fig = px.pie(
                milestone_data, 
                values='Count', 
                names='Status',
                title='Tractors by 900 Hour Milestone',
                color_discrete_map={
                    'Under 900 hrs': '#90EE90',
                    'Over 900 hrs': '#FFB6C1'
                }
            )
        
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
        
        # Convert to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'success': True,
            'graph': graphJSON
        })
        
    except Exception as e:
        return jsonify({'error': f'Error creating visualization: {str(e)}'}), 500

@app.route('/export', methods=['POST'])
def export_data():
    """Export data as CSV"""
    
    data_json = request.json.get('data')
    
    if not data_json:
        return jsonify({'error': 'No data provided'}), 400
    
    df = pd.DataFrame(data_json)
    
    # Create CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_data = output.getvalue()
    
    return jsonify({
        'success': True,
        'csv_data': csv_data,
        'filename': 'agtegra_tractor_hours.csv'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)