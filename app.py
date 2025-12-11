"""Streamlit web app for FitNotes to Hevy conversion."""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from io import StringIO
from main import parse_time_to_seconds

st.set_page_config(page_title="FitNotes to Hevy Converter", page_icon="🏋️")

st.title("🏋️ FitNotes to Hevy Converter")
st.markdown("Convert your FitNotes workout data to Hevy-compatible format")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    timezone_offset = st.number_input("Timezone Offset (hours)", value=10, min_value=-12, max_value=14)
    workout_time = st.time_input("Default Workout Time", value=datetime.strptime("07:00", "%H:%M").time())
    
# File upload
uploaded_file = st.file_uploader("Upload FitNotes CSV Export", type=['csv'])

if uploaded_file:
    try:
        # Read uploaded file
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Loaded {len(df)} workout sets from {df['Date'].nunique()} workouts")
        
        # Show preview
        with st.expander("📊 Preview Data"):
            st.dataframe(df.head(20))
        
        # Load mappings
        @st.cache_data
        def load_mappings():
            map_fn2hevy = {}
            for filename in ['default', 'extra', 'custom']:
                try:
                    with open(f'./files/map_fitnotes2hevy_{filename}.json', 'r') as f:
                        mapping = json.load(f)
                        if filename == 'custom':
                            mapping = {k: v for k, v in mapping.items() if not k.startswith('_')}
                        map_fn2hevy.update(mapping)
                except FileNotFoundError:
                    pass
            return map_fn2hevy
        
        mappings = load_mappings()
        
        # Show unmapped exercises
        unmapped = df[~df['Exercise'].isin(mappings.keys())]['Exercise'].unique()
        if len(unmapped) > 0:
            with st.expander(f"⚠️ {len(unmapped)} Unmapped Exercises"):
                st.warning("These exercises will keep their original names:")
                for ex in unmapped:
                    st.text(f"• {ex}")
        
        # Convert button
        if st.button("🔄 Convert to Hevy Format", type="primary"):
            with st.spinner("Converting..."):
                # Prepare data
                df['first_appearance'] = df.groupby(['Date', 'Exercise']).cumcount()
                df['exercise_order'] = df.groupby(['Date', 'Exercise'])['first_appearance'].transform('idxmin')
                
                # Convert fields
                df['Workout #'] = df.groupby('Date').ngroup() + 1
                workout_time_str = workout_time.strftime('%H:%M:%S')
                df['Date'] = (pd.to_datetime(df['Date'] + ' ' + workout_time_str) - 
                             timedelta(hours=timezone_offset)).dt.strftime('%Y-%m-%d %H:%M:%S')
                df['Workout Name'] = 'Workout'
                df['Duration (sec)'] = 3600
                df['Exercise Name'] = df['Exercise'].map(mappings).fillna(df['Exercise'])
                
                df = df.sort_values(['Date', 'exercise_order', 'first_appearance'])
                df['Set Order'] = df.groupby(['Date', 'Exercise Name']).cumcount() + 1
                df['Weight (kg)'] = df['Weight'].apply(lambda x: str(x) if pd.notna(x) and x != '' else '')
                df['Reps'] = df['Reps'].apply(lambda x: int(x) if pd.notna(x) and x != '' else '')
                df['RPE'] = ''
                df['Distance (meters)'] = ''
                df['Seconds'] = ''
                df['Notes'] = df.get('Comment', '').fillna('') if 'Comment' in df.columns else ''
                df['Workout Notes'] = 'Imported from FitNotes'
                
                # Output
                columns = ['Workout #', 'Date', 'Workout Name', 'Duration (sec)', 'Exercise Name', 
                          'Set Order', 'Weight (kg)', 'Reps', 'RPE', 'Distance (meters)', 
                          'Seconds', 'Notes', 'Workout Notes']
                output_df = df[columns]
                
                # Convert to CSV
                output = StringIO()
                output_df.to_csv(output, index=False, sep=';', quoting=1)
                csv_data = output.getvalue()
                
                st.success("✅ Conversion complete!")
                
                # Download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download Hevy CSV",
                    data=csv_data,
                    file_name=f"fitnotes2hevy_{timestamp}.csv",
                    mime="text/csv"
                )
                
                # Show preview
                with st.expander("👀 Preview Converted Data"):
                    st.dataframe(output_df.head(20))
                    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)
else:
    st.info("👆 Upload your FitNotes CSV export to get started")
    
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **Export from FitNotes**: Settings → Spreadsheet Export
        2. **Upload** the CSV file above
        3. **Configure** timezone and workout time in sidebar
        4. **Convert** and download the Hevy-compatible file
        5. **Import to Hevy**: Settings → Export & Import Data → Import Data
        """)
