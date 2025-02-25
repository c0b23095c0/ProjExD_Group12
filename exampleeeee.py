import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Gravity:
    """
    重力とジャンプを管理するクラス
    """
    def __init__(self, gravity: float = 0.5, jump_power: float = -10):
        """
        初期化
        引数:gravity: 下方向の加速度
            jump_power: ジャンプ時の上向き速度
        """
        self.gravity = gravity
        self.jump_power = jump_power

    def apply_gravity(self, vy: float) -> float:
        """
        縦方向速度に重力を適用する
        引数:vy:現在の縦方向速度
        戻り値:縦方向の速度
        """
        return vy + self.gravity

    def jump(self) -> float:
        """
        ジャンプ時の速度を返す
        戻り値:ジャンプの初速度
        """
        return self.jump_power
    
    def reverse_gravity(self, bird):
        """
        重力を反転させる
        """
        self.gravity = -self.gravity
        self.jump_power = -1 * self.jump_power
        bird.flip_v()


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_LEFT: (-3, 0),
        pg.K_RIGHT: (+3, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {
            (+3, 0): img,  # 右
            (-3, 0): img0,  # 左
        }

    def __init__(self, xy: tuple[int, int], gravity_manager: Gravity):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+3, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

        self.dire = (+3, 0)
        self.vy = 0
        self.gravity_maneger = gravity_manager
        self.reversing = False
        self.g_switch =False

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)

        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = sum_mv
        self.vy = self.gravity_maneger.apply_gravity(self.vy)
        self.rct.centery += self.vy

        # 地面・天井判定
        if self.gravity_maneger.gravity > 0:
            # 地面判定
            if self.rct.bottom >= HEIGHT:
                self.rct.bottom = HEIGHT
                self.vy = 0
               
        # 天井判定
        else:
            if self.rct.top <= 0:
                self.rct.top = 0
                self.vy = 0 

        # 横方向の向きを更新
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            if  self.g_switch:
                self.img = pg.transform.flip(self.img, False, True)

            self.dire = sum_mv
        
        if self.reversing:
            self.img = pg.transform.flip(self.img, False, True)
            self.flip_v()
        screen.blit(self.img, self.rct)
    
    def flip_v(self):
        """
        こうかとん描写の上下反転
        """
        self.reversing = not self.reversing


class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self, bomb:"Bomb"):
        """
        爆弾の位置に爆発のgifを描画する
        引数：爆弾のクラス
        """
        self.life = 100
        self.img = pg.image.load(f"fig/explosion.gif")
        self.img_rct = self.img.get_rect()
        self.img_rct.center = bomb.rct.center

    def update(self, screen: pg.Surface):
        """
        爆発をlifeの時間分画像を反転させながら描画する
        引数 screen:画面のSurface
        """
        self.life -= 1
        if self.life > 0:
            if self.life % 2 == 0:
                self.img = pg.transform.flip(self.img, -1, -1)
            screen.blit(self.img, self.img_rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")

    gravity_manager = Gravity()
    bird = Bird((300, 200), gravity_manager)

    #explosionリスト初期化
    explosions = []

    clock = pg.time.Clock()
    
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                #ジャンプの処理
                if bird.rct.bottom >= HEIGHT or bird.rct.top <= 0:  # 地面にいるときだけジャンプ
                    bird.vy = gravity_manager.jump()
                
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                gravity_manager.reverse_gravity(bird)
                bird.g_switch = not bird.g_switch
        screen.blit(bg_img, [0, 0])
            
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        explosions = [explosion for explosion in explosions if explosion.life > 0]
        for explosion in explosions:
            explosion.update(screen)
            
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
