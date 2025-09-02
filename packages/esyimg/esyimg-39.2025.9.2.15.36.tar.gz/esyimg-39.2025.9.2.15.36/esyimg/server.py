#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf', locals(), version=0)
html_dir = sfs.path_of("").ensure()

import dash
from dash import html, dcc
import os
from flask import Flask, send_file

class HtmlViewerServer:
    def __init__(self, port=8051):
        self.port = port
        self.server = Flask(__name__)
        self.app = None
        self.last_files = []
        self.refresh_enabled = {}
        self._setup_routes()
        self._initialize_app()

    def _get_html_files(self):
        """获取所有HTML文件及其修改时间"""
        return [(str(p), os.path.getmtime(p)) for p in html_dir.get_files(".html", list_r=True)]

    def _setup_routes(self):
        """设置Flask路由"""
        @self.server.route('/show_html/<int:file_idx>')
        def show_html(file_idx):
            html_files = self._get_html_files()
            if 0 <= file_idx < len(html_files):
                html_path = html_files[file_idx][0]
                return send_file(html_path)
            return "File not found", 404

    def _initialize_app(self):
        """初始化Dash应用"""
        # 初始文件列表
        self.last_files = self._get_html_files()
        self.refresh_enabled = {idx: True for idx in range(len(self.last_files))}

        # 创建Dash应用
        self.app = dash.Dash(__name__, server=self.server)
        self.app.layout = self._create_layout()
        self._register_callbacks()

    def _create_layout(self):
        """创建Dash应用布局"""
        return html.Div([
            html.H3(f"{html_dir} 下所有 HTML 文件动态显示（智能刷新）"),
            dcc.Interval(id="interval_main", interval=1000, n_intervals=0),
            html.Div([
                html.Div([
                    html.H4(f"HTML 文件 {idx}: {os.path.basename(self.last_files[idx][0])}"),
                    html.Button(
                        id=f"refresh_btn_{idx}",
                        children="禁用自动刷新",
                        n_clicks=0,
                        style={"marginBottom": "10px"}
                    ),
                    html.Iframe(
                        id=f"iframe_{idx}",
                        src=f"/show_html/{idx}",
                        style={"width": "100%", "height": "600px", "border": "none"}
                    )
                ]) for idx in range(len(self.last_files))
            ], id="all_iframes")
        ])

    def _register_callbacks(self):
        """注册Dash回调函数"""
        from dash.dependencies import Input, Output, State

        # 按钮点击回调函数
        for idx in range(len(self.last_files)):
            @self.app.callback(
                Output(f"refresh_btn_{idx}", "children"),
                Input(f"refresh_btn_{idx}", "n_clicks"),
                prevent_initial_call=True
            )
            def toggle_refresh(n_clicks, idx=idx):
                # 切换刷新状态
                self.refresh_enabled[idx] = not self.refresh_enabled[idx]
                # 更新按钮文本
                return "禁用自动刷新" if self.refresh_enabled[idx] else "启用自动刷新"

        @self.app.callback(
            Output("all_iframes", "children"),
            Input("interval_main", "n_intervals"),
            State("all_iframes", "children"),
        )
        def update_iframes(n, children):
            new_files = self._get_html_files()
            new_paths = [p for p, _ in new_files]
            last_paths = [p for p, _ in self.last_files]

            # 检查新增/删除
            if set(new_paths) != set(last_paths):
                self.last_files = new_files.copy()
                # 更新刷新状态字典
                for idx in range(len(new_files)):
                    if idx not in self.refresh_enabled:
                        self.refresh_enabled[idx] = True
                return [
                    html.Div([
                        html.H4(f"HTML 文件 {idx}: {os.path.basename(new_files[idx][0])}"),
                        html.Button(
                            id=f"refresh_btn_{idx}",
                            children="禁用自动刷新" if self.refresh_enabled.get(idx, True) else "启用自动刷新",
                            n_clicks=0,
                            style={"marginBottom": "10px"}
                        ),
                        html.Iframe(
                            id=f"iframe_{idx}",
                            src=f"/show_html/{idx}",
                            style={"width": "100%", "height": "600px", "border": "none"}
                        )
                    ]) for idx in range(len(new_files))
                ]
            # 检查内容变化（mtime变化）
            elif any(m1 != m2 for (_, m1), (_, m2) in zip(new_files, self.last_files)):
                updated_children = children.copy()
                for idx, ((path, m_new), (_, m_old)) in enumerate(zip(new_files, self.last_files)):
                    if m_new != m_old and idx < len(children):
                        # 只有在启用刷新的情况下才更新src
                        if self.refresh_enabled.get(idx, True):
                            updated_children[idx]['props']['children'][2]['props']['src'] = f"/show_html/{idx}?t={n}"
                self.last_files = new_files.copy()
                return updated_children
            else:
                # 无变化
                return children

    def run(self):
        """运行服务器"""
        self.app.run(debug=True, port=self.port)

def show_multiple_html_with_dash(port=8051):
    """创建并运行HTML查看器服务器"""
    server = HtmlViewerServer(port)
    server.run()
#%% main
if __name__ == '__main__':
    print(f'start {__file__}')
    show_multiple_html_with_dash()
    #%% end script
    print(f'end {__file__}')
