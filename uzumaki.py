import pyxel
import math
import random


class App:
    """
    Pyxelで渦巻きアートを描画するアプリケーションクラス
    """

    def __init__(self):
        """
        アプリケーションの初期化
        """
        # 画面を幅160ピクセル, 高さ120ピクセルで初期化
        pyxel.init(160, 120, title="Uzumaki Spiral", fps=60)

        # 渦巻きの色をランダムに決定 (黒(0)以外の15色から選択)
        self.spiral_color = random.randint(1, 15)

        # 描画する線の始点を格納する変数
        self.last_x = pyxel.width / 2
        self.last_y = pyxel.height / 2

        # 渦巻きの描画を進めるためのカウンター
        self.step = 0
        self.max_steps = 1000  # 渦巻きの細かさ・長さ

        # アプリケーションを開始 (updateとdrawを繰り返し呼び出す)
        pyxel.run(self.update, self.draw)

    def update(self):
        """
        毎フレームのデータ更新処理
        """
        # 'Q'キーが押されたらアプリケーションを終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # 渦巻きを少しずつ描画していく
        if self.step < self.max_steps:
            self.step += 5  # 一度に描画するステップ数（アニメーションの速度）
            if self.step > self.max_steps:
                self.step = self.max_steps

    def draw(self):
        """
        毎フレームの描画処理
        """
        # 画面を黒(色番号0)でクリア
        # 最初の一回だけクリアしたいので、stepが小さい時だけ実行
        if self.step <= 5:
            pyxel.cls(0)
            # 画面中央に操作説明を白(7)で表示
            pyxel.text(5, 5, "Q: Quit", 7)

        # 画面の中心座標
        center_x = pyxel.width / 2
        center_y = pyxel.height / 2

        # 画面の対角線の長さの半分を計算し、渦巻きが画面全体を覆うようにする
        max_radius = math.sqrt(pyxel.width**2 + pyxel.height**2) / 2

        # updateで進めたstepまで渦巻きを描画する
        # （last_x, last_yは前回の最後の描画座標を保持している）
        for i in range(self.step - 4, self.step + 1):
            if i <= 0:
                continue

            # 角度を計算 (円周率 * 2 = 360度)。6周する渦巻きにする
            angle = (i / self.max_steps) * (math.pi * 2) * 6
            # 半径を計算
            radius = (i / self.max_steps) * max_radius

            # 極座標 (角度と半径) から直交座標 (x, y) に変換
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # 前回の点から現在の点まで線を引く
            pyxel.line(self.last_x, self.last_y, x, y, self.spiral_color)

            # 現在の点を次の描画の始点として保存
            self.last_x = x
            self.last_y = y


# Appクラスのインスタンスを作成してアプリケーションを開始
App()
