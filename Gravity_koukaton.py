import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_FIRES = 5 # enemyの数
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
    def __init__(self, gravity: float = 0.5, jump_power: float = -20):
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


class Stege:
    """
    ステージに関するクラス
    """
    def __init__(self):
        #ステージを描画する四角形
        self.images = [
        [pg.Rect(0,500,300,20),
        pg.Rect(250,250,300,20),
        pg.Rect(500,500,300,20),
        pg.Rect(750,250,300,20),
        pg.Rect(1000,500,300,20)],
        [pg.Rect(0,560,80, 20),
        pg.Rect(100,350,40,20),
        pg.Rect(120,40,100,20),
        pg.Rect(225,570,50,20),
        pg.Rect(335,570,40,20),
        pg.Rect(440,570,100,20),
        pg.Rect(470,60,100,20),
        pg.Rect(640,60,100,20),
        pg.Rect(720,300,80,20),
        pg.Rect(830,60,80,20),
        pg.Rect(970,500,100,20)],
        [pg.Rect(30,580,20,20),
        pg.Rect(80,70,20,20),
        pg.Rect(140,580,20,20),
        pg.Rect(190,70,20,20),
        pg.Rect(232,580,20,20),
        pg.Rect(360,70,20,20),
        pg.Rect(480,580,20,20),
        pg.Rect(600,70,20,20),
        pg.Rect(705,70,20,20),
        pg.Rect(820,450,20,20),
        pg.Rect(900,580,20,20),
        pg.Rect(970,10,200,20),
        ]
        ]
        self.door_positions = [
            (1050, 460),  # ステージ1のドアの座標
            (1020, 450),  # ステージ2のドアの座標
            (1000, 100)   # ステージ3のドアの座標
        ]
        self.current_stage_index = 0
        self.image = self.images[self.current_stage_index]
        self.display_stage_message = False  # ステージ切り替え時の表示フラグ
        self.message_timer = 0  # ステージ切り替えメッセージの表示時間
        self.door_image = pg.image.load("fig/wooden-door.png")  # ドアの画像をロード
        self.door_rect = self.door_image.get_rect()
        self.display_stage_message = False  # ステージ切り替え時の表示フラグ
        self.message_timer = 0
        #ドアのサイズをbirdと同じにする
        bird_size = Bird.img.get_size()
        self.door_image = pg.transform.scale(pg.image.load("fig/wooden-door.png"), bird_size)
        self.door_rect = self.door_image.get_rect()
        self.goal = False
    def draw(self, screen: pg.Surface):
        """
        ステージ、ドア、文字の描画とゴールの処理
        引き値:　pg.Surface
        戻り値:
        """
        for x in self.image:
            pg.draw.rect(screen, (0, 0, 0), x)
        #ドアの描画
        if self.door_rect:
            screen.blit(self.door_image, self.door_rect)
        #ステージ変更時に文字を描画
        if self.display_stage_message:
            font = pg.font.Font(None, 50)
            text = font.render(f"stage {self.current_stage_index + 1}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            self.message_timer += 1
            if self.message_timer > 100:  
                self.display_stage_message = False
                self.message_timer = 0
        #ゴール処理
        if self.goal:
            font = pg.font.Font(None, 100)
            text = font.render("Goal", True, (0,0,0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
        

    def hit_stage(self, bird: Bird):
        """
        Birdがステージやドアに接触した場合の処理
        引数:Birdオブジェクト
        戻り値:Birdが地面やドアに接触したかどうか
        """
        bird_hit_stage = False
        for rect in self.image:
            if bird.gravity_maneger.gravity > 0:  # 通常の重力（下向き）
                if bird.rct.colliderect(rect) and bird.rct.bottom > rect.top:
                    bird.rct.bottom = rect.top
                    bird.vy = 0
                    bird_hit_stage = True
                    break
            else:  # 重力反転（上向き）
                if bird.rct.colliderect(rect) and bird.rct.top < rect.bottom:
                    bird.rct.top = rect.bottom
                    bird.vy = 0
                    bird_hit_stage = True
                    break


        # ドアに触れた場合の処理
        if self.door_rect and bird.rct.colliderect(self.door_rect):
            if self.current_stage_index == len(self.images) - 1:  # 最終ステージの場合
                self.goal = True
            else:
                self.current_stage_index += 1
                self.image = self.images[self.current_stage_index]
                self.display_stage_message = True
                self.setup_door(bird)
            return True

        bird.gravity_maneger.flag = not bird_hit_stage
        return bird_hit_stage
    
    def setup_door(self, bird: Bird):
        """
        ステージに応じてドアを設定し、必要に応じてBirdの初期位置を更新する
        引数:
        bird: Birdオブジェクト
        """
        if self.current_stage_index < len(self.door_positions):
            door_position = self.door_positions[self.current_stage_index]
            self.door_rect.topleft = door_position  # ドアの位置を更新

            if self.current_stage_index == 2:  # ステージ3の場合
                bird.rct.center = (30, 500)  # Birdの位置をステージ3用に変更
            else:
                bird.rct.center = (30, 540)  # Birdを初期位置に戻す
        else:
            self.door_rect = None  # ドアがない場合
# class Explosion:
#     """
#     爆発に関するクラス
#     """
#     def __init__(self, bomb:"Bomb"):
#         """
#         爆弾の位置に爆発のgifを描画する
#         引数：爆弾のクラス
#         """
#         self.life = 100
#         self.img = pg.image.load(f"fig/explosion.gif")
#         self.img_rct = self.img.get_rect()
#         self.img_rct.center = bomb.rct.center

#     def update(self, screen: pg.Surface):
#         """
#         爆発をlifeの時間分画像を反転させながら描画する
#         引数 screen:画面のSurface
#         """
#         self.life -= 1
#         if self.life > 0:
#             if self.life % 2 == 0:
#                 self.img = pg.transform.flip(self.img, -1, -1)
#             screen.blit(self.img, self.img_rct)


class Enemy:
    """
    こうかとんをこの世から消し去るためステージに置かれるりんごのクラス
    """
    def __init__(self, x:int, y:int, speed):
        """
        りんごの読み込みと初期速度
        """
        self.vy = speed
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/ringo.png"), 0, 0.05)
        self.rct = self.img.get_rect()
        self.rct.center = (x, y)
        self.rct.top = y
        self.x = x
        self.y = y

    def update(self, screen: pg.Surface):
        """
        りんごを速度ベクトルself.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if self.rct.bottom >= HEIGHT:
            self.rct.top = 10
        if self.rct.top <= 0:
            self.rct.bottom = 640
        self.rct.move_ip(0, self.vy)
        screen.blit(self.img, self.rct)
        

class ClearObj:
    def __init__(self, x:int, y:int):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/glayringo.png"), 0, 0.1)
        self.rct = self.img.get_rect()
        self.rct.right = x
        self.rct.bottom = y
        
    def update(self, screen: pg.Surface):
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("グラビティだよ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")

    gravity_manager = Gravity()
    bird = Bird((300, 200), gravity_manager)
    stage = Stege()
    stage.setup_door(bird)
    cringo = ClearObj(WIDTH, HEIGHT)
    isgravity = 0
    enemies1 = [
        Enemy(400, 15, 2),
        Enemy(400, 138, 2),
        Enemy(400, 266, 2),
        Enemy(400, 394, 2),
        Enemy(400, 522, 2)
    ]
    enemies2 = [
        Enemy(700, 15, -2),
        Enemy(700, 138, -2),
        Enemy(700, 266, -2),
        Enemy(700, 394, -2),
        Enemy(700, 522, -2)
    ]

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

                if bird.gravity_maneger.flag == False:  # 地面にいるときだけジャンプ
                    bird.vy = bird.gravity_maneger.jump()
                    bird.gravity_maneger.flag = True
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                gravity_manager.reverse_gravity(bird)
                bird.g_switch = not bird.g_switch
            if event.type == pg.KEYDOWN and event.key == pg.K_g and isgravity == 1:
                isgravity = 1 - isgravity
                screen.blit(bg_img, [0, 0])

        # if stage.hit_stage(bird):
        #     pass #これをするとこうかとんが振動しなくなる
        #goal処理
        if stage.goal:
            screen.fill((255, 255, 255))
            font = pg.font.Font(None, 100)
            text = font.render("Goal", True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            pg.display.update()  # ゴールメッセージを画面に反映
            pg.time.wait(2000)  # 「Goal」を2秒間表示
            return  # ゲーム終了
                
            
            

        for enemy in enemies1:
            if bird.rct.colliderect(enemy.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
            
        for enemy in enemies2:
            if bird.rct.colliderect(enemy.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
            
        if bird.rct.colliderect(cringo.rct):
                bird.change_img(6, screen)
                pg.display.update()
                time.sleep(1)
                return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        #enemy1.update(screen)
        cringo.update(screen)
        
        for enemy in enemies1:
            enemy.update(screen)
        for enemy in enemies2:
            enemy.update(screen)


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
