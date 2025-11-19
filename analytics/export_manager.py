"""
Export Manager - Handles CSV/Excel exports of analytics data
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ExportManager:
    """Manages data exports to CSV and Excel formats"""

    def __init__(self, processed_data: Dict, raw_results: List[Dict]):
        """
        Initialize export manager

        Args:
            processed_data: Processed analytics data
            raw_results: Raw scraping results
        """
        self.processed_data = processed_data
        self.raw_results = raw_results

    def export_operator_list(self, output_path: str) -> str:
        """
        Export full operator list to CSV

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        data = []

        for result in self.raw_results:
            row = {
                'Casino Name': result.get('casino_name', ''),
                'URL': result.get('website_url', ''),
                'Region': result.get('region', ''),
                'Country': result.get('country', ''),
                'Access Status': result.get('access_status', ''),
                'Triple Cherry Found': result.get('tripleCherryFound', ''),
                'Games Count': len(result.get('detected_games', [])),
                'Games List': ', '.join(result.get('detected_games', [])),
                'Provider Listed': 'Yes' if result.get('provider_mention') else 'No',
                'Coverage Category': result.get('coverage_category', ''),
                'Risk Level': result.get('risk_level', ''),
                'Issues': '; '.join(result.get('issues', [])),
                'Scan Date': result.get('scan_timestamp', ''),
            }
            data.append(row)

        df = pd.DataFrame(data)

        os.makedirs(output_path, exist_ok=True)
        filename = f"operator_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_path, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Operator list exported to: {filepath}")

        return filepath

    def export_game_matrix(self, output_path: str) -> str:
        """
        Export game presence matrix to CSV

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        # Get all unique games
        all_games = set()
        for result in self.raw_results:
            all_games.update(result.get('detected_games', []))

        all_games = sorted(list(all_games))

        # Build matrix
        matrix_data = []

        for result in self.raw_results:
            row = {
                'Casino Name': result.get('casino_name', ''),
                'Region': result.get('region', ''),
                'Country': result.get('country', ''),
            }
            detected = result.get('detected_games', [])

            for game in all_games:
                row[game] = 'Yes' if game in detected else 'No'

            row['Total Games'] = len(detected)

            matrix_data.append(row)

        df = pd.DataFrame(matrix_data)

        os.makedirs(output_path, exist_ok=True)
        filename = f"game_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_path, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Game matrix exported to: {filepath}")

        return filepath

    def export_risk_report(self, output_path: str) -> str:
        """
        Export risk analysis to CSV

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        risks = self.processed_data.get('risks', {})
        data = []

        # Access issues
        for item in risks.get('access_issues', []):
            data.append({
                'Risk Category': 'Access Issue',
                'Casino': item['casino'],
                'Issue': item['status'],
                'URL': item['url'],
                'Priority': 'High'
            })

        # Technical issues
        for item in risks.get('technical_issues', []):
            data.append({
                'Risk Category': 'Technical Issue',
                'Casino': item['casino'],
                'Issue': item['issue'],
                'URL': item['url'],
                'Priority': 'Medium'
            })

        # Commercial issues
        for item in risks.get('commercial_issues', []):
            data.append({
                'Risk Category': 'Commercial Issue',
                'Casino': item['casino'],
                'Issue': item['issue'],
                'URL': item['url'],
                'Priority': 'High'
            })

        # High risk casinos
        for item in risks.get('high_risk_casinos', []):
            data.append({
                'Risk Category': 'High Risk Casino',
                'Casino': item['casino'],
                'Issue': '; '.join(item['issues']),
                'URL': item['url'],
                'Priority': 'High'
            })

        df = pd.DataFrame(data)

        os.makedirs(output_path, exist_ok=True)
        filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_path, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Risk report exported to: {filepath}")

        return filepath

    def export_game_popularity(self, output_path: str) -> str:
        """
        Export game popularity rankings to CSV

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        game_pop = self.processed_data.get('game_popularity', [])

        data = []
        for i, game in enumerate(game_pop, 1):
            data.append({
                'Rank': i,
                'Game Name': game['game'],
                'Casino Appearances': game['appearances'],
                'Percentage': f"{game['percentage']}%"
            })

        df = pd.DataFrame(data)

        os.makedirs(output_path, exist_ok=True)
        filename = f"game_popularity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_path, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Game popularity exported to: {filepath}")

        return filepath

    def export_regional_summary(self, output_path: str) -> str:
        """
        Export regional summary to CSV

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        regional = self.processed_data.get('regional_stats', {})

        data = []
        for region, stats in regional.items():
            data.append({
                'Region': region,
                'Total Casinos': stats['total_casinos'],
                'With Triple Cherry': stats['with_triple_cherry'],
                'Penetration Rate': f"{stats['penetration_rate']}%",
                'Total Games Detected': stats['total_games_detected'],
                'Countries': ', '.join(stats['countries'])
            })

        df = pd.DataFrame(data)

        os.makedirs(output_path, exist_ok=True)
        filename = f"regional_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(output_path, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Regional summary exported to: {filepath}")

        return filepath

    def export_to_excel(self, output_path: str) -> str:
        """
        Export all data to a single Excel file with multiple sheets

        Args:
            output_path: Directory to save exports

        Returns:
            Path to exported file
        """
        os.makedirs(output_path, exist_ok=True)
        filename = f"triple_cherry_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_path, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary = self.processed_data.get('summary', {})
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Operator list
            operator_data = []
            for result in self.raw_results:
                operator_data.append({
                    'Casino Name': result.get('casino_name', ''),
                    'URL': result.get('website_url', ''),
                    'Region': result.get('region', ''),
                    'Country': result.get('country', ''),
                    'Status': result.get('access_status', ''),
                    'TC Found': result.get('tripleCherryFound', ''),
                    'Games': len(result.get('detected_games', [])),
                    'Coverage': result.get('coverage_category', ''),
                    'Risk': result.get('risk_level', '')
                })
            pd.DataFrame(operator_data).to_excel(writer, sheet_name='Operators', index=False)

            # Regional summary
            regional = self.processed_data.get('regional_stats', {})
            regional_data = []
            for region, stats in regional.items():
                regional_data.append({
                    'Region': region,
                    'Total Casinos': stats['total_casinos'],
                    'With TC': stats['with_triple_cherry'],
                    'Penetration %': stats['penetration_rate']
                })
            pd.DataFrame(regional_data).to_excel(writer, sheet_name='Regional', index=False)

            # Game popularity
            game_pop = self.processed_data.get('game_popularity', [])
            game_data = [{
                'Rank': i + 1,
                'Game': g['game'],
                'Appearances': g['appearances'],
                'Percentage': g['percentage']
            } for i, g in enumerate(game_pop)]
            pd.DataFrame(game_data).to_excel(writer, sheet_name='Game Popularity', index=False)

            # Risks
            risks = self.processed_data.get('risks', {})
            risk_data = []
            for category, items in risks.items():
                for item in items:
                    if isinstance(item, dict):
                        risk_data.append({
                            'Category': category,
                            'Casino': item.get('casino', ''),
                            'Issue': item.get('issue', item.get('status', '')),
                        })
            if risk_data:
                pd.DataFrame(risk_data).to_excel(writer, sheet_name='Risks', index=False)

        logger.info(f"Excel report exported to: {filepath}")
        return filepath

    def export_all(self, output_path: str) -> Dict[str, str]:
        """
        Export all reports

        Args:
            output_path: Directory to save exports

        Returns:
            Dictionary mapping export types to file paths
        """
        logger.info("Exporting all reports...")

        exports = {
            'operator_list': self.export_operator_list(output_path),
            'game_matrix': self.export_game_matrix(output_path),
            'risk_report': self.export_risk_report(output_path),
            'game_popularity': self.export_game_popularity(output_path),
            'regional_summary': self.export_regional_summary(output_path),
            'excel_workbook': self.export_to_excel(output_path)
        }

        logger.info(f"All exports completed. {len(exports)} files created.")
        return exports
