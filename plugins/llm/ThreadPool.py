import sys
from pathlib import Path

try:
    from .MsgQueue import MsgQueue
    from .API import API
except ImportError:
    CURRENT_DIR = Path(__file__).resolve().parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    from MsgQueue import MsgQueue
    from API import API
import threading



class ThreadPool:
    def __init__(self, friend_names, user_providers, user_sys_prompt_type, config, memory_len):
        self.models = {friend: API(
            provider_name=user_providers[friend],
            sys_prompt_type=user_sys_prompt_type[friend],
            config=config
        ) for friend in friend_names}  # str -> str
        self.threads = {}  # int -> threading.Thread
        self.model_response = {}  # int -> str
        self.thread_idx = 0
        self._idx_lock = threading.Lock()
        self._response_lock = threading.Lock()
        self.msg_queues = {friend: MsgQueue(memory_len) for friend in friend_names}

    def _get_idx(self):
        with self._idx_lock:
            if self.thread_idx >= 2_000_000_000:
                self.thread_idx = 0
            self.thread_idx += 1
            return self.thread_idx

    def _run_model(self, idx, sender):
        response = self.models[sender].sending_list(self.msg_queues[sender].content())
        with self._response_lock:
            self.model_response[idx] = response

    def add_msg(self, sender, msg):
        self.msg_queues[sender].put(msg)

    def clear(self, reloader):
        self.msg_queues[reloader].clear()

    def send_msg(self, msg, sender):
        '''
        创建发送这个 msg 的线程

        :param: msg, sender
        :return: 这个 msg 对应的编号
        '''
        self.msg_queues[sender].check_len()
        self.add_msg(sender, msg)
        idx = self._get_idx()
        thread = threading.Thread(target=self._run_model, args=(idx, sender))
        thread.start()
        print('线程正在运行...')
        self.threads[idx] = thread
        return idx

    def get_response(self, idx):
        self.threads[idx].join()
        print('线程运行完毕！')
        with self._response_lock:
            if idx not in self.model_response:
                return None
            response = self.model_response[idx]
            del self.model_response[idx]
        del self.threads[idx]
        return response









if __name__ == '__main__':
    demo_config = {
        'api': {
            'providers': {
                'RightCode': {
                    'api_key': '',
                    'url': 'https://api.openai.com/v1',
                    'model': 'gpt-4o-mini',
                }
            }
        },
        'model': {}
    }
    threadpool = ThreadPool(
        friend_names=['me'],
        user_providers={'me': 'RightCode'},
        user_sys_prompt_type={'me': 'zhu'},
        config=demo_config,
        memory_len=20
    )

    msg = {
        'role': 'user',
        'content': '你好'
    }

    idx1 = threadpool.send_msg(msg, sender='文件传输助手')
    idx2 = threadpool.send_msg(msg, sender='jrh')
    idx3 = threadpool.send_msg(msg, sender='wsh')
    response1 = threadpool.get_response(idx1)
    print(response1)
    response2 = threadpool.get_response(idx2)
    print(response2)
    response3 = threadpool.get_response(idx3)
    print(response3)

