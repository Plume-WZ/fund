# -*- coding: UTF-8 -*-
import html
import json
import re


# 歌词轮播常量
LYRICS = [
    '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
    '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
    '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
    '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
]


def get_lyrics_carousel_script():
    """生成歌词轮播JavaScript代码"""
    lyrics_json = json.dumps(LYRICS, ensure_ascii=False)
    return f'''
        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = {lyrics_json};
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}
        }});
    '''


def enhance_fund_tab_content(content, shares_map=None):
    """
    Enhance the fund tab content with operations panel, file operations, and shares input.
    Args:
        content: HTML content to enhance
        shares_map: Dict mapping fund_code -> shares value (optional)
    """
    file_operations = """
        <div class="file-operations" style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <button class="btn btn-secondary" onclick="downloadFundMap()" style="padding: 8px 16px;">📥 导出基金列表</button>
            <input type="file" id="uploadFile" accept=".json" style="display:none" onchange="uploadFundMap(this.files[0])">
            <button class="btn btn-secondary" onclick="document.getElementById('uploadFile').click()" style="padding: 8px 16px;">📤 导入基金列表</button>
            <span style="color: #f59e0b; font-size: 13px; margin-left: 10px;">
                <span style="color: #f59e0b;">⚠️</span> 导入/导出为覆盖性操作，直接应用最新配置（非累加）
            </span>
        </div>
    """

    position_summary = """
        <div id="positionSummary" class="position-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: var(--text-main); display: flex; justify-content: space-between; align-items: center;">
                💰 持仓统计
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button id="showoffBtn" onclick="openShowoffCard()"
                            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                   border: none; border-radius: 20px; padding: 6px 16px;
                                   color: white; font-size: 14px; font-weight: 600;
                                   cursor: pointer; display: flex; align-items: center; gap: 6px;
                                   box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                                   transition: all 0.3s ease; white-space: nowrap;">
                        ✨ 一键炫耀
                    </button>
                    <span id="toggleSensitiveValues" style="cursor: pointer; font-size: 18px; user-select: none;" title="显示 / 隐藏 收益明细">😀</span>
                </div>
            </h3>
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">总持仓金额</div>
                    <div id="totalValue" class="sensitive-value" style="font-size: 24px; font-weight: bold; color: var(--text-main); text-align: center;">
                        <span class="real-value">¥0.00</span><span class="hidden-value">****</span>
                    </div>
                </div>
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">今日预估涨跌</div>
                    <div id="estimatedGain" style="font-size: 24px; font-weight: bold; white-space: nowrap; color: var(--text-main); text-align: center;">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="estimatedGainPct"> (+0.00%)</span>
                    </div>
                </div>
                <div class="stat-item" style="text-align: center;">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">今日实际涨跌(已结算部分)</div>
                    <div id="actualGain" style="font-size: 24px; font-weight: bold; white-space: nowrap; color: var(--text-main); text-align: center;">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="actualGainPct"> (+0.00%)</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="fundDetailsSummary" class="fund-details-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: var(--text-main);">📊 持仓基金涨跌明细</h3>
            <div style="overflow-x: auto;">
                <table id="fundDetailsTable" style="width: 100%; min-width: 700px; border-collapse: collapse; font-size: 13px; table-layout: auto; white-space: nowrap;">
                    <thead>
                        <tr style="background: rgba(59, 130, 246, 0.1);">
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金代码</th>
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金名称</th>
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">持仓份额</th>
                            <th style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500;">操作</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 4)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">持仓市值</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 5)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 6)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估涨跌</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 7)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 8)" style="padding: 10px; text-align: center; white-space: nowrap; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际涨跌</th>
                        </tr>
                    </thead>
                    <tbody id="fundDetailsTableBody">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 炫耀卡片模态框 -->
        <div id="showoffModal" class="showoff-modal" onclick="closeShowoffCard(event)">
            <div class="showoff-card" onclick="event.stopPropagation()">
                <!-- 关闭按钮 -->
                <button class="showoff-close" onclick="closeShowoffCard()">✕</button>

                <!-- 左上角品牌标识 -->
                <div class="showoff-brand-corner">
                    <img src="/static/1.ico" alt="Lan Fund" class="brand-logo" onerror="this.style.display='none'">
                    <span class="brand-name">Lan Fund</span>
                </div>

                <!-- 卡片背景装饰 -->
                <div class="showoff-bg-decoration">
                    <div class="bg-circle circle-1"></div>
                    <div class="bg-circle circle-2"></div>
                    <div class="bg-circle circle-3"></div>
                    <div class="bg-stars"></div>
                </div>

                <!-- 卡片头部 -->
                <div class="showoff-header">
                    <div class="showoff-icon">💰</div>
                    <h2 class="showoff-title">今日收益</h2>
                    <p class="showoff-date" id="showoffDate">2026-02-03</p>
                </div>

                <!-- 持仓统计摘要 -->
                <div class="showoff-summary">
                    <div class="summary-row summary-row-total">
                        <div class="summary-item">
                            <div class="summary-label">总持仓</div>
                            <div class="summary-value" id="showoffTotalValue">¥0.00</div>
                        </div>
                    </div>
                    <div class="summary-row">
                        <div class="summary-item">
                            <div class="summary-label">今日预估</div>
                            <div class="summary-value" id="showoffEstimatedGain">+¥0.00</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">今日实际</div>
                            <div class="summary-value" id="showoffActualGain">+¥0.00</div>
                        </div>
                    </div>
                </div>

                <!-- Top3基金明细 -->
                <div class="showoff-funds">
                    <div class="funds-header">
                        <span class="funds-title">🏆 收益Top3</span>
                    </div>
                    <div class="funds-list" id="showoffFundsList">
                        <!-- 动态生成 -->
                    </div>
                </div>
            </div>
        </div>
    """

    operations_panel = """
        <div class="fund-operations">
            <div class="operation-group">
                <button class="btn btn-success" onclick="openFundSelectionModal('hold')">⭐ 添加标记</button>
                <button class="btn btn-secondary" onclick="openFundSelectionModal('unhold')">☆ 删除标记</button>
                <button class="btn btn-info" onclick="openFundSelectionModal('sector')">🏷️ 标注板块</button>
                <button class="btn btn-warning" onclick="openFundSelectionModal('unsector')">🏷️ 删除板块</button>
                <button class="btn btn-danger" onclick="openFundSelectionModal('delete')">🗑️ 删除基金</button>
                <label class="filter-hold-label" style="margin-left: 15px; display: flex; align-items: center; cursor: pointer; white-space: nowrap;">
                    <input type="checkbox" id="filterHeldOnly" onchange="filterHeldFunds()" style="margin-right: 5px; width: 16px; height: 16px; cursor: pointer;">
                    <span style="font-size: 14px; color: var(--text-main);">仅展示标记基金</span>
                </label>
            </div>
        </div>
    """

    add_fund_area = """
        <div class="add-fund-input">
            <input type="text" id="fundCodesInput" placeholder="输入基金代码（逗号分隔，如：016858,007872）">
            <button class="btn btn-primary" onclick="addFunds()">添加</button>
        </div>
    """

    content = re.sub(r'(<th[^>]*>近30天</th>)',
                     r'\1\n                    <th>持仓份额</th>',
                     content, count=1)

    def add_shares_to_row(match):
        row_content = match.group(0)
        code_match = re.search(r'<td[^>]*>(\d{6})</td>', row_content)
        if code_match:
            fund_code = code_match.group(1)

            shares = 0
            if shares_map and fund_code in shares_map:
                try:
                    shares = float(shares_map[fund_code])
                except (ValueError, TypeError):
                    shares = 0

            if shares > 0:
                button_text = '修改'
                button_color = '#10b981'
            else:
                button_text = '设置'
                button_color = '#3b82f6'

            row_with_shares = row_content[:-5] + f'''<td>
                <button class="shares-button" id="sharesBtn_{fund_code}"
                        onclick="openSharesModal('{fund_code}')"
                        style="padding: 6px 12px; background: {button_color}; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s;">
                    {button_text}
                </button>
            </td></tr>'''
            return row_with_shares
        return row_content

    content = re.sub(r'<tr>.*?</tr>', add_shares_to_row, content, flags=re.DOTALL)

    return file_operations + position_summary + operations_panel + add_fund_area + content


def get_table_html(title, data, sortable_columns=None):
    """
    生成单个表格的HTML代码。
    :param title: list, 表头标题列表。
    :param data: list of lists, 表格数据。
    :param sortable_columns: list, 可排序的列的索引 (从0开始)。例如 [1, 2, 3]
    """
    if sortable_columns is None:
        sortable_columns = []

    ths = []
    for i, col_name in enumerate(title):
        if i in sortable_columns:
            ths.append(f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">{col_name}</th>')
        else:
            ths.append(f"<th>{col_name}</th>")

    thead_html = f"""
    <thead>
        <tr>
            {''.join(ths)}
        </tr>
    </thead>
    """

    tbody_rows = []
    for row_data in data:
        tds = [f"<td>{x}</td>" for x in row_data]
        tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

    tbody_html = f"""
    <tbody>
        {''.join(tbody_rows)}
    </tbody>
    """

    return f"""
    <div class="table-container">
        <table class="style-table">
            {thead_html}
            {tbody_html}
        </table>
    </div>
    """


def generate_fund_row_html(fund_code, fund_data, is_held=True):
    """Generate a single fund row (replaces holdings cards)"""
    name = fund_data.get('fund_name', '')
    sectors = fund_data.get('sectors', [])
    shares = fund_data.get('shares', 0)

    safe_code = html.escape(str(fund_code))
    safe_name = html.escape(str(name))

    sector_tags = ''
    if is_held:
        sector_tags += '<span class="tag tag-hold">⭐ 持有</span>'
    if sectors:
        safe_sectors = html.escape(', '.join(str(s) for s in sectors))
        sector_tags += f'<span style="color: #8b949e; font-size: 12px;"> 🏷️ {safe_sectors}</span>'

    shares_html = ''
    if is_held:
        shares_html = f'''<div class="metric metric-shares">
        <span class="metric-label">持仓份额</span>
        <input type="number" class="shares-input" id="shares_{safe_code}"
               value="{shares}" step="0.01" min="0"
               onchange="updateShares('{safe_code}', this.value)">
      </div>'''

    return f'''<div class="fund-row" data-code="{safe_code}">
  <div class="fund-row-main">
    <div class="fund-info">
      <div class="fund-code-name">
        <span class="fund-code">{safe_code}</span>
        <span class="fund-name">{safe_name}</span>
      </div>
      <div class="fund-tags">{sector_tags}</div>
    </div>
    <div class="fund-metrics" id="metrics_{safe_code}">
      <!-- Metrics populated by JavaScript -->
      <div class="metric"><span class="metric-label">净值</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">估值增长</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">日涨幅</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">连涨/跌</span><span class="metric-value">--</span></div>
      <div class="metric"><span class="metric-label">近30天</span><span class="metric-value">--</span></div>
      {shares_html}
    </div>
  </div>
  <div class="fund-row-actions">
    <button class="btn-icon" onclick="toggleFundExpand('{safe_code}')" title="展开/收起">
      <span>▼</span>
    </button>
  </div>
</div>'''


def get_css_style():
    return r"""
    <style>
        :root {
            /* Professional Trading Terminal Theme */
            --terminal-bg: #0b0e14;
            --card-bg: #151921;
            --border: #2d343f;
            --accent: #3b82f6;
            --text-main: #f1f5f9;
            --text-dim: #94a3b8;
            --text-muted: #64748b;
            --up: #ef4444;    /* 专业红 */
            --down: #10b981;  /* 专业绿 */
            --font-mono: 'JetBrains Mono', 'Courier New', Consolas, monospace;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-family);
            background-color: var(--terminal-bg);
            color: var(--text-main);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
        }

        /* ==================== TERMINAL DASHBOARD (资产看板) ==================== */
        .terminal-dashboard {
            display: grid;
            grid-template-columns: 1.5fr 1fr 1fr;
            gap: 20px;
            background: var(--card-bg);
            padding: 24px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
        }

        .stat-group label {
            color: var(--text-dim);
            font-size: 13px;
            display: block;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .stat-group .big-num {
            font-family: var(--font-mono);
            font-size: 32px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 6px;
        }

        .stat-group .big-num.up {
            color: var(--up);
        }

        .stat-group .big-num.down {
            color: var(--down);
        }

        .stat-group .stat-change {
            font-size: 14px;
            font-family: var(--font-mono);
            color: var(--text-dim);
        }

        .stat-group .stat-change.up {
            color: var(--up);
        }

        .stat-group .stat-change.down {
            color: var(--down);
        }

        /* ==================== FUND GLASS CARDS (基金玻璃态卡片) ==================== */
        .holdings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .fund-glass-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 10px;
            transition: all 0.2s ease;
            position: relative;
        }

        .fund-glass-card:hover {
            border-color: var(--accent);
            background: #1c222d;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .card-title {
            font-weight: 600;
            font-size: 15px;
            color: var(--text-main);
            margin-bottom: 4px;
        }

        .card-code {
            color: var(--text-dim);
            font-family: var(--font-mono);
            font-size: 12px;
        }

        .card-code .tag {
            display: inline-block;
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 6px;
        }

        .card-badge {
            font-size: 20px;
            line-height: 1;
        }

        .card-main-data {
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin: 10px 0;
        }

        .est-pct {
            font-family: var(--font-mono);
            font-size: 24px;
            font-weight: 700;
        }

        .est-pct.up {
            color: var(--up);
        }

        .est-pct.down {
            color: var(--down);
        }

        .card-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-top: 1px solid var(--border);
            padding-top: 12px;
            gap: 8px;
        }

        .detail-item {
            font-size: 12px;
            color: var(--text-dim);
        }

        .detail-item b {
            color: var(--text-main);
            font-family: var(--font-mono);
            display: block;
            font-size: 14px;
            margin-top: 4px;
        }

        .detail-item b.up {
            color: var(--up);
        }

        .detail-item b.down {
            color: var(--down);
        }

        /* Navbar */
        .navbar {
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }

        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--accent), var(--down));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }

        .navbar-logo {
            width: 32px;
            height: 32px;
            margin-right: 0;
            vertical-align: middle;
            border-radius: 6px;
            object-fit: contain;
        }

        .navbar-quote {
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
        }

        .navbar-menu {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .navbar-item {
            font-weight: 500;
            font-size: 0.9rem;
        }

        /* Layout */
        .app-container {
            display: flex;
            min-height: calc(100vh - 60px); /* Subtract navbar height */
            overflow: hidden; /* Prevent body scroll */
        }

        .tabs-header {
            display: flex;
            border-bottom: 2px solid var(--border);
            margin-bottom: 1rem;
            background: var(--card-bg);
            padding: 0 1rem;
        }

        .tab-button {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            text-align: center;
            position: relative;
            transition: all 0.2s;
            color: var(--text-dim);
            font-size: 0.9rem;
            border-bottom: 2px solid transparent;
        }

        .tab-button:hover {
            color: var(--text-main);
            background-color: var(--card-bg);
        }

        .tab-button.active {
            color: var(--text-main);
            border-bottom: 2px solid var(--accent);
        }

        .tab-content {
            display: none;
            padding: 1rem 0;
            animation: fadeIn 0.2s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dashboard-grid {
            display: flex;
            flex-direction: column;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            padding-bottom: 40px;
        }

        .main-content {
            padding: 2rem;
            flex: 1;
            margin: 0;
            overflow-y: auto;
            height: calc(100vh - 60px);
            background-color: var(--terminal-bg);
        }

        /* Tables */
        .table-container {
            background: var(--card-bg);
            border: 1px solid var(--border);
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 1rem;
            border-radius: 12px;
        }

        .style-table {
            width: 100%;
            min-width: max-content;
            border-collapse: collapse;
            font-size: 0.9rem;
            white-space: nowrap;
        }

        .style-table th {
            text-align: center;
            padding: 12px 16px;
            background-color: var(--card-bg);
            font-weight: 600;
            color: var(--text-main);
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
            letter-spacing: 0.01em;
        }

        .style-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            font-weight: 400;
            text-align: center;
            white-space: nowrap;
        }

        .style-table tbody tr:hover {
            background-color: var(--card-bg);
        }

        /* 最后一行的下划线加粗 */
        .style-table tbody tr:last-child td {
            border-bottom: 1px solid var(--border);
        }

        /* Sortable Headers */
        .style-table th.sortable {
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }

        .style-table th.sortable:hover {
            color: var(--accent);
        }

        .style-table th.sortable::after {
            content: '↕';
            display: inline-block;
            margin-left: 8px;
            font-size: 0.8em;
            color: var(--text-muted);
        }

        .style-table th.sorted-asc::after {
            content: '↑';
            color: var(--accent);
        }

        .style-table th.sorted-desc::after {
            content: '↓';
            color: var(--accent);
        }

        /* Numeric Columns Alignment & Font */
        .style-table th:nth-child(n+2),
        .style-table td:nth-child(n+2) {
            text-align: center;
            vertical-align: middle;
            font-family: var(--font-mono);
            font-variant-numeric: tabular-nums;
        }

        /* Sticky first column for mobile/tablet */
        @media (max-width: 1024px) {
            .style-table th:first-child,
            .style-table td:first-child {
                position: sticky;
                left: 0;
                background-color: var(--terminal-bg);
                z-index: 10;
                box-shadow: 2px 0 4px rgba(0,0,0,0.1);
            }

            .style-table th:first-child {
                z-index: 20;
                background-color: var(--card-bg);
            }

            .style-table tbody tr:hover td:first-child {
                background-color: var(--card-bg);
            }
        }

        /* Colors */
        .positive {
            color: var(--up) !important;
            font-weight: 600;
        }

        .negative {
            color: var(--down) !important;
            font-weight: 600;
        }
        
        /* Specific tweaks for small screens */
        @media (max-width: 768px) {
            body {
                font-size: 14px;
            }

            /* Navbar */
            .navbar {
                padding: 0.6rem 1rem;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .navbar-brand {
                font-size: 1rem;
                flex: 0 0 auto;
                min-width: auto;
                display: flex;
                align-items: center;
            }

            .navbar-logo {
                width: 24px;
                height: 24px;
                margin-right: 0;
            }

            .navbar-quote {
                flex: 1;
                font-size: 0.75rem;
                font-weight: 500;
                padding: 0 0.5rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-align: center;
            }

            .navbar-menu {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                width: 100%;
                justify-content: flex-end;
            }

            .navbar-item {
                font-size: 0.75rem;
            }

            /* App container */
            .app-container {
                flex-direction: column;
                overflow: visible;
            }

            .main-content {
                height: auto;
                min-height: calc(100vh - 100px);
                padding: 1rem;
                overflow-y: visible;
            }

            .dashboard-grid {
                max-width: 100%;
                padding-bottom: 20px;
            }

            /* Tabs */
            .tabs-header {
                padding: 0;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
            }

            .tabs-header::-webkit-scrollbar {
                display: none;
            }

            .tab-button {
                padding: 10px 12px;
                font-size: 0.8rem;
                white-space: nowrap;
                flex: 0 0 auto;
                min-width: 80px;
            }

            /* Tables - Enable horizontal scroll */
            .table-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                border-radius: 0;
            }

            .style-table {
                font-size: 0.75rem;
                min-width: 100%;
            }

            .style-table th {
                padding: 8px 10px;
                font-size: 0.75rem;
                white-space: nowrap;
            }

            .style-table td {
                padding: 8px 10px;
                font-size: 0.75rem;
                white-space: nowrap;
            }

            /* Make numeric columns more compact on mobile */
            .style-table th:nth-child(n+4),
            .style-table td:nth-child(n+4) {
                padding: 8px 6px;
                font-size: 0.7rem;
                white-space: nowrap;
            }

            /* Ensure table container supports horizontal scroll on small screens */
            .table-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }

            .style-table {
                min-width: max-content;
            }

            /* Loading page adjustments */
            .loading-container {
                padding: 1rem;
            }

            .task-list {
                max-width: 100%;
            }

            .task-item {
                font-size: 0.85rem;
            }
        }

        /* Fund Operations Panel */
        .fund-operations {
            position: sticky;
            top: 0;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
            margin-bottom: 20px;
            z-index: 100;
            border: 1px solid var(--border);
        }

        .operation-group {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }

        .operation-group:last-child {
            margin-bottom: 0;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid transparent;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-primary {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-primary:hover {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-success {
            color: #ffffff;
            background-color: var(--down);
            border-color: var(--down);
        }

        .btn-success:hover {
            background-color: #059669;
            border-color: #059669;
        }

        .btn-warning {
            color: #ffffff;
            background-color: #f59e0b;
            border-color: #f59e0b;
        }

        .btn-warning:hover {
            background-color: #d97706;
            border-color: #d97706;
        }

        .btn-info {
            color: #ffffff;
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-info:hover {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-danger {
            color: #ffffff;
            background-color: var(--up);
            border-color: var(--up);
        }

        .btn-danger:hover {
            background-color: #dc2626;
            border-color: #dc2626;
        }

        .btn-secondary {
            color: #ffffff;
            background-color: #6b7280;
            border-color: #6b7280;
        }

        .btn-secondary:hover {
            background-color: #4b5563;
            border-color: #4b5563;
        }

        /* 份额按钮样式 */
        .shares-button {
            padding: 6px 12px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .shares-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .shares-button:active {
            transform: translateY(0);
        }

        #fundCodesInput {
            flex: 1;
            min-width: 250px;
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        #fundCodesInput:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.3);
        }

        #fundCodesInput::placeholder {
            color: var(--text-muted);
        }

        .selected-info {
            margin-left: auto;
            color: var(--text-dim);
            font-size: 14px;
        }

        .selected-info strong {
            color: var(--accent);
            font-size: 16px;
        }

        /* Checkbox styling */
        .fund-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent);
        }

        #selectAll {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent);
        }

        /* Sector Modal */
        .sector-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .sector-modal.active {
            display: flex;
        }

        .sector-modal-content {
            background: var(--terminal-bg);
            padding: 24px;
            border: 1px solid var(--border);
            border-radius: 6px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        .sector-modal-header {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-main);
        }

        .sector-modal-search {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 16px;
            font-size: 14px;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        .sector-modal-search:focus {
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.3);
        }

        .sector-category {
            margin-bottom: 16px;
        }

        .sector-category-header {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--accent);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sector-category-header:hover {
            text-decoration: underline;
        }

        .sector-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
        }

        .sector-item {
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            font-size: 13px;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        .sector-item:hover {
            background-color: var(--card-bg);
            border-color: var(--accent);
        }

        .sector-item.selected {
            background-color: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .sector-modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        /* Floating Action Bar */
        .floating-action-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--terminal-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 12px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: none;
            z-index: 100;
            gap: 8px;
            align-items: center;
        }

        .floating-action-bar.visible {
            display: flex;
        }

        /* Add Fund Input */
        .add-fund-input {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 20px;
            padding: 16px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
        }

        /* Confirm Dialog */
        .confirm-dialog {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .confirm-dialog.active {
            display: flex;
        }

        .confirm-dialog-content {
            background: var(--terminal-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 24px;
            max-width: 400px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        .confirm-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text-main);
        }

        .confirm-message {
            font-size: 14px;
            color: var(--text-dim);
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .confirm-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .floating-action-bar {
                flex-wrap: wrap;
                bottom: 10px;
                left: 10px;
                right: 10px;
                transform: none;
            }

            .add-fund-input {
                flex-direction: column;
                align-items: stretch;
            }

            .btn {
                justify-content: center;
            }

            #fundCodesInput {
                min-width: 100%;
            }

            .selected-info {
                margin-left: 0;
                text-align: center;
            }
        }
    </style>
    """


def get_news_page_html(news_content, username=None):
    """生成7*24快讯页面 - 简洁布局"""
    css_style = get_css_style()

    username_display = ''
    if username:
        username_display += '<span class="nav-user">{username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7*24快讯 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pages.css">
    <style>
        /* Common page styles (body, navbar, content-area, etc.) are now in pages.css */
        /* News-specific: content-area uses 20px padding (override pages.css 30px) */
        .content-area {{
            padding: 20px;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 快讯内容 */
        .news-content {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            /* 汉堡菜单显示 */
            .hamburger-menu {{
                display: flex !important;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            <a href="/market" class="sidebar-item active">
                <span class="sidebar-icon">📰</span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon">📊</span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon">💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon">🏢</span>
                <span>概念板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    📰 7*24快讯
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪全球市场动态</p>
            </div>

            <!-- 快讯内容 -->
            <div class="news-content">
                {news_content}
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        {lyrics_script}
        document.addEventListener('DOMContentLoaded', function() {{ autoColorize(); }});
    </script>
</body>
</html>'''.format(css_style=css_style, username_display=username_display, news_content=news_content, lyrics_script=get_lyrics_carousel_script())
    return html


def get_precious_metals_page_html(metals_data, username=None):
    """生成贵金属行情页面"""
    css_style = get_css_style()

    username_display = ''
    if username:
        username_display += '<span class="nav-user">{username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贵金属行情 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pages.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* Common page styles are now in pages.css */
        /* Metals-specific: content-area uses 20px padding (override pages.css 30px) */
        .content-area {{
            padding: 20px;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 贵金属网格布局 - 上下两栏 */
        .metals-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            max-width: 100%;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            width: 100%;
        }}

        .metal-card-realtime {{
            min-height: 200px;
        }}

        .metal-card-history {{
            min-height: 400px;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}

        .metal-card-header {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metal-card-title {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .metal-card-content {{
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
        }}

        .chart-container {{
            position: relative;
            height: 400px;
            width: 100%;
        }}

        /* 确保表格容器支持横向滚动 */
        .metal-card-realtime .table-container {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}

        .metal-card-realtime .style-table {{
            min-width: max-content;
            white-space: nowrap;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .metals-grid {{
                grid-template-columns: 1fr;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            /* 汉堡菜单显示 */
            .hamburger-menu {{
                display: flex !important;
            }}

            .metal-card-history {{
                min-height: 300px;
            }}

            .chart-container {{
                height: 280px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon">📰</span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon">📊</span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item active">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon">💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon">🏢</span>
                <span>概念板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    🪙 贵金属行情
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪贵金属价格走势</p>
            </div>

            <!-- 贵金属网格 - 上下两栏布局 -->
            <div class="metals-grid">
                <!-- 实时贵金属 -->
                <div class="metal-card metal-card-realtime">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>⚡</span>
                            <span>实时贵金属</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        {real_time_content}
                    </div>
                </div>

                <!-- 分时黄金价格 -->
                <div class="metal-card metal-card-history">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>📊</span>
                            <span>分时黄金价格</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        <!-- Hidden div to store one day gold data for parsing -->
                        <div id="goldOneDayData" style="display:none;">
                            {one_day_content}
                        </div>
                        <div class="chart-container">
                            <canvas id="goldOneDayChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- 历史金价 -->
                <div class="metal-card metal-card-history">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>📈</span>
                            <span>历史金价</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        <!-- Hidden div to store history data for parsing -->
                        <div id="goldHistoryData" style="display:none;">
                            {history_content}
                        </div>
                        <div class="chart-container">
                            <canvas id="goldPriceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>

        // 解析历史金价数据并创建图表
        function createGoldChart() {{
            // 从隐藏的div中获取历史金价表格
            const historyContainer = document.getElementById('goldHistoryData');
            if (!historyContainer) return;

            const table = historyContainer.querySelector('table');
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            const labels = [];
            const prices = [];

            rows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {{
                    labels.push(cells[0].textContent.trim());
                    prices.push(parseFloat(cells[1].textContent.trim()));
                }}
            }});

            // 创建图表
            const ctx = document.getElementById('goldPriceChart').getContext('2d');

            // 注册插件以在数据点上显示数值
            const dataLabelPlugin = {{
                id: 'dataLabelPlugin',
                afterDatasetsDraw(chart, args, options) {{
                    const {{ ctx }} = chart;
                    chart.data.datasets.forEach((dataset, datasetIndex) => {{
                        const meta = chart.getDatasetMeta(datasetIndex);
                        meta.data.forEach((datapoint, index) => {{
                            const value = dataset.data[index];
                            const x = datapoint.x;
                            const y = datapoint.y;

                            ctx.save();
                            ctx.fillStyle = '#f59e0b';
                            ctx.font = 'bold 11px sans-serif';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';
                            ctx.fillText(value.toFixed(2), x, y - 5);
                            ctx.restore();
                        }});
                    }});
                }}
            }};

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels.reverse(),
                    datasets: [{{
                        label: '金价 (元/克)',
                        data: prices.reverse(),
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af'
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }},
                plugins: [dataLabelPlugin]
            }});
        }}

        // 解析分时黄金价格数据并创建图表
        function createGoldOneDayChart() {{
            // 从隐藏的div中获取分时黄金价格数据
            const oneDayContainer = document.getElementById('goldOneDayData');
            if (!oneDayContainer) return;

            const dataText = oneDayContainer.textContent.trim();
            if (!dataText || dataText === 'None' || dataText === '') return;

            let data;
            try {{
                data = JSON.parse(dataText);
            }} catch (e) {{
                console.error('Failed to parse gold one day data:', e);
                return;
            }}

            if (!data || !Array.isArray(data) || data.length === 0) return;

            const labels = [];
            const prices = [];

            data.forEach(item => {{
                if (item.date && item.price !== undefined) {{
                    // 只显示时间部分 (HH:MM:SS)
                    const timePart = item.date.split(' ')[1] || item.date;
                    labels.push(timePart);
                    prices.push(parseFloat(item.price));
                }}
            }});

            // 创建图表
            const ctx = document.getElementById('goldOneDayChart').getContext('2d');

            // 获取最新价格和时间用于图例显示
            let labelText = '金价 (元/克)';
            if (data.length > 0) {{
                const latestData = data[data.length - 1];
                const timePart = latestData.date.split(' ')[1] || latestData.date;
                labelText = `金价 (元/克)  最新: ¥${{latestData.price}}  ${{timePart}}`;
            }}

            window.goldOneDayChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: labelText,
                        data: prices,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af'
                            }}
                        }},
                        tooltip: {{
                            enabled: true,
                            mode: 'index',
                            intersect: false
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                maxTicksLimit: 12
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }},
                    interaction: {{
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }}
                }}
            }});
        }}

        {lyrics_script}
        document.addEventListener('DOMContentLoaded', function() {{
            autoColorize();
            createGoldChart();
            createGoldOneDayChart();
        }});
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        real_time_content=metals_data.get('real_time', ''),
        one_day_content=metals_data.get('one_day', ''),
        history_content=metals_data.get('history', ''),
        lyrics_script=get_lyrics_carousel_script()
    )
    return html


def get_market_indices_page_html(market_charts=None, chart_data=None, timing_data=None, username=None):
    """生成市场指数页面 - 上证分时、全球指数和成交量趋势"""
    css_style = get_css_style()

    username_display = ''
    if username:
        username_display += '<span class="nav-user">{username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    indices_data_json = json.dumps(
        chart_data.get('indices', {'labels': [], 'prices': [], 'changes': []}) if chart_data else {'labels': [],
                                                                                                   'prices': [],
                                                                                                   'changes': []})
    volume_data_json = json.dumps(
        chart_data.get('volume', {'labels': [], 'total': [], 'sh': [], 'sz': [], 'bj': []}) if chart_data else {
            'labels': [], 'total': [], 'sh': [], 'sz': [], 'bj': []})

    timing_data_json = json.dumps(
        timing_data if timing_data else {'labels': [], 'prices': [], 'change_pcts': [], 'change_amounts': [],
                                         'volumes': [], 'amounts': []})

    market_content = '''
        <!-- 市场指数区域 -->
        <div class="market-indices-section" style="padding: 30px;">
            <div class="page-header" style="margin-bottom: 25px;">
                <h1 style="font-size: 1.5rem; font-weight: 600; margin: 0; color: var(--text-main); display: flex; align-items: center;">
                    📊 市场指数
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
            </div>

            <!-- 第一行：上证分时（全宽） -->
            <div class="timing-chart-row" style="margin-bottom: 20px;">
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 id="timingChartTitle" style="margin: 0; font-size: 1rem; color: var(--text-main);">📉 上证分时</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; height: 350px;">
                        <canvas id="timingChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 第二行：全球指数和成交量趋势 -->
            <div class="market-charts-grid">
                <!-- 全球指数 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);">🌍 全球指数</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {indices_content}
                    </div>
                </div>
                <!-- 成交量趋势 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);">📊 成交量趋势</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {volume_content}
                    </div>
                </div>
            </div>
        </div>
    '''.format(
        indices_content=market_charts.get('indices', ''),
        volume_content=market_charts.get('volume', '')
    )

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市场指数 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-star {{
            color: #e3b341;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-star:hover {{
            color: #f2c94c;
        }}

        .nav-feedback {{
            color: #8b949e;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-feedback:hover {{
            color: #58a6ff;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .chart-card-content::-webkit-scrollbar {{
            width: 4px;
        }}

        .chart-card-content::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.05);
        }}

        @media (max-width: 768px) {{
            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            .timing-chart-row .chart-card-content {{
                height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </div>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon">📰</span>
                <span>市场行情</span>
            </a>
            <a href="/market-indices" class="sidebar-item active">
                <span class="sidebar-icon">📊</span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon">💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon">🏢</span>
                <span>概念板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            {market_content}
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 上证分时数据
        const timingData = {timing_data_json};

        {lyrics_script}
        document.addEventListener('DOMContentLoaded', function() {{
            // 自动颜色化
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});

            // 初始化上证分时图表
            initTimingChart();
        }});

        // 上证分时图表 - 使用API返回的实际涨跌幅
        function initTimingChart() {{
            const ctx = document.getElementById('timingChart');
            if (!ctx || timingData.labels.length === 0) return;

            // 使用API返回的实际数据（已经处理好的）
            const changePercentages = timingData.change_pcts || [];
            const changeAmounts = timingData.change_amounts || [];  // 原始涨跌额数据
            const basePrice = timingData.prices[0];
            const lastPrice = timingData.prices[timingData.prices.length - 1];

            // 使用最后一个实际涨跌幅值
            const lastPct = changePercentages.length > 0 ? changePercentages[changePercentages.length - 1] : 0;
            const titleColor = lastPct >= 0 ? '#f44336' : '#4caf50';

            // 更新标题颜色 - 现在主要显示实际涨跌幅
            const titleElement = document.getElementById('timingChartTitle');
            if (titleElement) {{
                titleElement.style.color = titleColor;
                titleElement.innerHTML = '📉 上证分时 <span style="font-size:0.9em;">' +
                    (lastPct >= 0 ? '+' : '') + lastPct.toFixed(2) + '% (' + lastPrice.toFixed(2) + ')</span>';
            }}

            // 保存图表实例到全局变量，方便后续更新
            window.timingChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: timingData.labels,
                    datasets: [{{
                        label: '涨跌幅 (%)',
                        data: changePercentages,
                        borderColor: function(context) {{
                            // 动态返回颜色：>0% 红色，<0% 绿色，=0% 灰色
                            const index = context.dataIndex;
                            if (index === undefined || index < 0) return '#9ca3af';
                            const pct = changePercentages[index];
                            return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                        }},
                        segment: {{
                            borderColor: function(context) {{
                                // 根据线段的结束点判断颜色
                                const pct = changePercentages[context.p1DataIndex];
                                return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                            }}
                        }},
                        backgroundColor: function(context) {{
                            const chart = context.chart;
                            const {{ctx, chartArea}} = chart;
                            if (!chartArea) return null;
                            // 根据当前最新涨跌幅判断整体涨跌来设置背景色
                            const lastPct = changePercentages[changePercentages.length - 1];
                            const color = lastPct >= 0 ? '244, 67, 54' : '76, 175, 80';
                            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, 'rgba(' + color + ', 0.2)');
                            gradient.addColorStop(1, 'rgba(' + color + ', 0.0)');
                            return gradient;
                        }},
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{ size: 11 }},
                                boxWidth: 12,
                                generateLabels: function(chart) {{
                                    const lastPct = changePercentages[changePercentages.length - 1];
                                    const color = lastPct >= 0 ? '#ff4d4f' : '#52c41a';
                                    return [{{
                                        text: '涨跌幅: ' + (lastPct >= 0 ? '+' : '') + lastPct.toFixed(2) + '% (' + lastPrice.toFixed(2) + ')',
                                        fillStyle: color,
                                        strokeStyle: color,
                                        fontColor: color,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: 0
                                    }}];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return '时间: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const pct = changePercentages[index];
                                    const price = timingData.prices[index];
                                    const changeAmt = changeAmounts[index];  // 使用原始涨跌额数据
                                    const volume = timingData.volumes ? timingData.volumes[index] : 0;
                                    const amount = timingData.amounts ? timingData.amounts[index] : 0;
                                    return [
                                        '涨跌幅: ' + (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%',
                                        '上证指数: ' + price.toFixed(2),
                                        '涨跌额: ' + (changeAmt >= 0 ? '+' : '') + changeAmt.toFixed(2),
                                        '成交量: ' + volume.toFixed(0) + '万手',
                                        '成交额: ' + amount.toFixed(2) + '亿'
                                    ];
                                }}
                            }}
                        }},
                        datalabels: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                font: {{ size: 10 }},
                                maxTicksLimit: 6
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '涨跌幅 (%)',
                                color: '#9ca3af',
                                font: {{ size: 11 }}
                            }},
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        market_content=market_content,
        timing_data_json=timing_data_json,
        lyrics_script=get_lyrics_carousel_script()
    )
    return html


def get_portfolio_page_html(fund_content, fund_map, fund_chart_data=None, fund_chart_info=None, username=None):
    """生成持仓基金页面"""
    css_style = get_css_style()

    username_display = ''
    if username:
        username_display += '<span class="nav-user">{username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    fund_chart_data_json = json.dumps(
        fund_chart_data if fund_chart_data else {'labels': [], 'growth': [], 'net_values': []})
    fund_chart_info_json = json.dumps(fund_chart_info if fund_chart_info else {})

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓基金 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-star {{
            color: #e3b341;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-star:hover {{
            color: #f2c94c;
        }}

        .nav-feedback {{
            color: #8b949e;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-feedback:hover {{
            color: #58a6ff;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        .portfolio-header {{
            margin-bottom: 20px;
        }}

        .portfolio-header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
            color: var(--text-main);
        }}

        .portfolio-header p {{
            color: var(--text-dim);
            margin: 5px 0 0;
            font-size: 0.9rem;
        }}

        .operations-panel {{
            background: rgba(102, 126, 234, 0.05);
            border: 1px solid rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }}

        .operation-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .fund-content {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            /* 顶部导航栏两行布局 */
            .top-navbar {{
                flex-direction: row;
                flex-wrap: wrap;
                height: auto;
                padding: 0.5rem 1rem;
                align-items: center;
                border-bottom: none;
            }}

            .top-navbar > .top-navbar-brand {{
                order: 1;
                flex: 0 0 auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-menu {{
                order: 1;
                flex: 0 0 auto;
                margin-left: auto;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border);
            }}

            .top-navbar-quote {{
                order: 2;
                width: 100%;
                flex-basis: 100%;
                text-align: center;
                padding: 0.5rem 0;
                font-size: 0.8rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                border-top: 1px solid var(--border);
                margin-top: 0.5rem;
            }}

            .market-charts-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}

            .chart-card {{
                min-height: auto;
            }}

            .chart-card-content {{
                max-height: 200px;
            }}

            .chart-card h3 {{
                font-size: 0.9rem;
            }}
        }}

        @media (max-width: 1024px) {{
            .market-charts-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        /* 基金选择器容器 */
        .fund-selector-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
            flex: 1;
            min-width: 200px;
            max-width: 500px;
        }}

        /* 输入框样式 - 隐藏原生箭头 */
        #fundSelector {{
            flex: 1;
            width: 100%;
            min-width: 150px;
            padding: 6px 32px 6px 12px;
            background: var(--card-bg);
            color: var(--text-main);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 14px;
            line-height: 1.5;
            /* 隐藏原生datalist箭头 */
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
        }}

        /* 隐藏Webkit浏览器的下拉按钮 */
        #fundSelector::-webkit-calendar-picker-indicator {{
            opacity: 0;
            display: none;
        }}

        /* 输入框焦点样式 */
        #fundSelector:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }}

        /* 清除按钮 */
        .input-clear-btn {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: #9ca3af;
            color: #fff !important;
            font-size: 10px !important;
            font-weight: bold;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease, background-color 0.2s ease;
            z-index: 2;
        }}

        /* 有内容且hover时显示清除按钮 */
        .fund-selector-wrapper.has-value:hover .input-clear-btn {{
            opacity: 1;
        }}

        .input-clear-btn:hover {{
            background-color: #6b7280;
        }}

        /* 基金选择器下拉箭头 */
        .fund-selector-dropdown-arrow {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 10px;
            pointer-events: none;
            transition: transform 0.2s ease;
        }}

        .fund-selector-wrapper:hover .fund-selector-dropdown-arrow {{
            color: var(--text-main);
        }}

        /* 清除按钮位置调整 */
        .input-clear-btn {{
            right: 24px; /* 为箭头留出空间 */
        }}

        /* 基金选择列表项 */
        .fund-chart-selector-item {{
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            border-radius: 6px;
            transition: background-color 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .fund-chart-selector-item:hover {{
            background-color: rgba(59, 130, 246, 0.1);
        }}

        .fund-chart-selector-item .fund-code {{
            font-weight: 600;
            color: var(--text-main);
            min-width: 70px;
        }}

        .fund-chart-selector-item .fund-name {{
            flex: 1;
            color: var(--text-dim);
        }}

        .fund-chart-selector-item.is-default {{
            background-color: rgba(59, 130, 246, 0.15);
            border-left: 3px solid #3b82f6;
        }}

        /* 移动端优化 */
        @media (max-width: 768px) {{
            #fundSelector {{
                font-size: 16px; /* 防止iOS自动缩放 */
                padding: 8px 36px 8px 12px;
            }}

            .input-clear-btn {{
                width: 20px;
                height: 20px;
                font-size: 12px;
                right: 26px;
            }}

            .fund-selector-dropdown-arrow {{
                font-size: 12px;
                right: 10px;
            }}

            .fund-chart-selector-item {{
                padding: 16px 12px; /* 增大点击区域 */
            }}

            #fundChartSelectorModal .sector-modal-content {{
                width: 95%;
                max-height: 85vh;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon">📰</span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon">📊</span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item active">
                <span class="sidebar-icon">💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon">🏢</span>
                <span>概念板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="portfolio-header">
                <h1>
                    💼 持仓基金
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button">🔄 刷新</button>
                </h1>
            </div>

            <!-- Refresh button styling -->
            <style>
                .refresh-button {{
                    margin-left: 15px;
                    padding: 8px 16px;
                    background: var(--accent);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                }}
                .refresh-button:hover {{
                    background: #2563eb;
                    transform: translateY(-1px);
                }}
                .refresh-button:disabled {{
                    background: #6b7280;
                    cursor: not-allowed;
                    transform: none;
                }}
                .portfolio-header h1 {{
                    display: flex;
                    align-items: center;
                }}
            </style>

            <!-- 免责声明 -->
            <div style="margin-bottom: 20px; padding: 12px 15px; background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 8px; font-size: 0.85rem; color: var(--text-dim);">
                <p style="margin: 0; line-height: 1.5;">
                    <strong style="color: #ffc107;">⚠️ 免责声明</strong>：
                    预估收益根据您输入的持仓份额与实时估值计算得出，仅供参考。
                    实际收益以基金公司最终结算为准，可能因份额确认时间、分红方式、费用扣除等因素存在偏差。
                    投资有风险，入市需谨慎。
                </p>
            </div>

            <!-- 基金估值趋势图 -->
            <div id="fundChartContainer" class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 20px;">
                <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                        <h3 id="fundChartTitle" style="margin: 0; font-size: 1rem; color: var(--text-main); flex-shrink: 0;">📈 基金估值</h3>
                        <div class="fund-selector-wrapper" id="fundSelectorWrapper" style="flex: 1; min-width: 280px; max-width: 100%;">
                            <input type="text" id="fundSelector" placeholder="选择或搜索基金代码/名称..." autocomplete="off" readonly>
                            <span id="fundSelectorClear" class="input-clear-btn">✕</span>
                            <span class="fund-selector-dropdown-arrow" id="fundSelectorArrow">▼</span>
                        </div>
                    </div>
                </div>
                <div class="chart-card-content" style="padding: 15px; height: 300px;">
                    <canvas id="fundChart"></canvas>
                </div>
            </div>

            <!-- 基金内容 -->
            <div class="fund-content">
                {fund_content}
            </div>
        </div>
    </div>

    <!-- Modals (复用现有模态框) -->
    <div class="sector-modal" id="sectorModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header">选择板块</div>
            <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
            <div id="sectorCategories"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmSector()">确定</button>
            </div>
        </div>
    </div>

    <div class="sector-modal" id="fundSelectionModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
            <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
            </div>
        </div>
    </div>

    <div class="confirm-dialog" id="confirmDialog">
        <div class="confirm-dialog-content">
            <h3 id="confirmTitle" class="confirm-title"></h3>
            <p id="confirmMessage" class="confirm-message"></p>
            <div class="confirm-actions">
                <button class="btn btn-secondary" onclick="closeConfirmDialog()">取消</button>
                <button class="btn btn-primary" id="confirmBtn">确定</button>
            </div>
        </div>
    </div>

    <!-- 基金图表选择模态框 -->
    <div class="sector-modal" id="fundChartSelectorModal">
        <div class="sector-modal-content" style="max-width: 500px;">
            <div class="sector-modal-header">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundChartSelectorSearch" placeholder="搜索基金代码或名称...">
            <div id="fundChartSelectorList" style="max-height: 400px; overflow-y: auto;">
                <!-- 基金列表将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundChartSelectorModal()">取消</button>
            </div>
        </div>
    </div>

    <!-- 份额设置弹窗 -->
    <div class="sector-modal" id="sharesModal">
        <div class="sector-modal-content" style="max-width: 400px;">
            <div class="sector-modal-header">设置持仓份额</div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">基金代码</label>
                    <div id="sharesModalFundCode" style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; color: #3b82f6; font-weight: 600; font-family: monospace;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="sharesModalInput" style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">持仓份额</label>
                    <input type="number" id="sharesModalInput" step="0.01" min="0" placeholder="请输入份额"
                           style="width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; background: var(--card-bg); color: var(--text-main);">
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSharesModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmShares()">确定</button>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script>

        {lyrics_script}
        document.addEventListener('DOMContentLoaded', function() {{
            // 初始化基金估值趋势图
            initFundChartSelector();
            initFundChart();
        }});

        // 基金估值趋势数据和选择器
        let fundChartData = {fund_chart_data_json};
        let fundChartInfo = {fund_chart_info_json};

        // 基金图表选择器相关变量
        let fundChartSelectorFunds = [];
        let selectedFundCode = null;

        function initFundChartSelector() {{
            const selector = document.getElementById('fundSelector');
            const clearBtn = document.getElementById('fundSelectorClear');
            const wrapper = document.getElementById('fundSelectorWrapper');

            if (!selector || !fundChartInfo || Object.keys(fundChartInfo).length === 0) {{
                const container = document.getElementById('fundChartContainer');
                if (container) {{
                    container.style.display = 'none';
                }}
                return;
            }}

            // 转换基金信息为数组
            fundChartSelectorFunds = Object.entries(fundChartInfo).map(([code, info]) => ({{
                code: code,
                name: info.name,
                is_default: info.is_default || false
            }}));

            // 设置默认值
            const defaultFund = fundChartSelectorFunds.find(f => f.is_default);
            if (defaultFund) {{
                selector.value = `${{defaultFund.code}} - ${{defaultFund.name}}`;
                selectedFundCode = defaultFund.code;
            }}

            // 点击输入框打开模态框
            const openModal = () => {{
                renderFundChartSelectorList(fundChartSelectorFunds);
                document.getElementById('fundChartSelectorModal').classList.add('active');
                setTimeout(() => {{
                    const searchInput = document.getElementById('fundChartSelectorSearch');
                    if (searchInput) searchInput.focus();
                }}, 100);
            }};

            selector.addEventListener('click', openModal);

            // 清空按钮
            if (clearBtn && wrapper) {{
                const updateClearButtonVisibility = () => {{
                    if (selector.value.trim()) {{
                        wrapper.classList.add('has-value');
                    }} else {{
                        wrapper.classList.remove('has-value');
                    }}
                }};

                clearBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    selector.value = '';
                    selectedFundCode = null;
                    updateClearButtonVisibility();
                }});

                updateClearButtonVisibility();
            }}
        }}

        // 渲染基金选择列表
        function renderFundChartSelectorList(funds) {{
            const listContainer = document.getElementById('fundChartSelectorList');
            if (!listContainer) return;

            if (funds.length === 0) {{
                listContainer.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-dim);">未找到匹配的基金</div>';
                return;
            }}

            listContainer.innerHTML = funds.map(fund => `
                <div class="fund-chart-selector-item ${{fund.is_default ? 'is-default' : ''}}"
                     onclick="selectFundForChart('${{fund.code}}')">
                    <div class="fund-code">${{fund.code}}</div>
                    <div class="fund-name">${{fund.name}}</div>
                    ${{fund.is_default ? '<span style="color: #3b82f6; font-size: 12px;">⭐ 默认</span>' : ''}}
                </div>
            `).join('');
        }}

        // 选择基金并更新图表
        function selectFundForChart(fundCode) {{
            const fund = fundChartSelectorFunds.find(f => f.code === fundCode);
            if (!fund) return;

            const selector = document.getElementById('fundSelector');
            selector.value = `${{fund.code}} - ${{fund.name}}`;
            selectedFundCode = fund.code;

            const wrapper = document.getElementById('fundSelectorWrapper');
            if (wrapper) wrapper.classList.add('has-value');

            closeFundChartSelectorModal();
            loadFundChartData(fundCode);
        }}

        // 关闭模态框
        function closeFundChartSelectorModal() {{
            const modal = document.getElementById('fundChartSelectorModal');
            if (modal) modal.classList.remove('active');

            const searchInput = document.getElementById('fundChartSelectorSearch');
            if (searchInput) searchInput.value = '';
        }}

        // 搜索功能和模态框事件
        document.addEventListener('DOMContentLoaded', function() {{
            // 搜索过滤
            const searchInput = document.getElementById('fundChartSelectorSearch');
            if (searchInput) {{
                searchInput.addEventListener('input', function() {{
                    const keyword = this.value.toLowerCase().trim();
                    if (!keyword) {{
                        renderFundChartSelectorList(fundChartSelectorFunds);
                        return;
                    }}
                    const filtered = fundChartSelectorFunds.filter(fund =>
                        fund.code.includes(keyword) ||
                        fund.name.toLowerCase().includes(keyword)
                    );
                    renderFundChartSelectorList(filtered);
                }});
            }}

            // 点击背景关闭
            const modal = document.getElementById('fundChartSelectorModal');
            if (modal) {{
                modal.addEventListener('click', function(e) {{
                    if (e.target === modal) {{
                        closeFundChartSelectorModal();
                    }}
                }});
            }}
        }});

        function initFundChart() {{
            if (!fundChartData.labels || fundChartData.labels.length === 0) {{
                return;
            }}

            const ctx = document.getElementById('fundChart');
            if (!ctx) return;

            const growthData = fundChartData.growth || [];
            const netValues = fundChartData.net_values || [];
            const lastGrowth = growthData.length > 0 ? growthData[growthData.length - 1] : 0;
            const lastNetValue = netValues.length > 0 ? netValues[netValues.length - 1] : 0;

            // 更新标题
            const titleEl = document.getElementById('fundChartTitle');
            if (titleEl) {{
                const color = lastGrowth > 0 ? '#f44336' : (lastGrowth < 0 ? '#4caf50' : '#9ca3af');
                titleEl.innerHTML = `📈 基金估值`;
            }}

            window.fundChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: fundChartData.labels,
                    datasets: [{{
                        label: '涨幅 (%)',
                        data: growthData,
                        borderColor: function(context) {{
                            const index = context.dataIndex;
                            if (index === undefined || index < 0) return '#9ca3af';
                            const pct = growthData[index];
                            return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                        }},
                        segment: {{
                            borderColor: function(context) {{
                                const pct = growthData[context.p1DataIndex];
                                return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                            }}
                        }},
                        backgroundColor: function(context) {{
                            const chart = context.chart;
                            const {{ctx, chartArea}} = chart;
                            if (!chartArea) return null;
                            const lastPct = growthData[growthData.length - 1];
                            const color = lastPct >= 0 ? '244, 67, 54' : '76, 175, 80';
                            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, 'rgba(' + color + ', 0.2)');
                            gradient.addColorStop(1, 'rgba(' + color + ', 0.0)');
                            return gradient;
                        }},
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{ size: 11 }},
                                boxWidth: 12,
                                generateLabels: function(chart) {{
                                    const lastPct = growthData[growthData.length - 1];
                                    const color = lastPct >= 0 ? '#ff4d4f' : '#52c41a';
                                    return [{{
                                        text: '涨幅: ' + (lastPct >= 0 ? '+' : '') + lastPct.toFixed(2) + '% | 净值: ' + lastNetValue.toFixed(4),
                                        fillStyle: color,
                                        strokeStyle: color,
                                        fontColor: color,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: 0
                                    }}];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return '时间: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const growth = growthData[index];
                                    const netValue = netValues[index];
                                    const color = growth > 0 ? '#f44336' : (growth < 0 ? '#4caf50' : '#9ca3af');
                                    return [
                                        '涨幅: ' + (growth >= 0 ? '+' : '') + growth.toFixed(2) + '%',
                                        '净值: ' + netValue.toFixed(4)
                                    ];
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                font: {{ size: 10 }},
                                maxTicksLimit: 6
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '涨幅 (%)',
                                color: '#9ca3af',
                                font: {{ size: 11 }}
                            }},
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}

        async function loadFundChartData(fundCode) {{
            try {{
                const response = await fetch('/api/fund/chart-data?code=' + fundCode);
                const data = await response.json();

                // 更新全局数据
                fundChartData = data.chart_data;

                // 重新渲染图表
                const canvas = document.getElementById('fundChart');
                if (window.fundChartInstance) {{
                    window.fundChartInstance.destroy();
                }}
                initFundChart();

                // 保存用户偏好
                await fetch('/api/fund/chart-default', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ fund_code: fundCode }})
                }});
            }} catch (error) {{
                console.error('Failed to load fund chart data:', error);
            }}
        }}
    </script>
</body>
</html>'''.format(css_style=css_style, username_display=username_display, fund_content=fund_content,
                  fund_chart_data_json=fund_chart_data_json, fund_chart_info_json=fund_chart_info_json,
                  lyrics_script=get_lyrics_carousel_script())
    return html


def get_sectors_page_html(sectors_content, select_fund_content, fund_map, username=None):
    """生成概念板块基金查询页面"""
    css_style = get_css_style()

    username_display = ''
    if username:
        username_display += '<span class="nav-user">{username}</span>'.format(username=username)
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>概念板块 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/pages.css">
    <style>
        /* Common page styles are now in pages.css */

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 30px;
        }}

        .page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-main);
            border: none;
            text-decoration: none;
        }}

        .page-header p {{
            color: var(--text-dim);
            margin-top: 10px;
            border: none;
            text-decoration: none;
        }}

        /* Tab 内容 */
        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .content-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        /* Tab 切换按钮 */
        .tab-button {{
            padding: 10px 20px;
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .tab-button:hover {{
            color: var(--text-main);
        }}

        .tab-button.active {{
            color: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            /* 汉堡菜单显示 */
            .hamburger-menu {{
                display: flex !important;
            }}
            /* Responsive navbar styles are now in pages.css */
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 汉堡菜单按钮 (移动端) -->
        <button class="hamburger-menu" id="hamburgerMenu">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle">▶</div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon">📰</span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon">📊</span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon">💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item active">
                <span class="sidebar-icon">🏢</span>
                <span>概念板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- Tab 切换按钮 -->
            <div class="tab-buttons" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="tab-button active" onclick="switchTab('sectors')" id="tab-btn-sectors">
                    🏢 概念板块
                </button>
                <button class="tab-button" onclick="switchTab('query')" id="tab-btn-query">
                    🔍 板块基金查询
                </button>
            </div>

            <!-- 概念板块 Tab -->
            <div id="tab-sectors" class="tab-content active">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        🏢 概念板块
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查看各概念板块的市场表现</p>
                </div>
                <div class="content-card">
                    {sectors_content}
                </div>
            </div>

            <!-- 板块基金查询 Tab -->
            <div id="tab-query" class="tab-content">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        🔍 板块基金查询
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查询特定板块的基金产品</p>
                </div>
                <div class="content-card">
                    {select_fund_content}
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        function switchTab(tabName) {{
            // 隐藏所有 tab 内容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // 移除所有 tab 按钮的 active 状态
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // 显示选中的 tab
            document.getElementById('tab-' + tabName).classList.add('active');

            // 设置对应 tab 按钮为 active
            document.getElementById('tab-btn-' + tabName).classList.add('active');
        }}


        {lyrics_script}
        document.addEventListener('DOMContentLoaded', function() {{
            const firstTabBtn = document.querySelector('.tab-button');
            if (firstTabBtn) {{
                firstTabBtn.classList.add('active');
            }}
            autoColorize();
        }});
    </script>
</body>
</html>'''.format(
        css_style=css_style,
        username_display=username_display,
        sectors_content=sectors_content,
        select_fund_content=select_fund_content,
        lyrics_script=get_lyrics_carousel_script()
    )
    return html


def render_main_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>基金持仓系统</title>
    <style>
        body { font-family: Arial; background:#f5f6fa; }
        .btn { padding:8px 16px; border:none; border-radius:6px; cursor:pointer; }
        .btn-primary { background:#2563eb; color:white; }
        .btn-secondary { background:#999; color:white; }

        .sector-modal {
            display:none;
            position:fixed;
            left:0; top:0;
            width:100%; height:100%;
            background:rgba(0,0,0,0.5);
            justify-content:center;
            align-items:center;
        }

        .sector-modal-content {
            background:white;
            border-radius:10px;
            width:420px;
            overflow:hidden;
        }

        .sector-modal-header {
            background:#2563eb;
            color:white;
            padding:12px;
            font-size:16px;
        }

        .sector-modal-footer {
            padding:12px;
            text-align:right;
            background:#f1f5f9;
        }

        input, select {
            width:100%;
            padding:8px;
            margin-top:6px;
            border:1px solid #ccc;
            border-radius:6px;
        }
    </style>
</head>

<body>

<h2>基金持仓管理</h2>

<button class="btn btn-primary" onclick="openSharesModal('000001')">
    修改基金持仓
</button>

<!-- 买卖操作弹窗 -->
<div class="sector-modal" id="sharesModal">
    <div class="sector-modal-content">
        <div class="sector-modal-header">基金交易</div>

        <div style="padding:20px;">

            <div style="margin-bottom:15px;">
                <label>基金代码</label>
                <div id="sharesModalFundCode"
                     style="padding:8px;background:#eef;border-radius:6px;">
                </div>
            </div>

            <div style="margin-bottom:15px;">
                <label>交易类型</label>
                <select id="tradeType">
                    <option value="buy">买入</option>
                    <option value="sell">卖出</option>
                </select>
            </div>

            <div id="buyBlock" style="margin-bottom:15px;">
                <label>买入金额</label>
                <input type="number" id="buyAmount" step="0.01" min="0">
                <div style="margin-top:8px;color:#16a34a;">
                    本次可得份额：
                    <span id="buyResult">0</span>
                </div>
            </div>

            <div id="sellBlock" style="display:none;margin-bottom:15px;">
                <label>卖出份额</label>
                <input type="number" id="sellShares" step="0.01" min="0">
                <div style="margin-top:8px;color:#dc2626;">
                    卖出到账金额：
                    <span id="sellResult">0</span>
                </div>
            </div>

            <div style="margin-bottom:15px;">
                <label>手续费率(%)</label>
                <input type="number" id="feeRate" step="0.01" min="0" value="0.15">
            </div>

        </div>

        <div class="sector-modal-footer">
            <button class="btn btn-secondary" onclick="closeSharesModal()">取消</button>
            <button class="btn btn-primary" onclick="confirmTrade()">确定</button>
        </div>
    </div>
</div>

<script src="/static/main.js"></script>

</body>
</html>
"""