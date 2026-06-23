# -*- coding: utf-8 -*-
"""
图表展示组件
"""
from nicegui import ui


class ChartViewer:
    """图表展示组件（基于 pyecharts）"""

    def __init__(self):
        self.charts = []

    def render_bar_chart(self, title: str, x_data: list, y_data: list):
        """渲染柱状图"""
        from pyecharts import options as opts
        from pyecharts.charts import Bar

        bar = (
            Bar()
            .add_xaxis(x_data)
            .add_yaxis(title, y_data)
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )

        html_content = bar.render_embed()
        ui.html(html_content).classes('w-full')

    def render_pie_chart(self, title: str, data_pairs: list):
        """渲染饼图"""
        from pyecharts import options as opts
        from pyecharts.charts import Pie

        pie = (
            Pie()
            .add(title, data_pairs)
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )

        html_content = pie.render_embed()
        ui.html(html_content).classes('w-full')
