class Plugin:
    def __init__(self, state):
        self.state = state

    def init(self):
        self.state.group.setdefault('prohibit', [])
        print('[access_control] init 完成')

    def is_for_me(self, msg) -> bool:
        if msg is None:
            return False
        return msg.sender in set(self.state.group.get('prohibit', []))

    def handle_msg(self, msg):
        receiver = msg.roomid if msg.from_group() else msg.sender
        self.state.wcf.send_text('不好意思咯！\nhihi表示不想理你😭😭', receiver)
