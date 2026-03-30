import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime
import plotly.express as px

st.set_page_config(
    page_title="Bird Nuisance Dashboard",
    layout="wide",      
    initial_sidebar_state="collapsed"
)

# Load prepared dataset with cache for performance
@st.cache_data
def load_data():
    df = pd.read_csv('classified_bird_nuisance_cases.csv')
    df['date_received'] = pd.to_datetime(df['Received Date and Time'], errors='coerce')
    return df
df = load_data()

st.sidebar.title("Filters")

# Define min and max dates for the slider
min_date = datetime.date(2023, 1, 1)
max_date = datetime.date(2024, 12, 31)

# Double-ended date slider in sidebar
d_start, d_end = st.sidebar.slider(
    "Analysis Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),  # default selected range
    format="YYYY-MM-DD"
)

st.sidebar.write(f"Selected date range: {d_start} to {d_end}")

# Filter the DataFrame by selected date range
filtered_df = df[(df['date_received'].dt.date >= d_start) & 
                 (df['date_received'].dt.date <= d_end)]

left, center, right = st.columns([1, 8, 1])

with center:
    st.title("Bird Nuisance Feedback Analysis")
    st.markdown("""
        This dashboard provides insights into bird nuisance feedback across Singapore, based on data from the Municipal Services Office (MSO) for the years 2023 and 2024. 
        Click on the tabs to explore different aspects of the data, including the distribution of bird types and nuisance issues, trends over time, and detailed case information.
    
        Use the date slider in the sidebar to explore specific date ranges and analyze trends in bird types and nuisance issues.
    """,text_alignment ="justify")

    # tabs for different sections of the dashboard    
    main, bird_nature, trend_analysis, case_viewer = st.tabs(["Overview", "Bird Types & Nature of Nuisance", "Feedback Trend Analysis", "Case Viewer"])

    with bird_nature:
            
            st.subheader("Bird Types & Nature of Nuisance")

            # Data Visualisation
            # Get counts for each category
            bird_counts = filtered_df['bird_type'].value_counts(ascending=True)
            nature_counts = filtered_df['nature_type'].value_counts(ascending=True)

            # Create the figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Plot Bird Type (Horizontal)
            bird_counts.plot(kind='barh', ax=ax1, color='skyblue', edgecolor='black')
            ax1.set_title('Distribution of Pestbird Types', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Number of Reports')
            ax1.set_ylabel('') 

            # Plot Nature of Issue (Horizontal)
            nature_counts.plot(kind='barh', ax=ax2, color='salmon', edgecolor='black')
            ax2.set_title('Distribution of Nature of Issues', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Number of Reports')
            ax2.set_ylabel('')

            plt.tight_layout()

            # --- Streamlit render ---
            st.pyplot(fig)
        
            st.markdown("""- Most common feedback is regarding feeding of birds and noise.""",text_alignment ="justify") 
            st.markdown("""- Crows and Pigeons are commonly identified by feedback providers (FP).""",text_alignment ="justify")
            st.markdown("""- Unspecified Bird : FP not able to identify the bird/ rely on sound or could be unfamiliar with species.""",text_alignment ="justify")

            # Create the intersection
            pivot = pd.crosstab(filtered_df['bird_type'], filtered_df['nature_type'])

            # Plot
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.heatmap(pivot, annot=True, fmt="d", cmap="rocket_r", ax=ax)

            ax.set_title('Bird-Issue Intersection')

            # Render in Streamlit
            st.pyplot(fig)

            st.markdown("""- Most feedback identify Pigeons and crows when reporting feeding related issues.""",text_alignment ="justify")
            st.markdown("""- Large amount of feedback for feeding, noise and rescue do not identify the species.""",text_alignment ="justify")


    with trend_analysis:
            st.subheader("Feedback Trend Analysis")

            # --- PLOT 3: BIRD TYPE TREND ---
            top_birds = filtered_df['bird_type'].value_counts().head(5).index
            bird_trend = (filtered_df[filtered_df['bird_type'].isin(top_birds)]
                        .groupby([pd.Grouper(key='date_received', freq='MS'), 'bird_type'])
                        .size().unstack(fill_value=0))

            fig1, ax1 = plt.subplots(figsize=(12, 5))
            for bird in bird_trend.columns:
                ax1.plot(bird_trend.index, bird_trend[bird], marker='o', label=bird)

            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            plt.title('Monthly Trend: Bird Types')
            plt.ylabel('Number of Reports')
            plt.grid(True)
            plt.legend()

            st.pyplot(fig1)


            # --- PLOT 4: NUISANCE TYPE TREND ---
            top_nuisances = filtered_df['nature_type'].value_counts().head(5).index
            nuisance_trend = (filtered_df[filtered_df['nature_type'].isin(top_nuisances)]
                            .groupby([pd.Grouper(key='date_received', freq='MS'), 'nature_type'])
                            .size().unstack(fill_value=0))

            fig2, ax2 = plt.subplots(figsize=(12, 5))
            for nuisance in nuisance_trend.columns:
                ax2.plot(nuisance_trend.index, nuisance_trend[nuisance], marker='s', label=nuisance)

            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            plt.title('Monthly Trend: Nuisance Types')
            plt.ylabel('Number of Reports')
            plt.grid(True)
            plt.legend()

            st.pyplot(fig2)

            st.markdown("""- Increasing trend of feedback with unspecified bird type.""",text_alignment ="justify")
            st.markdown("""- Feeding related feedback remains consistently high throughout 2023-2024.""",text_alignment ="justify")
            st.markdown("""- Increase in Noise related feedback in 2024.""",text_alignment ="justify")

            st.subheader("Recommendations for MSO based on feedback trends:")
            st.markdown("""            
                        Reports of people feeding birds is consistently high
                        - Stricter enforcement of the Wildlife Act. 
                        - Use of technology to identify repeat offenders. 
                        - Noise is becoming more of a concern in 2024 
                        - Use feedback location to identify nesting hotspots.
                        - Conduct tree pruning, culling of crows, installing bird spikes or netting on ledges to prevent roosting.""", text_alignment ="justify")
            st.markdown("""
                        Improve the feedback system: Increasing number of FPs are unable to identify bird species or provide very generic feedback regarding the issue reported.
                        - Use AI to prompt users to provide details when reporting issues, so that issues are properly categorised and prioritised.
                        - Content provided may not be textual. e.g. Photo/Video, which can be intepreted using AI """, text_alignment ="justify")
            
                    
    with case_viewer:
        st.header("Search and view historical Bird Nuisance Cases")

        st.subheader("Latest Bird Nuisance Cases")
        view_cols = ["Case Identifier", "date_received", "bird_type", "nature_type", "Subject"]
        st.dataframe(filtered_df[view_cols].sort_values(by='date_received', ascending=False).head(5),hide_index = True)  
    
        st.subheader("Case Search")
        st.write("Search for specific cases by entering the Case Identifier. You can find the Case Identifier in the table above or on the map in the Home tab. The search will return cases that contain the entered text, allowing for partial matches. Click on a case to view detailed information, including the subject, description, and location on a map.")
        # Search by Case Identifier from dataframe
        def search_case(case_id: str, max_results: int = 10):
            if not case_id:
                return []
            
            # Find matches
            matches = filtered_df[filtered_df["Case Identifier"].str.contains(case_id, case=False)]
            
            # Convert to list of tuples
            results = [(row["Case Identifier"], row) for row in matches.to_dict(orient="records")]
            
            # Limit number of results
            return results[:max_results]


        # Custom labels
        column_labels = {
            "date_received": "Date Reported",
            "nature_type": "Nuisance Type",
            "bird_type": "Bird Type",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "Subject": "Subject",
            "Description": "Description"
        }

        # Columns you want to display in each Streamlit column
        col1_fields = ["date_received", "nature_type", "bird_type"]
        col2_fields = ["latitude", "longitude"]
        main_fields = ["Subject", "Description"]

        # --- Searchbox ---
        selected_case = st_searchbox(
            search_case,
            placeholder="Search Case ID...",
            key="Case Identifier"
        )

        # --- Display case ---
        if selected_case:

            st.subheader(f"Case ID: {selected_case['Case Identifier']}")
            col1, col2 = st.columns(2)

            # --- Left column ---
            with col1:
                for col in col1_fields:
                    label = column_labels.get(col, col)
                    st.write(f"**{label}:** {selected_case[col]}")

            # --- Right column ---
            with col2:
                for col in col2_fields:
                    label = column_labels.get(col, col)
                    st.write(f"**{label}:** {selected_case[col]}")
            
            # --- Main content ---
            for col in main_fields:
                label = column_labels.get(col, col)
                st.write(f"**{label}:** {selected_case[col]}")

            # --- Map at bottom ---
            if pd.notnull(selected_case.get("latitude")) and pd.notnull(selected_case.get("longitude")):
                st.subheader("Map of Case Location:")
                st.map(pd.DataFrame([selected_case], columns=["latitude", "longitude"]))
        
            
    with main:
        st.header("Overview of Bird Nuisance Feedback")

        monthly_counts = (
            filtered_df
            .groupby(pd.Grouper(key='date_received', freq='MS'))
            .size()
        )

        # --- Metrics Layout ---
        col1, col2, col3 = st.columns(3)

        # Inject CSS to force center both labels and values
        st.markdown("""
        <style>
        /* Center metric value */
        [data-testid="stMetricValue"] {
            text-align: center;
            display: block;
            margin: auto;
        }

        /* Center metric label */
        [data-testid="stMetricLabel"] {
            text-align: center;
            display: block;
            margin: auto;
        }
        </style>
        """, unsafe_allow_html=True)

        # Metric 1
        with col1:
            st.metric(
                label="Total Cases in Selected Date Range",
                value=len(filtered_df),
                border=True
            )

        # Metric 2
        top_bird = filtered_df['bird_type'].mode()[0]
        with col2:
            st.metric(
                label="Most Common Bird",
                value=top_bird,
                border=True, 
                delta=None
            )

        # Metric 3
        top_nature = filtered_df['nature_type'].mode()[0]
        with col3:
            st.metric(
                label="Top Nuisance Type",
                value=top_nature,
                border=True, 
                delta=None
            )
        
        st.subheader("Geographical Distribution of Bird Nuisance Cases")
        # Geomap with Plotly Express
        fig = px.scatter_map(
            filtered_df, 
            lat="latitude", 
            lon="longitude", 
            color="nature_type",
            zoom=10.5, 
            center={"lat": 1.3520, "lon": 103.8198}, 
            map_style="carto-positron", 
            title="<b>MSO Bird Nuisance Analysis: Singapore Hotspots</b>",
            labels={
                "Subject": "Subject"
            },
            hover_data={
                "latitude": False, 
                "longitude": False,
                "nature_type": False,
                "Case Identifier": True, 
                "Subject": True,
            }
        )

        # Layout adjustments
        fig.update_layout(
            height=700,
            margin={"r":20,"t":60,"l":20,"b":50},  # tighter for Streamlit
            paper_bgcolor="white",

            title={
                'text': "<b>Bird Nuisance Feedback Across Singapore (2023–2024)</b>",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },

            legend=dict(
                title="<b>Classification</b>",
                yanchor="top", y=0.95,
                xanchor="left", x=0.02,
                bgcolor="rgba(255, 255, 255, 1)", 
                bordercolor="Black",
                borderwidth=0.8
            ),

            annotations=[
                dict(
                    x=0.5, y=-0.05,   # slightly lower for Streamlit
                    showarrow=False,
                    text="Source: Municipal Services Office (MSO) Data | 2023-2024",
                    xref="paper", yref="paper",
                    font=dict(size=12, color="gray")
                )
            ]
        )

        fig.update_traces(marker=dict(opacity=0.8))

        # Streamlit render
        st.plotly_chart(fig, width='stretch')