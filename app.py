"""Streamlit web app for FitNotes to Hevy conversion."""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

from src.fitnotes2hevy import convert_fitnotes_to_hevy, load_exercise_mappings

st.set_page_config(page_title="FitNotes to Hevy Converter", page_icon="💪")

# Custom CSS
st.markdown("""
<style>
    /* Center content and constrain width v2 */
    .main .block-container {
        max-width: 1000px !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Center title */
    h1 {
        text-align: center !important;
        background: linear-gradient(135deg, #42A5F5, #64B5F6, #90CAF9) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    /* Hide header anchor links */
    h1 a, h2 a, h3 a {
        pointer-events: none !important;
        cursor: default !important;
    }
    h1 a:hover, h2 a:hover, h3 a:hover {
        text-decoration: none !important;
    }
    h1 a svg, h2 a svg, h3 a svg {
        display: none !important;
    }
    
    /* Center subtitle and increase size */
    .main .block-container > div:nth-child(1) > div:nth-child(2) p {
        text-align: center !important;
        font-size: 1.5rem !important;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 2rem 2rem !important;
        border: 3px dashed rgba(76, 175, 80, 0.5) !important;
        border-radius: 12px !important;
        min-height: 150px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploader"][data-drag-active="true"] section {
        border-color: #4CAF50 !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
        transform: scale(1.01) !important;
        background-color: rgba(76, 175, 80, 0.1) !important;
    }
    /* Customize upload text */
    [data-testid="stFileUploader"] section small {
        font-size: 1.1rem !important;
    }
    
    /* Center buttons */
    .stButton {
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Blue primary button */
    button[kind="primary"] {
        background-color: #1E88E5 !important;
        border-color: #1E88E5 !important;
    }
    button[kind="primary"]:hover {
        background-color: #1565C0 !important;
        border-color: #1565C0 !important;
    }
    
    /* GitHub link hover effect */
    .github-link {
        border: 1px solid currentColor !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
    }
    .github-link:hover {
        background-color: rgba(0, 0, 0, 0.05) !important;
        transform: scale(1.05) !important;
    }
    

    
    /* Tab styling - blue for selected tab */
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #42A5F5 !important;
        color: #42A5F5 !important;
    }
    [data-baseweb="tab-highlight"] {
        background-color: #42A5F5 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #42A5F5 !important;
        color: #42A5F5 !important;
    }
    /* Tab hover styling - lighter blue */
    button[data-baseweb="tab"]:hover {
        color: #90CAF9 !important;
    }
    
    /* Reduce spacing in custom mappings table */
    div[data-testid="stMarkdownContainer"] hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Green download button */
    .stDownloadButton {
        display: flex !important;
        justify-content: center !important;
    }
    .stDownloadButton button {
        background-color: #4CAF50 !important;
        border-color: #4CAF50 !important;
        color: white !important;
    }
    .stDownloadButton button:hover {
        background-color: #45a049 !important;
        border-color: #45a049 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("FitNotes to Hevy")
st.markdown('<p style="text-align: center; font-size: 1.2rem;">Seamlessly migrate your workout history from <a href="https://www.fitnotesapp.com/">FitNotes</a> to <a href="https://www.hevyapp.com/">Hevy</a>.<br>Upload your FitNotes CSV to get started.</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 0.9rem; font-style: italic; color: #666; margin-top: -0.5rem;">Refer to FAQ below on how to retrieve the FitNotes CSV.</p>', unsafe_allow_html=True)

# Load default mappings (only default.json for display)
@st.cache_data
def get_default_mappings():
    import json
    from pathlib import Path
    with open(Path('data/mappings/default.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

default_mappings = get_default_mappings()

# Load all mappings for conversion
@st.cache_data
def get_all_mappings():
    return load_exercise_mappings()

all_mappings = get_all_mappings()

# Initialize session state
if 'custom_mappings' not in st.session_state:
    st.session_state.custom_mappings = {}
if 'timezone_offset' not in st.session_state:
    st.session_state.timezone_offset = 10
if 'workout_time' not in st.session_state:
    st.session_state.workout_time = "07:00"
if 'workout_duration' not in st.session_state:
    st.session_state.workout_duration = "60m"
if 'workout_name' not in st.session_state:
    st.session_state.workout_name = "Workout"
if 'workout_notes' not in st.session_state:
    st.session_state.workout_notes = "Imported from FitNotes"

# File upload
uploaded_file = st.file_uploader(
    "Upload CSV",
    type="csv",
    accept_multiple_files=False,
    label_visibility="collapsed"
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        # Validate immediately after loading
        from src.fitnotes2hevy.converter import validate_fitnotes_dataframe
        validate_fitnotes_dataframe(df)
    except ValueError as e:
        st.error(str(e))
        df = None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        df = None
else:
    df = None

if uploaded_file and df is not None:
    try:
        # Merge all mappings (default+extra) with custom mappings
        mappings = {**all_mappings, **st.session_state.custom_mappings}
        
        # Convert button (centered)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            convert_clicked = st.button("Convert to Hevy CSV Format", type="primary", width='stretch')
        
        if convert_clicked:
            with st.spinner("Converting..."):
                # Convert using core module with session state values
                workout_time_str = st.session_state.workout_time + ":00" if st.session_state.workout_time.count(':') == 1 else st.session_state.workout_time
                output_df = convert_fitnotes_to_hevy(
                    df, mappings, st.session_state.timezone_offset, workout_time_str,
                    st.session_state.workout_name, st.session_state.workout_duration, st.session_state.workout_notes
                )
                
                # Convert to CSV
                output = StringIO()
                output_df.to_csv(output, index=False, sep=';', quoting=1)
                csv_data = output.getvalue()
                
                # Download button (centered)
                timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="Download Hevy CSV Format",
                        data=csv_data,
                        file_name=f"fitnotes2hevy_{timestamp}.csv",
                        mime="text/csv",
                        width="stretch"
                    )
                
                # Ko-fi donation prompt
                st.markdown("""
                <div style="text-align: center; margin-top: 1rem; padding: 1rem; background-color: rgba(66, 165, 245, 0.1); border-radius: 8px;">
                    <p style="margin: 0 0 0.5rem 0;">✨ Found this useful?</p>
                    <a href="https://ko-fi.com/alanjonesit" target="_blank" style="text-decoration: none; color: inherit; display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background-color: #FF5E5B; color: white; border-radius: 8px; transition: all 0.2s ease;">
                        <svg height="20" width="20" viewBox="0 0 24 24" fill="white"><path d="M23.881 8.948c-.773-4.085-4.859-4.593-4.859-4.593H.723c-.604 0-.679.798-.679.798s-.082 7.324-.022 11.822c.164 2.424 2.586 2.672 2.586 2.672s8.267-.023 11.966-.049c2.438-.426 2.683-2.566 2.658-3.734 4.352.24 7.422-2.831 6.649-6.916zm-11.062 3.511c-1.246 1.453-4.011 3.976-4.011 3.976s-.121.119-.31.023c-.076-.057-.108-.09-.108-.09-.443-.441-3.368-3.049-4.034-3.954-.709-.965-1.041-2.7-.091-3.71.951-1.01 3.005-1.086 4.363.407 0 0 1.565-1.782 3.468-.963 1.904.82 1.832 3.011.723 4.311zm6.173.478c-.928.116-1.682.028-1.682.028V7.284h1.77s1.971.551 1.971 2.638c0 1.913-.985 2.667-2.059 3.015z"/></svg>
                        Buy me a coffee
                    </a>
                    <p style="margin: 0.75rem 0 0 0; font-size: 0.9rem; color: #666; font-style: italic;">This started as a weekend project to solve my own FitNotes to Hevy migration headache. If it helped you too, a coffee would be much appreciated!</p>
                </div>
                """, unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

# Tabs for Settings, Exercise Mappings, and FAQ
tab1, tab2, tab3 = st.tabs(["Settings", "Exercise Mappings", "FAQ"])

with tab1:
    st.caption("Configure conversion settings. FitNotes does not store this information, so defaults are applied to all workouts.")
    
    # Timezone options
    timezone_options = {
        "UTC-12 (Baker Island)": -12,
        "UTC-11 (American Samoa)": -11,
        "UTC-10 (Hawaii)": -10,
        "UTC-9 (Alaska)": -9,
        "UTC-8 (Los Angeles, Vancouver)": -8,
        "UTC-7 (Denver, Phoenix)": -7,
        "UTC-6 (Chicago, Mexico City)": -6,
        "UTC-5 (New York, Toronto)": -5,
        "UTC-4 (Santiago, Halifax)": -4,
        "UTC-3 (Buenos Aires, São Paulo)": -3,
        "UTC-2 (South Georgia)": -2,
        "UTC-1 (Azores)": -1,
        "UTC+0 (London, Lisbon)": 0,
        "UTC+1 (Paris, Berlin, Rome)": 1,
        "UTC+2 (Athens, Cairo, Johannesburg)": 2,
        "UTC+3 (Moscow, Istanbul, Nairobi)": 3,
        "UTC+4 (Dubai, Baku)": 4,
        "UTC+5 (Karachi, Tashkent)": 5,
        "UTC+5:30 (Mumbai, Delhi)": 5.5,
        "UTC+6 (Dhaka, Almaty)": 6,
        "UTC+7 (Bangkok, Jakarta)": 7,
        "UTC+8 (Singapore, Beijing, Perth)": 8,
        "UTC+9 (Tokyo, Seoul)": 9,
        "UTC+9:30 (Adelaide)": 9.5,
        "UTC+10 (Sydney, Melbourne, Brisbane)": 10,
        "UTC+11 (Solomon Islands)": 11,
        "UTC+12 (Auckland, Fiji)": 12,
        "UTC+13 (Tonga)": 13,
        "UTC+14 (Kiribati)": 14
    }
    
    default_index = list(timezone_options.values()).index(st.session_state.timezone_offset)
    timezone_selection = st.selectbox(
        "Timezone",
        options=list(timezone_options.keys()),
        index=default_index,
        help="Select your timezone for accurate workout timestamps. If unsure, check your device's timezone settings."
    )
    st.session_state.timezone_offset = timezone_options[timezone_selection]
    
    st.session_state.workout_time = st.text_input(
        "Workout Start Time (24hr)", 
        value=st.session_state.workout_time,
        help="The time workouts will appear in Hevy (in your local timezone). Format: HH:MM"
    )
    
    st.session_state.workout_duration = st.text_input(
        "Workout Duration", 
        value=st.session_state.workout_duration,
        help="Format: '60m' for minutes or '3600s' for seconds."
    )
    
    st.session_state.workout_name = st.text_input(
        "Workout Name", 
        value=st.session_state.workout_name,
        help="Default name for all imported workouts."
    )
    
    st.session_state.workout_notes = st.text_input(
        "Workout Notes (optional)", 
        value=st.session_state.workout_notes,
        help="Notes added to all imported workouts."
    )

with tab2:
    st.info("FitNotes and Hevy use different exercise names. These mappings ensure your exercises are recognized correctly in Hevy instead of appearing as custom exercises.")
    subtab1, subtab2, subtab3 = st.tabs(["View Default Mappings", "Add Custom Mappings", "Preview Mappings"])
    
    with subtab1:
        st.caption("These mappings convert FitNotes exercise names to their Hevy equivalents. Use the search box in the table to find specific exercises.")
        mappings_df = pd.DataFrame(list(default_mappings.items()), columns=['FitNotes Exercise', 'Hevy Exercise'])
        st.dataframe(mappings_df, width="stretch", height=400, hide_index=True)
    
    with subtab2:
        st.caption("Add custom exercise mappings for exercises not in the default list. Custom mappings will override default mappings if the same FitNotes exercise name is used.")
        col1, col2 = st.columns(2)
        with col1:
            fitnotes_ex = st.text_input("FitNotes Exercise Name")
        with col2:
            hevy_ex = st.text_input("Hevy Exercise Name")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            add_clicked = st.button("Add Mapping", type="primary", width="stretch")
        
        if add_clicked:
            if fitnotes_ex and hevy_ex:
                st.session_state.custom_mappings[fitnotes_ex] = hevy_ex
                st.success(f"Added: {fitnotes_ex} → {hevy_ex}")
            else:
                st.error("Please enter both exercise names")
        
        if st.session_state.custom_mappings:
            st.write(f"**{len(st.session_state.custom_mappings)} custom mappings:**")
            st.caption("To delete a custom mapping, select the checkbox on the left-most column for the row you want to delete, then use Backspace or click the bin icon.")
            
            # Display as editable dataframe
            custom_df = pd.DataFrame(list(st.session_state.custom_mappings.items()), 
                                    columns=['FitNotes Exercise', 'Hevy Exercise'])
            edited_df = st.data_editor(
                custom_df, 
                width="stretch", 
                hide_index=True,
                num_rows="dynamic",
                key="custom_mappings_editor"
            )
            
            # Update mappings from edited dataframe
            if not edited_df.equals(custom_df):
                st.session_state.custom_mappings = dict(zip(edited_df['FitNotes Exercise'], edited_df['Hevy Exercise']))
                st.rerun()
            
            # Import/Export
            import json
            json_data = json.dumps(st.session_state.custom_mappings, indent=2)
            col1, col2 = st.columns(2)
            with col1:
                uploaded_mappings = st.file_uploader(
                    "Import Custom Mappings",
                    type="json",
                    key="import_mappings"
                )
                if uploaded_mappings:
                    try:
                        imported = json.load(uploaded_mappings)
                        st.session_state.custom_mappings.update(imported)
                        st.success(f"Imported {len(imported)} mappings")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error importing: {str(e)}")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="Export Custom Mappings",
                    data=json_data,
                    file_name="custom_mappings.json",
                    mime="application/json",
                    width="stretch"
                )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <style>
                .clear-all-btn button[kind="secondary"] {
                    background-color: #C62828 !important;
                    border-color: #C62828 !important;
                    color: white !important;
                }
                .clear-all-btn button[kind="secondary"]:hover {
                    background-color: #B71C1C !important;
                    border-color: #B71C1C !important;
                }
                .clear-all-btn button[kind="secondary"] p {
                    color: white !important;
                }
                </style>
                <div class="clear-all-btn">
                """, unsafe_allow_html=True)
                if st.button("🗑️ Clear All Custom Mappings", type="secondary", width="stretch"):
                    st.session_state.custom_mappings = {}
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    
    with subtab3:
        if uploaded_file and df is not None:
            # Merge all mappings for preview
            mappings = {**all_mappings, **st.session_state.custom_mappings}
            unique_exercises = df['Exercise'].unique()
            mapping_preview = pd.DataFrame({
                'FitNotes Exercise': unique_exercises,
                'Hevy Exercise': [mappings.get(ex, ex) for ex in unique_exercises],
                'Status': ['✅ Mapped' if ex in mappings else '⚠️ Unmapped' for ex in unique_exercises]
            })
            st.dataframe(mapping_preview, width='stretch')
            
            # Show unmapped exercises
            unmapped = df[~df['Exercise'].isin(mappings.keys())]['Exercise'].unique()
            if len(unmapped) > 0:
                st.warning(f"Warning: {len(unmapped)} exercise(s) will keep their original names and be created as custom exercises in Hevy.")
        else:
            st.warning("Please upload a FitNotes CSV file to preview exercise mappings.")

with tab3:
    with st.expander("Is my workout data private and secure?"):
        st.write("Yes! Your data is only held in memory during conversion and deleted immediately after. No workout data is saved to disk or stored anywhere.")
        st.write("For complete privacy, you can [run this tool locally on your machine](https://github.com/alanjonesit/FitNotes2Hevy#web-interface).")
    
    with st.expander("How do I export from FitNotes?"):
        st.write("Open FitNotes → Settings → Spreadsheet Export → select Workout Data → Save Export.")
    
    with st.expander("How do I import the converted file to Hevy?"):
        st.write("Open Hevy app → Settings → Export & Import Data → Import Data → Select the downloaded CSV file.")
        st.write("View Hevy's [official import tutorial](https://help.hevyapp.com/hc/en-us/articles/35687878672663-Tutorial-Log-Previous-Workouts-and-Import-CSV).")
    
    with st.expander("Why are my workout times wrong in Hevy?"):
        st.write("Adjust the timezone offset in the Settings section to match your location (e.g., UTC+10 for Sydney).")
    
    with st.expander("Some exercises appear as custom in Hevy. Why?"):
        st.write("This happens when exercise names don't match exactly or when exercises use different measurement types (e.g., time vs reps). The converter maps 300+ exercises automatically.")
    
    with st.expander("Will my workout history be preserved?"):
        st.write("Yes! All your sets, reps, weights, and dates are converted and preserved.")
    
    with st.expander("What format does this tool use?"):
        st.write("This tool converts FitNotes data to Strong app CSV format, which is the only format Hevy supports for imports.")
    
    with st.expander("Are there any known issues with specific exercises?"):
        st.write("Some exercises will appear as custom in Hevy even with exact names and measurements due to internal Hevy limitations:")
        st.write("• Overhead Triceps Extension (Cable)")
        st.write("• Rear Kick (Machine)")
    
    with st.expander("Does this import routines?"):
        st.write("No, this tool only imports workout history (exercises, sets, reps, weights). Routines are not imported.")
    
    with st.expander("Is there a limit on custom exercises?"):
        st.write("Without [Hevy Pro](https://hevy.com/plans), there is a limit of 7 custom exercises that can be imported. With Hevy Pro, there is no limit.")
    
    with st.expander("How do I report issues or request features?"):
        st.write("Visit the [GitHub repository](https://github.com/alanjonesit/FitNotes2Hevy/issues) to report issues or request new features.")

# Footer with GitHub and Ko-fi links
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid rgba(128, 128, 128, 0.2);">
    <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <a href="https://github.com/alanjonesit/FitNotes2Hevy" target="_blank" style="text-decoration: none; color: inherit; display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 8px; transition: all 0.2s ease;">
            <svg height="20" width="20" viewBox="0 0 16 16"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
            GitHub
        </a>
        <a href="https://ko-fi.com/alanjonesit" target="_blank" style="text-decoration: none; color: inherit; display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 8px; transition: all 0.2s ease;">
            <svg height="20" width="20" viewBox="0 0 24 24" fill="currentColor"><path d="M23.881 8.948c-.773-4.085-4.859-4.593-4.859-4.593H.723c-.604 0-.679.798-.679.798s-.082 7.324-.022 11.822c.164 2.424 2.586 2.672 2.586 2.672s8.267-.023 11.966-.049c2.438-.426 2.683-2.566 2.658-3.734 4.352.24 7.422-2.831 6.649-6.916zm-11.062 3.511c-1.246 1.453-4.011 3.976-4.011 3.976s-.121.119-.31.023c-.076-.057-.108-.09-.108-.09-.443-.441-3.368-3.049-4.034-3.954-.709-.965-1.041-2.7-.091-3.71.951-1.01 3.005-1.086 4.363.407 0 0 1.565-1.782 3.468-.963 1.904.82 1.832 3.011.723 4.311zm6.173.478c-.928.116-1.682.028-1.682.028V7.284h1.77s1.971.551 1.971 2.638c0 1.913-.985 2.667-2.059 3.015z"/></svg>
            Support on Ko-fi
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
