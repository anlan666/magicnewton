# stats_processor.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_charts(account_data):
    """
    生成游戏统计图表.

    Args:
        account_data: 账号数据列表 (字典列表).

    Returns:
        无 (直接显示图表).
    """
    if not account_data or not isinstance(account_data, list):
        print("No data to plot")
        return

    wins = [data.get('wins', 0) for data in account_data]
    losses = [data.get('losses', 0) for data in account_data]
    profit = [data.get('profit', 0) for data in account_data]

    # 创建子图：柱状图和折线图
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'bar'}, {'type': 'xy'}]],
                        subplot_titles=('Wins vs Losses', 'Profit Over Time'))

    # 柱状图：Wins vs Losses
    fig.add_trace(
        go.Bar(x=['Wins', 'Losses'], y=[sum(wins), sum(losses)], name='Game Results'),
        row=1, col=1
    )

    # 折线图：Profit
    fig.add_trace(
        go.Scatter(x=['Total Profit'], y=[sum(profit)], mode='lines+markers', name='Profit'),
        row=1, col=2
    )

    # 更新布局
    fig.update_layout(
        title_text="Game Statistics",
        height=600, width=1200,
        showlegend=True
    )

    fig.show()