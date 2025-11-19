#!/usr/bin/env python3
"""
Generate Visual Graphics for Dashboard Results
Creates PNG charts and graphs from analytics data
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from pathlib import Path
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory
output_dir = Path('outputs/visualizations')
output_dir.mkdir(parents=True, exist_ok=True)

# Load processed data
data_file = sorted(Path('data/processed').glob('processed_*.json'))[-1]
print(f"Loading data from: {data_file}")

with open(data_file, 'r') as f:
    data = json.load(f)

processed = data['processed']
insights = data['insights']

# Figure 1: Market Penetration Overview
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Triple Cherry Market Presence - Executive Dashboard', fontsize=20, fontweight='bold')

# 1.1: Penetration Rate Gauge (as bar)
summary = processed['summary']
ax = axes[0, 0]
penetration = summary['penetration_rate']
ax.barh(['Market Penetration'], [penetration], color='#C41E3A', height=0.4)
ax.barh(['Market Penetration'], [100-penetration], left=[penetration], color='#EEEEEE', height=0.4)
ax.set_xlim(0, 100)
ax.set_xlabel('Percentage (%)', fontsize=12)
ax.set_title(f'Market Penetration: {penetration}%', fontsize=14, fontweight='bold')
ax.text(penetration/2, 0, f'{penetration}%', ha='center', va='center', fontsize=16, fontweight='bold', color='white')

# 1.2: Key Metrics
ax = axes[0, 1]
ax.axis('off')
metrics_text = f"""
KEY METRICS

Total Casinos Scanned: {summary['total_casinos']}
Casinos with TC: {summary['casinos_with_tc']}
Penetration Rate: {summary['penetration_rate']}%
Unique Games: {summary['total_unique_games']}

COVERAGE QUALITY
• None: {len(processed['coverage_quality']['none'])} casinos
• Partial (1-2): {len(processed['coverage_quality']['partial'])} casinos
• Moderate (3-5): {len(processed['coverage_quality']['moderate'])} casinos
• Strong (5+): {len(processed['coverage_quality']['strong'])} casinos
"""
ax.text(0.1, 0.5, metrics_text, fontsize=12, family='monospace',
        verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 1.3: Regional Distribution
ax = axes[1, 0]
regional = processed['regional_stats']
regions = list(regional.keys())
totals = [regional[r]['total_casinos'] for r in regions]
with_tc = [regional[r]['with_triple_cherry'] for r in regions]

x = np.arange(len(regions))
width = 0.35
ax.bar(x - width/2, totals, width, label='Total Casinos', color='lightblue')
ax.bar(x + width/2, with_tc, width, label='With Triple Cherry', color='#C41E3A')

ax.set_xlabel('Region', fontsize=12)
ax.set_ylabel('Number of Casinos', fontsize=12)
ax.set_title('Regional Distribution', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(regions)
ax.legend()
ax.grid(axis='y', alpha=0.3)

# 1.4: Coverage Quality Pie
ax = axes[1, 1]
coverage = processed['coverage_quality']
sizes = [len(coverage['none']), len(coverage['partial']), len(coverage['moderate']), len(coverage['strong'])]
labels = [f'None\n({sizes[0]})', f'Partial\n({sizes[1]})', f'Moderate\n({sizes[2]})', f'Strong\n({sizes[3]})']
colors = ['#ff4444', '#ffaa00', '#66bb6a', '#00C851']
explode = (0.05, 0.05, 0.05, 0.1)  # Explode strong

ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
       shadow=True, startangle=90, textprops={'fontsize': 11})
ax.set_title('Coverage Quality Distribution', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'dashboard_overview.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: dashboard_overview.png")
plt.close()

# Figure 2: Game Popularity
fig, ax = plt.subplots(figsize=(14, 10))
games_pop = processed['game_popularity'][:15]  # Top 15

games = [g['game'] for g in games_pop]
appearances = [g['appearances'] for g in games_pop]
percentages = [g['percentage'] for g in games_pop]

# Horizontal bar chart
y_pos = np.arange(len(games))
colors_gradient = plt.cm.Reds(np.linspace(0.4, 0.9, len(games)))

bars = ax.barh(y_pos, appearances, color=colors_gradient)
ax.set_yticks(y_pos)
ax.set_yticklabels(games, fontsize=11)
ax.invert_yaxis()
ax.set_xlabel('Number of Casinos', fontsize=12)
ax.set_title('Top 15 Most Popular Triple Cherry Games', fontsize=16, fontweight='bold', pad=20)

# Add percentage labels
for i, (bar, pct) in enumerate(zip(bars, percentages)):
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
            f'{pct}%', ha='left', va='center', fontsize=10)

ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / 'game_popularity.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: game_popularity.png")
plt.close()

# Figure 3: Risk Analysis
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Risk Analysis Dashboard', fontsize=18, fontweight='bold')

risks = processed['risks']

# 3.1: Risk Categories Bar Chart
ax = axes[0]
risk_categories = ['Access\nIssues', 'Technical\nIssues', 'Commercial\nIssues', 'High Risk\nCasinos']
risk_counts = [
    len(risks['access_issues']),
    len(risks['technical_issues']),
    len(risks['commercial_issues']),
    len(risks['high_risk_casinos'])
]
risk_colors = ['#ff4444', '#ffaa00', '#ff9900', '#cc0000']

bars = ax.bar(risk_categories, risk_counts, color=risk_colors, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Number of Cases', fontsize=12)
ax.set_title('Risk Categories Overview', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Add count labels on bars
for bar, count in zip(bars, risk_counts):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(count)}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# 3.2: Risk Distribution by Region
ax = axes[1]
regional_risks = {}
for region in regional.keys():
    regional_risks[region] = {
        'total': regional[region]['total_casinos'],
        'at_risk': 0
    }

# Count risks by region from raw results
raw_file = sorted(Path('data/raw').glob('casino_data_*.json'))[-1]
with open(raw_file, 'r') as f:
    raw_data = json.load(f)

for result in raw_data['results']:
    region = result.get('region', 'Unknown')
    if result.get('risk_level') in ['medium', 'high']:
        if region in regional_risks:
            regional_risks[region]['at_risk'] += 1

regions_list = list(regional_risks.keys())
at_risk = [regional_risks[r]['at_risk'] for r in regions_list]
safe = [regional_risks[r]['total'] - regional_risks[r]['at_risk'] for r in regions_list]

x = np.arange(len(regions_list))
width = 0.6

p1 = ax.bar(x, safe, width, label='Low/No Risk', color='#66bb6a')
p2 = ax.bar(x, at_risk, width, bottom=safe, label='Medium/High Risk', color='#ff6666')

ax.set_ylabel('Number of Casinos', fontsize=12)
ax.set_title('Risk Distribution by Region', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(regions_list)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / 'risk_analysis.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: risk_analysis.png")
plt.close()

# Figure 4: Country Heatmap (Top 15)
fig, ax = plt.subplots(figsize=(16, 6))

country_dist = processed['country_distribution']
# Sort by penetration rate
sorted_countries = sorted(country_dist.items(),
                         key=lambda x: x[1]['penetration_rate'],
                         reverse=True)[:15]

countries = [c[0] for c in sorted_countries]
penetration = [c[1]['penetration_rate'] for c in sorted_countries]
totals = [c[1]['total'] for c in sorted_countries]

# Create color map
colors_map = plt.cm.RdYlGn(np.array(penetration) / 100)

bars = ax.bar(countries, penetration, color=colors_map, edgecolor='black', linewidth=1)
ax.set_ylabel('Penetration Rate (%)', fontsize=12)
ax.set_xlabel('Country', fontsize=12)
ax.set_title('Top 15 Countries by Triple Cherry Penetration Rate', fontsize=16, fontweight='bold', pad=20)
ax.set_ylim(0, 100)
plt.xticks(rotation=45, ha='right')

# Add labels
for i, (bar, pct, total) in enumerate(zip(bars, penetration, totals)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'{pct}%\n({total})', ha='center', va='bottom', fontsize=9)

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / 'country_penetration.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: country_penetration.png")
plt.close()

# Figure 5: Key Insights Summary
fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('off')

insights_list = insights['key_insights']
recommendations = insights['recommendations'][:5]  # Top 5

# Create formatted text
title_text = "KEY INSIGHTS & RECOMMENDATIONS"
insights_text = "\n".join([f"  {i+1}. {insight}" for i, insight in enumerate(insights_list)])

recommendations_text = "\n\nTOP RECOMMENDATIONS:\n"
for i, rec in enumerate(recommendations, 1):
    priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
    recommendations_text += f"\n  {priority_emoji} {rec['action']}\n"
    recommendations_text += f"     Priority: {rec['priority']} | Category: {rec['category']}\n"
    recommendations_text += f"     → {rec['description']}\n"

full_text = f"{title_text}\n{'='*70}\n\nINSIGHTS:\n{insights_text}\n{recommendations_text}"

ax.text(0.05, 0.95, full_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3, pad=1))

plt.tight_layout()
plt.savefig(output_dir / 'insights_summary.png', dpi=300, bbox_inches='tight')
print(f"✅ Saved: insights_summary.png")
plt.close()

print(f"\n✅ All visualizations generated successfully!")
print(f"📂 Saved to: {output_dir}/")
print(f"\nGenerated files:")
print(f"  1. dashboard_overview.png - Executive metrics and charts")
print(f"  2. game_popularity.png - Top 15 games ranking")
print(f"  3. risk_analysis.png - Risk breakdown and regional analysis")
print(f"  4. country_penetration.png - Country-level penetration rates")
print(f"  5. insights_summary.png - Key insights and recommendations")
