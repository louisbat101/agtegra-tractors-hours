# Agtegra Tractors Hours

A Streamlit-based dashboard for importing multiple CSV files and visualizing Agtegra tractor nickname vs. last known engine hours data with drag-and-drop functionality.

## Features

- 📁 Drag-and-drop CSV file upload
- 📊 Interactive graphs comparing nickname and engine hours
- 📈 Multiple visualization options (bar charts, scatter plots, line charts)
- 📋 Data table view with filtering and sorting
- 💾 Export functionality for processed data
- 🔄 Real-time data updates

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit dashboard:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the displayed URL (usually `http://localhost:8501`)

3. Upload your CSV files using the drag-and-drop interface

4. Explore the data visualizations and interactive features

## CSV File Format

Your CSV files should contain at least these columns:
- `nickname` (or similar): Tractor identifier/name
- `last_known_engine_hrs` (or similar): Engine hours value

Example CSV structure:
```csv
nickname,last_known_engine_hrs,date,location
Tractor_A,1250.5,2025-10-14,Field_1
Tractor_B,890.2,2025-10-14,Field_2
```

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── components/            # Reusable dashboard components
│   ├── __init__.py
│   ├── file_uploader.py   # File upload handling
│   ├── data_processor.py  # CSV data processing
│   └── visualizations.py  # Chart and graph components
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── data_utils.py      # Data manipulation helpers
├── data/                  # Sample data and uploads
│   └── sample_data.csv    # Sample CSV file
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.