# 从具体模块中导入类，暴露到顶层命名空间
from .WechatSendMsg import WeComMessageHandler  # 替换成你的实际模块名

# 可选：定义 __all__，明确 from SendMsg import * 时能导入的内容
__all__ = ["WeComMessageHandler"]