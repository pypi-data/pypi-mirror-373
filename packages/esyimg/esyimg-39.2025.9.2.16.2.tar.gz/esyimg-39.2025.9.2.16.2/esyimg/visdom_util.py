from functools import wraps
from inspect import isfunction
from visdom import pytorch_wrap
import visdom

def is_pytorch_wrapped(method):
    # 检查方法是否已经被 pytorch_wrap 装饰
    if isfunction(method):
        if hasattr(method, '__wrapped__') and isinstance(method.__wrapped__, type(pytorch_wrap)):
            return True
    return False

def class_decorator(child_cls):
    
    child_cls.environment_name = 'main'
    child_cls.window_name = 'main'
    parent_cls = child_cls.__bases__[0]
    for name, method in parent_cls.__dict__.items():
        if callable(method) and not name.startswith('__'):
            if is_pytorch_wrapped(method):
                # 如果方法已经被 pytorch_wrap 装饰，则应用额外的装饰器
                decorated_method = my_visdom_decorator(method)
                setattr(child_cls, name, decorated_method)
    return child_cls

def my_visdom_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if not 'env' in kwargs:
            kwargs['env'] = self.environment_name
        if not 'win' in kwargs:
            kwargs['win'] = self.window_name
        return func(*args, **kwargs)
    return wrapper

@ class_decorator
class VisWindow(visdom.Visdom):
    def __init__(self, env='main', win='main', port=8097, **args):
        self.window_name = win
        self.environment_name = env
        super().__init__(env=env, port=port, **args)
    
    def myline(self, Y, X, legend=None, xlabel=None, ylabel=None, title=None, opts=None, **args):
        
        if opts is None:
            opts = {}
        if legend is not None:
            opts['legend'] = legend
        if xlabel is not None:
            opts['xlabel'] = xlabel
        if ylabel is not None:
            opts['ylabel'] = ylabel
        if title is not None:
            opts['title'] = title
        
        return self.line(Y, X, opts=opts, **args)
    
        
       
    
class ScriptVisServer:
    """
    A class representing a script visualization server.

    This class is a child class of `dict` where all members are `VisWindow` objects.

    Attributes:
        port (int): The port number for the server.
        environment_name (str): The name of the environment.
        windows (dict): A dictionary containing `VisWindow` objects.

    Methods:
        __init__(self, env, port=8097): Initializes the `ScriptVisServer` object.
        __get_item__(self, key): Retrieves a `VisWindow` object from the `windows` dictionary.

    """

    def __init__(self, env, port=8097):
        
        env = env.replace('/', '_')
        if env.startswith('_'):
            env = env[1:]
        
        self.port = port
        self.env = env
        self.windows = {}
        
    @ property
    def environment_name(self):
        return self.env
        
    def __getitem__(self, key):
        if not key in self.windows:
            self.windows[key] = VisWindow(
                env=self.environment_name, 
                win=key,
                port=self.port, 
            )
        
        return self.windows[key]

    def save(self, fig, name='_l_cache'):
        import esypro
        fig_path = esypro.MyPath(self.env).cat(name, '.png').ensure()
        fig.savefig(fig_path)
        return fig_path
    
        




#region init project
# this should advancing all the codes
from esypro import ScriptResultManager
sfs = ScriptResultManager('zqf', locals())
#endregion

#region custom defination

#endregion

#region main
if __name__ == '__main__':
    figs = ScriptVisServer(sfs)
    figs['test'].line([1,2,3,4,5])
    figs['test2'].line([1,2,3,4])
    

#endregion 