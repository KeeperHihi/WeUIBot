import queue
import subprocess
import threading


class Plugin:
    def __init__(self, state):
        self.state = state
        self.output_queue = queue.Queue()
        self.cmd = 'error'
        self.cmd_mode = False
        self.cmd_event = threading.Event()
        self.process = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore',
        )
        self.owner_name = (self.state.group.get('owner') or [None])[0]

    def init(self):
        threading.Thread(target=self._read_output, daemon=True).start()
        threading.Thread(target=self._run, daemon=True).start()
        print('[cmd] init 完成')

    def is_for_me(self, msg) -> bool:
        if msg is None or msg.type != 0 or not isinstance(msg.content, str):
            return False
        if msg.sender != self.owner_name:
            return False
        text = msg.content.strip()
        return text.startswith('ps') or self.cmd_mode

    def handle_msg(self, msg):
        cmd = msg.content.strip()
        receiver = msg.roomid if msg.from_group() else msg.sender
        if cmd == 'ps':
            self.cmd_mode = True
            self.state.wcf.send_text('进入命令模式', receiver)
        elif cmd == 'exit':
            self.cmd_mode = False
            self.state.wcf.send_text('退出命令模式', receiver)
        self.cmd = cmd
        self.cmd_event.set()

    def _run(self):
        pre_cmd = self.cmd
        while True:
            self.cmd_event.wait()
            self.cmd_event.clear()
            cmd = self.cmd
            if not self.cmd_mode or cmd == 'ps' or cmd == 'exit':
                continue
            if cmd == pre_cmd:
                continue
            print('in thread cmd =', cmd)
            pre_cmd = cmd

            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()

            output = ''
            while True:
                try:
                    line = self.output_queue.get(timeout=0.2)
                    output += line + '\n'
                except queue.Empty:
                    break

            if cmd == 'pwd' and len(output) > 11:
                output = output[11:]
                while output and output[-1] == '\n':
                    output = output[:-1]

            if self.owner_name:
                self.state.wcf.send_text(output, self.owner_name)

    def _read_output(self):
        for line in iter(self.process.stdout.readline, ''):
            self.output_queue.put(line.strip())
        self.process.stdout.close()
