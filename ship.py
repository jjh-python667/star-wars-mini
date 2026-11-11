from pygame.sprite import Sprite


class Ship(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # 拷一份战斗区域。飞船只在这块里移动，不进入顶部分数和底部提示。
        self.play_area = ai_game.play_area.copy()

        self.image = ai_game.images['ship']
        self.rect = self.image.get_rect()
        # 底部中间
        self.rect.midbottom = self.play_area.midbottom

        # 用小数记位置
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self, frame_scale=1.0):
        # 同时按左右时方向是 0，飞船停在原地。
        direction = int(self.moving_right) - int(self.moving_left)
        self.x += direction * self.settings.ship_speed * frame_scale
        # Clamp the floating-point position too, including at higher levels.
        self.x = max(self.play_area.left, min(
            self.x, self.play_area.right - self.rect.width))
        self.rect.x = round(self.x)

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        # 撞完拉回来
        self.rect.midbottom = self.play_area.midbottom
        self.x = float(self.rect.x)
