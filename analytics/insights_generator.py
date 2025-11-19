"""
Insights Generator - Generates business insights and recommendations
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generates executive insights and recommendations from processed data"""

    def __init__(self, processed_data: Dict, raw_results: List[Dict]):
        """
        Initialize with processed data

        Args:
            processed_data: Processed analytics data
            raw_results: Raw scraping results
        """
        self.processed_data = processed_data
        self.raw_results = raw_results

    def generate_executive_summary(self) -> str:
        """
        Generate executive summary text

        Returns:
            Executive summary as formatted string
        """
        summary = self.processed_data.get('summary', {})

        text = f"""
EXECUTIVE SUMMARY - TRIPLE CHERRY MARKET PRESENCE
{'=' * 60}

MARKET OVERVIEW:
- Total Casinos Scanned: {summary.get('total_casinos', 0)}
- Casinos with Triple Cherry Games: {summary.get('casinos_with_tc', 0)}
- Market Penetration Rate: {summary.get('penetration_rate', 0)}%
- Unique TC Games Detected: {summary.get('total_unique_games', 0)}

"""

        # Regional breakdown
        regional = self.processed_data.get('regional_stats', {})
        if regional:
            text += "REGIONAL DISTRIBUTION:\n"
            for region, data in sorted(regional.items()):
                text += f"  {region}: {data['with_triple_cherry']}/{data['total_casinos']} casinos ({data['penetration_rate']}%)\n"
            text += "\n"

        # Top games
        games = self.processed_data.get('game_popularity', [])[:5]
        if games:
            text += "TOP 5 MOST POPULAR GAMES:\n"
            for i, game in enumerate(games, 1):
                text += f"  {i}. {game['game']} - {game['appearances']} casinos ({game['percentage']}%)\n"
            text += "\n"

        # Risk overview
        risks = self.processed_data.get('risks', {})
        text += "RISK OVERVIEW:\n"
        text += f"  - Access Issues: {len(risks.get('access_issues', []))} casinos\n"
        text += f"  - Technical Issues: {len(risks.get('technical_issues', []))} cases\n"
        text += f"  - Commercial Issues: {len(risks.get('commercial_issues', []))} cases\n"
        text += f"  - High Risk Casinos: {len(risks.get('high_risk_casinos', []))}\n"

        return text

    def generate_key_insights(self) -> List[str]:
        """
        Generate key business insights

        Returns:
            List of insight strings
        """
        insights = []

        summary = self.processed_data.get('summary', {})
        regional = self.processed_data.get('regional_stats', {})
        games = self.processed_data.get('game_popularity', [])
        coverage = self.processed_data.get('coverage_quality', {})

        # Penetration insights
        penetration = summary.get('penetration_rate', 0)
        if penetration < 30:
            insights.append(f"⚠️ LOW PENETRATION: Only {penetration}% market penetration. Significant growth opportunity.")
        elif penetration < 60:
            insights.append(f"📊 MODERATE PENETRATION: {penetration}% market presence. Room for expansion.")
        else:
            insights.append(f"✅ STRONG PENETRATION: {penetration}% market coverage achieved.")

        # Regional insights
        if regional:
            best_region = max(regional.items(), key=lambda x: x[1]['penetration_rate'])
            worst_region = min(regional.items(), key=lambda x: x[1]['penetration_rate'])

            insights.append(
                f"🌍 REGIONAL LEADERS: {best_region[0]} shows strongest presence ({best_region[1]['penetration_rate']}%)"
            )

            if worst_region[1]['penetration_rate'] < 20:
                insights.append(
                    f"🎯 EXPANSION OPPORTUNITY: {worst_region[0]} is underrepresented ({worst_region[1]['penetration_rate']}%)"
                )

        # Game popularity insights
        if games:
            top_game = games[0]
            insights.append(
                f"🎮 TOP PERFORMER: '{top_game['game']}' appears in {top_game['appearances']} casinos ({top_game['percentage']}%)"
            )

            # Check for underperforming games
            low_performing = [g for g in games if g['percentage'] < 10]
            if low_performing and len(low_performing) > 3:
                insights.append(
                    f"📉 UNDERPERFORMING GAMES: {len(low_performing)} games appear in <10% of casinos"
                )

        # Coverage quality insights
        strong_coverage = len(coverage.get('strong', []))
        partial_coverage = len(coverage.get('partial', []))

        if strong_coverage > 0:
            insights.append(
                f"💪 STRONG PARTNERS: {strong_coverage} casinos feature 5+ TC games"
            )

        if partial_coverage > strong_coverage:
            insights.append(
                f"📈 UPSELL OPPORTUNITY: {partial_coverage} casinos have partial coverage (1-2 games) - potential for expansion"
            )

        return insights

    def generate_recommendations(self) -> List[Dict]:
        """
        Generate actionable recommendations

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        regional = self.processed_data.get('regional_stats', {})
        risks = self.processed_data.get('risks', {})
        coverage = self.processed_data.get('coverage_quality', {})

        # Priority 1: Fix access issues
        access_issues = risks.get('access_issues', [])
        if access_issues:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Technical',
                'action': 'Resolve Access Issues',
                'description': f'{len(access_issues)} casinos have access problems (blocked/timeout)',
                'impact': 'Immediate revenue loss',
                'next_steps': [
                    'Identify geo-blocking issues',
                    'Contact operators with timeout issues',
                    'Verify game integration status'
                ]
            })

        # Priority 2: Commercial issues
        commercial_issues = risks.get('commercial_issues', [])
        if commercial_issues:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Commercial',
                'action': 'Investigate Missing Games',
                'description': f'{len(commercial_issues)} operators list TC as provider but show no games',
                'impact': 'Brand presence without revenue',
                'next_steps': [
                    'Contact operators to verify game deployment',
                    'Check integration status',
                    'Identify technical barriers'
                ]
            })

        # Priority 3: Expand partial coverage
        partial = coverage.get('partial', [])
        if len(partial) > 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Business Development',
                'action': 'Expand Game Portfolio at Existing Operators',
                'description': f'{len(partial)} operators have only 1-2 TC games',
                'impact': 'Quick revenue increase from existing relationships',
                'next_steps': [
                    'Identify most popular games',
                    'Present portfolio expansion to operators',
                    'Offer promotional support for new games'
                ]
            })

        # Priority 4: Regional expansion
        if regional:
            low_regions = [r for r, d in regional.items() if d['penetration_rate'] < 20]
            if low_regions:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Market Expansion',
                    'action': f'Target Growth in {", ".join(low_regions)}',
                    'description': f'Low penetration in {len(low_regions)} region(s)',
                    'impact': 'New market opportunities',
                    'next_steps': [
                        'Research top operators in target regions',
                        'Identify local partnerships',
                        'Adapt marketing strategy for region'
                    ]
                })

        # Priority 5: Technical issues
        technical_issues = risks.get('technical_issues', [])
        if technical_issues:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Technical',
                'action': 'Improve Game Discoverability',
                'description': f'{len(technical_issues)} cases of games without direct URLs or poor listing',
                'impact': 'Reduced player engagement',
                'next_steps': [
                    'Work with operators on game categorization',
                    'Ensure proper metadata in game feeds',
                    'Verify SEO and search functionality'
                ]
            })

        return recommendations

    def generate_opportunities(self) -> List[Dict]:
        """
        Identify market opportunities

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        coverage = self.processed_data.get('coverage_quality', {})
        country_dist = self.processed_data.get('country_distribution', {})

        # Casinos with no TC presence
        no_coverage = coverage.get('none', [])
        if no_coverage:
            opportunities.append({
                'type': 'New Partnerships',
                'description': f'{len(no_coverage)} casinos scanned have zero Triple Cherry games',
                'potential_value': 'High',
                'action': 'Prioritize business development outreach'
            })

        # Countries with low penetration
        low_pen_countries = {
            country: data for country, data in country_dist.items()
            if data['penetration_rate'] < 30 and data['total'] >= 3
        }

        if low_pen_countries:
            opportunities.append({
                'type': 'Geographic Expansion',
                'description': f'{len(low_pen_countries)} countries with <30% penetration and 3+ casinos',
                'potential_value': 'Medium',
                'action': 'Focus regional marketing and partnership efforts',
                'countries': list(low_pen_countries.keys())
            })

        return opportunities

    def generate_full_report(self) -> Dict:
        """
        Generate complete insights report

        Returns:
            Complete insights dictionary
        """
        logger.info("Generating business insights and recommendations...")

        report = {
            'executive_summary': self.generate_executive_summary(),
            'key_insights': self.generate_key_insights(),
            'recommendations': self.generate_recommendations(),
            'opportunities': self.generate_opportunities(),
            'generated_at': None  # Will be set by caller
        }

        logger.info("Insights generation completed")
        return report
