#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

from .server import html_dir
import os
import time
from plotly import graph_objects
from plotly.graph_objects import *

class Figure(graph_objects.Figure):
    html_path = None
    def show(self):
        """
        show figure in browser by a background server started with

            ``` bash
            python -m esyimg
            ```
        """
        if self.html_path is None:
            title = 'auto'
            if self.layout.title:
                title = self.layout.title.text
            self.html_path = html_dir / f"{int(time.time())}_{title}.html"
        self.write_html(str(self.html_path))



#%% 示例用法
if __name__ == '__main__':

    figs = [
        Figure(data=Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers')),
        Figure(data=Bar(x=["A", "B", "C"], y=[7, 8, 9]))
    ]
    for i, fig in enumerate(figs):
        fig.update_layout(title=f"Plotly 图表 {i+1}")
        html_path = html_dir / f"my_custom_plotly_chart_{i}.html"
        fig.show()

    # 主线程动态更新数据
    t = 0
    while True:
        figs[0].data[0].y = [4+t, 5*t, 6+t]
        figs[0].update_layout(title=f"Plotly 图表 1 动态 {t}")
        figs[0].show()
        time.sleep(3)
        t += 1

# %%
