# Built-in audio licenses

SLAP! Mobile vendors the following sound effects into this repository so the PWA can play them without runtime hotlinking.

## Kenney — Impact Sounds 1.0
License: Creative Commons Zero (CC0 1.0). Attribution is appreciated but not required.
Source: https://kenney.nl/assets/impact-sounds

Vendored selections:
- `sounds/slap-soft.ogg` — `impactSoft_medium_000.ogg`
- `sounds/slap-medium.ogg` — `impactPunch_medium_000.ogg`
- `sounds/slap-heavy.ogg` — `impactPunch_heavy_000.ogg`
- `sounds/bonk.ogg` — `impactWood_heavy_000.ogg`
- `sounds/crash.ogg` — `impactGlass_heavy_000.ogg`
- `sounds/bell.ogg` — `impactBell_heavy_004.ogg`

## OpenGameArt — Meow by IgnasD
License: CC0.
Source: https://opengameart.org/content/meow
Vendored when upstream download is available: `sounds/cat.ogg`.

## OpenGameArt — Short alarm by yd
License: CC0.
Source: https://opengameart.org/content/short-alarm
Vendored when upstream download is available: `sounds/alarm.ogg`.

If an optional upstream file is unavailable during vendoring, SLAP! Mobile keeps its synthesized fallback for that preset.

## Human hit voice pack — CC0

The following files are vendored into `sounds/voices/` for local/offline playback.

- **EZduzziteh — Hurt Sound Effects** — CC0 — https://opengameart.org/content/hurt-sound-effects
  - `hurt-01.mp3` through `hurt-06.mp3`
- **GreyFrogGames — Player Hit (damage)** — CC0 — https://opengameart.org/content/player-hit-damage
  - `player-hit.mp3`
- **Nocturnal_Vanguard / AuraVoice — Female Hurt Grunts & Groans** — CC0 — https://opengameart.org/content/female-hurt-grunts-groans
  - split into short `female-*.ogg` reaction clips
- **Nocturnal_Vanguard / AuraVoice — Female Scream 1** — CC0 — https://opengameart.org/content/female-scream-1
  - `female-scream.ogg`
- **HaelDB — Male Grunt/Yelling sounds** — offered under CC0 (also lists OGA-BY 3.0) — https://opengameart.org/content/male-gruntyelling-sounds
  - compact converted selections `male-*.ogg`
- **EmoPreben — Pain sounds** — CC0 — https://opengameart.org/content/pain-sounds-by-emopreben
  - compact converted selections `pain-*.ogg`

Background-compatible playback uses persistent `HTMLAudioElement` instances, `navigator.audioSession.type = "playback"` where supported, and Media Session controls. Browsers may still suspend JavaScript and motion sensors when a page is backgrounded.
