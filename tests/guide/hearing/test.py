import logging

def xinfo_decorator(original_func):
    def wrapper(self, *args, **kwargs):
        # 修改传入的消息
        # if len(args) > 0 and isinstance(args[0], str):
        args = (f"{self.__class__.__name__}: ",)
        # return original_func(self, *args, **kwargs)
        return original_func(self, *args)
    return wrapper

# def info_decorator(self, original_func):
#     def wrapper(msg0):
#         print(f'msg: {msg0}')
#         # if len(args) > 0:
#         #     print(f'args[0]: {args[0]}')
#         # if len(args) > 0 and isinstance(args[0], str):
#         #     args = ("AAA: " + args[0],) + args[1:]
#         # original_func(self, *args, **kwargs)
#         original_func(msg=self.__class__.__name__ + msg0)
#     return wrapper

class MyClass:
    def info_decorator(self, original_func):
        def wrapper(msg0):
            print(f'msg: {msg0}')
            original_func(msg=self.__class__.__name__ + msg0)
        return wrapper

    def __init__(self):
        # 创建自定义的日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 创建处理器，并将格式化器关联到处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(console_handler)

        # 对日志记录器的 info 方法应用装饰器
        self.logger.info = self.info_decorator(self.logger.info)

    def some_method(self):
        self.logger.info("message 1")
        self.logger.info("message 2")

my_object = MyClass()
my_object.some_method()
