#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)
from rich.progress import Progress, TimeRemainingColumn, BarColumn, TimeElapsedColumn, ProgressColumn
import time
progress = Progress(
    "[progress.description]{task.description}",
    BarColumn(bar_width=10),
    "[progress.percentage]{task.percentage:>3.0f}%",
    "{task.completed}:", TimeElapsedColumn(),
    "{task.total}:", TimeRemainingColumn(),  # 使用内置列
    expand=True,
    transient=True,
    )
def rich_tqdm(iterable, progress=progress, count_time=True, **kwargs):
    
    kwargs['description'] = kwargs.get('description', kwargs.get('desc', 'processing'))
    # 如果有任务了，就打开进度条
    if count_time:
        start_time = time.time()
    with progress:
        if not 'total' in kwargs:
            try:
                total = len(iterable)
            except:
                total = 100
            kwargs['total'] = total
        try:
            task = progress.add_task(**kwargs)
            for item in iterable:
                progress.update(task, advance=0)
                yield item
                progress.update(task, advance=1)
        finally:
            progress.remove_task(task)
            if count_time:
                print(f'cost time for {task}: {time.time()-start_time}')

#%% main
if __name__ == '__main__':
    print(f'start {__file__}')

    import time
    for i in rich_tqdm(range(100), desc='test'):
        for j in rich_tqdm(range(100), desc='test2'):
            time.sleep(0.01)
        time.sleep(0.1) 
     
    
    #%% end script
    print(f'end {__file__}')
