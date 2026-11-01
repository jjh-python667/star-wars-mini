from pathlib import Path


class GameStats:
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        # 最高分存旁边这个文件
        self.high_score_file = Path(__file__).with_name('high_score.txt')
        self.reset_stats()
        self.high_score = self.read_high_score()

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def read_high_score(self):
        try:
            text = self.high_score_file.read_text(encoding='utf-8').strip()
            if text == '':
                return 0
            return int(text)
        except Exception:
            return 0

    def save_high_score(self):
        try:
            self.high_score_file.write_text(str(self.high_score), encoding='utf-8')
        except Exception:
            pass
