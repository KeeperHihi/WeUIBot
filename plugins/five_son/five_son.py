import os
import random
import threading
import time

from .Draw_adj import Draw


board_root = ''
wcf = None
last_content = {}
is_gaming = {}


def send(msg, text):
    receiver = msg.roomid if msg.from_group() else msg.sender
    wcf.send_text(text, receiver)

class Five_son:
    def __init__(self):
        # 定义棋型得分常量
        self.FIVE = 1000000
        self.LIVE_FOUR = 10000
        self.CHONG_FOUR = 5000
        self.LIVE_THREE = 1000
        self.SLEEP_THREE = 200
        self.LIVE_TWO = 100
        self.SLEEP_TWO = 10
        self.DEFEND_WEIGHT = 1.2  # 防守得分权重
        self.boardname='board.png'

    def show(self, msg, adj):
        board_path = os.path.join(board_root, msg.sender + '.png')
        Draw(adj, filename=board_path)
        receiver = msg.roomid if msg.from_group() else msg.sender
        res = wcf.send_image(board_path, receiver)
        print(f'res = {res}')
        # n = len(adj)
        # print("  ", end="")
        # for i in range(n):
        #     print(chr(ord('a') + i), end=" \n"[i == n - 1])
        # for i in range(n):
        #     print(chr(ord('a') + i), end=" ")
        #     for j in range(n):
        #         if adj[i][j] == 7:
        #             c = '.'
        #         elif adj[i][j] == 0:
        #             c = 'X'
        #         elif adj[i][j] == 1:
        #             c = 'O'
        #         print(c, end=" \n"[j == n - 1])
        # print()

    def check(self, adj):
        n = len(adj)
        cnt = 0
        for i in range(n):
            for j in range(n):
                cnt += adj[i][j] == 7
                cur = []
                for a in range(5):
                    if i - a < 0: break
                    cur.append(adj[i - a][j])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if i - a < 0 or j + a >= n: break
                    cur.append(adj[i - a][j + a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if j + a >= n: break
                    cur.append(adj[i][j + a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if i + a >= n or j + a >= n: break
                    cur.append(adj[i + a][j + a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if i + a >= n: break
                    cur.append(adj[i + a][j])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if i + a >= n or j - a < 0: break
                    cur.append(adj[i + a][j - a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if j - a < 0: break
                    cur.append(adj[i][j - a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()

                for a in range(5):
                    if i - a < 0 or j - a < 0: break
                    cur.append(adj[i - a][j - a])
                if cur.count(0) == 5: return 0
                if cur.count(1) == 5: return 1
                cur.clear()
        if cnt == 0:
            return 3
        return 2

    # 辅助函数：在给定方向评估当前玩家下子的得分
    def evaluateDirection(self, x, y, dx, dy, player, adj):
        n = len(adj)
        left = 0
        right = 0

        # 向左/上方向检查连续棋子
        i = x - dx
        j = y - dy
        while i >= 0 and i < n and j >= 0 and j < n and adj[i][j] == player:
            left += 1
            i -= dx
            j -= dy

        # 向右/下方向检查连续棋子
        i = x + dx
        j = y + dy
        while i >= 0 and i < n and j >= 0 and j < n and adj[i][j] == player:
            right += 1
            i += dx
            j += dy

        total = left + right + 1

        # 判断左右是否开放
        leftOpen = False
        rightOpen = False
        li = x - dx * (left + 1)
        lj = y - dy * (left + 1)
        if li >= 0 and li < n and lj >= 0 and lj < n and adj[li][lj] == 7:
            leftOpen = True
        ri = x + dx * (right + 1)
        rj = y + dy * (right + 1)
        if ri >= 0 and ri < n and rj >= 0 and rj < n and adj[ri][rj] == 7:
            rightOpen = True

        # 根据棋型返回得分
        if total >= 5:
            return self.FIVE
        elif total == 4:
            if leftOpen and rightOpen: return self.LIVE_FOUR
            elif leftOpen or rightOpen: return self.CHONG_FOUR
        elif total == 3:
            if leftOpen and rightOpen: return self.LIVE_THREE
            elif leftOpen or rightOpen: return self.SLEEP_THREE
        elif total == 2:
            if leftOpen and rightOpen: return self.LIVE_TWO
            elif leftOpen or rightOpen: return self.SLEEP_TWO
        return 0

    # 评估在(x,y)位置下子对player的得分
    def evaluatePosition(self, x, y, player, adj):
        score = 0
        # 四个方向：水平、垂直、两对角线
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dir in dirs:
            score += self.evaluateDirection(x, y, dir[0], dir[1], player, adj)
        return score

    # 计算评分矩阵
    def calculate_score_matrix(self, adj, player):
        n = len(adj)
        score = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if adj[i][j] == 7:  # 空位
                    attack = self.evaluatePosition(i, j, player, adj)
                    defend = self.evaluatePosition(i, j, player ^ 1, adj)
                    score[i][j] = attack + defend * self.DEFEND_WEIGHT
                else:
                    score[i][j] = -1
        return score

    def decider(self, adj, player):
        n = len(adj)
        score = self.calculate_score_matrix(adj, player)
        mx = -1
        pos = []
        for i in range(n):
            for j in range(n):
                if score[i][j] > mx:
                    pos.clear()
                    pos.append([i, j])
                    mx = score[i][j]
                elif score[i][j] == mx:
                    pos.append([i, j])
        x, y = pos[random.randint(0, len(pos) - 1)]
        return (x, y)


def playing(msg, player, n):

    game = Five_son()
    adj = [[7 for _ in range(n)] for _ in range(n)]

    if player == 1:
        adj[n // 2][n // 2] = 0

    game.show(msg, adj)

    last_inpos = last_content[msg.sender]



    while True:
        inpos = last_content[msg.sender]
        if inpos == last_inpos:
            time.sleep(1)
            continue
        last_inpos = inpos
        if inpos == '？？？':
            continue
        if inpos == '我不想玩了':
            send(msg, '那好吧呜呜呜😭拜拜')
            break
        if len(inpos) != 2:
            send(msg, '无效输入 (输入格式：fh)')
            continue
        if not inpos.isalpha():
            send(msg, '无效输入 (输入格式：fh)')
            continue
        mx = ord(inpos[0]) - ord('a')
        my = ord(inpos[1]) - ord('a')
        if mx >= n or my >= n:
            send(msg, '超出棋盘范围！')
            continue
        if adj[mx][my] != 7:
            send(msg, '无效位置 (该处已落子)')
            continue
        adj[mx][my] = player
        if game.check(adj) == 3:
            send(msg, '跟我下还能和棋？？\n你个笨蛋👎')
            break
        if game.check(adj) == player:
            game.show(msg, adj)
            time.sleep(0.5)
            send(msg, '恭喜！😀\n你赢嘞！！！😊')
            break
        rx, ry = game.decider(adj, player ^ 1)
        adj[rx][ry] = player ^ 1
        game.show(msg, adj)
        if game.check(adj) == 3:
            send(msg, '跟我下还能和棋？？\n你个笨蛋👎')
            break
        if game.check(adj) == (player ^ 1):
            time.sleep(0.5)
            send(msg, '你个蠢货...我真无语了...')
            break

    is_gaming[msg.sender] = False



def add_player(msg, character, n):
    thread = threading.Thread(target=playing, args=(msg, character, n))
    thread.start()








if __name__ == '__main__':
    pass
