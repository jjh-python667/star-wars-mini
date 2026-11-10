"""Regression tests use real Pygame sprites with an off-screen SDL display."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

from alien import Alien
from alien_invasion import AlienInvasion
from bullet import Bullet
from game_stats import GameStats
from settings import Settings


class GameTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.score_path = Path(self.directory.name) / 'high_score.txt'
        self.game = AlienInvasion(high_score_file=self.score_path)
        self.addCleanup(pygame.quit)
        pygame.event.clear()

    def key(self, key):
        self.game._check_keydown_events(pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_waits_for_play_and_inactive_space_does_nothing(self):
        self.key(pygame.K_SPACE)
        self.assertFalse(self.game.game_active)
        self.assertEqual(len(self.game.bullets), 0)

    def test_at_most_three_bullets_even_after_repeated_shots(self):
        self.game._start_game()
        for _ in range(20):
            self.key(pygame.K_SPACE)
        self.assertEqual(len(self.game.bullets), 3)
        self.game.bullets.sprites()[0].kill()
        self.key(pygame.K_SPACE)
        self.assertEqual(len(self.game.bullets), 3)

    def test_three_hits_end_the_game_without_a_fourth_life(self):
        self.game._start_game()
        for remaining in (2, 1, 0):
            self.game.respawn_remaining_ms = 0
            self.game._ship_hit()
            self.assertEqual(self.game.stats.ships_left, remaining)
            self.assertEqual(len(self.game.sb.ships), remaining)
            self.assertEqual(self.game.game_active, remaining > 0)
        self.game._ship_hit()
        self.assertEqual(self.game.stats.ships_left, 0)
        self.assertTrue(pygame.mouse.get_visible())

    def test_hit_recovery_does_not_lose_another_life_or_accept_fire(self):
        self.game._start_game()
        self.game._ship_hit()
        self.game._ship_hit()
        self.key(pygame.K_SPACE)
        self.key(pygame.K_RIGHT)
        self.assertEqual(self.game.stats.ships_left, 2)
        self.assertEqual(len(self.game.bullets), 0)
        self.assertFalse(self.game.ship.moving_right)
        self.assertEqual(self.game.respawn_remaining_ms, 500)

    def test_recovery_freezes_simulation_but_expires(self):
        self.game._start_game()
        self.game._ship_hit()
        alien = self.game.aliens.sprites()[0]
        position = alien.rect.copy()
        for _ in range(32):
            if self.game.respawn_remaining_ms <= 0:
                break
            self.game._update_game()
            self.assertEqual(alien.rect, position)
        self.assertEqual(self.game.respawn_remaining_ms, 0)
        self.game._update_game()
        self.assertGreater(alien.x, position.x)

    def test_pause_stops_motion_shots_and_recovery_timer(self):
        self.game._start_game()
        self.key(pygame.K_RIGHT)
        self.key(pygame.K_p)
        self.assertTrue(self.game.paused)
        self.assertFalse(self.game.ship.moving_right)
        before = self.game.ship.x
        aliens = [alien.x for alien in self.game.aliens]
        self.game.respawn_remaining_ms = 200
        self.key(pygame.K_RIGHT)
        self.key(pygame.K_SPACE)
        self.game._update_game(3)
        self.assertEqual(self.game.ship.x, before)
        self.assertEqual([alien.x for alien in self.game.aliens], aliens)
        self.assertEqual(self.game.respawn_remaining_ms, 200)
        self.assertEqual(len(self.game.bullets), 0)
        self.key(pygame.K_ESCAPE)
        self.assertFalse(self.game.paused)

    def test_focus_loss_pauses_and_focus_gain_needs_explicit_resume(self):
        self.game._start_game()
        self.key(pygame.K_LEFT)
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.game._check_events()
        self.assertTrue(self.game.paused)
        self.assertFalse(self.game.ship.moving_left)
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSGAINED))
        self.game._check_events()
        self.assertTrue(self.game.paused)
        self.key(pygame.K_p)
        self.assertFalse(self.game.paused)

    def test_pause_before_start_is_harmless(self):
        self.key(pygame.K_ESCAPE)
        self.assertFalse(self.game.paused)
        self.assertFalse(self.game.game_active)

    def test_click_uses_event_position_and_only_left_button(self):
        center = self.game.play_button.rect.center
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=3, pos=center))
        self.game._check_events()
        self.assertFalse(self.game.game_active)
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=center))
        self.game._check_events()
        self.assertTrue(self.game.game_active)

    def test_ship_is_clamped_at_both_edges_at_high_speed(self):
        ship = self.game.ship
        self.game.settings.ship_speed = 10000
        ship.moving_right = True
        ship.update(3)
        self.assertEqual(ship.rect.right, self.game.screen.get_width())
        self.assertEqual(ship.x, self.game.screen.get_width() - ship.rect.width)
        ship.moving_right = False
        ship.moving_left = True
        ship.update(3)
        self.assertEqual(ship.rect.left, 0)
        self.assertEqual(ship.x, 0)

    def test_opposite_directions_cancel_without_drifting(self):
        ship = self.game.ship
        before = ship.x
        ship.moving_right = ship.moving_left = True
        ship.update()
        self.assertEqual(ship.x, before)

    def test_key_release_stops_movement(self):
        self.game._start_game()
        self.key(pygame.K_RIGHT)
        self.game._check_keyup_events(
            pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT))
        before = self.game.ship.x
        self.game.ship.update()
        self.assertEqual(self.game.ship.x, before)

    def test_motion_scales_with_elapsed_time(self):
        ship = self.game.ship
        ship.moving_right = True
        start = ship.x
        ship.update(2)
        self.assertAlmostEqual(ship.x - start, 2 * self.game.settings.ship_speed)
        bullet = Bullet(self.game)
        start_y = bullet.y
        bullet.update(2)
        self.assertAlmostEqual(start_y - bullet.y, 2 * self.game.settings.bullet_speed)
        alien = Alien(self.game)
        start_x = alien.x
        alien.update(2)
        self.assertAlmostEqual(alien.x - start_x, 2 * self.game.settings.alien_speed)

    def test_offscreen_bullets_are_removed(self):
        self.game._start_game()
        self.game._fire_bullet()
        bullet = self.game.bullets.sprites()[0]
        bullet.y = -100
        self.game._update_bullets()
        self.assertEqual(len(self.game.bullets), 0)

    def test_collision_keeps_exact_75_points_and_advances_level(self):
        self.game._start_game()
        self.game.aliens.empty()
        alien = Alien(self.game)
        self.game.aliens.add(alien)
        bullet = Bullet(self.game)
        bullet.rect.center = alien.rect.center
        self.game.bullets.add(bullet)
        self.game.settings.alien_points = 75
        self.game._check_bullet_alien_collisions()
        self.assertEqual(self.game.stats.score, 75)
        self.assertEqual(self.game.stats.high_score, 75)
        self.assertEqual(self.game.stats.level, 2)
        self.assertEqual(len(self.game.bullets), 0)
        self.assertGreater(len(self.game.aliens), 0)
        self.assertFalse(self.score_path.exists(), 'Do not write a file on every hit')

    def test_new_game_resets_difficulty_and_keeps_high_score(self):
        self.game._start_game()
        self.game.settings.increase_speed()
        self.game.stats.high_score = 750
        self.game.stats.score = 750
        self.game.stats.level = 3
        self.game._ship_hit()
        self.game._start_game()
        self.assertEqual(self.game.settings.ship_speed, 1.5)
        self.assertEqual(self.game.settings.alien_points, 50)
        self.assertEqual(self.game.stats.score, 0)
        self.assertEqual(self.game.stats.level, 1)
        self.assertEqual(self.game.stats.ships_left, 3)
        self.assertEqual(self.game.stats.high_score, 750)
        self.assertEqual(self.game.respawn_remaining_ms, 0)

    def test_fleet_uses_configured_drop_and_corrects_overshoot(self):
        self.game.aliens.empty()
        alien = Alien(self.game)
        alien.rect.right = self.game.screen.get_width() + 5
        alien.x = float(alien.rect.x)
        self.game.aliens.add(alien)
        self.game.settings.fleet_drop_speed = 27
        old_y = alien.rect.y
        self.game._check_fleet_edges()
        self.assertEqual(alien.rect.y - old_y, 27)
        self.assertEqual(alien.rect.right, self.game.screen.get_width())
        self.assertEqual(self.game.settings.fleet_direction, -1)
        self.game._check_fleet_edges()
        self.assertEqual(alien.rect.y - old_y, 27, 'Do not bounce again while moving in')

    def test_left_edge_reverses_without_drawing_outside(self):
        self.game.aliens.empty()
        alien = Alien(self.game)
        alien.rect.left = -5
        alien.x = float(alien.rect.x)
        self.game.aliens.add(alien)
        self.game.settings.fleet_direction = -1
        self.game._check_fleet_edges()
        self.assertEqual(alien.rect.left, 0)
        self.assertEqual(self.game.settings.fleet_direction, 1)

    def test_ship_collision_and_bottom_together_only_cost_one_life(self):
        self.game._start_game()
        self.game.aliens.empty()
        alien = Alien(self.game)
        alien.rect = self.game.ship.rect.copy()
        alien.x = float(alien.rect.x)
        self.game.aliens.add(alien)
        self.game._update_aliens(0)
        self.assertEqual(self.game.stats.ships_left, 2)

    def test_playfield_reserves_space_for_hud_and_controls(self):
        self.assertTrue(all(alien.rect.top >= self.game.play_area.top
                            for alien in self.game.aliens))
        self.assertLessEqual(self.game.sb.level_rect.bottom, self.game.play_area.top)
        self.assertEqual(self.game.ship.rect.bottom, self.game.play_area.bottom)
        help_top = self.game.screen.get_height() - 8 - self.game.help_image.get_height()
        self.assertLess(self.game.ship.rect.bottom, help_top)

    def test_bottom_hit_uses_playfield_boundary(self):
        self.game._start_game()
        self.game.aliens.empty()
        alien = Alien(self.game)
        alien.rect.bottom = self.game.play_area.bottom
        self.game.aliens.add(alien)
        self.game._check_aliens_bottom()
        self.assertEqual(self.game.stats.ships_left, 2)

    def test_images_load_once_and_are_reused_by_fleet_and_life_icons(self):
        with patch('pygame.image.load', wraps=pygame.image.load) as load:
            game = AlienInvasion(high_score_file=self.score_path)
            game._start_game()
            game._ship_hit()
            game.sb.prep_ships()
        self.assertEqual(load.call_count, 2)
        self.assertIs(game.ship.image, game.sb.ships.sprites()[0].image)
        self.assertIs(game.images['alien'], game.aliens.sprites()[0].image)

    def test_launch_from_another_working_directory(self):
        previous = Path.cwd()
        try:
            os.chdir(self.directory.name)
            game = AlienInvasion(high_score_file=self.score_path)
            game._update_screen()
            self.assertGreater(len(game.aliens), 0)
        finally:
            os.chdir(previous)

    def test_all_screen_states_render(self):
        self.game._update_screen()
        self.game._start_game()
        self.game._update_screen()
        self.game._toggle_pause()
        self.game._update_screen()
        self.game._toggle_pause()
        self.game._ship_hit()
        self.game._update_screen()
        self.game.game_active = False
        self.game.stats.ships_left = 0
        self.game._update_screen()

    def test_quit_during_recovery_saves_and_shuts_down_pygame(self):
        self.game._start_game()
        self.game.stats.high_score = 125
        self.game._ship_hit()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game.run_game()
        self.assertEqual(self.score_path.read_text(encoding='utf-8'), '125')
        self.assertFalse(self.game.running)
        self.assertFalse(pygame.get_init())

    def test_quit_key_exits_the_loop(self):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        self.game.run_game()
        self.assertFalse(self.game.running)
        self.assertFalse(self.game.game_active, 'Ignore further events after quit')
        self.assertFalse(pygame.get_init())


class HighScoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'high_score.txt'
        self.game = SimpleNamespace(settings=Settings())

    def test_missing_file_starts_at_zero(self):
        self.assertEqual(GameStats(self.game, self.path).high_score, 0)

    def test_invalid_empty_negative_and_non_utf8_files_are_safe(self):
        for data in (b'', b'not-a-score', b'-99', b'\xff\xfe'):
            with self.subTest(data=data):
                self.path.write_bytes(data)
                self.assertEqual(GameStats(self.game, self.path).high_score, 0)

    def test_atomic_save_round_trips_exact_score(self):
        stats = GameStats(self.game, self.path)
        stats.high_score = 175
        stats.save_high_score()
        self.assertEqual(GameStats(self.game, self.path).high_score, 175)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])

    def test_failed_replace_keeps_previous_record_and_removes_temporary_file(self):
        self.path.write_text('75', encoding='utf-8')
        stats = GameStats(self.game, self.path)
        stats.high_score = 175
        with patch('game_stats.os.replace', side_effect=PermissionError('read only')):
            with self.assertLogs('game_stats', level='WARNING'):
                stats.save_high_score()
        self.assertEqual(self.path.read_text(encoding='utf-8'), '75')
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])


if __name__ == '__main__':
    unittest.main()
