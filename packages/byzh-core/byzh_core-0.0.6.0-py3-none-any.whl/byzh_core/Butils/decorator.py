def b_validate_params(specs): # specs是@validate_params()传入的内容
    '''
    >>> @b_validate_params({
    >>>     "my_str": {"literal": "happy" or "sad"},
    >>>     "my_int": {"example": 114514}
    >>> })
    >>> def awa(my_str, my_int):
    >>>     return "qwq"
    '''
    def decorator(func): # func是调用修饰器的函数本身
        def wrapper(*args, **kwargs): # *args, **kwargs是函数本身收到的参数
            ...
            return func(*args, **kwargs) # 在此处真正调用函数本身
        return wrapper
    return decorator