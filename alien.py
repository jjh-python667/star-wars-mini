from pygame.sprite import Sprite


class Alien(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.image = ai_game.images['alien']
        self.rect = self.image.get_rect()
        # 先放左上，后面再排队
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def check_edges(self):
        # 只看左右有没有碰到窗口边缘。上下边界在主程序里另算。
        screen_rect = self.screen.get_rect()
        if self.settings.fleet_direction > 0:
            return self.rect.right >= screen_rect.right
        return self.rect.left <= screen_rect.left

    def update(self, frame_scale=1.0):
        self.x += (self.settings.alien_speed *
                   self.settings.fleet_direction * frame_scale)
        self.rect.x = round(self.x)
