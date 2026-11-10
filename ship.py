from pygame.sprite import Sprite


class Ship(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.play_area.copy()

        self.image = ai_game.images['ship']
        self.rect = self.image.get_rect()
        # 底部中间
        self.rect.midbottom = self.screen_rect.midbottom

        # 用小数记位置
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self, frame_scale=1.0):
        direction = int(self.moving_right) - int(self.moving_left)
        self.x += direction * self.settings.ship_speed * frame_scale
        # Clamp the floating-point position too, including at higher levels.
        self.x = max(self.screen_rect.left, min(
            self.x, self.screen_rect.right - self.rect.width))
        self.rect.x = round(self.x)

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        # 撞完拉回来
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
