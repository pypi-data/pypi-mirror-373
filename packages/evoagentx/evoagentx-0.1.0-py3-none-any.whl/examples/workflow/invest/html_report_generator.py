#!/usr/bin/env python3
"""
HTML Report Generator for Stock Analysis
Generates a beautiful neomorphism-style HTML page with optimized content layout.
"""

import os
import re
import json
import base64
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import markdown
from dataclasses import dataclass
import shutil


@dataclass
class ReportSection:
    """Represents a section of the report with its content and metadata."""
    title: str
    content: Dict[str, Any]
    order: int
    visible: bool = True


class MarkdownParser:
    """Parses markdown content and extracts structured data."""
    
    def __init__(self, md_content: str):
        self.md_content = md_content
        self.sections = {}
        self.metadata = {}
        self.parse_content()
    
    def parse_content(self):
        """Parse the markdown content into structured sections."""
        lines = self.md_content.split('\n')
        current_section = None
        current_content = []
        
        # Extract metadata first
        self.metadata = self._extract_metadata(lines)
        
        for line in lines:
            line = line.strip()
            
            # Main section headers (##)
            if line.startswith('## '):
                if current_section:
                    section_data = {
                        'subsections': self._parse_subsections(current_content),
                        'raw_content': '\n'.join(current_content)
                    }
                    # Only add sections with actual content
                    if section_data['subsections']:
                        self.sections[current_section] = section_data
                current_section = line[3:].strip()
                current_content = []
            
            # Subsection headers (###)
            elif line.startswith('### '):
                current_content.append(line)
            
            else:
                current_content.append(line)
        
        # Store the last section
        if current_section:
            section_data = {
                'subsections': self._parse_subsections(current_content),
                'raw_content': '\n'.join(current_content)
            }
            # Only add sections with actual content
            if section_data['subsections']:
                self.sections[current_section] = section_data
    
    def _extract_metadata(self, lines: List[str]) -> Dict[str, str]:
        """Extract metadata from the markdown header."""
        metadata = {}
        
        for line in lines:
            # Extract key-value pairs like **Date**: 2025年07月25日
            if '**' in line and ':' in line:
                match = re.search(r'\*\*([^*]+)\*\*:\s*(.+)', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    metadata[key] = value
        
        return metadata
    
    def _parse_subsections(self, content: List[str]) -> Dict[str, Any]:
        """Parse subsections from content lines."""
        subsections = {}
        current_subsection = None
        current_content = []
        
        for line in content:
            if line.startswith('### '):
                if current_subsection:
                    subsection_data = self._parse_subsection_content(current_content)
                    # Only add subsections with actual content
                    if self._has_content(subsection_data):
                        subsections[current_subsection] = subsection_data
                current_subsection = line[4:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_subsection:
            subsection_data = self._parse_subsection_content(current_content)
            # Only add subsections with actual content
            if self._has_content(subsection_data):
                subsections[current_subsection] = subsection_data
        
        return subsections
    
    def _has_content(self, subsection_data: Dict[str, Any]) -> bool:
        """Check if subsection has meaningful content."""
        tables = subsection_data.get('tables', [])
        lists = subsection_data.get('lists', [])
        text = subsection_data.get('text', [])
        
        # Check for meaningful tables (not empty or header-only)
        meaningful_tables = []
        for table in tables:
            rows = table.get('rows', [])
            if rows and not all(all(cell in ['', '-', 'N/A', '无', '0'] for cell in row) for row in rows):
                meaningful_tables.append(table)
        
        # Check for meaningful lists
        meaningful_lists = [lst for lst in lists if lst and any(item.strip() for item in lst)]
        
        # Check for meaningful text
        meaningful_text = [line for line in text if line.strip() and line.strip() not in ['---', '无', '-']]
        
        return bool(meaningful_tables or meaningful_lists or meaningful_text)
    
    def _parse_subsection_content(self, content: List[str]) -> Dict[str, Any]:
        """Parse subsection content including tables, lists, and text."""
        tables = []
        lists = []
        text_content = []
        
        i = 0
        while i < len(content):
            line = content[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Parse tables
            if '|' in line and line.count('|') >= 2:
                table_data, consumed_lines = self._extract_table(content, i)
                if table_data:
                    tables.append(table_data)
                    i += consumed_lines
                    continue
            
            # Parse lists
            elif line.startswith('- ') or line.startswith('* '):
                list_items, consumed_lines = self._extract_list(content, i)
                if list_items:
                    lists.append(list_items)
                    i += consumed_lines
                    continue
            
            # Regular text
            elif line and not line.startswith('---'):
                text_content.append(line)
            
            i += 1
        
        return {
            'tables': tables,
            'lists': lists,
            'text': text_content
        }
    
    def _extract_table(self, content: List[str], start_idx: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """Extract table data starting from start_idx and return consumed lines count."""
        if start_idx >= len(content):
            return None, 0
        
        table_lines = []
        i = start_idx
        
        # Collect table lines
        while i < len(content) and content[i].strip() and '|' in content[i]:
            table_lines.append(content[i].strip())
            i += 1
        
        if len(table_lines) < 2:
            return None, 1
        
        # Parse headers
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # Find data lines (skip separator line if present)
        data_start_idx = 1
        if len(table_lines) > 1 and all(c in '-|: ' for c in table_lines[1]):
            data_start_idx = 2
        
        # Parse data rows
        rows = []
        for line in table_lines[data_start_idx:]:
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(cells) == len(headers):
                    rows.append(cells)
        
        consumed_lines = len(table_lines)
        
        if headers and rows:
            return {
                'headers': headers,
                'rows': rows
            }, consumed_lines
        
        return None, consumed_lines
    
    def _extract_list(self, content: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Extract list items starting from start_idx and return consumed lines count."""
        items = []
        i = start_idx
        
        while i < len(content):
            line = content[i].strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
                i += 1
            else:
                break
        
        consumed_lines = i - start_idx
        return items, consumed_lines
    
    def get_metadata(self) -> Dict[str, str]:
        """Get extracted metadata."""
        return self.metadata


class HTMLGenerator:
    """Generates the HTML report with neomorphism styling and optimized layout."""
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create assets directory
        self.assets_dir = self.output_path.parent / 'assets'
        self.assets_dir.mkdir(exist_ok=True)
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64字符串"""
        try:
            if not image_path or not os.path.exists(image_path):
                return ""
            
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️ 无法读取图片 {image_path}: {e}")
            return ""
    
    def _get_latest_close_price(self, stock_code: str, timestamp: str) -> str:
        """从股票日线数据CSV文件中读取最新的收盘价"""
        try:
            # 构建CSV文件路径
            csv_path = Path(f"{stock_code}/{timestamp}/data/stock_daily_catl_{timestamp}_{stock_code}.csv")
            
            if not csv_path.exists():
                print(f"⚠️ 股票日线数据文件不存在: {csv_path}")
                return "N/A"
            
            # 读取CSV文件
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 跳过表头，获取最后一行数据
            if len(lines) < 2:
                print(f"⚠️ 股票日线数据文件为空或格式错误: {csv_path}")
                return "N/A"
                
            # 获取最后一行数据（最新的交易日）
            last_line = lines[-1].strip()
            if not last_line:  # 如果最后一行为空，取倒数第二行
                last_line = lines[-2].strip()
                
            # 解析CSV数据：index,date,open,high,low,close,volume,amount,outstanding_share,turnover
            fields = last_line.split(',')
            if len(fields) >= 6:
                close_price = fields[5]  # close价格在第6列（索引5）
                return close_price
            else:
                print(f"⚠️ 股票日线数据格式错误: {last_line}")
                return "N/A"
                
        except Exception as e:
            print(f"⚠️ 读取股票收盘价失败: {e}")
            return "N/A"
    
    def generate_report(self, md_file_path: str, technical_chart_path: str, 
                       price_volume_chart_path: str) -> str:
        """Generate the complete HTML report with base64 encoded images."""
        
        # Read and parse markdown content
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        parser = MarkdownParser(md_content)
        metadata = parser.get_metadata()
        
        # Encode images to base64
        technical_chart_base64 = self.encode_image_to_base64(technical_chart_path)
        price_volume_chart_base64 = self.encode_image_to_base64(price_volume_chart_path)
        
        # Generate HTML content
        html_content = self._generate_html_structure(
            parser, 
            metadata, 
            technical_chart_base64, 
            price_volume_chart_base64
        )
        
        # Write HTML file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(self.output_path)
    
    def _read_news_from_csv(self, stock_code: str, timestamp: str) -> List[Dict[str, str]]:
        """Read news data from CSV file and return the latest 10 entries."""
        try:
            # Construct the CSV file path
            csv_path = Path(f"{stock_code}/{timestamp}/data/stock_news_catl_{timestamp}_{stock_code}.csv")
            
            if not csv_path.exists():
                return []
            
            news_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse datetime and sort by time
                    news_data.append({
                        '新闻标题': row.get('新闻标题', ''),
                        '来源': row.get('文章来源', ''),
                        '发布时间': row.get('发布时间', ''),
                        '影响程度': '中',  # Default value, could be enhanced
                        '解读': row.get('新闻内容', '')[:100] + '...' if len(row.get('新闻内容', '')) > 100 else row.get('新闻内容', ''),
                        '链接': row.get('新闻链接', '')
                    })
            
            # Sort by time (newest first) and return top 10
            news_data.sort(key=lambda x: x['发布时间'], reverse=True)
            return news_data[:10]
            
        except Exception as e:
            print(f"Error reading news CSV: {e}")
            return []
    
    def _read_ratings_from_csv(self, stock_code: str, timestamp: str) -> List[Dict[str, str]]:
        """Read institution rating data from CSV file and return the latest 10 entries."""
        try:
            # Construct the CSV file path
            csv_path = Path(f"{stock_code}/{timestamp}/data/institution_recommendation_catl_{timestamp}_{stock_code}.csv")
            
            if not csv_path.exists():
                return []
            
            ratings_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ratings_data.append({
                        '机构名称': row.get('评级机构', ''),
                        '评级': row.get('最新评级', ''),
                        '目标价': row.get('目标价', '-'),
                        '评级日期': row.get('评级日期', ''),
                        '分析师': row.get('分析师', '不详')
                    })
            
            # Sort by date (newest first) and return top 10
            ratings_data.sort(key=lambda x: x['评级日期'], reverse=True)
            return ratings_data[:10]
            
        except Exception as e:
            print(f"Error reading ratings CSV: {e}")
            return []

    def _generate_fundamentals_section_from_csv(self, metadata: Dict[str, str]) -> str:
        """Generate fundamentals section content directly from CSV files."""
        if not metadata:
            return ""
        
        # Extract stock code and timestamp from metadata
        stock_code = metadata.get('股票代码', '300750')
        # Try to extract timestamp from various possible keys
        timestamp = metadata.get('日期', '')
        if not timestamp:
            # If no date in metadata, try to extract from file names or use current date
            timestamp = datetime.now().strftime('%Y%m%d')
        else:
            # Convert date format like "2025年08月01日" to "20250801"
            import re
            date_match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', timestamp)
            if date_match:
                year, month, day = date_match.groups()
                timestamp = f"{year}{month}{day}"
            else:
                timestamp = datetime.now().strftime('%Y%m%d')
        
        # Read data from CSV files
        news_data = self._read_news_from_csv(stock_code, timestamp)
        ratings_data = self._read_ratings_from_csv(stock_code, timestamp)
        
        # Debug information
        print(f"Debug: Stock code: {stock_code}, Timestamp: {timestamp}")
        print(f"Debug: Found {len(news_data)} news items")
        print(f"Debug: Found {len(ratings_data)} rating items")
        
        # Generate news section
        news_html = ""
        if news_data:
            news_headers = ['新闻标题', '来源', '发布时间', '影响程度', '解读', '链接']
            news_rows = []
            for news in news_data:
                news_rows.append([
                    news['新闻标题'],
                    news['来源'], 
                    news['发布时间'],
                    news['影响程度'],
                    news['解读'],
                    news['链接']
                ])
            
            news_table_data = {'headers': news_headers, 'rows': news_rows}
            news_html = f"""
            <div class="subsection">
                <h3 class="subsection-title"><i class="fas fa-caret-right"></i> 4.1 最新新闻动态</h3>
                <div class="scrollable-table-container">
                    {self._generate_table(news_table_data)}
                </div>
            </div>
            """
        
        # Generate ratings section 
        ratings_html = ""
        if ratings_data:
            ratings_headers = ['机构名称', '评级', '目标价', '评级日期', '分析师']
            ratings_rows = []
            for rating in ratings_data:
                ratings_rows.append([
                    rating['机构名称'],
                    rating['评级'],
                    rating['目标价'],
                    rating['评级日期'],
                    rating['分析师']
                ])
            
            ratings_table_data = {'headers': ratings_headers, 'rows': ratings_rows}
            ratings_html = f"""
            <div class="subsection">
                <h3 class="subsection-title"><i class="fas fa-caret-right"></i> 4.2 机构评级汇总</h3>
                <div class="scrollable-table-container">
                    {self._generate_table(ratings_table_data)}
                </div>
            </div>
            """
        
        return news_html + ratings_html

    def _generate_html_structure(self, parser: MarkdownParser, metadata: Dict[str, str],
                                 technical_chart_base64: str, price_volume_chart_base64: str) -> str:
        """Generate the complete HTML structure with neomorphism design."""
        
        # Get header
        header_html = self._generate_neomorphism_header(metadata, parser.sections)
        
        # Generate charts section
        charts_html = self._generate_charts_section(technical_chart_base64, price_volume_chart_base64)
        
        # Generate dashboard overview
        dashboard_html = self._generate_dashboard_overview(parser.sections, metadata)
        
        # Generate detailed sections
        sections_html = self._generate_detailed_sections(parser.sections, metadata)
        
        # Get footer
        footer_html = self._generate_footer(metadata)
        
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{metadata.get('股票名称', 'Unknown')} ({metadata.get('股票代码', 'Unknown')}) - 投资分析报告</title>
            <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
            <style>
                {self._get_neomorphism_css()}
            </style>
        </head>
        <body>
            <div class="container">
                {header_html}
                {dashboard_html}
                {charts_html}
                {sections_html}
                {footer_html}
            </div>
            
            <script>
                {self._get_javascript()}
            </script>
        </body>
        </html>
        """
    
    def _generate_neomorphism_header(self, metadata: Dict[str, str], sections: Dict[str, Any]) -> str:
        """Generate the neomorphism-style header exactly like the reference image."""
        
        stock_name = metadata.get('股票名称', 'Unknown')
        stock_code = metadata.get('股票代码', 'Unknown')
        
        # Get current data
        now = datetime.now()
        date = now.strftime("%Y年%m月%d日")
        time = now.strftime("%H:%M:%S")
        
        # Extract current price from stock daily data CSV file
        current_price = "N/A"
        
        # Try to get the latest close price from CSV data
        if stock_code != 'Unknown':
            # Extract timestamp from date (convert from "2025年08月14日" to "20250814")
            date_match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date)
            if date_match:
                timestamp = f"{date_match.group(1)}{date_match.group(2)}{date_match.group(3)}"
                current_price = self._get_latest_close_price(stock_code, timestamp)
        
        # Fallback: try to extract from metadata if CSV method failed
        if current_price == "N/A" and '当前持仓' in metadata:
            holding_info = metadata['当前持仓']
            if '平均成本' in holding_info:
                price_match = re.search(r'平均成本\s*(\d+(?:\.\d+)?)', holding_info)
                if price_match:
                    current_price = price_match.group(1)
        
        return f"""
            <div class="main-header">
                <h1 class="main-title">{stock_name}({stock_code})</h1>
                <p class="main-subtitle">新拟态风格投资分析报告</p>
                
                <div class="header-info-cards">
                    <div class="info-card">
                        <div class="info-icon">📅</div>
                        <span>{date}</span>
                    </div>
                    <div class="info-card">
                        <div class="info-icon">🕐</div>
                        <span>{time}</span>
                    </div>
                    <div class="info-card">
                        <div class="info-icon">📊</div>
                        <span>当前价格: ¥{current_price}</span>
                    </div>
                </div>
            </div>
        """
    
    def _generate_dashboard_overview(self, sections: Dict[str, Any], metadata: Dict[str, str]) -> str:
        """Generate a dashboard overview with key metrics extracted from actual report data."""
        
        # 默认值作为后备
        investment_advice = "持有"
        investment_reason = "基于技术分析和基本面评估的专业建议"
        risk_level = "中等"
        confidence_level = "中等"
        target_price = "285"
        stop_price = "270" 
        expected_return = "2%"
        strategy_period = "短期持仓"
        
        # 1. 从"一、交易操作决策"部分提取投资建议和风险级别
        trading_section = sections.get('一、交易操作决策', {})
        if trading_section:
            subsections = trading_section.get('subsections', {})
            
            # 提取核心决策
            core_decision = subsections.get('1.1 核心决策', {})
            if core_decision:
                tables = core_decision.get('tables', [])
                if tables and len(tables) > 0:
                    rows = tables[0].get('rows', [])
                    if rows and len(rows) > 0:
                        row = rows[0]
                        if len(row) >= 4:
                            investment_advice = row[1] if row[1] else investment_advice
                            investment_reason = row[2] if row[2] else investment_reason
                            risk_level = row[3] if row[3] else risk_level
            
            # 提取价格目标
            price_targets = subsections.get('1.3 价格目标', {})
            if price_targets:
                tables = price_targets.get('tables', [])
                if tables and len(tables) > 0:
                    rows = tables[0].get('rows', [])
                    if rows and len(rows) > 0:
                        row = rows[0]
                        if len(row) >= 4:
                            target_price = str(row[1]).replace('RMB', '').replace(' ', '') if row[1] else target_price
                            stop_price = str(row[2]).replace('RMB', '').replace(' ', '') if row[2] else stop_price
                            expected_return = str(row[3]) if row[3] else expected_return
        
        # 2. 从"五、风险评估"部分提取风险信息
        risk_section = sections.get('五、风险评估', {})
        if risk_section:
            subsections = risk_section.get('subsections', {})
            
            # 从风险因素表格中提取总体风险评估
            risk_factors = subsections.get('5.1 风险因素', {})
            if risk_factors:
                tables = risk_factors.get('tables', [])
                if tables and len(tables) > 0:
                    rows = tables[0].get('rows', [])
                    # 计算平均风险级别
                    risk_levels = []
                    for row in rows:
                        if len(row) >= 2 and row[1]:
                            risk_levels.append(row[1])
                    if risk_levels:
                        # 简单的风险级别统计
                        high_count = risk_levels.count('高')
                        mid_count = risk_levels.count('中')
                        low_count = risk_levels.count('低')
                        if high_count > mid_count and high_count > low_count:
                            risk_level = "高"
                        elif mid_count >= high_count and mid_count >= low_count:
                            risk_level = "中等"
                        else:
                            risk_level = "低"
        
        # 3. 从"七、投资建议"部分提取策略信息
        advice_section = sections.get('七、投资建议', {})
        if advice_section:
            subsections = advice_section.get('subsections', {})
            
            # 从短期操作建议中提取信心级别和期间
            short_term = subsections.get('7.1 短期操作建议', {})
            if short_term:
                text_content = short_term.get('text_content', [])
                if text_content:
                    content_text = ' '.join(text_content)
                    # 提取预期收益
                    return_match = re.search(r'预期收益[：:]\s*([0-9.]+%)', content_text)
                    if return_match:
                        expected_return = return_match.group(1)
            
            # 从中长期策略中提取持有周期
            long_term = subsections.get('7.2 中长期策略', {})
            if long_term:
                text_content = long_term.get('text_content', [])
                if text_content:
                    content_text = ' '.join(text_content)
                    # 提取持有周期
                    period_match = re.search(r'持有周期[：:]\s*([^。\n]+)', content_text)
                    if period_match:
                        period = period_match.group(1).strip()
                        if '月' in period or '年' in period:
                            strategy_period = "中长期持仓"
                        else:
                            strategy_period = "短期持仓"
        
        # 根据投资建议确定信心级别
        if investment_advice in ['买入', '强烈买入']:
            confidence_level = "高"
        elif investment_advice in ['卖出', '强烈卖出']:
            confidence_level = "低"
        elif investment_advice in ['部分卖出', '部分买入']:
            confidence_level = "中等"
        else:  # 持有
            confidence_level = "中等"
        
        # 清理价格数据（移除非数字字符）
        target_price = re.sub(r'[^0-9.]', '', str(target_price))
        stop_price = re.sub(r'[^0-9.]', '', str(stop_price))
        
        return f"""
            <div class="analysis-summary">
                <div class="summary-card">
                    <div class="card-icon green">
                        <i class="icon">👍</i>
                    </div>
                    <h3>投资建议</h3>
                    <div class="main-value">{investment_advice}</div>
                    <div class="sub-text">{investment_reason[:50]}{'...' if len(investment_reason) > 50 else ''}</div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon blue">
                        <i class="icon">🎯</i>
                    </div>
                    <h3>价格目标</h3>
                    <div class="price-targets">
                        <div class="price-item">
                            <span class="label">目标价</span>
                            <span class="value">¥{target_price}</span>
                        </div>
                        <div class="price-item">
                            <span class="label">止损价</span>
                            <span class="value">¥{stop_price}</span>
                        </div>
                    </div>
                    <div class="sub-text">预期收益: {expected_return}</div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon orange">
                        <i class="icon">🛡️</i>
                    </div>
                    <h3>风险评估</h3>
                    <div class="risk-levels">
                        <div class="risk-item">
                            <span class="label">风险级别</span>
                            <span class="value">{risk_level}</span>
                        </div>
                        <div class="risk-item">
                            <span class="label">信心级别</span>
                            <span class="value">{confidence_level}</span>
                        </div>
                    </div>
                    <div class="sub-text">{strategy_period}</div>
                </div>
            </div>
        """
    
    def _get_neomorphism_css(self) -> str:
        """Get the enhanced neomorphism CSS styles for the report."""
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: #e0e5ec;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Main Header Styles - Like Reference Image */
        .main-header {
            background: #e0e5ec;
            border-radius: 25px;
            padding: 60px 40px;
            margin-bottom: 30px;
            box-shadow: 20px 20px 60px #bebebe, -20px -20px 60px #ffffff;
            text-align: center;
        }
        
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }
        
        .main-subtitle {
            font-size: 1.2rem;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 40px;
        }
        
        .header-info-cards {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .info-card {
            display: flex;
            align-items: center;
            gap: 10px;
            background: #e0e5ec;
            padding: 15px 25px;
            border-radius: 15px;
            box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 12px 12px 24px #bebebe, -12px -12px 24px #ffffff;
        }
        
        .info-icon {
            font-size: 1.2rem;
        }
        
        .info-card span {
            font-weight: 600;
            color: #2d3748;
            font-size: 0.9rem;
        }
        
        /* Analysis Summary - Like Reference Image */
        .analysis-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: #e0e5ec;
            border-radius: 25px;
            padding: 40px;
            box-shadow: 25px 25px 75px #bebebe, -25px -25px 75px #ffffff;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 30px 30px 90px #bebebe, -30px -30px 90px #ffffff;
        }
        
        .card-icon {
            width: 80px;
            height: 80px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px auto;
            box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
        }
        
        .card-icon.green {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        
        .card-icon.blue {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        }
        
        .card-icon.orange {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }
        
        .card-icon .icon {
            font-size: 2.5rem;
        }
        
        .summary-card h3 {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 20px;
        }
        
        .main-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: #10b981;
            margin-bottom: 15px;
        }
        
        .sub-text {
            font-size: 0.9rem;
            color: #6b7280;
            font-weight: 500;
            line-height: 1.4;
        }
        
        .price-targets, .risk-levels {
            display: flex;
            justify-content: space-around;
            gap: 20px;
            margin: 20px 0;
        }
        
        .price-item, .risk-item {
            background: #e0e5ec;
            padding: 15px 20px;
            border-radius: 15px;
            box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;
            text-align: center;
            flex: 1;
        }
        
        .price-item .label, .risk-item .label {
            font-size: 0.8rem;
            color: #6b7280;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            display: block;
        }
        
        .price-item .value, .risk-item .value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        /* Chart Section Styles - Neomorphism Frames */
        .chart-section {
            background: #e0e5ec;
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 25px 25px 75px #bebebe, -25px -25px 75px #ffffff;
            transition: all 0.3s ease;
        }
        
        .chart-section:hover {
            transform: translateY(-3px);
            box-shadow: 30px 30px 90px #bebebe, -30px -30px 90px #ffffff;
        }
        
        .chart-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(190, 190, 190, 0.2);
        }
        
        .chart-icon {
            font-size: 1.8rem;
        }
        
        .chart-header h3 {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        .chart-container {
            background: #e0e5ec;
            border-radius: 20px;
            padding: 20px;
            box-shadow: inset 10px 10px 20px #bebebe, inset -10px -10px 20px #ffffff;
            text-align: center;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 15px;
            box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
            transition: all 0.3s ease;
        }
        
        .chart-container img:hover {
            transform: scale(1.02);
            box-shadow: 12px 12px 24px #bebebe, -12px -12px 24px #ffffff;
        }
        
        /* Detail Sections */
        .detail-section {
            background: #e0e5ec;
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 20px 20px 40px #bebebe, -20px -20px 40px #ffffff;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(190, 190, 190, 0.2);
        }
        
        .section-icon {
            width: 50px;
            height: 50px;
            border-radius: 15px;
            background: #e0e5ec;
            box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        .section-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #2d3748;
        }
        
        /* Subsections */
        .subsection {
            margin-bottom: 25px;
            padding: 20px;
            background: #e0e5ec;
            border-radius: 15px;
            box-shadow: inset 10px 10px 20px #bebebe, inset -10px -10px 20px #ffffff;
        }
        
        .subsection-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Tables */
        .table-container {
            overflow: hidden;
            border-radius: 15px;
            margin: 20px 0;
            background: #e0e5ec;
            box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            border: none;
        }
        
        .data-table td {
            padding: 15px;
            border-bottom: 1px solid rgba(190, 190, 190, 0.2);
            font-size: 0.9rem;
            color: #2d3748;
            background: #e0e5ec;
        }
        
        .data-table tr:nth-child(even) td {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .data-table tr:hover td {
            background: rgba(102, 126, 234, 0.1);
        }
        
        /* Scrollable table container for news and ratings */
        .scrollable-table-container {
            max-height: 400px;
            overflow-y: auto;
            overflow-x: hidden;
            border-radius: 15px;
            background: #e0e5ec;
            box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff;
            padding: 5px;
            margin: 10px 0;
        }
        
        .scrollable-table-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .scrollable-table-container::-webkit-scrollbar-track {
            background: #e0e5ec;
            border-radius: 4px;
        }
        
        .scrollable-table-container::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 4px;
        }
        
        .scrollable-table-container::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a67d8, #6b46c1);
        }
        
        /* Status badges */
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff;
        }
        
        .status-买入, .status-增持50股, .status-增持50100股 {
            background: #10b981;
            color: white;
        }
        
        .status-卖出 {
            background: #ef4444;
            color: white;
        }
        
        .status-持有 {
            background: #f59e0b;
            color: white;
        }
        
        .risk-高 {
            background: #ef4444;
            color: white;
        }
        
        .risk-中, .risk-中等 {
            background: #f59e0b;
            color: white;
        }
        
        .risk-低 {
            background: #10b981;
            color: white;
        }
        
        /* Links */
        .news-title-link, .news-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .news-title-link:hover, .news-link:hover {
            color: #5a67d8;
            text-decoration: underline;
        }
        
        /* Lists */
        ul {
            margin: 15px 0;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 8px;
            color: #2d3748;
        }
        
        /* Footer */
        .footer {
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 20px;
            margin-top: 30px;
            box-shadow: 20px 20px 40px #bebebe, -20px -20px 40px #ffffff;
        }
        
        .footer-content p {
            margin-bottom: 8px;
            opacity: 0.9;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 20px 10px;
            }
            
            .main-header {
                padding: 40px 20px;
            }
            
            .main-title {
                font-size: 2.2rem;
            }
            
            .header-info-cards {
                flex-direction: column;
                align-items: center;
                gap: 15px;
            }
            
            .info-card {
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }
            
            .analysis-summary {
                grid-template-columns: 1fr;
            }
            
            .price-targets, .risk-levels {
                flex-direction: column;
                gap: 15px;
            }
            
            .chart-section {
                padding: 25px 15px;
            }
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .detail-section, .chart-section, .analysis-summary {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: #e0e5ec;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
            border: 2px solid #e0e5ec;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a67d8, #6b46c1);
        }
        """
    
    def _get_section_icon(self, section_name: str) -> str:
        """Get appropriate icon for section based on name."""
        section_lower = section_name.lower()
        
        if '交易' in section_lower or '决策' in section_lower:
            return '💼'
        elif '市场' in section_lower or '环境' in section_lower:
            return '🌍'
        elif '技术' in section_lower or '分析' in section_lower:
            return '📈'
        elif '基本面' in section_lower or '资讯' in section_lower:
            return '📰'
        elif '风险' in section_lower or '评估' in section_lower:
            return '🛡️'
        elif '历史' in section_lower or '表现' in section_lower:
            return '📊'
        elif '投资' in section_lower or '建议' in section_lower:
            return '💡'
        else:
            return '📄'
    
    def _generate_charts_section(self, technical_chart_base64: str, price_volume_chart_base64: str) -> str:
        """Generate the charts section with neomorphism styling."""
        if not technical_chart_base64 and not price_volume_chart_base64:
            return ""
        
        charts_html = []
        
        if price_volume_chart_base64:
            charts_html.append(f"""
                <div class="chart-section">
                    <div class="chart-header">
                        <div class="chart-icon">📊</div>
                        <h3>K线图技术分析</h3>
                    </div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{price_volume_chart_base64}" alt="K线图分析" />
                    </div>
                </div>
            """)
        
        if technical_chart_base64:
            charts_html.append(f"""
                <div class="chart-section">
                    <div class="chart-header">
                        <div class="chart-icon">📈</div>
                        <h3>技术指标综合分析</h3>
                    </div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{technical_chart_base64}" alt="技术指标分析" />
                    </div>
                </div>
            """)
        
        return ''.join(charts_html)
    
    def _generate_detailed_sections(self, sections, metadata: Dict[str, str] = None) -> str:
        """Generate detailed analysis sections with optimized layout."""
        sections_html = []
        
        # Priority order for sections
        section_order = [
            '1. 交易操作决策',
            '2. 市场环境分析', 
            '3. 技术分析',
            '4. 基本面分析（资讯动向）',
            '5. 风险评估',
            '6. 历史表现回顾',
            '7. 投资建议'
        ]
        
        # Generate sections in priority order
        for section_key in section_order:
            if section_key in sections:
                section_data = sections[section_key]
                section_name = section_key.split('. ', 1)[1] if '. ' in section_key else section_key
                
                # Special handling for 基本面分析 section - use CSV data
                if '基本面分析' in section_name:
                    section_content = self._generate_fundamentals_section_from_csv(metadata)
                else:
                    section_content = self._generate_section_content(section_data)
                
                section_html = f"""
                    <div class="detail-section">
                        <div class="section-header">
                            <div class="section-icon">{self._get_section_icon(section_name)}</div>
                            <h2 class="section-title">{section_name}</h2>
                        </div>
                        <div class="section-content">
                            {section_content}
                        </div>
                    </div>
                """
                sections_html.append(section_html)
        
        # Add any remaining sections not in the priority list
        for section_key, section_data in sections.items():
            if section_key not in section_order:
                section_name = section_key.split('. ', 1)[1] if '. ' in section_key else section_key
                
                # Special handling for 基本面分析 section - use CSV data
                if '基本面分析' in section_name:
                    section_content = self._generate_fundamentals_section_from_csv(metadata)
                else:
                    section_content = self._generate_section_content(section_data)
                
                section_html = f"""
                    <div class="detail-section">
                        <div class="section-header">
                            <div class="section-icon">{self._get_section_icon(section_name)}</div>
                            <h2 class="section-title">{section_name}</h2>
                        </div>
                        <div class="section-content">
                            {section_content}
                        </div>
                    </div>
                """
                sections_html.append(section_html)
        
        return ''.join(sections_html)
    

    
    def _generate_subsection(self, subsection_name: str, subsection_data: Dict[str, Any]) -> str:
        """Generate a single subsection."""
        content_parts = []
        
        # Add tables
        for table in subsection_data.get('tables', []):
            content_parts.append(self._generate_table(table))
        
        # Add lists
        for list_items in subsection_data.get('lists', []):
            content_parts.append(self._generate_list(list_items))
        
        # Add text content
        if subsection_data.get('text'):
            content_parts.append(self._generate_text_content(subsection_data['text']))
        
        return f"""
        <div class="subsection">
            <h3 class="subsection-title"><i class="fas fa-caret-right"></i> {subsection_name}</h3>
            {''.join(content_parts)}
        </div>
        """
    
    def _generate_table(self, table_data: Dict[str, Any]) -> str:
        """Generate HTML table from table data."""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers:
            return ""
        
        # Check if this is a news table (has news-related headers)
        is_news_table = any(keyword in ' '.join(headers).lower() for keyword in ['新闻', 'news', '标题', 'title'])
        has_link_column = any(keyword in ' '.join(headers).lower() for keyword in ['链接', 'url', 'link'])
        
        header_html = '<tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr>'
        
        rows_html = []
        for row in rows:
            cells_html = []
            for i, cell in enumerate(row):
                header_name = headers[i].lower()
                
                # Apply special styling for certain columns
                if any(keyword in header_name for keyword in ['决策', '操作建议', '决策类型']):
                    # Clean up cell content for CSS class
                    cell_class = cell.replace(' ', '').replace('-', '').replace('股', '')
                    cells_html.append(f'<td><span class="status-badge status-{cell_class}">{cell}</span></td>')
                elif any(keyword in header_name for keyword in ['风险等级', '等级', '风险级别']):
                    cells_html.append(f'<td><span class="status-badge risk-{cell}">{cell}</span></td>')
                # Handle news title links
                elif is_news_table and has_link_column and any(keyword in header_name for keyword in ['新闻标题', '标题', 'title']):
                    # Find the corresponding link in the same row
                    link_index = None
                    for j, header in enumerate(headers):
                        if any(keyword in header.lower() for keyword in ['链接', 'url', 'link']):
                            link_index = j
                            break
                    
                    if link_index is not None and link_index < len(row):
                        link_url = row[link_index]
                        if link_url and link_url.lower() not in ['n/a', '-', 'na', ''] and ('http://' in link_url.lower() or 'https://' in link_url.lower()):
                            cells_html.append(f'<td><a href="{link_url}" target="_blank" class="news-title-link">{cell}</a></td>')
                        else:
                            cells_html.append(f'<td>{cell}</td>')
                    else:
                        cells_html.append(f'<td>{cell}</td>')
                # Handle link columns
                elif any(keyword in header_name for keyword in ['链接', 'url', 'link']):
                    if cell and cell.lower() not in ['n/a', '-', 'na', ''] and ('http://' in cell.lower() or 'https://' in cell.lower()):
                        cells_html.append(f'<td><a href="{cell}" target="_blank" class="news-link">{cell}</a></td>')
                    else:
                        cells_html.append(f'<td>{cell}</td>')
                else:
                    cells_html.append(f'<td>{cell}</td>')
            rows_html.append('<tr>' + ''.join(cells_html) + '</tr>')
        
        return f"""
        <div class="table-container">
            <table class="data-table">
                <thead>{header_html}</thead>
                <tbody>{''.join(rows_html)}</tbody>
            </table>
        </div>
        """
    
    def _generate_list(self, list_items: List[str]) -> str:
        """Generate HTML list from list items."""
        items_html = ''.join(f'<li>{item}</li>' for item in list_items)
        return f'<ul style="margin: 1rem 0; padding-left: 2rem;">{items_html}</ul>'
    
    def _generate_text_content(self, text_lines: List[str]) -> str:
        """Generate HTML from text content."""
        # Filter out empty lines and markdown formatting
        filtered_lines = []
        for line in text_lines:
            if line and not line.startswith('---'):
                # Convert markdown formatting
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
                filtered_lines.append(line)
        
        if not filtered_lines:
            return ""
        
        return f'<div style="margin: 1rem 0; line-height: 1.6;">{"<br>".join(filtered_lines)}</div>'
    
    def _generate_section_content(self, section_data: Dict[str, Any]) -> str:
        """Generate content for a report section with subsections."""
        content_html = []
        
        # Get subsections from the section data
        subsections = section_data.get('subsections', {})
        
        # Generate subsections
        for subsection_name, subsection_data in subsections.items():
            content_html.append(self._generate_subsection(subsection_name, subsection_data))
        
        return ''.join(content_html)
    
    def _generate_charts_section(self, technical_chart_base64: str, price_volume_chart_base64: str) -> str:
        """Generate the enhanced charts section exactly like reference report."""
        charts_html = []
        
        # K线图分析 (参考报告的顺序)
        if price_volume_chart_base64:
            charts_html.append(f"""
        <div class="chart-section">
            <h2 class="section-title">
                <div class="section-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                K线图技术分析
            </h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{price_volume_chart_base64}" alt="K线图分析" />
            </div>
        </div>
            """)
        
        # 技术指标分析
        if technical_chart_base64:
            charts_html.append(f"""
        <div class="chart-section">
            <h2 class="section-title">
                <div class="section-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                技术指标综合分析
            </h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{technical_chart_base64}" alt="技术指标分析" />
            </div>
        </div>
            """)
        
        return ''.join(charts_html)
    
    def _generate_footer(self, metadata: Dict[str, str]) -> str:
        """Generate the footer section."""
        return f"""
        <footer class="footer">
            <div class="footer-content">
                <p>报告生成时间: {metadata.get('报告生成时间', 'Unknown')}</p>
                <p>数据来源: 股票市场数据、经济新闻、行业分析报告</p>
                <p><strong>免责声明:</strong> 本报告仅供个人投资参考，不构成投资建议</p>
            </div>
        </footer>
        """
    
    def _get_javascript(self) -> str:
        """Get the JavaScript for interactivity."""
        return """
        // Intersection Observer for smooth animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            // Observe all sections for animations
            const sections = document.querySelectorAll('.detail-section, .chart-section, .analysis-summary');
            sections.forEach(section => {
                observer.observe(section);
            });
            
            // Add hover effects to tables
            const tables = document.querySelectorAll('.data-table');
            tables.forEach(table => {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    row.addEventListener('mouseenter', () => {
                        row.style.transform = 'scale(1.01)';
                        row.style.transition = 'transform 0.2s ease';
                    });
                    row.addEventListener('mouseleave', () => {
                        row.style.transform = 'scale(1)';
                    });
                });
            });
            
            // Add smooth hover effects to cards
            const cards = document.querySelectorAll('.info-card, .summary-card');
            cards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    card.style.transition = 'all 0.3s ease';
                });
            });
        });
        """


def main():
    """Main function to run the HTML report generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HTML stock analysis report')
    parser.add_argument('output_path', help='Path for the generated HTML file')
    parser.add_argument('md_file', help='Path to the markdown file')
    parser.add_argument('technical_chart', help='Path to technical analysis chart')
    parser.add_argument('price_volume_chart', help='Path to price/volume chart')
    
    args = parser.parse_args()
    
    generator = HTMLGenerator(args.output_path)
    output_file = generator.generate_report(args.md_file, args.technical_chart, args.price_volume_chart)
    
    print(f"HTML report generated successfully: {output_file}")


if __name__ == "__main__":
    main() 