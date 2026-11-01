"""Headless checks for the GUI package and its connection to the game core."""

import re
import tkinter as tk
import unittest
from pathlib import Path

import fifth_alibi_gui as gui
from fifth_alibi import CaseGenerator


class GUICompatibilityTests(unittest.TestCase):
    def test_tcl_interpreter_is_available(self):
        interpreter = tk.Tcl()
        self.assertTrue(interpreter.eval("info patchlevel"))

    def test_colours_are_plain_tk_hex_values(self):
        for colour in [gui.BG, gui.PAPER, gui.PANEL, gui.CARD,
                       gui.INK, gui.RED, gui.GOLD, gui.MUTED]:
            self.assertRegex(colour, r"^#[0-9a-fA-F]{6}$")

    def test_gui_uses_current_case_model(self):
        case = CaseGenerator.generate("WH-GUI-COMPATIBILITY")
        self.assertEqual(len(case.evidence), 15)
        self.assertTrue(all(person.personal_pressure for person in case.characters.values()))

    def test_required_gui_stages_exist(self):
        required = [
            "show_start_screen", "show_incident_screen", "show_identity_screen",
            "show_suspects_screen", "show_briefing_screen", "start_round", "open_investigate",
            "open_persuade", "open_deceive", "begin_vote",
            "resolve_vote", "open_final_builder", "resolve_final",
        ]
        for method in required:
            self.assertTrue(callable(getattr(gui.FifthAlibiGUI, method, None)))

    def test_runtime_compatibility_check_exists(self):
        self.assertTrue(callable(gui.runtime_compatibility_error))

    def test_fonts_and_labels_do_not_contain_control_characters(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        invalid = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", source)
        self.assertEqual(invalid, [])

    def test_all_red_noir_portraits_are_packaged(self):
        portrait_dir = Path(gui.__file__).resolve().parent / "assets" / "portraits"
        self.assertEqual(len(gui.PORTRAIT_FILES), 7)
        for filename in gui.PORTRAIT_FILES.values():
            path = portrait_dir / filename
            self.assertTrue(path.is_file(), filename)
            self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_readability_layout_uses_custom_buttons_and_evidence_cards(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        self.assertNotIn("tk.Button(", source)
        self.assertIn("class TextActionButton", source)
        self.assertIn("def _add_evidence_card", source)
        self.assertIn("self.center.grid_rowconfigure(1, weight=1)", source)

    def test_body_text_and_action_labels_meet_minimum_sizes(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        self.assertIn('font=("Arial", 12)', source)
        self.assertIn('font=("Arial Black", 11)', source)

    def test_new_shell_keeps_identity_actions_and_evidence_visible(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        self.assertIn('body.grid_columnconfigure(0, weight=0, minsize=320)', source)
        self.assertIn('body.grid_columnconfigure(1, weight=1, minsize=620)', source)
        self.assertIn('body.grid_columnconfigure(2, weight=0, minsize=250)', source)
        self.assertIn('self.left.pack_propagate(False)', source)
        self.assertIn('self.right.pack_propagate(False)', source)
        self.assertIn('class ActionTile', source)
        self.assertIn('self.player_suspicion_var', source)
        self.assertIn('REPORTS WILL APPEAR HERE', source)
        self.assertIn('def open_modal', source)
        self.assertIn('def _render_round_view', source)

    def test_narrow_dossier_rail_preserves_name_and_suspicion_bars(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        self.assertIn('self.player_name_label = tk.Label(\n            self.player_card', source)
        self.assertIn('self.player_name_label.pack(fill="x"', source)
        self.assertIn('image=self.portraits_card[person.character_id]', source)
        self.assertIn('suspicion_bar = self._suspicion_bar(info, suspicion, card_bg)', source)
        self.assertIn('self.player_row = tk.Frame(self.player_card', source)
        self.assertIn('self.player_copy = tk.Frame(self.player_row', source)
        refresh = source.split('    def refresh_people(self):', 1)[1].split('    def show_dossier_window', 1)[0]
        self.assertIn('self.player_row, self.player_portrait, self.player_copy', refresh)
        self.assertNotIn('player_row, self.player_portrait, player_copy', refresh)

    def test_victim_file_reserves_height_before_flexible_suspect_grid(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        victim_pack = source.index('self.victim_card.pack(side="bottom"')
        suspects_pack = source.index('self.people_container.pack(side="top"')
        self.assertLess(victim_pack, suspects_pack)
        self.assertIn('self.victim_card.configure(height=108)', source)
        self.assertIn('self.victim_card.pack_propagate(False)', source)

    def test_evidence_text_wraps_to_actual_card_width(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        evidence = source.split('    def _add_evidence_card(', 1)[1].split('    def start_round(', 1)[0]
        self.assertIn('available = max(40, event.width - 8)', evidence)
        self.assertIn('labels = (category_label, title_label, detail_label, footer_label)', evidence)
        self.assertIn('copy.bind("<Configure>", fit_evidence_text)', evidence)
        self.assertNotIn('wraplength=205', evidence)

    def test_vote_controls_and_evidence_scrolling(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        self.assertIn('style.configure("Vote.TCombobox", padding=(12, 12)', source)
        vote = source.split('    def show_vote(', 1)[-1] if '    def show_vote(' in source else source
        self.assertIn('font=("Arial", 19), style="Vote.TCombobox"', vote)
        self.assertIn('self.evidence_scroll.pack(side="right", fill="y")', source)
        self.assertLess(source.index('self.evidence_scroll.pack(side="right"'),
                        source.index('self.evidence_canvas.pack(side="left"'))
        self.assertIn('self._bind_evidence_wheel(self.evidence_cards)', source)

    def test_sidebar_visibility_after_layout_initialization(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        constructor = source.split("    def __init__(self, root):", 1)[1].split("    def handle_callback_error", 1)[0]
        self.assertLess(constructor.index("self._build_layout()"),
                        constructor.index("self.show_start_screen()"))
        self.assertNotIn("self._set_rails_visible", constructor)
        layout = source.split("    def _build_layout(self):", 1)[1].split("    def set_content", 1)[0]
        self.assertLess(layout.index("body = tk.Frame(outer"), layout.index("self.body = body"))
        start = source.split("    def show_start_screen(self):", 1)[1].split("    def start_case", 1)[0]
        self.assertIn("self._set_rails_visible(False)", start)

    def test_gui_investigation_requires_player_lead_selection(self):
        source = Path(gui.__file__).read_text(encoding="utf-8")
        method = source.split("    def open_investigate(self):", 1)[1]
        method = method.split("    def open_persuade(self):", 1)[0]
        self.assertIn("listbox.curselection()", method)
        self.assertIn("leads[listbox.curselection()[0]]", method)
        self.assertNotIn("self.game.rng.choice(leads)", method)


if __name__ == "__main__":
    unittest.main()
