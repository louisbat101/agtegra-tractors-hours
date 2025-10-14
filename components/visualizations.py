import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional

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
        
        if 'source_file' in df.columns:
            fig.update_traces(
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                              'Engine Hours: %{y}<br>' +
                              '<extra></extra>'
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
    
    def create_histogram(self, df: pd.DataFrame) -> go.Figure:
        """Create a histogram of engine hours distribution"""
        
        fig = px.histogram(
            df,
            x='engine_hours',
            nbins=20,
            title='Engine Hours Distribution Histogram',
            labels={'engine_hours': 'Engine Hours', 'count': 'Number of Tractors'}
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Engine Hours",
            yaxis_title="Number of Tractors"
        )
        
        return fig
    
    def create_summary_metrics(self, df: pd.DataFrame) -> dict:
        """Create summary metrics for the dashboard"""
        
        if df.empty:
            return {}
        
        return {
            'total_tractors': len(df),
            'average_hours': df['engine_hours'].mean(),
            'median_hours': df['engine_hours'].median(),
            'max_hours': df['engine_hours'].max(),
            'min_hours': df['engine_hours'].min(),
            'std_hours': df['engine_hours'].std()
        }