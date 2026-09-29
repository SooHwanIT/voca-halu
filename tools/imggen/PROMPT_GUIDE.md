# Scene-prompt guide (for Stable Diffusion 1.5 / DreamShaper 8)

Each line of a chunk file is: `id<TAB>word<TAB>English sentence<TAB>Korean translation`.
The target vocabulary word is wrapped in [brackets] in the English sentence.

Write ONE scene prompt per line that a learner would look at and instantly connect with the
sentence — especially with the meaning of the bracketed word.

Rules
1. English, 12–35 words, comma-separated phrases, most important subject first.
2. Describe only WHAT is in the picture (subjects, action, setting, key objects, mood).
   NO art-style words (no "cartoon", "photo", "watercolor", "3d", "illustration", "realistic",
   "high quality") — the style is added later per theme.
3. Make the bracketed word's meaning visible. Abstract words → pick one concrete visual
   situation or metaphor (e.g. "decline" → a downward red arrow on a big chart board... but see rule 4:
   prefer a person looking worried at a falling graph line rather than readable numbers).
4. NEVER ask for readable text, letters, numbers, logos, signs with words, speech bubbles, or
   screens full of text. SD cannot draw text. Use shapes, arrows, icons, colors, gestures instead.
5. Keep it simple: 1–3 people or main objects, one clear action. Generic people only
   ("a businesswoman", "an office worker", "a smiling customer") — never names like "Ms. Park".
6. Negatives/absence: show the positive visual consequence instead (e.g. "no one came" →
   "an empty conference room with rows of empty chairs").
7. Keep TOEIC-business settings realistic: offices, stores, hotels, factories, airports, meetings.

Output: write a UTF-8 file with exactly one line per input line, same order:
`id<TAB>prompt` — no header, no quotes, no extra lines, no tabs inside the prompt.
