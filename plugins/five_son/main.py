from pathlib import Path
import os

from . import five_son


class Plugin:
	def __init__(self, state):
		self.state = state
		self.last_content = {}
		self.is_gaming = {}

	def init(self):
		plugin_root = Path(__file__).resolve().parent
		board_root = plugin_root / 'board'
		board_root.mkdir(parents=True, exist_ok=True)
		five_son.board_root = str(board_root)
		five_son.wcf = self.state.wcf
		five_son.last_content = self.last_content
		five_son.is_gaming = self.is_gaming
		print('[five_son] init 完成')

	def is_for_me(self, msg) -> bool:
		if msg is None or msg.type != 0 or not isinstance(msg.content, str):
			return False
		sender = msg.sender
		if self.is_gaming.get(sender, False):
			return True
		if msg.sender not in set(self.state.group.get('commander', [])):
			return False
		return msg.content.startswith('来把五子棋')

	def handle_msg(self, msg):
		sender = msg.sender
		text = msg.content.strip()
		self.last_content.setdefault(sender, '')

		if self.is_gaming.get(sender, False):
			if text == '？？？':
				board_path = os.path.join(five_son.board_root, sender + '.png')
				receiver = msg.roomid if msg.from_group() else msg.sender
				self.state.wcf.send_image(board_path, receiver)
			self.last_content[sender] = text
			return

		if len(text) < 9:
			self._send(msg, '语法错误')
			return
		if not text[6].isdigit() or not text[8:].isdigit():
			self._send(msg, '语法错误')
			return

		character = int(text[6])
		n = int(text[8:])
		if n < 5:
			self._send(msg, '棋盘太小！')
			return
		if n > 26:
			self._send(msg, '棋盘太大！')
			return

		self.is_gaming[sender] = True
		self.last_content[sender] = '？？？'
		five_son.add_player(msg, character, n)
		self._send(msg, '来了！')

	def _send(self, msg, text):
		receiver = msg.roomid if msg.from_group() else msg.sender
		self.state.wcf.send_text(text, receiver)

