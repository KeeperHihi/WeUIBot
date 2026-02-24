from PIL import Image, ImageDraw, ImageFont

def Draw(board, cell_size=30, filename='board.png'):
    """
    根据字符矩阵生成五子棋棋盘图片
    参数：
    board - 二维列表，包含 7 0 1 的矩阵
    cell_size - 每个格子的像素大小 (默认30)
    filename - 输出文件名 (默认board.png)
    """
    # 计算画布尺寸
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    width = (cols + 2) * cell_size + 1  # 多一列用于显示字母坐标
    height = (rows + 2) * cell_size + 1  # 多一行用于显示字母坐标

    # 创建白色背景图片
    img = Image.new('RGB', (width, height), (254,211,129))
    draw = ImageDraw.Draw(img)

    # 加载字体
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # 绘制棋盘网格
    for i in range(rows):
        for j in range(cols):
            # 格子左上角和右下角坐标
            x0 = (j + 1) * cell_size
            y0 = (i + 1) * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            # 绘制格子边框
            draw.rectangle([x0, y0, x1, y1], outline='black')

            # 计算圆心坐标和半径
            center_x = x0 + cell_size // 2
            center_y = y0 + cell_size // 2
            radius = cell_size // 2 - 2  # 留出边距

            # 根据字符绘制棋子
            if board[i][j] == 0:
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], fill='black')
            elif board[i][j] == 1:
                # 先画白底黑边圆
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], fill='white', outline='black')

    # 绘制左侧字母坐标
    for i in range(rows):
        letter = chr(ord('a') + i)  # 'a' 到 'o' 的字母
        draw.text((5, (i + 1) * cell_size + cell_size // 8), letter, font=font, fill='black')

    # 绘制顶部字母坐标
    for j in range(cols):
        letter = chr(ord('a') + j)  # 'a' 到 'o' 的字母
        draw.text(((j + 1) * cell_size + cell_size // 3, 5), letter, font=font, fill='black')

    # 保存图片
    img.save(filename)
    print(f"棋盘已保存为 {filename}")

# 示例用法
if __name__ == "__main__":
    # 示例棋盘 (可替换为任意n*n矩阵)
    sample_board = [
        [7, 0, 1, 7],
        [1, 7, 0, 7],
        [7, 0, 7, 1],
        [1, 7, 0, 7]
    ]

    Draw(sample_board, cell_size=50, filename='sample_board_with_coords.png')
