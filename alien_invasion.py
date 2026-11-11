"""纵向射击小游戏，用来练习 Pygame。

运行：python alien_invasion.py
说明和操作见 README.md。窗口标题是 Star Wars Mini。
"""

from pathlib import Path

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    def __init__(self, high_score_file=None):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        self.play_area = pygame.Rect(
            0, self.settings.hud_height, self.settings.screen_width,
            self.settings.screen_height - self.settings.hud_height -
            self.settings.controls_height)
        pygame.display.set_caption("Star Wars Mini")
        image_dir = Path(__file__).resolve().parent / 'images'
        # Each bitmap is read once, shared by the fleet and life icons.
        self.images = {
            name: pygame.image.load(image_dir / f'{name}.bmp').convert()
            for name in ('ship', 'alien')
        }

        self.stats = GameStats(self, high_score_file)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # 先别开打，等点Play
        self.game_active = False
        self.paused = False
        self.running = True
        self.respawn_remaining_ms = 0
        self.play_button = Button(self, "Play")
        self.help_font = pygame.font.Font(None, 26)
        self.help_image = self.help_font.render(
            'Arrows: move    Space: shoot    P / Esc: pause    Q: quit',
            True, (60, 60, 60))
        self.pause_image = self.play_button.font.render(
            'Paused - P / Esc to resume', True, (30, 30, 30))
        self.ready_image = self.play_button.font.render(
            'Get ready', True, (30, 30, 30))
        self.game_over_image = self.play_button.font.render(
            'Game over', True, (30, 30, 30))
        self.pause_overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.pause_overlay.fill((230, 230, 230, 210))

    def run_game(self):
        try:
            while self.running:
                # Scale speeds to this frame. A stall cannot skip more than the cap.
                frame_scale = min(
                    self.clock.tick(self.settings.fps) * self.settings.fps / 1000,
                    self.settings.max_frame_scale)
                self._check_events()
                if not self.running:
                    break
                self._update_game(frame_scale)
                self._update_screen()
        finally:
            self.stats.save_high_score()
            pygame.mouse.set_visible(True)
            pygame.quit()

    def _update_game(self, frame_scale=1.0):
        if not self.game_active or self.paused:
            return
        if self.respawn_remaining_ms > 0:
            self.respawn_remaining_ms = max(
                0, self.respawn_remaining_ms - frame_scale * 1000 / self.settings.fps)
            return
        self.ship.update(frame_scale)
        self._update_bullets(frame_scale)
        self._update_aliens(frame_scale)

    def _can_play(self):
        return (self.game_active and not self.paused and
                self.respawn_remaining_ms <= 0)

    def _stop_moving(self):
        self.ship.moving_right = False
        self.ship.moving_left = False

    def _toggle_pause(self):
        if not self.game_active:
            return
        self.paused = not self.paused
        self._stop_moving()
        pygame.mouse.set_visible(self.paused)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.WINDOWFOCUSLOST:
                self._stop_moving()
                if self.game_active and not self.paused:
                    self._toggle_pause()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
                if not self.running:
                    return
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._check_play_button(event.pos)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()

    def _start_game(self):
        # 新游戏，速度重置
        self.settings.initialize_dynamic_settings()

        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.sb.prep_high_score()

        self.bullets.empty()
        self.aliens.empty()

        self._create_fleet()
        self.ship.center_ship()
        self._stop_moving()

        self.game_active = True
        self.paused = False
        self.respawn_remaining_ms = 0
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT and self._can_play():
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT and self._can_play():
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            if not self.game_active:
                self._start_game()
            else:
                self._toggle_pause()
        elif event.key == pygame.K_ESCAPE:
            self._toggle_pause()
        elif event.key == pygame.K_q:
            self.running = False

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if not self._can_play():
            return
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self, frame_scale=1.0):
        self.bullets.update(frame_scale)

        # 飞出屏幕就删
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for hit_aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(hit_aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        # 打光了就下一关
        if len(self.aliens) == 0:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _create_fleet(self):
        # 先弄一个量宽高
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        self.settings.fleet_direction = 1

        current_x = alien_width
        current_y = self.play_area.top + alien_height
        # 底下留点空
        available_space_y = self.play_area.bottom - (4 * alien_height)

        while current_y < available_space_y:
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        # Keep the whole formation inside the screen after an overshoot.
        left = min(alien.rect.left for alien in self.aliens)
        right = max(alien.rect.right for alien in self.aliens)
        correction = max(0, -left) + min(0, self.settings.screen_width - right)
        for alien in self.aliens.sprites():
            alien.x += correction
            alien.rect.x = round(alien.x)
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self, frame_scale=1.0):
        self.aliens.update(frame_scale)
        self._check_fleet_edges()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            return

        self._check_aliens_bottom()

    def _ship_hit(self):
        if not self._can_play():
            return
        self.stats.ships_left = max(0, self.stats.ships_left - 1)
        self.sb.prep_ships()
        self._stop_moving()
        self.bullets.empty()
        self.aliens.empty()
        self.ship.center_ship()

        if self.stats.ships_left == 0:
            self.game_active = False
            self.stats.save_high_score()
            pygame.mouse.set_visible(True)
        else:
            self._create_fleet()
            # Keep polling events while the ship recovers, instead of sleeping.
            self.respawn_remaining_ms = self.settings.respawn_delay_ms

    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.play_area.bottom:
                self._ship_hit()
                break

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()
            if self.stats.ships_left == 0:
                rect = self.game_over_image.get_rect(
                    center=(self.screen.get_width() // 2,
                            self.screen.get_height() // 2 - 65))
                self.screen.blit(self.game_over_image, rect)
        elif self.paused:
            self.screen.blit(self.pause_overlay, (0, 0))
            self.screen.blit(self.pause_image, self.pause_image.get_rect(
                center=self.screen.get_rect().center))
        elif self.respawn_remaining_ms > 0:
            self.screen.blit(self.ready_image, self.ready_image.get_rect(
                center=self.screen.get_rect().center))

        self.screen.blit(self.help_image, self.help_image.get_rect(
            midbottom=(self.screen.get_width() // 2, self.screen.get_height() - 8)))

        pygame.display.flip()


def main():
    ai = AlienInvasion()
    ai.run_game()


if __name__ == '__main__':
    main()
