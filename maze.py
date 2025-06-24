import pyxel
import random

# --- 定数 ---
# 迷路のセルの数 (40x40 に変更)
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
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Maze Game", fps=60)

        # ゲームの状態を管理する変数
        self.generating = True  # 最初は迷路生成モード
        self.goal_reached = False

        self.start_new_generation()

        pyxel.run(self.update, self.draw)

    def start_new_generation(self):
        """迷路の生成プロセスを開始/リセットする"""
        self.generating = True
        self.goal_reached = False

        # 迷路データと訪問済みフラグを初期化
        self.maze_data = [[0] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
        self.visited = [[False] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]

        # スタックを準備し、スタート地点から開始
        self.stack = []
        cx, cy = MAZE_WIDTH - 1, MAZE_HEIGHT - 1
        self.visited[cy][cx] = True
        self.stack.append((cx, cy))

        # スタートとゴールのセル座標を設定
        self.start_cell = (MAZE_WIDTH - 1, MAZE_HEIGHT - 1)
        self.goal_cell = (0, 0)

    def _create_display_grid(self, maze_data):
        """迷路データから、描画用の詳細なグリッドを生成する"""
        grid_w = MAZE_WIDTH * 2 + 1
        grid_h = MAZE_HEIGHT * 2 + 1
        grid = [[1] * grid_w for _ in range(grid_h)]  # 1:壁, 0:通路

        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                # 訪問済みのセル（通路）を描画
                if self.visited[y][x]:
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
            self.start_new_generation()
            return

        if self.generating:
            # --- 迷路生成中の処理 ---
            if self.stack:
                # 1フレームに1ステップ、迷路生成を進める
                cx, cy = self.stack[-1]
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
                        and not self.visited[ny][nx]
                    ):
                        neighbors.append((nx, ny, direction))

                if neighbors:
                    nx, ny, direction = random.choice(neighbors)
                    self.maze_data[cy][cx] |= direction
                    self.maze_data[ny][nx] |= OPPOSITE[direction]
                    self.visited[ny][nx] = True
                    self.stack.append((nx, ny))
                else:
                    self.stack.pop()
            else:
                # スタックが空になったら生成完了
                self.generating = False
                # プレイヤーをスタート地点に配置
                self.player_gx = self.start_cell[0] * 2 + 1
                self.player_gy = self.start_cell[1] * 2 + 1

        elif not self.goal_reached:
            # --- プレイヤー操作中の処理 ---
            if pyxel.btn(pyxel.KEY_UP):
                if self._is_path(self.player_gx, self.player_gy - 1):
                    self.player_gy -= 1
            elif pyxel.btn(pyxel.KEY_DOWN):
                if self._is_path(self.player_gx, self.player_gy + 1):
                    self.player_gy += 1
            elif pyxel.btn(pyxel.KEY_LEFT):
                if self._is_path(self.player_gx - 1, self.player_gy):
                    self.player_gx -= 1
            elif pyxel.btn(pyxel.KEY_RIGHT):
                if self._is_path(self.player_gx + 1, self.player_gy):
                    self.player_gx += 1

            # ゴール判定
            goal_gx = self.goal_cell[0] * 2 + 1
            goal_gy = self.goal_cell[1] * 2 + 1
            if (self.player_gx, self.player_gy) == (goal_gx, goal_gy):
                self.goal_reached = True

    def _is_path(self, gx, gy):
        """指定されたグリッド座標が通路かどうかを判定する"""
        # 迷路生成が完了してから使うため、display_gridを参照する
        # （迷路生成中は壁判定が不完全なため、移動できない）
        grid_w = MAZE_WIDTH * 2 + 1
        grid_h = MAZE_HEIGHT * 2 + 1
        if 0 <= gx < grid_w and 0 <= gy < grid_h:
            # display_gridをその場で生成して判定
            return self._create_display_grid(self.maze_data)[gy][gx] == 0
        return False

    def draw(self):
        """毎フレームの描画処理"""
        pyxel.cls(7)  # 背景を壁の色(白)でクリア

        # 描画用のグリッドを現在の迷路の状態から生成
        grid_to_draw = self._create_display_grid(self.maze_data)

        # グリッドを元に迷路を描画
        for y, row in enumerate(grid_to_draw):
            for x, cell_type in enumerate(row):
                if cell_type == 0:  # 0なら通路
                    pyxel.rect(x * SCALE, y * SCALE, SCALE, SCALE, 0)  # 通路を黒で描画

        if self.generating:
            # --- 迷路生成中の描画 ---
            if self.stack:
                # 現在の掘削位置を緑でハイライト
                cx, cy = self.stack[-1]
                gx, gy = cx * 2 + 1, cy * 2 + 1
                pyxel.rect(gx * SCALE, gy * SCALE, SCALE, SCALE, 11)
        else:
            # --- プレイヤー操作中の描画 ---
            # スタート(赤)とゴール(緑)を表示
            start_gx, start_gy = self.start_cell[0] * 2 + 1, self.start_cell[1] * 2 + 1
            pyxel.rect(start_gx * SCALE, start_gy * SCALE, SCALE, SCALE, 8)
            goal_gx, goal_gy = self.goal_cell[0] * 2 + 1, self.goal_cell[1] * 2 + 1
            pyxel.rect(goal_gx * SCALE, goal_gy * SCALE, SCALE, SCALE, 11)

            # プレイヤーを描画 (水色)
            pyxel.rect(self.player_gx * SCALE, self.player_gy * SCALE, SCALE, SCALE, 12)

            # ゴールメッセージの表示
            if self.goal_reached:
                msg = "GOAL!"
                msg_w = len(msg) * pyxel.FONT_WIDTH
                msg_x = (SCREEN_WIDTH - msg_w) / 2
                msg_y = (SCREEN_HEIGHT - pyxel.FONT_HEIGHT) / 2
                pyxel.rect(msg_x - 2, msg_y - 2, msg_w + 4, pyxel.FONT_HEIGHT + 4, 7)
                pyxel.text(msg_x, msg_y, msg, 0)


App()
