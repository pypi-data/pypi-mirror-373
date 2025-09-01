

import fire 
from .dbasr import DBASR


class ENTRY(object):
    """主入口类"""
    
    def __init__(self):
        # 使用装饰器创建VPC访问控制代理
        self.dbasr  = DBASR()

    
    def auc(self):
        self.dbasr.auc()







def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)

