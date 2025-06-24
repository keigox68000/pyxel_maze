import pyxel
import random

# --- 定数 ---
# 迷路のセルの数
MAZE_WIDTH = 20
MAZE_HEIGHT = 20

# 描画設定：迷路の1ブロックを何ピクセルで描画するか
SCALE = 2

# 画面サイズを計算
SCREEN_WIDTH = (MAZE_WIDTH * 2 + 1) * SCALE
SCREEN_HEIGHT = (MAZE_HEIGHT * 2 + 1) * SCALE

# 壁の方向を表す定数 (ビットマスク用)
N, S, E, W = 1, 2, 4, 8
OPPOSITE = {E: W, W: E, N: S, S: N}


# --- メインアプリケーションクラス ---
class App:
    def __init__(self):
        """アプリケーションの初期化"""
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Maze Game", fps=30)

        # ゲームの状態を管理する変数を初期化
        self.goal_reached = False

        self.generate_new_maze()

        pyxel.run(self.update, self.draw)

    def generate_new_maze(self):
        """新しい迷路データを生成し、ゲームの状態をリセットする"""
        # 1. 20x20の迷路データを生成する (再帰的バックトラッカー法)
        self.maze_data = self._create_maze_data()

        # 2. 迷路データから描画用の高解像度グリッドを生成する
        self.display_grid = self._create_display_grid(self.maze_data)

        # 3. スタートとゴールの位置を設定
        self.start_cell = (MAZE_WIDTH - 1, MAZE_HEIGHT - 1)
        self.goal_cell = (0, 0)

        # 4. プレイヤーの位置をスタート地点にリセット (描画グリッド座標系に変更)
        self.player_gx = self.start_cell[0] * 2 + 1
        self.player_gy = self.start_cell[1] * 2 + 1

        # 5. ゴール状態をリセット
        self.goal_reached = False

    def _create_maze_data(self):
        """再帰的バックトラッカー法で迷路の接続情報を生成する"""
        maze = [[0] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
        visited = [[False] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
        stack = []

        cx, cy = MAZE_WIDTH - 1, MAZE_HEIGHT - 1
        visited[cy][cx] = True
        stack.append((cx, cy))

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for direction, (dx, dy) in [
                (N, (0, -1)),
                (S, (0, 1)),
                (W, (-1, 0)),
                (E, (1, 0)),
            ]:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < MAZE_WIDTH
                    and 0 <= ny < MAZE_HEIGHT
                    and not visited[ny][nx]
                ):
                    neighbors.append((nx, ny, direction))

            if neighbors:
                nx, ny, direction = random.choice(neighbors)
                maze[cy][cx] |= direction
                maze[ny][nx] |= OPPOSITE[direction]
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        return maze

    def _create_display_grid(self, maze_data):
        """迷路データから、描画用の詳細なグリッドを生成する"""
        grid_w = MAZE_WIDTH * 2 + 1
        grid_h = MAZE_HEIGHT * 2 + 1
        grid = [[1] * grid_w for _ in range(grid_h)]  # 1:壁, 0:通路

        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                grid[y * 2 + 1][x * 2 + 1] = 0
                if maze_data[y][x] & S:
                    grid[y * 2 + 2][x * 2 + 1] = 0
                if maze_data[y][x] & E:
                    grid[y * 2 + 1][x * 2 + 2] = 0
        return grid

    def update(self):
        """毎フレームの更新処理"""
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_R):
            self.generate_new_maze()
            return

        if self.goal_reached:
            return

        # プレイヤーの移動処理
        if pyxel.btn(pyxel.KEY_UP):
            if self.display_grid[self.player_gy - 1][self.player_gx] == 0:
                self.player_gy -= 1
        elif pyxel.btn(pyxel.KEY_DOWN):
            if self.display_grid[self.player_gy + 1][self.player_gx] == 0:
                self.player_gy += 1
        elif pyxel.btn(pyxel.KEY_LEFT):
            if self.display_grid[self.player_gy][self.player_gx - 1] == 0:
                self.player_gx -= 1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            if self.display_grid[self.player_gy][self.player_gx + 1] == 0:
                self.player_gx += 1

        # ゴール判定
        goal_gx = self.goal_cell[0] * 2 + 1
        goal_gy = self.goal_cell[1] * 2 + 1
        if (self.player_gx, self.player_gy) == (goal_gx, goal_gy):
            self.goal_reached = True

    def draw(self):
        """毎フレームの描画処理"""
        # 背景を壁の色(白)でクリア
        pyxel.cls(7)

        # 描画用グリッドを元に迷路を描画
        for y, row in enumerate(self.display_grid):
            for x, cell_type in enumerate(row):
                if cell_type == 0:  # 0なら通路
                    # 通路を黒で描画
                    pyxel.rect(x * SCALE, y * SCALE, SCALE, SCALE, 0)

        # スタート(赤)とゴール(緑)を表示
        start_gx, start_gy = self.start_cell[0] * 2 + 1, self.start_cell[1] * 2 + 1
        pyxel.rect(start_gx * SCALE, start_gy * SCALE, SCALE, SCALE, 8)
        goal_gx, goal_gy = self.goal_cell[0] * 2 + 1, self.goal_cell[1] * 2 + 1
        # ゴールの色を黄色から緑に変更して見やすくする
        pyxel.rect(goal_gx * SCALE, goal_gy * SCALE, SCALE, SCALE, 11)

        # プレイヤーを描画 (水色)
        pyxel.rect(self.player_gx * SCALE, self.player_gy * SCALE, SCALE, SCALE, 12)

        # ゴールメッセージの表示
        if self.goal_reached:
            msg = "GOAL!"
            msg_w = len(msg) * pyxel.FONT_WIDTH
            msg_x = (SCREEN_WIDTH - msg_w) / 2
            msg_y = (SCREEN_HEIGHT - pyxel.FONT_HEIGHT) / 2
            # メッセージの背景を白に、文字を黒にする
            pyxel.rect(msg_x - 2, msg_y - 2, msg_w + 4, pyxel.FONT_HEIGHT + 4, 7)
            pyxel.text(msg_x, msg_y, msg, 0)

        # 操作説明のテキストを削除


App()
