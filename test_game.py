"""Standard-library tests for The Fifth Alibi."""

import unittest

from fifth_alibi import CaseGenerator, DemoGame, Game, ROUND_TYPES


class CaseGenerationTests(unittest.TestCase):
    def test_same_code_recreates_case(self):
        first = CaseGenerator.generate("WH-12345")
        second = CaseGenerator.generate("WH-12345")
        self.assertEqual(first.killer_id, second.killer_id)
        self.assertEqual(first.location, second.location)
        self.assertEqual(first.round_order, second.round_order)
        self.assertEqual(
            [(item.title, item.detail) for item in first.evidence],
            [(item.title, item.detail) for item in second.evidence],
        )

    def test_three_balanced_rounds(self):
        case = CaseGenerator.generate("WH-BALANCE")
        self.assertEqual(len(case.round_order), 3)
        self.assertEqual(len(case.evidence), 15)
        expected_subjects = sorted(case.characters)
        for round_number in range(1, 4):
            items = [item for item in case.evidence if item.round_number == round_number]
            self.assertEqual(len(items), 5)
            self.assertEqual(sorted(item.subject_id for item in items), expected_subjects)

    def test_rounds_are_three_distinct_themes_sampled_from_five(self):
        allowed = set(ROUND_TYPES)
        selections = [tuple(CaseGenerator.generate(f"WH-SCENES-{seed}").round_order)
                      for seed in range(100)]
        self.assertTrue(all(len(selection) == len(set(selection)) == 3
                            and set(selection) <= allowed for selection in selections))
        self.assertEqual(set().union(*(set(selection) for selection in selections)), allowed)
        self.assertGreater(len(set(selections)), 1)

    def test_attitudes_include_three_groups(self):
        case = CaseGenerator.generate("WH-ATTITUDES")
        attitudes = {person.attitude for person in case.characters.values() if person.character_id != "e"}
        self.assertTrue({"ally", "hostile", "neutral"}.issubset(attitudes))

    def test_complete_demo(self):
        messages = []
        game = DemoGame(CaseGenerator.generate("WH-DEMO-TEST"), output_function=messages.append)
        game.run_demo()
        self.assertEqual(len(game.votes), 15)
        self.assertEqual(len(game.found_evidence), 6)
        self.assertIn("Demo completed", messages[-1])

    def test_misleading_exchange_never_accuses_speaker(self):
        case = CaseGenerator.generate("WH-EXCHANGE")
        messages = []
        game = Game(case, input_function=lambda _: "", output_function=messages.append)
        adrian = case.characters["a"]
        offered = case.evidence[0]
        game.exchange_information(adrian, offered, success=False)
        source, information = game.public_information[-1]
        self.assertEqual(source, "Adrian Vale")
        self.assertFalse(information.startswith("Adrian Vale"))

    def test_npc_investigations_are_distinct(self):
        case = CaseGenerator.generate("WH-NPC-RESEARCH")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        game.round_number = 1
        game.assign_npc_investigations()
        assignments = game.round_assignments[1]
        self.assertEqual(len(assignments), 4)
        self.assertEqual(len({item["evidence"] for item in assignments}), 4)

    def test_exchange_is_genuinely_two_way(self):
        case = CaseGenerator.generate("WH-TWO-WAY")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        game.round_number = 1
        game.assign_npc_investigations()
        adrian = case.characters["a"]
        offered = next(item for item in case.evidence if item.round_number == 1)
        game.exchange_information(adrian, offered, success=True)
        self.assertIn(offered.evidence_id, adrian.known_evidence)
        self.assertGreaterEqual(len(game.public_information), 1)

    def test_low_credibility_increases_suspicion_score(self):
        case = CaseGenerator.generate("WH-CREDIBILITY")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        observer = case.characters["n"]
        evelyn = case.characters["e"]
        game.credibility = 80
        high_credibility_score = game.suspicion_score(observer, evelyn)
        game.credibility = 20
        low_credibility_score = game.suspicion_score(observer, evelyn)
        self.assertGreater(low_credibility_score, high_credibility_score)

    def test_deception_uses_probability(self):
        class FixedRandom:
            def __init__(self, value):
                self.value = value

            def random(self):
                return self.value

        case = CaseGenerator.generate("WH-DECEPTION")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        game.lies.append({"target": "a", "text": "Test lie", "risk": 25, "checked": False})
        game.rng = FixedRandom(0.0)
        self.assertEqual(len(game.check_lies()), 1)

        game.lies.append({"target": "a", "text": "Second lie", "risk": 70, "checked": False})
        game.rng = FixedRandom(0.99)
        self.assertEqual(len(game.check_lies()), 0)

    def test_evidence_chain_requires_different_types(self):
        case = CaseGenerator.generate("WH-CHAIN")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        killer = case.characters[case.killer_id]
        killer_items = [item for item in case.evidence
                        if item.subject_id == killer.character_id and item.points > 0]
        score, bonus = game.evaluate_evidence_chain(killer, killer_items[:2])
        self.assertGreater(score, 0)
        self.assertEqual(bonus, 6)

    def test_intro_explains_objective_and_input_system(self):
        case = CaseGenerator.generate("WH-GUIDANCE")
        messages = []
        game = Game(case, input_function=lambda _: "", output_function=messages.append)
        game.show_intro()
        intro = "\n".join(messages)
        self.assertIn("YOUR OBJECTIVE", intro)
        self.assertIn("90 suspicion", intro)
        self.assertIn("Three of the five investigation themes", intro)
        self.assertIn("mandatory vote", intro)
        self.assertIn("0-100 scale", intro)

    def test_evidence_choices_show_decision_context(self):
        case = CaseGenerator.generate("WH-EVIDENCE-LABEL")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        item = case.evidence[0]
        label = game.evidence_option(item, include_detail=True)
        self.assertIn(game.character(item.subject_id).name, label)
        self.assertIn(item.stage, label)
        self.assertIn(item.summary, label)
        self.assertIn(item.detail, label)

    def test_each_character_has_a_complete_personal_pressure(self):
        case = CaseGenerator.generate("WH-MOTIVES")
        for person in case.characters.values():
            self.assertTrue(person.personal_pressure)
        self.assertEqual(case.characters[case.killer_id].personal_pressure, case.motive)

    def test_character_specific_statements_are_distinct(self):
        case = CaseGenerator.generate("WH-VOICES")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        item = case.evidence[0]
        blamed = case.characters["e"]
        lines = {
            person.character_id: game.character_statement(person, "truth", item, blamed)
            for person in case.characters.values()
            if person.character_id != "e"
        }
        self.assertEqual(len(set(lines.values())), 4)
        self.assertTrue(all(item.detail in line for line in lines.values()))

    def test_detective_review_and_final_reasoning_are_explained(self):
        case = CaseGenerator.generate("WH-DETECTIVE")
        messages = []
        game = Game(case, input_function=lambda _: "", output_function=messages.append)
        game.round_number = 1
        item = next(evidence for evidence in case.evidence if evidence.round_number == 1)
        game.add_evidence(item)
        tally = {character_id: 0 for character_id in case.characters}
        tally["a"] = 3
        votes = [{"round": 1, "from": "e", "to": "a", "proof": item.evidence_id}]
        game.detective_round_review(votes, tally, item)

        ranking = list(case.characters.values())
        scores = {
            person.character_id: {
                "votes": 0, "evidence": 0, "chain": 0,
                "theory": 0, "total": 10 - index,
            }
            for index, person in enumerate(ranking)
        }
        game.explain_final_decision(None, scores, ranking, [item])
        output = "\n".join(messages)
        self.assertIn("DETECTIVE REED'S ROUND REVIEW", output)
        self.assertIn("Reed to Adrian Vale", output)
        self.assertIn("DETECTIVE REED'S REASONING", output)
        self.assertIn("Decision threshold", output)

    def test_shared_final_formula_returns_complete_scores(self):
        case = CaseGenerator.generate("WH-SHARED-VERDICT")
        game = Game(case, input_function=lambda _: "", output_function=lambda _: None)
        theory = case.characters["a"]
        proof = [item for item in case.evidence if item.subject_id == "a"][:2]
        scores, ranking = game.calculate_final_scores(theory, proof)
        self.assertEqual(set(scores), set(case.characters))
        self.assertEqual(len(ranking), 5)
        for score in scores.values():
            self.assertEqual(
                set(score), {"votes", "evidence", "chain", "theory", "total"}
            )


if __name__ == "__main__":
    unittest.main()
