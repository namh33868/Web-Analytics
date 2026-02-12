# gui/charts.py - VERSION ULTRA STABLE (NO CSS SELECTORS)
import pandas as pd
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


def create_simple_charts(df: pd.DataFrame):
    """Tạo 2 biểu đồ PNG đơn giản dưới dạng Base64."""
    charts_b64 = []

    # Chart 1: Word Count Bar (Top 5)
    plt.figure(figsize=(10, 4))
    top5 = df.nlargest(5, 'word_count')
    plt.barh(range(len(top5)), top5['word_count'], color='#3498db')
    plt.yticks(range(len(top5)), [url[:20] + '...' for url in top5['url']])
    plt.xlabel('Word Count')
    plt.title('Top 5 Pages by Content')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts_b64.append(base64.b64encode(buf.read()).decode())
    plt.close()

    # Chart 2: Link Pie
    plt.figure(figsize=(8, 6))
    labels = ['Internal', 'External']
    sizes = [df['internal_links'].sum(), df['external_links'].sum()]
    colors = ['#2ecc71', '#e74c3c']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Link Distribution')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    charts_b64.append(base64.b64encode(buf.read()).decode())
    plt.close()

    return charts_b64


class ChartGenerator:
    @staticmethod
    def create_dashboard_charts(df: pd.DataFrame) -> str:
        """
        Dashboard HTML PURE - KHÔNG CSS *, KHÔNG JS, 100% STABLE
        """
        if len(df) == 0:
            return """
            <html><body style="font-family:Arial; padding:40px; text-align:center; background:#f0f0f0;">
                <h2 style="color:#666;">📊 No Data Yet</h2>
                <p>Scrape some URLs first!</p>
            </body></html>
            """
        
        # Tạo HTML table đơn giản + stats
        total_pages = len(df)
        avg_words = int(df['word_count'].mean())
        total_internal = int(df['internal_links'].sum())
        total_external = int(df['external_links'].sum())
        
        # Top 10 table
        top10_html = ""
        for _, row in df.nlargest(10, 'word_count').iterrows():
            top10_html += f"""
            <tr style="border-bottom:1px solid #ddd;">
                <td style="padding:10px; max-width:250px; overflow:hidden;">{row['url'][:40]}...</td>
                <td style="padding:10px; text-align:right; font-weight:bold;">{int(row['word_count']):,}</td>
                <td style="padding:10px; text-align:right;">{int(row['img_count'])}</td>
            </tr>
            """

        # Tạo 2 biểu đồ PNG đơn giản
        chart1_b64, chart2_b64 = create_simple_charts(df)
        chart_html = f"""
        <!-- Charts Section -->
        <div style="display:flex; gap:20px; margin-bottom:30px; flex-wrap:wrap;">
            <div style="flex:1; min-width:320px; background:#fff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="margin-top:0;">📊 Top Content</h3>
                <img src="data:image/png;base64,{chart1_b64}" style="width:100%; max-height:320px; border-radius:8px; object-fit:contain;">
            </div>
            <div style="flex:1; min-width:320px; background:#fff; padding:20px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h3 style="margin-top:0;">🔗 Link Distribution</h3>
                <img src="data:image/png;base64,{chart2_b64}" style="width:100%; max-height:320px; border-radius:8px; object-fit:contain;">
            </div>
        </div>
        """
        
        html = f"""
<html>
<head><title>Web Analytics</title></head>
<body style="font-family:Arial,sans-serif; margin:0; padding:20px; background:#f8f9fa;">
    <div style="max-width:1200px; margin:0 auto;">
        <!-- Header -->
        <div style="text-align:center; background:#fff; padding:30px; border-radius:12px; margin-bottom:30px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <h1 style="margin:0; color:#2c3e50; font-size:2.2em;">🌐 Web Analytics Dashboard</h1>
            <p style="margin:10px 0 0 0; color:#7f8c8d; font-size:1.1em;">
                Analyzed <strong>{total_pages}</strong> pages | {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
        </div>
        
        <!-- Stats Row -->
        <div style="display:flex; gap:20px; margin-bottom:30px; flex-wrap:wrap;">
            <div style="flex:1; min-width:220px; background:#e8f5e8; padding:25px; border-radius:12px; text-align:center;">
                <div style="font-size:2.5em; color:#27ae60; font-weight:bold;">{total_pages}</div>
                <div style="color:#229954; font-size:1em;">Total Pages</div>
            </div>
            <div style="flex:1; min-width:220px; background:#ebf3fd; padding:25px; border-radius:12px; text-align:center;">
                <div style="font-size:2.5em; color:#3498db; font-weight:bold;">{avg_words:,}</div>
                <div style="color:#2980b9; font-size:1em;">Avg Words/Page</div>
            </div>
            <div style="flex:1; min-width:220px; background:#fdf2e8; padding:25px; border-radius:12px; text-align:center;">
                <div style="font-size:2.5em; color:#f39c12; font-weight:bold;">{total_internal:,}</div>
                <div style="color:#e67e22; font-size:1em;">Internal Links</div>
            </div>
            <div style="flex:1; min-width:220px; background:#fce4ec; padding:25px; border-radius:12px; text-align:center;">
                <div style="font-size:2.5em; color:#e74c3c; font-weight:bold;">{total_external:,}</div>
                <div style="color:#c0392b; font-size:1em;">External Links</div>
            </div>
        </div>
        
        <!-- Top 10 Table -->
        <div style="background:#fff; padding:30px; border-radius:12px; margin-bottom:30px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color:#2c3e50; font-size:1.4em;">📈 Top 10 Pages by Word Count</h3>
            <table style="width:100%; border-collapse:collapse; font-size:14px;">
                <thead>
                    <tr style="background:#ecf0f1;">
                        <th style="padding:15px; text-align:left; border-bottom:3px solid #bdc3c7; font-weight:600;">URL</th>
                        <th style="padding:15px; text-align:right; border-bottom:3px solid #bdc3c7; font-weight:600;">Words</th>
                        <th style="padding:15px; text-align:right; border-bottom:3px solid #bdc3c7; font-weight:600;">Images</th>
                    </tr>
                </thead>
                <tbody>
                    {top10_html}
                </tbody>
            </table>
        </div>

        {chart_html}
        
        <!-- Summary Metrics -->
        <div style="background:#fff; padding:30px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color:#2c3e50;">📊 Key Metrics</h3>
            <div style="display:flex; gap:30px; flex-wrap:wrap; font-size:15px;">
                <div><strong>Total Words:</strong> {int(df['word_count'].sum()):,}</div>
                <div><strong>Total Images:</strong> {int(df['img_count'].sum())}</div>
                <div><strong>Avg Images/Page:</strong> {df['img_count'].mean():.1f}</div>
                <div><strong>Link Ratio:</strong> {total_internal}:{total_external}</div>
                <div><strong>Latest Crawl:</strong> {df['crawl_time'].max()}</div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html
