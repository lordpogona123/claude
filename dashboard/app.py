"""
Triple Cherry Casino Analytics Dashboard
Executive-level visual analytics interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Triple Cherry Analytics",
    page_icon="🍒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #C41E3A;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .risk-high {
        background-color: #ff4444;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .risk-medium {
        background-color: #ffaa00;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .risk-low {
        background-color: #00C851;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


def load_latest_data():
    """Load the most recent data file"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')

    if not os.path.exists(data_dir):
        return None, None

    files = [f for f in os.listdir(data_dir) if f.startswith('processed_') and f.endswith('.json')]

    if not files:
        return None, None

    # Get most recent file
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
    filepath = os.path.join(data_dir, latest_file)

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Also load raw data
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    raw_files = [f for f in os.listdir(raw_dir) if f.startswith('casino_data_') and f.endswith('.json')]

    if raw_files:
        latest_raw = max(raw_files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
        raw_filepath = os.path.join(raw_dir, latest_raw)

        with open(raw_filepath, 'r') as f:
            raw_data = json.load(f)

        return data, raw_data.get('results', [])

    return data, []


def create_coverage_gauge(value, title):
    """Create a gauge chart for coverage metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "#C41E3A"},
            'steps': [
                {'range': [0, 30], 'color': "#ffcccc"},
                {'range': [30, 60], 'color': "#ff9999"},
                {'range': [60, 100], 'color': "#ff6666"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def create_regional_chart(regional_stats):
    """Create regional distribution chart"""
    regions = []
    total = []
    with_tc = []
    penetration = []

    for region, data in regional_stats.items():
        regions.append(region)
        total.append(data['total_casinos'])
        with_tc.append(data['with_triple_cherry'])
        penetration.append(data['penetration_rate'])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Total Casinos',
        x=regions,
        y=total,
        marker_color='lightblue'
    ))

    fig.add_trace(go.Bar(
        name='With Triple Cherry',
        x=regions,
        y=with_tc,
        marker_color='#C41E3A'
    ))

    fig.update_layout(
        title='Regional Distribution',
        barmode='group',
        xaxis_title='Region',
        yaxis_title='Number of Casinos',
        height=400
    )

    return fig


def create_game_popularity_chart(game_popularity):
    """Create game popularity chart"""
    top_games = game_popularity[:10]

    games = [g['game'] for g in top_games]
    appearances = [g['appearances'] for g in top_games]
    percentages = [g['percentage'] for g in top_games]

    fig = go.Figure(go.Bar(
        y=games[::-1],  # Reverse for better readability
        x=appearances[::-1],
        orientation='h',
        marker=dict(
            color=percentages[::-1],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Coverage %")
        ),
        text=[f"{p}%" for p in percentages[::-1]],
        textposition='auto',
    ))

    fig.update_layout(
        title='Top 10 Most Popular Games',
        xaxis_title='Number of Casinos',
        yaxis_title='Game Title',
        height=500,
        margin=dict(l=200)
    )

    return fig


def create_coverage_pie(coverage_quality):
    """Create coverage quality pie chart"""
    labels = []
    values = []
    colors = ['#ff4444', '#ffaa00', '#66bb6a', '#00C851']

    for category in ['none', 'partial', 'moderate', 'strong']:
        if category in coverage_quality:
            labels.append(category.capitalize())
            values.append(len(coverage_quality[category]))

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4
    )])

    fig.update_layout(
        title='Coverage Quality Distribution',
        height=400
    )

    return fig


def create_country_heatmap(country_dist):
    """Create country distribution heatmap"""
    countries = []
    total = []
    penetration = []

    for country, data in sorted(country_dist.items(), key=lambda x: x[1]['penetration_rate'], reverse=True)[:15]:
        countries.append(country)
        total.append(data['total'])
        penetration.append(data['penetration_rate'])

    fig = go.Figure(data=go.Heatmap(
        z=[penetration],
        x=countries,
        y=['Penetration Rate'],
        colorscale='RdYlGn',
        text=[[f"{p}%" for p in penetration]],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Penetration %")
    ))

    fig.update_layout(
        title='Top 15 Countries by Penetration Rate',
        height=200,
        xaxis_title='Country',
        margin=dict(l=20, r=20, t=60, b=80)
    )

    return fig


def main():
    """Main dashboard application"""

    # Header
    st.markdown('<div class="main-header">🍒 Triple Cherry Casino Analytics</div>', unsafe_allow_html=True)
    st.markdown('---')

    # Load data
    data, raw_results = load_latest_data()

    if data is None:
        st.error("No data available. Please run the scraper first using: `python main.py --scrape`")
        st.info("After scraping, the dashboard will automatically display the results.")
        return

    # Sidebar
    with st.sidebar:
        st.header("Dashboard Controls")

        # Data info
        st.subheader("Data Information")
        if 'scan_date' in data.get('metadata', {}):
            st.write(f"**Last Updated:** {data['metadata']['scan_date'][:10]}")

        st.write(f"**Total Casinos:** {data['processed']['summary']['total_casinos']}")

        # Filters
        st.subheader("Filters")

        show_all = st.checkbox("Show All Data", value=True)

        if not show_all:
            region_filter = st.multiselect(
                "Select Regions",
                options=list(data['processed']['regional_stats'].keys())
            )

    # Main content
    processed = data.get('processed', {})
    summary = processed.get('summary', {})
    insights = data.get('insights', {})

    # Key Metrics Row
    st.header("📊 Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Casinos Scanned",
            value=summary.get('total_casinos', 0),
            delta=None
        )

    with col2:
        st.metric(
            label="With Triple Cherry",
            value=summary.get('casinos_with_tc', 0),
            delta=f"{summary.get('penetration_rate', 0)}%"
        )

    with col3:
        st.metric(
            label="Unique Games Detected",
            value=summary.get('total_unique_games', 0)
        )

    with col4:
        risks = processed.get('risks', {})
        total_risks = sum(len(v) for v in risks.values())
        st.metric(
            label="Total Risk Items",
            value=total_risks,
            delta="Issues Identified",
            delta_color="inverse"
        )

    st.markdown('---')

    # Coverage Gauges
    st.header("📈 Market Penetration")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            create_coverage_gauge(
                summary.get('penetration_rate', 0),
                "Overall Penetration Rate"
            ),
            use_container_width=True
        )

    with col2:
        # Provider mention rate
        regional = processed.get('regional_stats', {})
        if regional:
            avg_penetration = sum(r['penetration_rate'] for r in regional.values()) / len(regional)
            st.plotly_chart(
                create_coverage_gauge(
                    round(avg_penetration, 2),
                    "Avg Regional Penetration"
                ),
                use_container_width=True
            )

    with col3:
        # Calculate quality score
        coverage = processed.get('coverage_quality', {})
        total_with_tc = summary.get('casinos_with_tc', 1)
        strong = len(coverage.get('strong', []))
        quality_score = round((strong / total_with_tc * 100), 2) if total_with_tc > 0 else 0

        st.plotly_chart(
            create_coverage_gauge(
                quality_score,
                "Quality Score (Strong Coverage %)"
            ),
            use_container_width=True
        )

    st.markdown('---')

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            create_regional_chart(processed.get('regional_stats', {})),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            create_coverage_pie(processed.get('coverage_quality', {})),
            use_container_width=True
        )

    # Charts Row 2
    st.plotly_chart(
        create_game_popularity_chart(processed.get('game_popularity', [])),
        use_container_width=True
    )

    # Country Heatmap
    st.plotly_chart(
        create_country_heatmap(processed.get('country_distribution', {})),
        use_container_width=True
    )

    st.markdown('---')

    # Key Insights
    st.header("💡 Key Insights")

    if insights and 'key_insights' in insights:
        for insight in insights['key_insights']:
            st.info(insight)

    st.markdown('---')

    # Recommendations
    st.header("🎯 Recommendations")

    if insights and 'recommendations' in insights:
        for rec in insights['recommendations']:
            priority_color = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }

            with st.expander(f"{priority_color.get(rec['priority'], '⚪')} {rec['action']} [{rec['priority']} Priority]"):
                st.write(f"**Category:** {rec['category']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Impact:** {rec['impact']}")

                st.write("**Next Steps:**")
                for step in rec['next_steps']:
                    st.write(f"- {step}")

    st.markdown('---')

    # Risk Analysis
    st.header("⚠️ Risk Analysis")

    risks = processed.get('risks', {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Access Issues")
        access_issues = risks.get('access_issues', [])
        if access_issues:
            df = pd.DataFrame(access_issues)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("No access issues detected")

    with col2:
        st.subheader("Commercial Issues")
        commercial = risks.get('commercial_issues', [])
        if commercial:
            df = pd.DataFrame(commercial)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("No commercial issues detected")

    st.markdown('---')

    # Detailed Tables
    st.header("📋 Detailed Data")

    tab1, tab2, tab3 = st.tabs(["Operator List", "Game Popularity", "Regional Summary"])

    with tab1:
        if raw_results:
            operator_data = []
            for result in raw_results:
                operator_data.append({
                    'Casino': result.get('casino_name', ''),
                    'Region': result.get('region', ''),
                    'Country': result.get('country', ''),
                    'Status': result.get('access_status', ''),
                    'TC Found': result.get('tripleCherryFound', ''),
                    'Games': len(result.get('detected_games', [])),
                    'Coverage': result.get('coverage_category', ''),
                    'Risk': result.get('risk_level', '')
                })

            df = pd.DataFrame(operator_data)
            st.dataframe(df, use_container_width=True, height=400)

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Operator List (CSV)",
                data=csv,
                file_name=f"operator_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with tab2:
        game_pop = processed.get('game_popularity', [])
        if game_pop:
            df = pd.DataFrame(game_pop)
            st.dataframe(df, use_container_width=True, height=400)

    with tab3:
        regional = processed.get('regional_stats', {})
        if regional:
            regional_data = []
            for region, stats in regional.items():
                regional_data.append({
                    'Region': region,
                    'Total Casinos': stats['total_casinos'],
                    'With TC': stats['with_triple_cherry'],
                    'Penetration %': stats['penetration_rate'],
                    'Countries': len(stats['countries'])
                })

            df = pd.DataFrame(regional_data)
            st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
