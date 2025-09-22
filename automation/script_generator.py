"""Generate a short comedic script based on the chosen topic."""
from __future__ import annotations

import random
from textwrap import wrap
from typing import List


def _wrap_line(text: str, width: int = 35) -> str:
    """Nicely wrap text for the visual component."""

    return "\n".join(wrap(text, width=width))


def generate_script(topic: str) -> List[str]:
    """Return a list of narrated lines for the video."""

    setup_templates = [
        "Have you heard what's trending about {topic}? Let's cartoonify it!",
        "Breaking news from the doodle universe: {topic}!",
        "Today's wacky headline reads '{topic}', so naturally we drew it.",
    ]

    punchlines = [
        "Our hero tried to google '{topic}' and the search bar laughed back.",
        "In this universe, {topic} comes with a free cartoon sound effect.",
        "{topic} is now officially a snack flavour. Crunchy, meme-y goodness!",
        "Scientists confirm {topic} is best understood while wearing clown shoes.",
        "Remember: if {topic} knocks, offer it a sketchbook and two crayons.",
    ]

    closers = [
        "Stick around tomorrow when we animate an even weirder trend!",
        "Like, sub, and bring popcorn for tomorrow's doodle drop!",
        "Tune in tomorrow—our crayons don't sleep and neither do the trends!",
    ]

    random.seed(hash(topic) & 0xFFFFFFFF)
    script = [
        _wrap_line(random.choice(setup_templates).format(topic=topic)),
        _wrap_line(random.choice(punchlines).format(topic=topic)),
        _wrap_line(random.choice(punchlines).format(topic=topic)),
        _wrap_line(random.choice(closers)),
    ]

    # Ensure uniqueness by shuffling interior lines while keeping bookends stable
    middle = script[1:-1]
    random.shuffle(middle)
    script[1:-1] = middle

    return script
