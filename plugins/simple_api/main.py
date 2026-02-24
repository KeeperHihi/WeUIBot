from pathlib import Path

from .simple_api import get_answer, get_handwriting_image_bytes, get_word, password


class Plugin:
	def __init__(self, state):
		self.state = state

	def init(self):
		plugin_root = Path(__file__).resolve().parent
		self.images_dir = plugin_root / 'images'
		self.images_dir.mkdir(parents=True, exist_ok=True)
		print('[simple_api] init 完成')

	def is_for_me(self, msg) -> bool:
		if msg is None or msg.type != 0 or not isinstance(msg.content, str):
			return False
		if msg.sender not in set(self.state.group.get('commander', [])):
			return False
		content = msg.content
		return (
			content.startswith('加密')
			or content.startswith('解密')
			or content == '答案之书'
			or content.startswith('说句人话')
			or content.startswith('HW')
		)

	def handle_msg(self, msg):
		content = msg.content
		receiver = msg.roomid if msg.from_group() else msg.sender

		if content.startswith('加密'):
			parts = content.split(' ')
			if len(parts) < 3:
				self.state.wcf.send_text('格式错误', receiver)
				return
			key = parts[1]
			query = content[2 + 1 + len(key) + 1:]
			res = password(query, key, 1)
			if res == '':
				self.state.wcf.send_text('解析错误', receiver)
			else:
				self.state.wcf.send_text(res, receiver)
			return

		if content.startswith('解密'):
			parts = content.split(' ')
			if len(parts) < 3:
				self.state.wcf.send_text('格式错误', receiver)
				return
			key = parts[1]
			query = content[2 + 1 + len(key) + 1:]
			res = password(query, key, 2)
			if not isinstance(res, str):
				res = str(res)
			if res == '':
				self.state.wcf.send_text('解析错误', receiver)
			else:
				self.state.wcf.send_text(res, receiver)
			return

		if content == '答案之书':
			res = get_answer()
			if res == '':
				res = 'hihi'
			self.state.wcf.send_text(res, receiver)
			return

		if content.startswith('说句人话'):
			query = '新海诚'
			if len(content) > 5:
				query = content[5:]
			res = get_word(query)
			if res == '' or res.startswith('请传递需要搜索'):
				self.state.wcf.send_text('请你说人话', receiver)
				return
			self.state.wcf.send_text(res, receiver)
			return

		if content.startswith('HW'):
			text = content[3:]
			data = get_handwriting_image_bytes(text)
			if not data:
				self.state.wcf.send_text('获取失败', receiver)
				return
			out_path = self.images_dir / 'HW.png'
			out_path.write_bytes(data)
			self.state.wcf.send_image(str(out_path), receiver)

