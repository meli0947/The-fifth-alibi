"""The Fifth Alibi - terminal murder mystery game.

Run this file to start the game:
    python3 fifth_alibi.py

Only Python standard-library modules are used.
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path


# Case templates are shared by the terminal and GUI; three of five topics are
# selected for each replayable case code.
PLAYER_ID = "e"
ROUND_TYPES = [
    ("scene_a", "Crime Scene I: Objects and Space"),
    ("scene_b", "Crime Scene II: Forensic Traces"),
    ("movement", "Movements: Minute-by-Minute Timeline"),
    ("secret", "Secrets: Conflict and Concealment"),
    ("testimony", "Testimony: Contradictions and Relationships"),
]
ROUNDS_PER_CASE = 3


CHARACTER_DATA = [
    {
        "id": "e",
        "name": "Evelyn Hart",
        "role": "Charles's fiancee",
        "traits": ["elegant", "perceptive", "performative"],
        "preference": "emotion",
        "honesty": 55,
        "self_protection": 65,
        "retaliation_sensitivity": 1.0,
        "evidence_focus": 0.8,
        "relationship": "The engagement looked perfect, but Charles was controlling.",
    },
    {
        "id": "a",
        "name": "Adrian Vale",
        "role": "business partner",
        "traits": ["logical", "proud", "ambitious"],
        "preference": "bargain",
        "honesty": 42,
        "self_protection": 82,
        "retaliation_sensitivity": 1.1,
        "evidence_focus": 1.15,
        "relationship": "Their fifteen-year partnership was beginning to collapse.",
    },
    {
        "id": "c",
        "name": "Clara Finch",
        "role": "private secretary",
        "traits": ["careful", "quiet", "observant"],
        "preference": "emotion",
        "honesty": 68,
        "self_protection": 72,
        "retaliation_sensitivity": 0.8,
        "evidence_focus": 0.9,
        "relationship": "She controlled Charles's schedule, keys and private files.",
    },
    {
        "id": "j",
        "name": "Julian Cross",
        "role": "Charles's younger brother",
        "traits": ["impulsive", "sensitive", "approval-seeking"],
        "preference": "emotion",
        "honesty": 50,
        "self_protection": 58,
        "retaliation_sensitivity": 1.6,
        "evidence_focus": 0.75,
        "relationship": "He depended on Charles financially and resented his control.",
    },
    {
        "id": "n",
        "name": "Nora Bell",
        "role": "dinner photographer",
        "traits": ["independent", "curious", "fact-focused"],
        "preference": "evidence",
        "honesty": 76,
        "self_protection": 48,
        "retaliation_sensitivity": 0.7,
        "evidence_focus": 1.45,
        "relationship": "She was secretly investigating the Whitmore family.",
    },
]


METHODS = [
    {
        "name": "poisoning",
        "locations": ["dining room", "conservatory", "study"],
        "weapons": ["digitalis in wine", "swapped medication", "a poisoned glass rim"],
        "cause": "cardiac arrest caused by poison",
        "trace": "chemical residue",
    },
    {
        "name": "blunt-force attack",
        "locations": ["study", "gallery", "wine cellar"],
        "weapons": ["brass candlestick", "marble statue", "cellar wrench"],
        "cause": "a fatal blow to the back of the head",
        "trace": "blood and fabric traces",
    },
    {
        "name": "stabbing",
        "locations": ["kitchen", "study", "conservatory"],
        "weapons": ["letter opener", "silver dinner knife", "gardening knife"],
        "cause": "blood loss from a single chest wound",
        "trace": "blood and handle impressions",
    },
    {
        "name": "fatal fall",
        "locations": ["terrace", "main staircase", "conservatory platform"],
        "weapons": ["loosened railing", "stair edge", "platform handrail"],
        "cause": "fatal injuries from a fall",
        "trace": "shoe prints and railing marks",
    },
]


MOTIVES = {
    "e": ["escape Charles's control", "stop a prenuptial agreement", "hide transferred money"],
    "a": ["hide missing company funds", "stop Charles ending their partnership", "take control of the company"],
    "c": ["prevent forged documents being exposed", "end years of humiliation", "protect a damaging archive"],
    "j": ["escape debt", "recover a changed inheritance", "retaliate after public humiliation"],
    "n": ["stop her research being destroyed", "protect a source", "recover confiscated photographs"],
}

TIMES = ["10:18 pm", "10:25 pm", "10:32 pm", "10:38 pm"]
COVER_UPS = [
    "moved an object to suggest a different crime scene",
    "changed a clock to create a false time of death",
    "deleted a record and tried to implicate someone else",
    "placed a key object among another suspect's belongings",
]
NEUTRAL_PLACES = ["dining-room doorway", "east corridor", "drawing-room fireplace", "servants' stairs", "garden path"]


# These small domain objects keep generated facts separate from mutable beliefs.
# The same instances are consumed by both interfaces.
class Evidence:
    """A report or clue tied to one suspect and one investigation round."""
    def __init__(self, evidence_id, round_number, stage, subject_id, title,
                 summary, detail, points, category):
        self.evidence_id = evidence_id
        self.round_number = round_number
        self.stage = stage
        self.subject_id = subject_id
        self.title = title
        self.summary = summary
        self.detail = detail
        self.points = points
        self.category = category


class Character:
    """A suspect's public profile, private beliefs, and changing relationships."""
    def __init__(self, character_id, name, role, traits, preference,
                 relationship, public_suspicion, trust_evelyn,
                 suspicion_evelyn, attitude, honesty=50, self_protection=50,
                 retaliation_sensitivity=1.0, evidence_focus=1.0,
                 personal_pressure=""):
        self.character_id = character_id
        self.name = name
        self.role = role
        self.traits = traits
        self.preference = preference
        self.relationship = relationship
        self.public_suspicion = public_suspicion
        self.trust_evelyn = trust_evelyn
        self.suspicion_evelyn = suspicion_evelyn
        self.attitude = attitude
        self.honesty = honesty
        self.self_protection = self_protection
        self.retaliation_sensitivity = retaliation_sensitivity
        self.evidence_focus = evidence_focus
        self.personal_pressure = personal_pressure
        self.private_suspicion = {}
        self.known_evidence = []
        self.retaliation = 0

    def attitude_label(self):
        if self.character_id == PLAYER_ID:
            return "player"
        if self.suspicion_evelyn >= 66:
            return "hostile / suspicious"
        if self.suspicion_evelyn >= 40:
            return "neutral / watchful"
        return "trusting / friendly"


class Case:
    """The fixed solution and generated clues for one reproducible mystery."""
    def __init__(self, seed, killer_id, method, location, weapon, time,
                 motive, cover_up, round_order, characters, evidence):
        self.seed = seed
        self.killer_id = killer_id
        self.method = method
        self.location = location
        self.weapon = weapon
        self.time = time
        self.motive = motive
        self.cover_up = cover_up
        self.round_order = round_order
        self.characters = characters
        self.evidence = evidence


# A local random generator makes one case code produce the same hidden
# solution, clue set, and round order on every replay.
class CaseGenerator:
    """Creates a reproducible case from a case code."""

    @staticmethod
    def generate(seed):
        rng = random.Random(seed)
        killer_data = rng.choice(CHARACTER_DATA)
        method = rng.choice(METHODS).copy()
        location = rng.choice(method["locations"])
        weapon = rng.choice(method["weapons"])
        time = rng.choice(TIMES)
        motive = rng.choice(MOTIVES[killer_data["id"]])
        cover_up = rng.choice(COVER_UPS)
        round_order = ROUND_TYPES.copy()
        rng.shuffle(round_order)
        round_order = round_order[:ROUNDS_PER_CASE]

        attitudes = ["ally", "hostile", "neutral", rng.choice(["ally", "hostile", "neutral"])]
        rng.shuffle(attitudes)
        attitude_index = 0
        characters = {}

        for data in CHARACTER_DATA:
            if data["id"] == PLAYER_ID:
                trust, suspicion, attitude = 70, 0, "self"
            else:
                attitude = attitudes[attitude_index]
                attitude_index += 1
                ranges = {
                    "ally": ((68, 82), (18, 32)),
                    "hostile": ((18, 32), (66, 80)),
                    "neutral": ((42, 56), (40, 55)),
                }
                trust_range, suspicion_range = ranges[attitude]
                trust = rng.randint(*trust_range)
                suspicion = rng.randint(*suspicion_range)

            character = Character(
                character_id=data["id"],
                name=data["name"],
                role=data["role"],
                traits=data["traits"].copy(),
                preference=data["preference"],
                relationship=data["relationship"],
                public_suspicion=rng.randint(12, 30),
                trust_evelyn=trust,
                suspicion_evelyn=suspicion,
                attitude=attitude,
                honesty=data["honesty"],
                self_protection=data["self_protection"],
                retaliation_sensitivity=data["retaliation_sensitivity"],
                evidence_focus=data["evidence_focus"],
                personal_pressure=(motive if data["id"] == killer_data["id"]
                                   else rng.choice(MOTIVES[data["id"]])),
            )
            characters[character.character_id] = character

        for observer in characters.values():
            for target in characters.values():
                if observer.character_id != target.character_id:
                    observer.private_suspicion[target.character_id] = rng.randint(12, 45)

        evidence = CaseGenerator._make_evidence(
            rng, killer_data["id"], method, location, weapon, time,
            motive, characters, round_order
        )
        return Case(seed, killer_data["id"], method, location, weapon, time,
                    motive, cover_up, round_order, characters, evidence)

    @staticmethod
    def _make_evidence(rng, killer_id, method, location, weapon, time,
                       motive, characters, round_order):
        all_evidence = []
        for character in characters.values():
            is_killer = character.character_id == killer_id
            place = rng.choice(NEUTRAL_PLACES)
            personal_secret = character.personal_pressure
            nearby_time = rng.choice(["10:11 pm", "10:16 pm", "10:22 pm", "10:29 pm", "10:35 pm"])

            templates = {
                "scene_a": {
                    "title": f"An object connected to {character.name}",
                    "summary": f"An object linked to {character.name} was found near the {location}.",
                    "detail": (
                        f"The contact marks appear recent, but the object may have been used normally during dinner. "
                        f"It does not prove that {character.name} committed the {method['name']}."
                        if is_killer else
                        f"The object belongs to {character.name}, but dust and placement indicate that it was there before the murder."
                    ),
                    "points": 1 if is_killer else 0,
                    "category": "crime-scene object",
                },
                "scene_b": {
                    "title": f"Forensic trace associated with {character.name}",
                    "summary": f"A possible trace connected to {character.name} was examined.",
                    "detail": (
                        f"The trace evidence ({method['trace']}) formed close to {time} and matches the use of {weapon}. "
                        "It becomes meaningful only when combined with evidence from other rounds."
                        if is_killer else
                        f"The trace is connected to {character.name}, but it formed before the death interval and does not support use of {weapon}."
                    ),
                    "points": 2 if is_killer else -1,
                    "category": "forensic review",
                },
                "movement": {
                    "title": f"{character.name}'s recorded movements",
                    "summary": f"Records place {character.name} at a specific time and location.",
                    "detail": (
                        f"At {nearby_time}, {character.name} was recorded on the route to the {location}. "
                        f"There is no confirmed record during the minutes around {time}."
                        if is_killer else
                        f"At {nearby_time}, {character.name} was seen at the {place}. A short gap remains, "
                        f"but reaching the {location} during it would have been difficult."
                    ),
                    "points": 2 if is_killer else -1,
                    "category": "exact timeline",
                },
                "secret": {
                    "title": f"{character.name}'s hidden conflict",
                    "summary": f"Private material reveals an undisclosed conflict involving {character.name}.",
                    "detail": (
                        f"{character.name} was under pressure to {motive} and tried to stop Charles from acting that night."
                        if is_killer else
                        f"{character.name} argued with Charles about an attempt to {personal_secret}. "
                        "This explains a lie, but does not connect the character to the killing method."
                    ),
                    "points": 2 if is_killer else 1,
                    "category": "secret and motive",
                },
                "testimony": {
                    "title": f"Cross-checked testimony about {character.name}",
                    "summary": f"Two accounts disagree slightly about {character.name}.",
                    "detail": (
                        f"{character.name} claimed to have company all evening, but the witness can confirm this only until {nearby_time}. "
                        "The remaining gap covers the critical period."
                        if is_killer else
                        f"The witnesses disagree about the exact minute, but both place {character.name} at the {place}. "
                        "Their central account is consistent."
                    ),
                    "points": 2 if is_killer else -1,
                    "category": "testimony review",
                },
            }

            for round_number, (stage_id, _) in enumerate(round_order, start=1):
                template = templates[stage_id]
                all_evidence.append(Evidence(
                    evidence_id=f"{stage_id}-{character.character_id}",
                    round_number=round_number,
                    stage=stage_id,
                    subject_id=character.character_id,
                    title=template["title"],
                    summary=template["summary"],
                    detail=template["detail"],
                    points=template["points"],
                    category=template["category"],
                ))

        for round_number in range(1, len(round_order) + 1):
            items = [item for item in all_evidence if item.round_number == round_number]
            rng.shuffle(items)
            positions = [index for index, item in enumerate(all_evidence) if item.round_number == round_number]
            for position, item in zip(positions, items):
                all_evidence[position] = item
        return sorted(all_evidence, key=lambda item: item.round_number)


# Game owns the rules. The GUI invokes these methods rather than maintaining
# a second, potentially inconsistent, version of the mystery.
class Game:
    """Run the shared case rules and the text-based player experience."""
    def __init__(self, case, input_function=input, output_function=print):
        self.case = case
        self.rng = random.Random(case.seed + "-gameplay")
        self.input = input_function
        self.output = output_function
        self.round_number = 0
        self.player_suspicion = case.characters[PLAYER_ID].public_suspicion
        self.credibility = self.rng.randint(65, 80)
        self.found_evidence = []
        self.public_information = []
        self.votes = []
        self.statements = []
        self.lies = []
        self.round_assignments = {}
        self.round_reports = {}
        self.ended_early = False

    def say(self, text=""):
        self.output(text)

    def character(self, character_id):
        return self.case.characters[character_id]

    def evidence(self, evidence_id):
        for item in self.case.evidence:
            if item.evidence_id == evidence_id:
                return item
        return None

    def ask_number(self, prompt, minimum, maximum, allow_zero=False):
        while True:
            answer = self.input(prompt).strip()
            if allow_zero and answer == "0":
                return 0
            try:
                number = int(answer)
                if minimum <= number <= maximum:
                    return number
            except ValueError:
                pass
            self.say(f"Please enter a number from {minimum} to {maximum}.")

    def choose(self, title, options, allow_cancel=False):
        self.say(f"\n{title}")
        for index, option in enumerate(options, start=1):
            self.say(f"  {index}. {option}")
        if allow_cancel:
            self.say("  0. Cancel")
        selected = self.ask_number("> ", 1, len(options), allow_cancel)
        return None if selected == 0 else selected - 1

    def evidence_option(self, item, include_detail=False):
        """Return a decision-friendly label without revealing hidden truth."""
        subject = self.character(item.subject_id).name
        effect = "raises suspicion" if item.points > 0 else "may support an alibi"
        label = f"{item.title} | Subject: {subject} | Type: {item.stage} | {effect}"
        if include_detail:
            label += f"\n     {item.summary} {item.detail}"
        return label

    def terminal_evidence_option(self, item, include_detail=False, accused=None):
        """Show readable evidence labels without exposing internal stage IDs."""
        subject = self.character(item.subject_id).name
        effect = ("raises suspicion" if item.points > 0 else
                  "supports an alibi" if item.points < 0 else "inconclusive")
        link = " | SUPPORTS ACCUSATION" if accused and item.subject_id == accused.character_id and item.points > 0 else ""
        label = f"{item.title} — {subject} [{effect}]{link}"
        if include_detail:
            label += f"\n     {item.summary} {item.detail}"
        return label

    def run(self):
        """Guide the player through the introduction, three rounds, and verdict."""
        self.show_intro()
        for round_number in range(1, len(self.case.round_order) + 1):
            self.play_round(round_number)
            if self.player_suspicion >= 90:
                self.ended_early = True
                self.show_early_arrest()
                break
        if not self.ended_early:
            self.final_phase()
        self.write_history()

    def show_intro(self):
        """Introduce the generated case without revealing its hidden solution."""
        self.say("=" * 68)
        self.say("THE FIFTH ALIBI")
        self.say("A procedural social-deduction mystery")
        self.say("=" * 68)
        self.say(f"Case code: {self.case.seed}")
        self.say(f"Charles Whitmore was found dead in the {self.case.location}.")
        self.say(f"Preliminary cause: {self.case.method['cause']}.")
        self.say("Detective Arthur Reed: 'The killer is one of the five suspects.'")
        self.say("You are Evelyn Hart. She appears calm, remembers the evening clearly,")
        self.say("and denies involvement. The game will not reveal her identity early.")
        self.say("\nYOUR OBJECTIVE")
        self.say("Investigate the case while keeping Evelyn from reaching 90 suspicion.")
        self.say("If Evelyn is innocent, expose the real killer. If she is the killer,")
        self.say("avoid conviction. You must discover which situation applies through play.")
        self.say("\nHOW A ROUND WORKS")
        self.say("Three of the five investigation themes are chosen at random for each case.")
        self.say("Each round gives you action points.")
        self.say("Investigate, persuade or deceive until every action point is spent; viewing")
        self.say("the evidence board and dossiers is free. Then everyone makes a mandatory vote.")
        self.say("NPCs investigate independently and may tell the truth, lie or remain silent.")
        self.say("Trust and suspicion use a 0-100 scale: higher trust helps cooperation;")
        self.say("higher suspicion makes accusation more likely. Deception risk is the base")
        self.say("chance of discovery, modified by trust, credibility and counter-evidence.")
        self.say("At the end, votes and two supporting evidence items form the final verdict.")
        self.say("Evidence from different stages can create a stronger linked chain.")
        self.pause()
        self.show_profiles()

    def pause(self):
        self.input("\nPress Enter to continue...")

    def show_profiles(self):
        """Present the five suspects and their initial public information."""
        self.say("\nCHARACTER DOSSIERS")
        self.say("-" * 68)
        for person in self.case.characters.values():
            self.say("")
            self.say(f"{person.name} - {person.role}")
            self.say(f"  Traits: {', '.join(person.traits)}")
            self.say(f"  Relationship: {person.relationship}")
            self.say(f"  Known pressure: {person.personal_pressure.capitalize()}.")
            if person.character_id != PLAYER_ID:
                self.say(f"  Attitude to Evelyn: {person.attitude_label()}")
                self.say(f"  Trust: {person.trust_evelyn}")

    def play_round(self, round_number):
        """Apply the action budget, investigation, statements, and vote for a round."""
        self.round_number = round_number
        if round_number > 1:
            for person in self.case.characters.values():
                if person.character_id != PLAYER_ID:
                    person.public_suspicion = max(0, int(person.public_suspicion * 0.92))
        stage_id, stage_name = self.case.round_order[round_number - 1]
        action_points = 2 if self.player_suspicion >= 55 else 3
        limits = {"investigate": 0, "persuade": 0, "deceive": 0}
        self.assign_npc_investigations()

        self.say("\n" + "=" * 68)
        self.say(f"ROUND {round_number}/{len(self.case.round_order)}  |  {stage_name}")
        self.say("=" * 68)
        self.say("Detective Reed: 'You may investigate only two of five leads.")
        self.say("The others are conducting their own investigations.'")
        self.say(f"You have {action_points} action points. Investigate costs 1 (maximum 2);")
        self.say("persuade costs 1 (maximum 1); deceive costs 1 (maximum 1).")
        if round_number == 1:
            self.say("Free reference actions do not consume a point. All action points must be spent.")

        while action_points > 0:
            self.say(f"\n[ACTIONS] {action_points} left  |  Suspicion {self.player_suspicion}/100  |  Credibility {self.credibility}/100")
            actions = []
            for key, title, remaining in (
                ("investigate", "Investigate", 2 - limits["investigate"]),
                ("persuade", "Persuade / exchange information", 1 - limits["persuade"]),
                ("deceive", "Deceive", 1 - limits["deceive"]),
            ):
                if remaining:
                    actions.append((key, f"{title} ({remaining} use{'s' if remaining != 1 else ''} left)"))
            actions.extend((("evidence", "View evidence board (free)"),
                            ("profiles", "View character dossiers (free)")))
            choice = self.choose("Choose an action", [label for _, label in actions])
            action = actions[choice][0]

            if action == "investigate":
                if limits["investigate"] >= 2:
                    self.say("You have already investigated twice this round.")
                elif self.investigate():
                    limits["investigate"] += 1
                    action_points -= 1
            elif action == "persuade":
                if limits["persuade"] >= 1:
                    self.say("You have already persuaded someone this round.")
                elif self.persuade():
                    limits["persuade"] += 1
                    action_points -= 1
            elif action == "deceive":
                if limits["deceive"] >= 1:
                    self.say("You have already attempted deception this round.")
                elif self.deceive():
                    limits["deceive"] += 1
                    action_points -= 1
            elif action == "evidence":
                self.show_evidence_board()
            elif action == "profiles":
                self.show_profiles()

        exposed = self.check_lies()
        if exposed:
            self.say("\nDetective Reed presents contradictions found during the round:")
            for text in exposed:
                self.say(f"  - {text}")

        self.prepare_npc_statements()
        self.voting_phase()

    def current_available_evidence(self):
        """Return clues for the current topic that have not yet been found."""
        return [item for item in self.case.evidence
                if item.round_number == self.round_number
                and item.evidence_id not in self.found_evidence]

    def investigate(self):
        """Spend an investigation action to reveal a chosen available clue."""
        available = self.current_available_evidence()
        if not available:
            self.say("There are no unexamined leads in this round.")
            return False
        choice = self.choose(
            "Choose a lead to investigate (the subject is who the lead concerns)",
            [self.terminal_evidence_option(item) for item in available], True
        )
        if choice is None:
            return False
        item = available[choice]
        self.add_evidence(item)
        self.say(f"\n{item.title}")
        self.say(f"Initial finding: {item.summary}")
        self.say(f"Full detail: {item.detail}")
        return True

    def add_evidence(self, item):
        """Record a clue once so later choices can use the same evidence board."""
        if item.evidence_id not in self.found_evidence:
            self.found_evidence.append(item.evidence_id)
            subject = self.character(item.subject_id)
            subject.public_suspicion = max(0, subject.public_suspicion + item.points * 2)
            if item.subject_id == PLAYER_ID:
                self.player_suspicion = max(0, self.player_suspicion + item.points * 2)

    def choose_npc(self, title):
        people = [person for person in self.case.characters.values() if person.character_id != PLAYER_ID]
        choice = self.choose(title, [f"{p.name} (trust {p.trust_evelyn})" for p in people], True)
        return None if choice is None else people[choice]

    def persuade(self):
        """Resolve a conversation using the listener's personality and trust."""
        person = self.choose_npc("Who will you approach?")
        if person is None:
            return False
        purposes = [
            "Defend Evelyn - reduce this person's suspicion of her",
            "Redirect suspicion - argue that another person is responsible",
            "Exchange information - offer one known clue for a possible reply",
        ]
        purpose_choice = self.choose("Choose your purpose", purposes, True)
        if purpose_choice is None:
            return False
        tones = ["evidence", "emotion", "bargain", "pressure"]
        tone_labels = [
            "Evidence - appeal to facts and contradictions",
            "Emotion - appeal to sympathy or personal loyalty",
            "Bargain - offer mutual help or information",
            "Pressure - confront them forcefully (can backfire)",
        ]
        self.say("A character responds best to an approach matching their personality;")
        self.say("their exact preference is not shown, but the dossier provides clues.")
        tone_choice = self.choose("Choose your approach", tone_labels, True)
        if tone_choice is None:
            return False
        tone = tones[tone_choice]
        fit = 18 if tone == person.preference else 0
        if tone == "pressure":
            fit -= 15
        persuasion_score = (
            person.trust_evelyn + fit + len(self.found_evidence) * 2
            + (self.credibility - 50) * 0.25
            - max(0, person.suspicion_evelyn - 40) * 0.15
        )
        success = persuasion_score >= 58

        if purpose_choice == 0:
            if success:
                person.suspicion_evelyn = max(0, person.suspicion_evelyn - 12)
                person.trust_evelyn = min(100, person.trust_evelyn + 7)
                self.say(f"{person.name} accepts part of your explanation.")
            else:
                person.suspicion_evelyn = min(100, person.suspicion_evelyn + 6)
                person.trust_evelyn = max(0, person.trust_evelyn - 4)
                self.say(f"{person.name} remains unconvinced.")
            return True

        if purpose_choice == 1:
            targets = [p for p in self.case.characters.values()
                       if p.character_id not in (PLAYER_ID, person.character_id)]
            target_choice = self.choose("Whom should they suspect?", [p.name for p in targets], True)
            if target_choice is None:
                return False
            target = targets[target_choice]
            increase = 12 if success else 2
            person.private_suspicion[target.character_id] += increase
            self.say(f"{person.name} listens to your argument about {target.name}.")
            return True

        if not self.found_evidence:
            self.say("You have no evidence to offer, so the exchange cannot proceed.")
            return True
        items = [self.evidence(item_id) for item_id in self.found_evidence]
        give_choice = self.choose(
            "Choose information to offer (the recipient will remember it)",
            [self.terminal_evidence_option(item, True) for item in items], True
        )
        if give_choice is None:
            return False
        given = items[give_choice]
        self.exchange_information(person, given, success)
        return True

    def exchange_information(self, person, given, success):
        # Information genuinely changes both characters' knowledge. The NPC
        # receives Evelyn's selected evidence before deciding what to return.
        """Trade known information with a suspect when the conversation succeeds."""
        if given.evidence_id not in person.known_evidence:
            person.known_evidence.append(given.evidence_id)
            person.private_suspicion[given.subject_id] = (
                person.private_suspicion.get(given.subject_id, 0) + given.points * 4
            )
        known = [self.evidence(item_id) for item_id in person.known_evidence
                 if item_id not in self.found_evidence and item_id != given.evidence_id]
        disclosure_score = (
            person.trust_evelyn + person.honesty * 0.25
            + (self.credibility - 50) * 0.2
            - person.suspicion_evelyn * 0.2
        )
        shares_evidence = success and known and self.rng.random() * 100 < disclosure_score
        if shares_evidence:
            received = max(known, key=lambda item: abs(item.points))
            self.add_evidence(received)
            text = f"{received.title}: {received.summary} {received.detail}"
        else:
            possible = [p for p in self.case.characters.values()
                        if p.character_id != person.character_id]
            framed = max(possible, key=lambda p: (
                person.suspicion_evelyn if p.character_id == PLAYER_ID
                else person.private_suspicion.get(p.character_id, 0) + p.public_suspicion
            ))
            text = f"{framed.name} was seen carrying something similar to the weapon near the time of death."
        self.public_information.append((person.name, text))
        self.say(f"You give: {given.title}")
        self.say(f"{person.name} tells you: {text}")

    def deceive(self):
        """Record a risky false statement for later contradiction checks."""
        person = self.choose_npc("Whom will you deceive?")
        if person is None:
            return False
        choices = [
            ("I never went near the crime scene.", 70),
            ("I left long before the death.", 55),
            ("I concealed only a private argument.", 25),
            ("I saw another suspect leaving the area.", 45),
        ]
        self.say("Risk is the statement's base chance of being exposed. Counter-evidence")
        self.say("raises it; trust and Evelyn's credibility can lower it.")
        selection = self.choose(
            "Choose a deceptive statement",
            [f"{text} (base discovery risk: {risk}%)" for text, risk in choices], True
        )
        if selection is None:
            return False
        text, risk = choices[selection]
        self.lies.append({"target": person.character_id, "text": text, "risk": risk, "checked": False})
        person.suspicion_evelyn = max(0, person.suspicion_evelyn - 8)
        self.player_suspicion = max(0, self.player_suspicion - 4)
        self.say(f"{person.name} hears your statement. Its consequences will emerge later.")
        return True

    def check_lies(self):
        """Compare prior false statements with newly discovered contradictions."""
        exposed = []
        for lie in self.lies:
            if lie["checked"]:
                continue
            person = self.character(lie["target"])
            counter_count = sum(
                1 for item_id in person.known_evidence
                if self.evidence(item_id).subject_id == PLAYER_ID
                and self.evidence(item_id).points > 0
            )
            discovery_probability = (
                lie["risk"] / 100
                + counter_count * 0.14
                + max(0, person.suspicion_evelyn - 45) / 250
                - person.trust_evelyn / 500
                - self.credibility / 1000
            )
            discovery_probability = max(0.05, min(0.95, discovery_probability))
            caught = self.rng.random() < discovery_probability
            lie["checked"] = True
            if caught:
                person.suspicion_evelyn = min(100, person.suspicion_evelyn + 22)
                person.trust_evelyn = max(0, person.trust_evelyn - 14)
                self.player_suspicion = min(100, self.player_suspicion + 13)
                self.credibility = max(0, self.credibility - 15)
                exposed.append(f"{person.name} challenges Evelyn's claim: '{lie['text']}'")
        return exposed

    def suspicion_score(self, observer, target):
        """Compute a suspect's current estimate of another person's guilt."""
        if target.character_id == PLAYER_ID:
            credibility_penalty = max(0, 65 - self.credibility) * 0.45
            score = (observer.suspicion_evelyn
                     + observer.retaliation * observer.retaliation_sensitivity
                     + credibility_penalty)
        else:
            score = observer.private_suspicion.get(target.character_id, 0) + target.public_suspicion
        for evidence_id in observer.known_evidence:
            item = self.evidence(evidence_id)
            if item.subject_id == target.character_id:
                score += item.points * 5 * observer.evidence_focus
        if observer.character_id == self.case.killer_id and target.character_id != self.case.killer_id:
            score += target.public_suspicion * (0.2 + observer.self_protection / 250)
        return score

    def assign_npc_investigations(self):
        """Give each NPC a distinct private lead before player actions."""
        if self.round_number in self.round_assignments:
            return
        pool = [item for item in self.case.evidence
                if item.round_number == self.round_number]
        assignments = []
        people = [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]
        self.rng.shuffle(people)
        for person in people:
            targets = [target for target in self.case.characters.values()
                       if target.character_id != person.character_id]
            targets.sort(key=lambda target: self.suspicion_score(person, target), reverse=True)
            item = None
            for target in targets:
                item = next((lead for lead in pool if lead.subject_id == target.character_id), None)
                if item:
                    break
            if item is None:
                item = pool[0]
            pool.remove(item)
            if item.evidence_id not in person.known_evidence:
                person.known_evidence.append(item.evidence_id)
            assignments.append({"speaker": person.character_id,
                                "evidence": item.evidence_id})
        self.round_assignments[self.round_number] = assignments

    def character_statement(self, person, mode, item, blamed):
        """Build a character-specific line while keeping reliability hidden."""
        if mode == "truth":
            openings = {
                "a": [
                    "Let us deal in facts, not theatre.",
                    "I checked the point everyone else was avoiding.",
                ],
                "c": [
                    "I compared this with Charles's private schedule.",
                    "I kept records because Charles often changed his story.",
                ],
                "j": [
                    "I know none of you expect me to be careful, but I checked.",
                    "Charles blamed me for everything; this time I verified it myself.",
                ],
                "n": [
                    "My photographs preserve details that memory does not.",
                    "I checked the record twice before speaking.",
                ],
            }
            return f"{self.rng.choice(openings[person.character_id])} {item.detail}"

        if mode == "partial":
            lines = {
                "a": f"I examined {item.title}. {item.summary} The rest is not yet useful to you.",
                "c": f"The schedule contains an entry about {item.title}. {item.summary} I will not disclose the private note.",
                "j": f"I found something about {item.title}. {item.summary} I am not giving you another reason to twist my words.",
                "n": f"I can confirm one observable point: {item.summary} I am withholding the source for now.",
            }
            return lines[person.character_id]

        if mode == "silent":
            if person.retaliation > 0:
                lines = {
                    "a": "Evelyn accused me first. Any information I have stays with me.",
                    "c": "After Evelyn's accusation, I will release nothing without the detective present.",
                    "j": "She pointed at me, and now she expects help? No.",
                    "n": "An accusation changes the risk of disclosure. I am withholding my record.",
                }
            else:
                lines = {
                    "a": "I have a lead, but disclosure would weaken my position.",
                    "c": "I found a private record. I am not prepared to expose its owner yet.",
                    "j": "I know something, but nobody here listens without turning it against me.",
                    "n": "My source is not protected, so I will not publish the detail yet.",
                }
            return lines[person.character_id]

        lines = {
            "a": [
                f"The numbers in {blamed.name}'s account do not survive scrutiny.",
                f"If anyone profited from the gap in the timeline, it was {blamed.name}.",
            ],
            "c": [
                f"Charles's schedule places {blamed.name} near the {self.case.location}.",
                f"A missing appointment entry concerns {blamed.name}, not me.",
            ],
            "j": [
                f"Everyone keeps protecting {blamed.name}. I saw enough to know that is a mistake.",
                f"Ask {blamed.name} why the story changes whenever someone checks it.",
            ],
            "n": [
                f"A timestamp I reviewed conflicts with {blamed.name}'s account.",
                f"The visual record puts pressure on {blamed.name}'s version of events.",
            ],
        }
        return self.rng.choice(lines[person.character_id])

    def prepare_npc_statements(self):
        """Decide what each NPC says after all persuasion and deception."""
        if self.round_number in self.round_reports:
            return
        if self.round_number not in self.round_assignments:
            self.assign_npc_investigations()
        reports = []
        for assignment in self.round_assignments[self.round_number]:
            person = self.character(assignment["speaker"])
            item = self.evidence(assignment["evidence"])
            targets = [target for target in self.case.characters.values()
                       if target.character_id != person.character_id]
            targets.sort(key=lambda target: self.suspicion_score(person, target), reverse=True)

            self_risk = item.subject_id == person.character_id and item.points > 0
            disclosure_score = (
                person.trust_evelyn * 0.35
                + person.honesty * 0.45
                + self.credibility * 0.15
                - person.suspicion_evelyn * 0.20
            )
            if self_risk:
                disclosure_score -= person.self_protection * 0.35
            if person.character_id == self.case.killer_id and item.subject_id == person.character_id:
                disclosure_score -= 30
            disclosure_score += self.rng.randint(-12, 12)

            if disclosure_score >= 48:
                mode = "truth"
            elif disclosure_score >= 31:
                mode = "partial"
            elif disclosure_score >= 16:
                mode = "silent"
            else:
                mode = "lie"
            blamed = targets[0]
            statement = self.character_statement(person, mode, item, blamed)
            reports.append({
                "speaker": person.character_id,
                "evidence": item.evidence_id,
                "mode": mode,
                "statement": statement,
            })
            if mode != "silent":
                self.public_information.append((person.name, statement))
        self.round_reports[self.round_number] = reports

    def prepare_npc_investigations(self):
        """Compatibility helper used by tests and the automatic demo."""
        self.assign_npc_investigations()
        self.prepare_npc_statements()

    def npc_vote(self, voter):
        """Select an accusation from an NPC's private suspicion and knowledge."""
        candidates = [person for person in self.case.characters.values()
                      if person.character_id != voter.character_id]
        ranked = []
        for target in candidates:
            score = self.suspicion_score(voter, target)
            recent = [self.evidence(item_id) for item_id in voter.known_evidence
                      if self.evidence(item_id).round_number == self.round_number
                      and self.evidence(item_id).subject_id == target.character_id]
            score += sum(item.points * 4 * voter.evidence_focus for item in recent)
            score += self.rng.uniform(-9, 9)
            ranked.append((score, target))
        return max(ranked, key=lambda pair: pair[0])[1]

    def detective_round_review(self, round_votes, tally, proof):
        """Explain the round and press the person under the most pressure."""
        highest = max(tally.values())
        leaders = [self.character(character_id) for character_id, count in tally.items()
                   if count == highest]
        leaders.sort(key=lambda person: (
            self.player_suspicion if person.character_id == PLAYER_ID
            else person.public_suspicion
        ), reverse=True)
        focus = leaders[0]
        stage_id, stage_name = self.case.round_order[self.round_number - 1]
        round_evidence = [self.evidence(evidence_id) for evidence_id in self.found_evidence
                          if self.evidence(evidence_id).round_number == self.round_number]

        self.say("\nDETECTIVE REED'S ROUND REVIEW")
        if len(leaders) == 1:
            self.say(f"Reed: '{focus.name} received the most pressure this round: {highest} vote(s).' ")
        else:
            names = ", ".join(person.name for person in leaders)
            self.say(f"Reed: 'The vote is divided at {highest} each between {names}.'")
        self.say(f"Reed: 'This round examined {stage_name.lower()}.'")

        if round_evidence:
            incriminating = [item for item in round_evidence if item.points > 0]
            exculpatory = [item for item in round_evidence if item.points < 0]
            neutral = [item for item in round_evidence if item.points == 0]
            self.say(
                "Reed: 'Evelyn uncovered "
                f"{len(incriminating)} suspicious, {len(exculpatory)} exculpatory and "
                f"{len(neutral)} inconclusive lead(s).'"
            )
        if proof:
            if proof.subject_id == focus.character_id:
                self.say(f"Reed: 'The evidence presented in the vote directly concerns {focus.name}.'")
            else:
                subject = self.character(proof.subject_id)
                self.say(f"Reed: 'The vote focused on {focus.name}, but its stated evidence concerns {subject.name}. That link is weak.'")

        questions = {
            "scene_a": f"Why was an object connected to you found near the {self.case.location}?",
            "scene_b": f"How do you explain the forensic trace associated with you?",
            "movement": f"Where exactly were you during the minutes around {self.case.time}?",
            "secret": f"Did your pressure to {focus.personal_pressure} give you a reason to confront Charles?",
            "testimony": "Why does the account about your movements contain a contradiction?",
        }
        self.say(f"Reed to {focus.name}: '{questions[stage_id]}'")
        if focus.character_id == PLAYER_ID:
            response = "Suspicion is not proof. Test every claim against the physical record."
        else:
            responses = {
                "a": "Charles and I had business disputes, but conflict is not murder. Follow the money and the timing.",
                "c": "I managed Charles's private affairs. Access explains my proximity, not guilt.",
                "j": "I argued with him, yes. That does not place me there when he died.",
                "n": "My work required me to observe people and rooms. Verify the timestamps before accusing me.",
            }
            response = responses[focus.character_id]
        self.say(f"{focus.name}: '{response}'")

    def voting_phase(self):
        """Collect Evelyn's evidence-backed vote and the four independent votes."""
        self.say("\n" + "-" * 68)
        self.say("MANDATORY VOTE")
        self.say("Detective Reed: 'Each suspect must now accuse one person.'")
        self.say("Evelyn must vote. Your supporting evidence will be shared with everyone;")
        self.say("evidence concerning the accused is much more persuasive than unrelated evidence.")
        candidates = [person for person in self.case.characters.values()
                      if person.character_id != PLAYER_ID]
        choice = self.choose("Whom does Evelyn accuse?", [p.name for p in candidates])
        target = candidates[choice]

        if self.found_evidence:
            proof_items = [self.evidence(item_id) for item_id in self.found_evidence]
            proof_choice = self.choose(
                "Choose supporting evidence",
                [self.terminal_evidence_option(item) for item in proof_items]
            )
            proof = proof_items[proof_choice]
            target.public_suspicion += 7 if proof.subject_id == target.character_id and proof.points > 0 else 2
            for person in self.case.characters.values():
                if person.character_id != PLAYER_ID:
                    if proof.evidence_id not in person.known_evidence:
                        person.known_evidence.append(proof.evidence_id)
                    person.private_suspicion[target.character_id] = (
                        person.private_suspicion.get(target.character_id, 0)
                        + (proof.points * 2 if proof.subject_id == target.character_id else 1)
                    )
        else:
            proof = None
            target.public_suspicion += 3

        target.retaliation += 10
        if target.character_id != PLAYER_ID:
            target.suspicion_evelyn = min(100, target.suspicion_evelyn + 5)

        round_votes = [{"round": self.round_number, "from": PLAYER_ID,
                        "to": target.character_id, "proof": proof.evidence_id if proof else None}]
        for voter in [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]:
            accused = self.npc_vote(voter)
            round_votes.append({"round": self.round_number, "from": voter.character_id,
                                "to": accused.character_id, "proof": None})

        self.votes.extend(round_votes)
        tally = {character_id: 0 for character_id in self.case.characters}
        for vote in round_votes:
            tally[vote["to"]] += 1
        for character_id, count in tally.items():
            if character_id == PLAYER_ID:
                self.player_suspicion = min(100, self.player_suspicion + count * 6)
            else:
                self.character(character_id).public_suspicion += count * 2

        reports = {report["speaker"]: report for report in self.round_reports[self.round_number]}
        self.say("\n[STATEMENTS]")
        self.say("Detective Reed records each statement without judging it.")
        evelyn_line = f"{target.name} must explain the contradictions in the evidence."
        self.say(f"Evelyn Hart: '{evelyn_line}'")
        self.statements.append((self.round_number, PLAYER_ID, evelyn_line))
        for person in [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]:
            statement = reports[person.character_id]["statement"]
            self.say(f"{person.name}: '{statement}'")
            self.statements.append((self.round_number, person.character_id, statement))

        self.say("\n[VOTE RESULT]")
        for vote in round_votes:
            self.say(f"  {self.character(vote['from']).name} -> {self.character(vote['to']).name}")
        if 5 in tally.values():
            unanimous_id = next(character_id for character_id, count in tally.items() if count == 5)
            self.say(f"All five votes accuse {self.character(unanimous_id).name}.")
        self.say(f"Evelyn suspicion is now {self.player_suspicion}.")
        self.detective_round_review(round_votes, tally, proof)
        for person in self.case.characters.values():
            if person.character_id != PLAYER_ID:
                person.retaliation = max(0, person.retaliation - 5)
        self.pause()

    def show_evidence_board(self):
        """Display every discovered clue and shared piece of information."""
        self.say("\nEVIDENCE BOARD")
        self.say("-" * 68)
        if not self.found_evidence and not self.public_information:
            self.say("No information has been recorded.")
            return
        for evidence_id in self.found_evidence:
            item = self.evidence(evidence_id)
            self.say(f"[{item.category}] {item.title}")
            self.say(f"  {item.summary}")
            self.say(f"  {item.detail}")
        if self.public_information:
            self.say("\nINFORMATION PROVIDED BY OTHERS")
            for source, text in self.public_information:
                self.say(f"  {source}: {text}")

    def vote_totals(self):
        """Count all votes across the completed investigation rounds."""
        totals = {character_id: 0 for character_id in self.case.characters}
        for vote in self.votes:
            totals[vote["to"]] += 1
        return totals

    def unanimous_target(self):
        """Find a suspect unanimously accused in any completed round."""
        for round_number in range(1, len(self.case.round_order) + 1):
            votes = [vote for vote in self.votes if vote["round"] == round_number]
            if len(votes) == 5 and all(vote["to"] == votes[0]["to"] for vote in votes):
                return votes[0]["to"]
        return None

    def evaluate_evidence_chain(self, person, selected_proof):
        """Score evidence and reward two different, mutually supporting types."""
        linked = [item for item in selected_proof
                  if item.subject_id == person.character_id]
        evidence_score = sum(item.points for item in linked)
        positive = [item for item in linked if item.points > 0]
        different_types = len({item.stage for item in positive})
        chain_bonus = 0
        if len(positive) >= 2 and different_types >= 2:
            chain_bonus = 6
        elif len(positive) == 1:
            chain_bonus = 1
        return evidence_score, chain_bonus

    def calculate_final_scores(self, theory, selected_proof):
        """Apply one shared verdict formula for terminal and GUI versions."""
        totals = self.vote_totals()
        scores = {}
        for person in self.case.characters.values():
            evidence_score, chain_bonus = self.evaluate_evidence_chain(person, selected_proof)
            theory_score = 3 if person.character_id == theory.character_id else 0
            total = (totals[person.character_id] * 2 + evidence_score * 2
                     + theory_score + chain_bonus)
            scores[person.character_id] = {
                "votes": totals[person.character_id],
                "evidence": evidence_score,
                "chain": chain_bonus,
                "theory": theory_score,
                "total": total,
            }
        ranking = sorted(
            self.case.characters.values(),
            key=lambda person: scores[person.character_id]["total"],
            reverse=True,
        )
        return scores, ranking

    def decide_verdict(self, scores, ranking):
        """Return the convicted character and the rule that produced the result."""
        unanimous = self.unanimous_target()
        if unanimous:
            return (self.character(unanimous),
                    "A unanimous round created a binding social consensus.")
        leader = ranking[0]
        runner_up = ranking[1]
        if (scores[leader.character_id]["total"] >= 13
                and scores[leader.character_id]["total"]
                - scores[runner_up.character_id]["total"] >= 3):
            if scores[leader.character_id]["chain"] > 0:
                reason = ("The accumulated votes, a linked evidence chain and final "
                          "theory produced a clear lead.")
            else:
                reason = ("The accumulated votes and final theory produced a clear lead "
                          "despite a weak evidence chain.")
            return leader, reason
        return None, "The votes remained divided and the final evidence chain was insufficient."

    def final_phase(self):
        """Collect the final theory and evidence before calculating the verdict."""
        self.say("\n" + "=" * 68)
        self.say("FINAL THEORY")
        self.say("=" * 68)
        totals = self.vote_totals()
        self.say("VOTES SO FAR")
        for character_id, count in sorted(totals.items(), key=lambda pair: -pair[1]):
            self.say(f"  {self.character(character_id).name:<18} {count}")
        self.say("\nEVIDENCE YOU FOUND")
        for evidence_id in self.found_evidence:
            self.say("  • " + self.terminal_evidence_option(self.evidence(evidence_id)))

        candidates = [person for person in self.case.characters.values()
                      if person.character_id != PLAYER_ID]
        choice = self.choose("Whom does Evelyn finally accuse?", [p.name for p in candidates])
        theory = candidates[choice]

        available = [self.evidence(item_id) for item_id in self.found_evidence]
        selected_proof = []
        if len(available) >= 2:
            self.say(f"\nAccused: {theory.name}. Select two clues; only evidence that raises")
            self.say("suspicion of this person strengthens your accusation. Different themes")
            self.say("can form a stronger chain. You may still submit unrelated evidence.")
            first = self.choose(
                "Choose the first final evidence item",
                [self.terminal_evidence_option(item, accused=theory) for item in available]
            )
            selected_proof.append(available[first])
            remaining = [item for index, item in enumerate(available) if index != first]
            second = self.choose(
                "Choose the second final evidence item",
                [self.terminal_evidence_option(item, accused=theory) for item in remaining]
            )
            selected_proof.append(remaining[second])
        else:
            selected_proof = available

        linked = [item for item in selected_proof
                  if item.subject_id == theory.character_id and item.points > 0]
        if not linked:
            self.say(f"\nNOTE: Your selected evidence does not support the accusation against {theory.name}.")

        scores, ranking = self.calculate_final_scores(theory, selected_proof)
        convicted, reason = self.decide_verdict(scores, ranking)

        self.show_verdict(convicted, reason, scores, ranking, selected_proof, theory)

    def explain_final_decision(self, convicted, scores, ranking, selected_proof):
        """Translate the scoring rules into a readable chain of reasoning."""
        totals = self.vote_totals()
        vote_high = max(totals.values())
        vote_leaders = [self.character(cid).name for cid, count in totals.items()
                        if count == vote_high]
        self.say("\nDETECTIVE REED'S REASONING")
        self.say(f"1. Vote history: {', '.join(vote_leaders)} led with {vote_high} accumulated vote(s).")

        if selected_proof:
            self.say("2. Evelyn's final evidence:")
            for item in selected_proof:
                subject = self.character(item.subject_id)
                if item.points > 0:
                    effect = "supports suspicion"
                elif item.points < 0:
                    effect = "supports an alibi"
                else:
                    effect = "is inconclusive"
                self.say(f"   - {item.title} concerns {subject.name} and {effect}.")
        else:
            self.say("2. Evelyn presented no final supporting evidence.")

        top = ranking[0]
        top_score = scores[top.character_id]
        runner_score = scores[ranking[1].character_id]
        if top_score["chain"] >= 6:
            chain_text = "two supporting clues came from different investigation stages"
        elif top_score["chain"] > 0:
            chain_text = "only one supporting clue was directly linked"
        else:
            chain_text = "the selected clues did not form a linked cross-stage chain"
        self.say(f"3. Evidence chain: for {top.name}, {chain_text}.")
        self.say(
            f"4. Decision threshold: {top.name} scored {top_score['total']}; "
            f"the next suspect scored {runner_score['total']} (gap {top_score['total'] - runner_score['total']})."
        )

        unanimous = self.unanimous_target()
        if unanimous:
            person = self.character(unanimous)
            round_number = next(
                number for number in range(1, len(self.case.round_order) + 1)
                if len([vote for vote in self.votes if vote["round"] == number
                        and vote["to"] == unanimous]) == 5
            )
            self.say(f"5. Binding rule: all five suspects accused {person.name} in round {round_number}.")
        elif convicted:
            self.say("5. Binding rule: the leader cleared the minimum score of 13 and led by at least 3.")
        else:
            self.say("5. Binding rule: no suspect satisfied both the minimum score and the three-point lead.")

    def show_verdict(self, convicted, reason, scores, ranking, selected_proof=None, theory=None):
        """Explain the outcome, ranking, and actual solution to the player."""
        killer = self.character(self.case.killer_id)
        correct = convicted is not None and convicted.character_id == self.case.killer_id
        if self.case.killer_id == PLAYER_ID:
            result = "Evelyn is exposed and loses." if correct else "Evelyn avoids conviction and wins."
        elif correct:
            result = "Evelyn identifies the real killer and wins."
        elif convicted and convicted.character_id == PLAYER_ID:
            result = "Evelyn is innocent but is wrongly convicted."
        else:
            result = "Evelyn fails to secure the correct conviction."
        self.say("\n" + "=" * 68)
        self.say("CASE VERDICT  |  " + ("YOU WIN" if "wins." in result else "YOU LOSE"))
        self.say("=" * 68)
        self.say(result)
        if theory:
            self.say(f"Your accusation: {theory.name}")
        self.say(f"Convicted: {convicted.name if convicted else 'No one'}  |  True killer: {killer.name}")
        self.say("\n[VOTES AND SCORES]")
        for person in ranking:
            score = scores[person.character_id]
            self.say(f"{person.name}: votes {score['votes']}, evidence {score['evidence']}, "
                     f"chain {score['chain']}, theory {score['theory']}, total {score['total']}")
        self.say(f"\n[WHY] {reason}")
        self.explain_final_decision(convicted, scores, ranking, selected_proof or [])
        self.say(f"\n[WHAT REALLY HAPPENED] {killer.name}")
        self.say(f"At {self.case.time}, {killer.name} used {self.case.weapon} in the {self.case.location}")
        self.say(f"to kill Charles, motivated by a desire to {self.case.motive}.")
        self.say(f"Afterwards, the killer {self.case.cover_up}.")

    def show_early_arrest(self):
        """End the case when Evelyn's suspicion reaches the arrest threshold."""
        self.say("\nEvelyn's public suspicion has reached 90.")
        self.say("Detective Reed orders her detention before the investigation can continue.")
        killer = self.character(self.case.killer_id)
        self.say(f"The complete case file later identifies {killer.name} as the true killer.")

    def write_history(self):
        """Append the completed case result to a local JSON history file."""
        data = {
            "case_code": self.case.seed,
            "completed_at": datetime.now().isoformat(timespec="seconds"),
            "rounds_completed": self.round_number,
            "player_suspicion": self.player_suspicion,
            "credibility": self.credibility,
            "found_evidence": self.found_evidence,
            "votes": self.votes,
            "true_killer": self.character(self.case.killer_id).name,
        }
        path = Path("fifth_alibi_history.json")
        try:
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self.say(f"\nGame history saved to {path}.")
        except OSError as error:
            self.say(f"\nThe game finished, but the history file could not be written: {error}")


class DemoGame(Game):
    """Runs a complete non-interactive smoke test."""

    def __init__(self, case, output_function=print):
        super().__init__(case, input_function=lambda _: "", output_function=output_function)

    def pause(self):
        return

    def run_demo(self):
        """Exercise a complete three-round game without interactive input."""
        self.say(f"Demo case: {self.case.seed}")
        for round_number in range(1, len(self.case.round_order) + 1):
            self.round_number = round_number
            self.assign_npc_investigations()
            leads = self.current_available_evidence()
            self.add_evidence(leads[0])
            self.add_evidence(leads[1])
            self.prepare_npc_statements()
            target = max(
                [p for p in self.case.characters.values() if p.character_id != PLAYER_ID],
                key=lambda p: p.public_suspicion,
            )
            player_vote = {"round": round_number, "from": PLAYER_ID,
                           "to": target.character_id, "proof": leads[0].evidence_id}
            npc_votes = []
            for voter in [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]:
                accused = self.npc_vote(voter)
                npc_votes.append({"round": round_number, "from": voter.character_id,
                                  "to": accused.character_id, "proof": None})
            self.votes.extend([player_vote] + npc_votes)
        assert len(self.case.evidence) == 5 * len(self.case.round_order)
        assert len(self.votes) == 5 * len(self.case.round_order)
        assert all(len([item for item in self.case.evidence if item.round_number == number]) == 5
                   for number in range(1, len(self.case.round_order) + 1))
        self.say("Demo completed: three rounds, 15 evidence items and 15 votes generated.")


def get_case_code():
    print("=" * 68)
    print("CASE SETUP")
    print("A random case creates a new mystery. A case code reproduces the same")
    print("killer, evidence, location and round order for replay or testing.")
    print("\n1. Generate a random case")
    print("2. Enter a case code")
    while True:
        choice = input("> ").strip()
        if choice == "1":
            return f"WH-{random.SystemRandom().randint(10000, 99999)}"
        if choice == "2":
            code = input("Case code: ").strip()
            if code:
                return code
        print("Please enter 1 or 2.")


def main():
    if "--demo" in sys.argv:
        code = "WH-DEMO-2026"
        game = DemoGame(CaseGenerator.generate(code))
        game.run_demo()
        return
    code = get_case_code()
    game = Game(CaseGenerator.generate(code))
    game.run()


if __name__ == "__main__":
    main()
