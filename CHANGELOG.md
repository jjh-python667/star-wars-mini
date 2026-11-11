# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not publish version numbers, so each entry is a date.

## 2026-11-11

The 2026-11-10 gameplay behavior is unchanged. Pause, exact scores, three lives, three bullets, and the high-score file are described in `GAMEPLAY.md`.

### Added

- Notes on the BMP images, the book text, and the Star Wars name are in `README.md`.
- Bilingual `README.md` that describes the behavior in the current source, how to run it, the controls, and the file layout.
- `docs/screenshot-start.png` and `docs/screenshot.png`, captured under Xvfb while running `alien_invasion.py`.
- This changelog.

### Changed

- `.gitignore` also ignores `*.pyo`, `venv/`, `env/`, pytest, mypy, and coverage caches, `Thumbs.db`, and `.idea/`. `high_score.txt` was already ignored.
- `Ship` keeps its movement limit on `play_area`. That attribute is the same play-field rectangle the ship already copied.
- The per-frame catch-up limit of 3 lives in `Settings.max_frame_scale`. The game loop still uses that cap.
- `requirements.txt` notes that `pygame==2.6.1` is the version used for the tests and the screenshot run.
- `GAMEPLAY.md` now points to `README.md` for the project introduction.
