from pathlib import Path

import utils as U
from Wcf import Wcf


class State:
    def __init__(self):
        # 通用全局变量
        self.base_path = Path(__file__).resolve().parent
        self.config = U.load_yaml(self.base_path / 'config' / 'config.yaml')
        self.group = self.config.get('group', {}) # 用户分类，比如 owner, commander, prohibit
        self.stop_requested = False


    def init(self):
        # Wcf 相关，涉及到 UI 操作
        self.wcf = Wcf()
        self.friend_names = self.wcf.get_friends()
        self.stop_requested = False


    def print_state(self):
        print(f'当前工作目录：{self.base_path}')
        print('好友列表如下：')
        for friend_name in self.friend_names:
            print(friend_name)
        print()
        print('管理员列表如下：')
        for person in self.group.get('commander', []):
            print(person, end=', ')


state = State()
