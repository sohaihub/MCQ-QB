import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Set page configuration with custom theme and favicon
st.set_page_config(
    page_title="📚 Premium MCQ Question Bank",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f9ff, #e0f2fe, #f0f9ff);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #bfdbfe;
    }
    .stat-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    .stSelectbox label, .stRadio label {
        font-weight: 600;
        color: #1E3A8A;
    }
    .answer-correct {
        margin-top: 20px;
        padding: 15px;
        background-color: #d1e7dd;
        border-left: 5px solid #0d6832;
        border-radius: 8px;
        color: black;
    }
    .question-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    .question-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .question-number {
        background-color: #3b82f6;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .question-difficulty {
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .difficulty-easy {
        background-color: #10b981;
    }
    .difficulty-medium {
        background-color: #f59e0b;
    }
    .difficulty-hard {
        background-color: #ef4444;
    }
    .question-meta {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 10px;
    }
    .filter-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.8rem;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📚 Premium MCQ Question Bank</h1>', unsafe_allow_html=True)

# Google Sheets Authentication using Service Account
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds = {
        "type": "service_account",
        "project_id": "gen-lang-client-0825677129",
        "private_key_id": "65f8068623bb08e2a09f82daf250edad3daf20fe",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtYR/SqwX0Amy7
0VUaHe0x01B20FPgQQvFTXLxgNdTk6g2wIcj997NQ2I3gboV5htkax18NBQZ6KZy
g7il4e9oQYa7VBaEXyqgDKrrFlpzt+KHGzQLF0jdRbWJuL5U4hBFpoHIr5vC7Oc6
y6uKRHRqhGuYWV5BBx4EGtWsFRQ5JXuJDiF64wioh170xAAsEgnKIcpjg3kG1c+n
3BruIsP0p5hbM5azCTpdVHbBL7F/RCYqULgov6LrrYXsAbgXaISYdbs0msUpp2ze
FlGqOA5ywHgRDOj/vzf2C1UG0aNODi+gfndxkkTV5+//eq/n5+DZk11hxJ8VuOZp
NcGReau3AgMBAAECggEAFsfTKZgFETmcVdU8bFEQUGKmiOX4j1ecl1EE0EyQfk/B
Y2hKmWRBJxE6f3aRH717TedxGVeyaHEUJam/AjS8gyNQ854p0zy52guwDXGDcv7v
Sbc+UFK/5Sr6nlzizT5iyvQEy3yfZ64+94+5O1KhRTme9YaQhtTLkdiAyLqATL2z
nIq2gmKjyCz2KviaaGF5OvyEHOrl38UQMxkBjbE1muxJGPa3CXsbH4JxdSeoljc+
JFc1LRqFzasdamWxIWL02pGWFWyIZw9iwyKmGD5paB44hS3p5XRhEC3deMiPuLHi
uSO9XHEgsq48Jv7GolQJaEx1xEs+r1k6O1BUA+ccyQKBgQDd5EqdYwKQLWbgSFU8
HyYiS2mvYBSFqpE33dpgCkbYigBD/SKHXuHnBd535LYScplYv8EIaUlYN8qICYF5
gdjibM3LX8l4OlQQKQUp3FUQlYDwyI4WXjxDdAI2YIqq1RFEJ5/GQU/XuN0Q/14J
mLYIFjrjDDGYAhvmXkMqKXkacwKBgQDIB9AANe3I0Lm9X/m1uKv/Yj70h9kPpJn6
Cj70CfquQl+fISgZo5Yb7/xYAIDxQUsXwI7eUxt4oQLMuhDVKVBNfEx/3rqXqDB+
rCprLJ6JAwuaFwrgNNAHMO+XsDxP/Qcp/gs93NqbYMw8dn8f3q28sENl1Ar8iOX/
lKrYNaMErQKBgQCXwYjed1bLcKHJhu70fYFBNz6CuT2P5YYIJW0y/hRSCKAB3+B7
oQLzU+pBKWT03PfP4OWOcSO+d/nGbGnmxk2lHjDphQtvdMUFgGiNpqlu/DEBfMjg
t3aT04Wn1wM/rxVt/YOivgxzR3W6KE0SVyU4BqwjmLVadybJuXJKJa8zzQKBgQDG
pqOWIfik700W2kLGisEdnjdBZ8xUcbaNEDHW8DYpazdFdIs7cy93TU1BJDbp4Vsv
GoeIGeb1VInQQZTH7QCYAzKB5vNN+7U1h8uUpjpHfWO/QtUFNs3F5n57GYW8NmAv
/uCxLi1YE7ig71lukBnggvhcH0pN47LusHk+wX3E/QKBgHQP6jf1iALdJm7fEnPu
Y6BdUP8Sl0Ps/1QN5/9ZyqczCsVLd5G6XXEgDhUESTHsYMIMNfEEfjuaNtKd8d1Q
VA9ot2yW/IqKGDpdBRWEHmFFJI2c4X812RTFbibS6FjvgLY+CR2ee7uh0WKEGcyf
tiYUBwODxZRuycZYl3eOICdP
-----END PRIVATE KEY-----""",
        "client_email": "data-774@gen-lang-client-0825677129.iam.gserviceaccount.com",
        "client_id": "101552404875723380663",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/data-774%40gen-lang-client-0825677129.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    with st.spinner("📝 Loading question bank data..."):
        client = gspread.service_account_from_dict(creds)
        spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1K2HJSL0U0vay4UaW4s3QPAIkQ_noj742ZRQJxbTTbQ0/edit?gid=0")
        worksheet = spreadsheet.get_worksheet(0)
        data = pd.DataFrame(worksheet.get_all_records())
    
    # Show success message with data size
    st.sidebar.success(f"✅ Connected to database ({len(data)} questions loaded)")
    
except Exception as e:
    st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
    st.stop()

# Data preprocessing
def preprocess_data(df):
    # Normalize column values
    df['Topic'] = df['Topic'].str.strip().str.title()
    df['Domain'] = df['Domain'].str.strip().str.title()
    df['Category'] = df['Category'].str.strip().str.title()
    df['Difficulty'] = df['Difficulty'].str.strip().str.title()
    
    # Convert timestamp strings to datetime if available
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    return df

data = preprocess_data(data)

# Function to map correct answers (A, B, C, D) to indexes (0, 1, 2, 3)
def get_correct_option_index(correct_answer):
    option_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    return option_map.get(correct_answer.strip().upper(), -1)

# Sidebar configuration
st.sidebar.markdown('<div class="filter-card">', unsafe_allow_html=True)
page = st.sidebar.selectbox("📑 Select a Page", ["Quiz", "Topic Stats", "Advanced Analytics"], index=0)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Display last update time
current_time = datetime.now().strftime("%d %b %Y, %H:%M:%S")
st.sidebar.markdown(f"<div style='font-size:0.8rem; color:#6b7280; margin-top:2rem;'>Last updated: {current_time}</div>", unsafe_allow_html=True)

# Topic Stats Page
if page == "Topic Stats":
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏷️ By Domain", "📂 By Category", "📈 Trends"])
    
    # Overview Tab
    with tab1:
        # Calculate key metrics
        total_questions = len(data)
        total_topics = data['Topic'].nunique()
        total_domains = data['Domain'].nunique() if 'Domain' in data.columns else 0
        total_categories = data['Category'].nunique() if 'Category' in data.columns else 0
        
        # Display metrics in a row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Questions", total_questions)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Topics", total_topics)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Domains", total_domains)
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Categories", total_categories)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Topic-wise Difficulty Distribution
        st.markdown('<h3 class="section-header">Topic-wise Question Distribution</h3>', unsafe_allow_html=True)
        
        # Normalize topic names and difficulty levels
        topic_stats = (
            data.groupby(['Topic', 'Difficulty'])
            .agg(total_questions=('Question', 'count'))
            .unstack(fill_value=0)
            .reset_index()
        )
        
        # Ensure consistency in difficulty levels
        difficulty_columns = ['Easy', 'Medium', 'Hard']
        for level in difficulty_columns:
            if ('total_questions', level) not in topic_stats.columns:
                topic_stats[('total_questions', level)] = 0
        
        # If multi-level columns, flatten them
        if isinstance(topic_stats.columns, pd.MultiIndex):
            topic_stats.columns = [col[1] if col[1] else col[0] for col in topic_stats.columns]
        
        # Add total column
        if 'Total' not in topic_stats.columns:
            topic_stats['Total'] = topic_stats[difficulty_columns].sum(axis=1)
        
        # Sort by total questions
        topic_stats = topic_stats.sort_values('Total', ascending=False)
        
        # Display the stats with styling
        st.dataframe(
            topic_stats,
            height=400,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Topic": st.column_config.TextColumn("Topic"),
                "Easy": st.column_config.NumberColumn("Easy", format="%d"),
                "Medium": st.column_config.NumberColumn("Medium", format="%d"),
                "Hard": st.column_config.NumberColumn("Hard", format="%d"),
                "Total": st.column_config.NumberColumn("Total", format="%d"),
            }
        )
        
        # Visualization: Difficulty distribution
        st.markdown('<h3 class="section-header">Difficulty Distribution</h3>', unsafe_allow_html=True)
        
        difficulty_counts = data['Difficulty'].value_counts().reset_index()
        difficulty_counts.columns = ['Difficulty', 'Count']
        
        fig = px.pie(
            difficulty_counts,
            values='Count',
            names='Difficulty',
            color='Difficulty',
            color_discrete_map={
                'Easy': '#10b981',
                'Medium': '#f59e0b',
                'Hard': '#ef4444'
            },
            hole=0.4
        )
        fig.update_layout(
            legend_title="Difficulty Level",
            margin=dict(t=30, b=0, l=0, r=0),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Domain Tab
    with tab2:
        if 'Domain' in data.columns:
            st.markdown('<h3 class="section-header">Domain-wise Question Distribution</h3>', unsafe_allow_html=True)
            
            # Domain-wise stats
            domain_stats = (
                data.groupby(['Domain', 'Difficulty'])
                .agg(total_questions=('Question', 'count'))
                .unstack(fill_value=0)
                .reset_index()
            )
            
            # Ensure consistency in difficulty levels
            for level in difficulty_columns:
                if ('total_questions', level) not in domain_stats.columns:
                    domain_stats[('total_questions', level)] = 0
            
            # If multi-level columns, flatten them
            if isinstance(domain_stats.columns, pd.MultiIndex):
                domain_stats.columns = [col[1] if col[1] else col[0] for col in domain_stats.columns]
            
            # Add total column
            if 'Total' not in domain_stats.columns:
                domain_stats['Total'] = domain_stats[difficulty_columns].sum(axis=1)
            
            # Sort by total questions
            domain_stats = domain_stats.sort_values('Total', ascending=False)
            
            # Display the stats with styling
            st.dataframe(
                domain_stats,
                height=400,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Domain": st.column_config.TextColumn("Domain"),
                    "Easy": st.column_config.NumberColumn("Easy", format="%d"),
                    "Medium": st.column_config.NumberColumn("Medium", format="%d"),
                    "Hard": st.column_config.NumberColumn("Hard", format="%d"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                }
            )
            
            # Visualization: Domain distribution
            st.markdown('<h3 class="section-header">Domain Question Distribution</h3>', unsafe_allow_html=True)
            
            # Create a bar chart for domain distribution
            domain_totals = domain_stats[['Domain', 'Total']].sort_values('Total', ascending=True)
            
            fig = px.bar(
                domain_totals,
                x='Total',
                y='Domain',
                orientation='h',
                color='Total',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_title="Number of Questions",
                yaxis_title="Domain",
                margin=dict(t=0, b=0, l=0, r=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Domain-Topic breakdown
            st.markdown('<h3 class="section-header">Domain-Topic Breakdown</h3>', unsafe_allow_html=True)
            
            # Select domain for breakdown
            selected_domain = st.selectbox("Select Domain for Topic Breakdown", data['Domain'].unique())
            
            # Filter data for selected domain
            domain_topic_data = data[data['Domain'] == selected_domain]
            
            # Create topic breakdown for the selected domain
            topic_breakdown = domain_topic_data.groupby('Topic').size().reset_index(name='Count')
            topic_breakdown = topic_breakdown.sort_values('Count', ascending=True)
            
            # Create a horizontal bar chart
            fig = px.bar(
                topic_breakdown,
                x='Count',
                y='Topic',
                orientation='h',
                color='Count',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_title="Number of Questions",
                yaxis_title="Topic",
                margin=dict(t=0, b=0, l=0, r=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Domain data is not available in the dataset.")
    
    # Category Tab
    with tab3:
        if 'Category' in data.columns:
            st.markdown('<h3 class="section-header">Category-wise Question Distribution</h3>', unsafe_allow_html=True)
            
            # Category-wise stats
            category_stats = (
                data.groupby(['Category', 'Difficulty'])
                .agg(total_questions=('Question', 'count'))
                .unstack(fill_value=0)
                .reset_index()
            )
            
            # Ensure consistency in difficulty levels
            for level in difficulty_columns:
                if ('total_questions', level) not in category_stats.columns:
                    category_stats[('total_questions', level)] = 0
            
            # If multi-level columns, flatten them
            if isinstance(category_stats.columns, pd.MultiIndex):
                category_stats.columns = [col[1] if col[1] else col[0] for col in category_stats.columns]
            
            # Add total column
            if 'Total' not in category_stats.columns:
                category_stats['Total'] = category_stats[difficulty_columns].sum(axis=1)
            
            # Sort by total questions
            category_stats = category_stats.sort_values('Total', ascending=False)
            
            # Display the stats with styling
            st.dataframe(
                category_stats,
                height=400,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Category": st.column_config.TextColumn("Category"),
                    "Easy": st.column_config.NumberColumn("Easy", format="%d"),
                    "Medium": st.column_config.NumberColumn("Medium", format="%d"),
                    "Hard": st.column_config.NumberColumn("Hard", format="%d"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                }
            )
            
            # Visualization: Category distribution
            st.markdown('<h3 class="section-header">Category Distribution</h3>', unsafe_allow_html=True)
            
            fig = px.pie(
                category_stats,
                values='Total',
                names='Category',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            
            fig.update_layout(
                legend_title="Category",
                margin=dict(t=0, b=0, l=0, r=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Advanced: Cross-domain category analysis
            if 'Domain' in data.columns:
                st.markdown('<h3 class="section-header">Cross-Domain Category Analysis</h3>', unsafe_allow_html=True)
                
                # Create a pivot table of Domain vs Category
                cross_analysis = pd.crosstab(
                    data['Domain'],
                    data['Category'],
                    values=data.index,
                    aggfunc='count',
                    margins=True,
                    margins_name='Total'
                ).fillna(0).astype(int)
                
                # Show the cross-analysis table
                st.dataframe(cross_analysis, height=400, use_container_width=True)
        
        else:
            st.info("Category data is not available in the dataset.")
    
    # Trends Tab (for time-based analysis if available)
    with tab4:
        st.markdown('<h3 class="section-header">Question Bank Growth</h3>', unsafe_allow_html=True)
        
        # If timestamp data is available, show growth over time
        if 'Timestamp' in data.columns and not data['Timestamp'].isna().all():
            # Group by date and count questions
            data['Date'] = data['Timestamp'].dt.date
            growth_data = data.groupby('Date').size().reset_index(name='New Questions')
            growth_data['Cumulative Questions'] = growth_data['New Questions'].cumsum()
            
            # Create growth chart
            fig = px.line(
                growth_data,
                x='Date',
                y='Cumulative Questions',
                title='Question Bank Growth Over Time'
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Total Questions",
                margin=dict(t=50, b=0, l=0, r=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent additions
            st.markdown('<h3 class="section-header">Recent Additions</h3>', unsafe_allow_html=True)
            
            recent_data = data.sort_values('Timestamp', ascending=False).head(10)
            recent_questions = recent_data[['Topic', 'Question', 'Difficulty', 'Timestamp']]
            
            st.dataframe(
                recent_questions,
                height=300,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Topic": st.column_config.TextColumn("Topic"),
                    "Question": st.column_config.TextColumn("Question"),
                    "Difficulty": st.column_config.TextColumn("Difficulty"),
                    "Timestamp": st.column_config.DatetimeColumn("Added On", format="DD MMM YYYY"),
                }
            )
        
        else:
            # Create static breakdown of difficulty distribution by topic
            st.info("Timestamp data is not available for growth analysis. Showing static content distribution instead.")
            
            # Get top topics
            top_topics = data['Topic'].value_counts().head(10).index.tolist()
            
            # Filter data for top topics
            top_data = data[data['Topic'].isin(top_topics)]
            
            # Create a grouped bar chart for difficulty distribution by topic
            topic_diff_counts = pd.crosstab(top_data['Topic'], top_data['Difficulty'])
            
            # Create stacked bar chart
            fig = go.Figure()
            
            for difficulty in topic_diff_counts.columns:
                color = '#10b981' if difficulty == 'Easy' else '#f59e0b' if difficulty == 'Medium' else '#ef4444'
                fig.add_trace(go.Bar(
                    name=difficulty,
                    x=topic_diff_counts.index,
                    y=topic_diff_counts[difficulty],
                    marker_color=color
                ))
            
            fig.update_layout(
                barmode='stack',
                title="Difficulty Distribution Across Topics",
                xaxis_title="Topic",
                yaxis_title="Number of Questions",
                legend_title="Difficulty",
                margin=dict(t=50, b=0, l=0, r=0),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Advanced Analytics Page
elif page == "Advanced Analytics":
    st.markdown('<h2 class="section-header">📊 Advanced Question Bank Analytics</h2>', unsafe_allow_html=True)
    
    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["🔍 Gap Analysis", "🎯 Coverage Matrix", "⚖️ Balance Analyzer"])
    
    # Gap Analysis Tab
    with tab1:
        st.markdown('<h3 class="section-header">Difficulty Coverage Gaps</h3>', unsafe_allow_html=True)
        
        # Create a heatmap of topic vs difficulty
        topic_difficulty_matrix = pd.pivot_table(
            data,
            values='Question',
            index='Topic',
            columns='Difficulty',
            aggfunc='count',
            fill_value=0
        )
        
        # Get topics with missing difficulty levels
        gap_analysis = pd.DataFrame()
        gap_analysis['Topic'] = topic_difficulty_matrix.index
        
        for difficulty in ['Easy', 'Medium', 'Hard']:
            if difficulty in topic_difficulty_matrix.columns:
                gap_analysis[f'{difficulty}_Count'] = topic_difficulty_matrix[difficulty]
                gap_analysis[f'Has_{difficulty}'] = topic_difficulty_matrix[difficulty] > 0
            else:
                gap_analysis[f'{difficulty}_Count'] = 0
                gap_analysis[f'Has_{difficulty}'] = False
        
        # Calculate gap score (0 = all difficulties covered, 3 = none covered)
        gap_analysis['Gap_Score'] = 3 - (gap_analysis['Has_Easy'] + gap_analysis['Has_Medium'] + gap_analysis['Has_Hard'])
        
        # Filter to show only topics with gaps
        topics_with_gaps = gap_analysis[gap_analysis['Gap_Score'] > 0].sort_values('Gap_Score', ascending=False)
        
        if not topics_with_gaps.empty:
            # Display gap analysis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Topics Missing Difficulty Levels")
                
                # Create custom display for gaps
                for _, row in topics_with_gaps.iterrows():
                    missing_levels = []
                    if not row['Has_Easy']: missing_levels.append("Easy")
                    if not row['Has_Medium']: missing_levels.append("Medium")
                    if not row['Has_Hard']: missing_levels.append("Hard")
                    
                    st.markdown(f"""
                    <div style="
                        background-color: white;
                        padding: 10px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        border-left: 4px solid #ef4444;">
                        <strong>{row['Topic']}</strong> is missing {', '.join(missing_levels)} difficulty levels
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                # Summary metrics
                st.markdown("### Gap Summary")
                
                total_topics = len(gap_analysis)
                complete_coverage = sum(gap_analysis['Gap_Score'] == 0)
                partial_coverage = sum((gap_analysis['Gap_Score'] > 0) & (gap_analysis['Gap_Score'] < 3))
                no_coverage = sum(gap_analysis['Gap_Score'] == 3)
                
                st.markdown(f"""
                <div class="stat-card">
                    <p><strong>Total Topics:</strong> {total_topics}</p>
                    <p><strong>Complete Coverage:</strong> {complete_coverage} ({(complete_coverage/total_topics*100):.1f}%)</p>
                    <p><strong>Partial Coverage:</strong> {partial_coverage} ({(partial_coverage/total_topics*100):.1f}%)</p>
                    <p><strong>Missing All Levels:</strong> {no_coverage} ({(no_coverage/total_topics*100):.1f}%)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Recommendation
                if partial_coverage > 0:
                    st.markdown("""
                    <div style="background-color: #fef3c7; padding: 10px; border-radius: 8px; margin-top: 10px;">
                        <strong>Recommendation:</strong> Focus on adding questions to topics with partial coverage first.
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("Great job! All topics have questions across all difficulty levels.")
        
        # Domain Gap Analysis (if available)
        if 'Domain' in data.columns:
            st.markdown('<h3 class="section-header">Domain Coverage Analysis</h3>', unsafe_allow_html=True)
            
            # Create a bar chart showing the number of topics per domain
            domain_topic_counts = data.groupby('Domain')['Topic'].nunique().reset_index()
            domain_topic_counts.columns = ['Domain', 'Unique Topics']
            domain_topic_counts = domain_topic_counts.sort_values('Unique Topics', ascending=True)
            
            fig = px.bar(
                domain_topic_counts,
                x='Unique Topics',
                y='Domain',
                orientation='h',
                color='Unique Topics',
                color_continuous_scale='Blues',
                title='Topic Coverage by Domain'
            )
            
            fig.update_layout(
                margin=dict(t=50, b=0, l=0, r=0),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Coverage Matrix Tab
    with tab2:
        st.markdown('<h3 class="section-header">Topic-Difficulty Coverage Matrix</h3>', unsafe_allow_html=True)
        
        # Create heatmap of topic vs difficulty
        pivot_data = pd.pivot_table(
            data,
            values='Question',
            index='Topic',
            columns='Difficulty',
            aggfunc='count',
            fill_value=0
        )
        
        # Ensure all difficulty columns exist
        for diff in ['Easy', 'Medium', 'Hard']:
            if diff not in pivot_data.columns:
                pivot_data[diff] = 0
        
        # Sorting topics by total count
        pivot_data['Total'] = pivot_data.sum(axis=1)
        pivot_data = pivot_data.sort_values('Total', ascending=False)
        
        # Keep only the difficulty columns for the heatmap
        heatmap_data = pivot_data[['Easy', 'Medium', 'Hard']]
        
        # Create heatmap using Plotly
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Difficulty", y="Topic", color="Question Count"),
            x=['Easy', 'Medium', 'Hard'],
            y=heatmap_data.index,
            color_continuous_scale='Blues',
            aspect="auto"
        )
        
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=600,
            yaxis=dict(tickmode='linear')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Topic Distribution Across Domains (if available)
        if 'Domain' in data.columns:
            st.markdown('<h3 class="section-header">Domain-Topic Distribution</h3>', unsafe_allow_html=True)
            
            # Get unique domains and topics
            domains = sorted(data['Domain'].unique())
            
            # Select domain for detailed view
            selected_domains = st.multiselect(
                "Select Domains to Compare",
                domains,
                default=domains[:2] if len(domains) >= 2 else domains
            )
            
            if selected_domains:
                # Filter data for selected domains
                domain_data = data[data['Domain'].isin(selected_domains)]
                
                # Create crosstab of domain vs topic
                domain_topic_matrix = pd.crosstab(
                    domain_data['Topic'],
                    domain_data['Domain'],
                    values=domain_data.index,
                    aggfunc='count',
                    normalize='columns'
                ).fillna(0)
                
                # Create heatmap
                fig = px.imshow(
                    domain_topic_matrix,
                    labels=dict(x="Domain", y="Topic", color="Proportion"),
                    color_continuous_scale='Blues',
                    aspect="auto"
                )
                
                fig.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=600,
                    yaxis=dict(tickmode='linear')
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Balance Analyzer Tab
    with tab3:
        st.markdown('<h3 class="section-header">Question Bank Balance Analysis</h3>', unsafe_allow_html=True)
        
        # Calculate difficulty distribution
        difficulty_dist = data['Difficulty'].value_counts(normalize=True).to_dict()
        
        # Calculate topic distribution
        topic_dist = data['Topic'].value_counts()
        topic_concentration = (topic_dist.max() / topic_dist.sum()) * 100
        
        # Calculate domain distribution (if available)
        domain_concentration = 0
        if 'Domain' in data.columns:
            domain_dist = data['Domain'].value_counts()
            domain_concentration = (domain_dist.max() / domain_dist.sum()) * 100
        
        # Create metrics for balance analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown("### Difficulty Balance")
            
            # Create a gauge for difficulty balance
            easy_pct = difficulty_dist.get('Easy', 0) * 100
            medium_pct = difficulty_dist.get('Medium', 0) * 100
            hard_pct = difficulty_dist.get('Hard', 0) * 100
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = medium_pct,
                title = {'text': "Medium Questions"},
                delta = {'reference': 40, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#f59e0b"},
                    'steps': [
                        {'range': [0, 20], 'color': "#fee2e2"},
                        {'range': [20, 30], 'color': "#fef3c7"},
                        {'range': [30, 50], 'color': "#d1fae5"},
                        {'range': [50, 70], 'color': "#fef3c7"},
                        {'range': [70, 100], 'color': "#fee2e2"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 40
                    }
                }
            ))
            
            fig.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between;">
                <div>Easy: {easy_pct:.1f}%</div>
                <div>Medium: {medium_pct:.1f}%</div>
                <div>Hard: {hard_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommendation for difficulty balance
            ideal_ratio = "30% Easy, 40% Medium, 30% Hard"
            st.markdown(f"<p><strong>Ideal Ratio:</strong> {ideal_ratio}</p>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown("### Topic Concentration")
            
            # Create a gauge for topic concentration
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = topic_concentration,
                title = {'text': "Max Topic %"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#3b82f6"},
                    'steps': [
                        {'range': [0, 15], 'color': "#d1fae5"},
                        {'range': [15, 30], 'color': "#fef3c7"},
                        {'range': [30, 100], 'color': "#fee2e2"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 20
                    }
                }
            ))
            
            fig.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # Show most and least covered topics
            most_covered = topic_dist.idxmax()
            most_covered_pct = (topic_dist.max() / topic_dist.sum()) * 100
            
            least_covered = topic_dist.idxmin()
            least_covered_pct = (topic_dist.min() / topic_dist.sum()) * 100
            
            st.markdown(f"""
            <p><strong>Most Covered:</strong> {most_covered} ({most_covered_pct:.1f}%)</p>
            <p><strong>Least Covered:</strong> {least_covered} ({least_covered_pct:.1f}%)</p>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            
            if 'Domain' in data.columns:
                st.markdown("### Domain Balance")
                
                # Create a gauge for domain concentration
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = domain_concentration,
                    title = {'text': "Max Domain %"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#8b5cf6"},
                        'steps': [
                            {'range': [0, 25], 'color': "#d1fae5"},
                            {'range': [25, 50], 'color': "#fef3c7"},
                            {'range': [50, 100], 'color': "#fee2e2"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 40
                        }
                    }
                ))
                
                fig.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # Show domain distribution
                domain_counts = data['Domain'].value_counts()
                
                most_covered_domain = domain_counts.idxmax()
                most_covered_domain_pct = (domain_counts.max() / domain_counts.sum()) * 100
                
                least_covered_domain = domain_counts.idxmin()
                least_covered_domain_pct = (domain_counts.min() / domain_counts.sum()) * 100
                
                st.markdown(f"""
                <p><strong>Most Covered:</strong> {most_covered_domain} ({most_covered_domain_pct:.1f}%)</p>
                <p><strong>Least Covered:</strong> {least_covered_domain} ({least_covered_domain_pct:.1f}%)</p>
                """, unsafe_allow_html=True)
            else:
                st.markdown("### Domain Balance")
                st.info("Domain data is not available in the dataset.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Overall balance score
        st.markdown('<h3 class="section-header">Overall Question Bank Health</h3>', unsafe_allow_html=True)
        
        # Calculate overall balance score (0-100)
        # Factors: difficulty distribution, topic concentration, domain concentration
        
        # Difficulty balance score (ideal: 30% easy, 40% medium, 30% hard)
        easy_score = 100 - abs(easy_pct - 30) * 2.5
        medium_score = 100 - abs(medium_pct - 40) * 2.5
        hard_score = 100 - abs(hard_pct - 30) * 2.5
        difficulty_score = (easy_score + medium_score + hard_score) / 3
        
        # Topic concentration score (lower is better)
        topic_score = 100 - topic_concentration
        
        # Domain score (if available)
        domain_score = 100 - domain_concentration if 'Domain' in data.columns else 100
        
        # Overall score
        overall_score = (difficulty_score * 0.4 + topic_score * 0.4 + domain_score * 0.2)
        
        # Display overall score
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #d1fae5, #f0fdfa);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        ">
            <h2 style="margin: 0; color: #047857;">Question Bank Health Score: {overall_score:.1f}/100</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Health assessment
        health_message = ""
        if overall_score >= 80:
            health_message = "Your question bank is well-balanced and diverse. Keep up the great work!"
        elif overall_score >= 60:
            health_message = "Your question bank is reasonably balanced, but there's room for improvement in some areas."
        else:
            health_message = "Your question bank needs attention to improve balance and coverage across topics and difficulty levels."
        
        st.markdown(f"""
        <div style="
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        ">
            <h3 style="margin-top: 0;">Assessment</h3>
            <p>{health_message}</p>
            
            <h4>Recommendations:</h4>
            <ul>
        """, unsafe_allow_html=True)
        
        # Generate recommendations based on scores
        recommendations = []
        
        if difficulty_score < 70:
            if easy_pct < 25:
                recommendations.append("Add more Easy questions to help beginners.")
            elif easy_pct > 35:
                recommendations.append("Add more Medium and Hard questions to balance difficulty.")
            
            if medium_pct < 35:
                recommendations.append("Increase the number of Medium difficulty questions.")
            
            if hard_pct < 25:
                recommendations.append("Add more Hard questions to challenge advanced users.")
            elif hard_pct > 35:
                recommendations.append("Consider reducing the proportion of Hard questions.")
        
        if topic_score < 70:
            recommendations.append(f"Diversify your question bank by adding more questions to topics other than {most_covered}.")
            recommendations.append(f"Focus on adding more questions to underrepresented topics like {least_covered}.")
        
        if 'Domain' in data.columns and domain_score < 70:
            recommendations.append(f"Balance your domains by adding more questions to domains other than {most_covered_domain}.")
            recommendations.append(f"Add more questions to the {least_covered_domain} domain to improve coverage.")
        
        # Display recommendations
        for rec in recommendations:
            st.markdown(f"<li>{rec}</li>", unsafe_allow_html=True)
        
        if not recommendations:
            st.markdown("<li>Continue maintaining the current balance as you add new questions.</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Quiz Page (Default)
else:  # page == "Quiz"
    # Sidebar filters
    st.sidebar.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🎯 Question Filters")
    
    # Topic filter
    topics = sorted(data['Topic'].unique())
    selected_topic = st.sidebar.selectbox("Select Topic", topics)
    
    # Filter by topic
    filtered_data = data[data['Topic'] == selected_topic]
    
    # Difficulty filter
    difficulties = sorted(filtered_data['Difficulty'].unique())
    selected_difficulty = st.sidebar.selectbox("Select Difficulty", difficulties)
    
    # Apply difficulty filter
    filtered_data = filtered_data[filtered_data['Difficulty'] == selected_difficulty]
    
    # Domain filter (if available)
    if 'Domain' in filtered_data.columns and len(filtered_data['Domain'].unique()) > 1:
        domains = sorted(filtered_data['Domain'].unique())
        selected_domain = st.sidebar.selectbox("Select Domain", domains)
        filtered_data = filtered_data[filtered_data['Domain'] == selected_domain]
    
    # Category filter (if available)
    if 'Category' in filtered_data.columns and len(filtered_data['Category'].unique()) > 1:
        categories = sorted(filtered_data['Category'].unique())
        selected_category = st.sidebar.selectbox("Select Category", categories)
        filtered_data = filtered_data[filtered_data['Category'] == selected_category]
    
    # Number of questions to display
    num_questions = st.sidebar.slider("Number of Questions", 1, min(20, len(filtered_data)), 5)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Quiz settings
    st.sidebar.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.sidebar.markdown("### ⚙️ Quiz Settings")
    
    # Quiz mode
    quiz_mode = st.sidebar.radio("Quiz Mode", ["Practice", "Test"], index=0)
    
    # Show explanation option
    show_explanation = st.sidebar.checkbox("Show Explanations", True)
    
    # Time limit (for Test mode)
    time_limit = None
    if quiz_mode == "Test":
        time_limit = st.sidebar.slider("Time Limit (minutes)", 1, 30, 10)
    
    # Randomize questions
    randomize = st.sidebar.checkbox("Randomize Questions", True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Display questions
    st.markdown(f"<h2 class='section-header'>{selected_topic} - {selected_difficulty} Questions</h2>", unsafe_allow_html=True)
    
    # Quiz instructions
    if quiz_mode == "Practice":
        st.info("Practice Mode: Take your time to answer each question. Immediate feedback will be provided.")
    else:
        st.warning(f"Test Mode: You have {time_limit} minutes to complete all questions. Feedback will be shown at the end.")
    
    # Sample questions
    if randomize:
        quiz_questions = filtered_data.sample(min(num_questions, len(filtered_data)))
    else:
        quiz_questions = filtered_data.head(min(num_questions, len(filtered_data)))
    
    # Initialize session state for tracking answers if not already done
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Quiz form
    with st.form("quiz_form"):
        # Display each question
        for i, (_, question_data) in enumerate(quiz_questions.iterrows()):
            question_id = str(question_data.name)  # Use dataframe index as question ID
            question_text = question_data["Question"]
            options = [
                question_data["Option A"],
                question_data["Option B"],
                question_data["Option C"],
                question_data["Option D"]
            ]
            correct_answer = question_data["Correct Answer"]
            correct_index = get_correct_option_index(correct_answer)
            
            # Determine difficulty class for styling
            difficulty_class = ""
            if question_data["Difficulty"] == "Easy":
                difficulty_class = "difficulty-easy"
            elif question_data["Difficulty"] == "Medium":
                difficulty_class = "difficulty-medium"
            elif question_data["Difficulty"] == "Hard":
                difficulty_class = "difficulty-hard"
            
            # Question card
            st.markdown(f"""
            <div class="question-card">
                <div class="question-header">
                    <span class="question-number">Question {i+1}</span>
                    <span class="question-difficulty {difficulty_class}">{question_data["Difficulty"]}</span>
                </div>
                <div class="question-meta">
                    Topic: {question_data["Topic"]}
                    {f' | Domain: {question_data["Domain"]}' if 'Domain' in question_data and not pd.isna(question_data["Domain"]) else ''}
                    {f' | Category: {question_data["Category"]}' if 'Category' in question_data and not pd.isna(question_data["Category"]) else ''}
                </div>
                <div class="question-text">
                    {question_text}
                </div>
            """, unsafe_allow_html=True)
            
            # Display radio buttons for options
            selected_option = st.radio(
                f"Select your answer for Question {i+1}:",
                options,
                key=f"question_{question_id}"
            )
            
            # Store answer in session state
            selected_index = options.index(selected_option)
            st.session_state.answers[question_id] = {
                "selected_index": selected_index,
                "correct_index": correct_index,
                "explanation": question_data.get("Explanation", "No explanation provided.")
            }
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submit_button = st.form_submit_button("Submit Answers")
        
        if submit_button:
            st.session_state.submitted = True
    
    # Display results after submission
    if st.session_state.submitted:
        st.markdown('<h3 class="section-header">Quiz Results</h3>', unsafe_allow_html=True)
        
        # Calculate score
        correct_count = sum(1 for ans in st.session_state.answers.values() 
                           if ans["selected_index"] == ans["correct_index"])
        total_questions = len(st.session_state.answers)
        score_percentage = (correct_count / total_questions) * 100
        
        # Display score
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #d1fae5, #f0fdfa);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        ">
            <h2 style="margin: 0; color: #047857;">Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Results breakdown for each question
        for i, (question_id, (_, question_data)) in enumerate(zip(st.session_state.answers.keys(), quiz_questions.iterrows())):
            answer_data = st.session_state.answers[question_id]
            is_correct = answer_data["selected_index"] == answer_data["correct_index"]
            
            options = [
                question_data["Option A"],
                question_data["Option B"],
                question_data["Option C"],
                question_data["Option D"]
            ]
            
            # Question result card
            st.markdown(f"""
            <div class="question-card" style="border-left: 4px solid {'#10b981' if is_correct else '#ef4444'};">
                <div class="question-header">
                    <span class="question-number">Question {i+1}</span>
                    <span style="color: {'#10b981' if is_correct else '#ef4444'}; font-weight: bold;">
                        {'✓ Correct' if is_correct else '✗ Incorrect'}
                    </span>
                </div>
                <div class="question-text">
                    {question_data["Question"]}
                </div>
                <div style="margin-top: 10px;">
                    <strong>Your Answer:</strong> {options[answer_data["selected_index"]]}
                </div>
                <div style="margin-top: 5px;">
                    <strong>Correct Answer:</strong> {options[answer_data["correct_index"]]}
                </div>
            """, unsafe_allow_html=True)
            
            # Show explanation if enabled
            if show_explanation and "Explanation" in question_data and not pd.isna(question_data["Explanation"]):
                st.markdown(f"""
                <div class="answer-correct">
                    <strong>Explanation:</strong> {question_data["Explanation"]}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("Start New Quiz"):
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.experimental_rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>© 2023 Premium MCQ Question Bank | Last updated: April 2025</p>
    <p>For educational purposes only</p>
</div>
""", unsafe_allow_html=True)
