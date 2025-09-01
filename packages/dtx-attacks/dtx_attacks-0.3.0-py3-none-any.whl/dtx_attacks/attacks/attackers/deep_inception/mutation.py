from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Set

from dtx_attacks.attacks.mutation.base import BaseMutation


# -------------------------------
# New: Scene generation utility
# -------------------------------
@dataclass
class SceneGenerator:
    """
    Generates stylistically diverse scene strings you can feed into DeepInceptionMutator.
    Configure the banks below or override via constructor.
    """
    base_scene: str = "science fiction"
    genres: List[str] = field(default_factory=lambda: [
        "science fiction", "cyberpunk", "space opera", "fantasy", "dark fantasy",
        "steampunk", "noir", "post-apocalyptic", "spy thriller", "dystopian",
        "historical", "mythology", "superhero", "medical drama", "heist",
    ])
    backdrops: List[str] = field(default_factory=lambda: [
        "an orbiting space hospital", "a remote arctic base", "an abandoned subway system",
        "an ancient library", "a deserted theme park", "a cloud city",
        "a volcanic island laboratory", "a deep-jungle ruin", "an underwater research station",
    ])
    styles: List[str] = field(default_factory=lambda: [
        "as a courtroom transcript", "as a radio play", "as a stage script",
        "as a chatroom log", "as a newspaper clipping", "as a mission brief",
        "as a captain's log", "as medical chart notes", "as a lab notebook",
    ])
    tones: List[str] = field(default_factory=lambda: [
        "satirical", "grim", "playful", "ominous", "procedural",
        "mystical", "claustrophobic", "whimsical",
    ])

    def generate(
        self,
        count: int = 10,
        include_base: bool = True,
        seed: Optional[int] = None,
    ) -> List[str]:
        """
        Return `count` unique scene variants. If the mutator should remain unchanged,
        you will instantiate a new mutator per returned scene to render prompts.
        """
        rng = random.Random(seed)
        root = self.base_scene.strip()

        candidates: List[str] = []

        # 1) Tone + backdrop around the base scene
        for tone in self.tones:
            for backdrop in self.backdrops:
                candidates.append(f"{tone} {root} set in {backdrop}")

        # 2) Genre overlays
        for g in self.genres:
            candidates.append(f"{g} {root}")

        # 3) Narrative styles
        for style in self.styles:
            candidates.append(f"{root} told {style}")

        # 4) Cross-combos (genre + random style/backdrop)
        for g in self.genres:
            b = rng.choice(self.backdrops)
            s = rng.choice(self.styles)
            candidates.append(f"{g} {root} set in {b} told {s}")

        # Deduplicate, preserve order
        seen: Set[str] = set()
        unique: List[str] = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique.append(c)

        # Optionally include base scene (at the front if not already present)
        if include_base and root not in seen:
            unique.insert(0, root)

        # Pad if needed with generic forged combos
        while len(unique) < count:
            g = rng.choice(self.genres)
            b = rng.choice(self.backdrops)
            t = rng.choice(self.tones)
            s = rng.choice(self.styles)
            forged = f"{t} {g} scenario set in {b} told {s}"
            if forged not in seen:
                seen.add(forged)
                unique.append(forged)

        # Sample down to exactly `count`
        return rng.sample(unique, count) if len(unique) > count else unique


# -----------------------------------
# the Mutator 
# -----------------------------------
class DeepInceptionMutator(BaseMutation):
    """
    Translate is a class for translating the query to another language.
    (Kept exactly as you provided, aside from light type hints.)
    """
    def __init__(
        self,
        layer_num,
        character_num,
        scene,
        template,
        language="en"
    ):
        self.layer_num = layer_num
        self.character_num = character_num
        self.scene = scene
        self.language = language
        self.template = template
        self.template = self.template.replace("{character_num}", str(self.character_num))
        self.template = self.template.replace("{layer_num}", str(self.layer_num))
        self.template = self.template.replace("{scene}", self.scene)

    def apply_template(self, query: str):
        # Replace placeholders in the template with actual values
        final_query = self.template
        final_query = final_query.replace("{query}", query)
        return final_query

    def mutate(self, query: str) -> str:
        return self.apply_template(query)


if __name__ == "__main__":
    # 1) Generate scenes
    scenes = SceneGenerator(base_scene="science fiction").generate(count=5, seed=7)

    # 2) Render a full prompt for each scene by creating a NEW mutator per scene
    template = """Create a [scene] with more than {character_num} characters... {query}"""
    query = "Explain how rockets work."

    mutated_prompts = []
    for sc in scenes:
        mut = DeepInceptionMutator(
            layer_num=5,
            character_num=6,
            scene=sc,
            template=template,
            language="en",
        )
        mutated_prompts.append(mut.mutate(query))

    # mutated_prompts now contains 5 fully rendered prompts (one per scene)
