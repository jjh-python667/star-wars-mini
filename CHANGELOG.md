# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not publish version numbers, so each entry is a date.

## [Unreleased]

## [2026-11-11]

The 2026-11-10 gameplay behavior is unchanged. Pause, exact scores, three lives, three bullets, and the high-score file are described in `GAMEPLAY.md`.

### Added

- `LICENSE`, the MIT License for the source code and project documentation, plus a scope note for the two BMP images, the textbook text, and the Star Wars name.
- Bilingual `README.md` that describes the behavior in the current source, how to run it, the controls, and the file layout.
- `docs/screenshot-start.png` and `docs/screenshot.png`, saved from the game window while running `alien_invasion.py`.
- This changelog.

### Changed

- `.gitignore` also ignores `*.pyo`, `venv/`, `env/`, pytest, mypy, and coverage caches, `Thumbs.db`, and `.idea/`. `high_score.txt` was already ignored.
- `Ship` keeps its movement limit on `play_area`. That attribute is the same play-field rectangle the ship already copied.
- The per-frame catch-up limit of 3 lives in `Settings.max_frame_scale`. The game loop still uses that cap.
- `requirements.txt` notes that `pygame==2.6.1` is the version used for the tests and the screenshot run.
- `GAMEPLAY.md` now points to `README.md` for the project introduction.
