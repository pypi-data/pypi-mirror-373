#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

if __name__ == '__main__':
    from .server import show_multiple_html_with_dash, html_dir
    # 清空html_dir
    import shutil
    shutil.rmtree(html_dir)
    html_dir.ensure()
    # 启动后台服务器
    show_multiple_html_with_dash()
