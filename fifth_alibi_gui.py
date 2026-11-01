"""Tkinter GUI for The Fifth Alibi.

Run this file for the graphical version:
    python3 fifth_alibi_gui.py

Tkinter is part of Python's standard library. No third-party packages are used.
"""

import random
import sys
import traceback
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from fifth_alibi import CaseGenerator, Game, PLAYER_ID


BG = "#0d0d0d"
PAPER = "#dfddd7"
PANEL = "#d2d0ca"
CARD = "#f4f3ef"
INK = "#0d0d0d"
RED = "#c52331"
RED_DARK = "#7f1119"
MUTED = "#4f4f4b"
LINE = "#85837e"
DARK = "#252525"
SILVER = "#bbb9b3"
WHITE = "#fffefa"
# Retained for compatibility with earlier validation scripts. The red-noir
# system deliberately replaces the former gold accent with clue red.
GOLD = RED

PORTRAIT_FILES = {
    "e": "evelyn_hart.png",
    "a": "adrian_vale.png",
    "c": "clara_finch.png",
    "j": "julian_cross.png",
    "n": "nora_bell.png",
    "detective": "arthur_reed.png",
    "victim": "charles_whitmore.png",
}

ROUND_ART_FILES = {
    "scene_a": "scene_a.png",
    "scene_b": "scene_b.png",
    "movement": "movement.png",
    "secret": "secret.png",
    "testimony": "testimony.png",
}

DEATH_SCENE_FILES = {
    "poisoning": "01_poison.png",
    "blunt-force attack": "02_blunt_force.png",
    "stabbing": "03_stabbing.png",
    "fatal fall": "04_fall.png",
}
DEATH_SCENE_WIDTHS = (1024, 1440, 1600, 1760, 1856, 2048)
IDENTITY_ART_WIDTHS = (320, 400, 480, 560, 720, 880, 1040, 1200)


def draw_icon(canvas, name, colour):
    """Draw a small dependency-free pictogram on a Tk canvas."""
    canvas.delete("all")
    line = lambda *points, **kw: canvas.create_line(
        *points, fill=colour, width=2, capstyle="round", joinstyle="round", **kw
    )
    oval = lambda x1, y1, x2, y2, **kw: canvas.create_oval(
        x1, y1, x2, y2, outline=colour, width=2, **kw
    )
    rect = lambda x1, y1, x2, y2, **kw: canvas.create_rectangle(
        x1, y1, x2, y2, outline=colour, width=2, **kw
    )

    if name == "search":
        oval(4, 4, 18, 18)
        line(16, 16, 25, 25)
    elif name == "persuade":
        line(3, 10, 9, 7, 14, 11, 19, 7, 25, 10)
        line(4, 12, 10, 19, 14, 17, 18, 20, 24, 12)
        line(10, 19, 13, 23, 17, 20)
    elif name == "deceive":
        canvas.create_polygon(3, 8, 14, 4, 25, 8, 22, 20, 14, 24, 6, 20,
                              fill="", outline=colour, width=2)
        oval(7, 11, 12, 15)
        oval(16, 11, 21, 15)
    elif name == "accuse":
        canvas.create_polygon(14, 3, 26, 24, 2, 24, fill="", outline=colour, width=2)
        line(14, 9, 14, 16)
        oval(13, 20, 15, 22, fill=colour)
    elif name == "vote":
        rect(4, 11, 24, 25)
        line(8, 11, 8, 6, 20, 6, 20, 11)
        line(10, 17, 13, 20, 19, 14)
    elif name == "next":
        line(5, 14, 23, 14)
        line(17, 8, 23, 14, 17, 20)
    elif name == "case":
        rect(5, 3, 22, 25)
        line(9, 9, 18, 9)
        line(9, 14, 18, 14)
        line(9, 19, 15, 19)
    elif name == "dossier":
        oval(10, 4, 18, 12)
        line(5, 24, 7, 18, 14, 15, 21, 18, 23, 24)
    elif name == "scene":
        canvas.create_polygon(3, 13, 14, 4, 25, 13, fill="", outline=colour, width=2)
        rect(6, 13, 22, 25)
        rect(12, 17, 17, 25)
    elif name == "forensic":
        oval(7, 4, 21, 24)
        oval(10, 8, 18, 21)
        line(14, 11, 14, 24)
        line(5, 15, 5, 21)
        line(23, 15, 23, 21)
    elif name == "movement":
        oval(4, 4, 24, 24)
        line(14, 7, 14, 14, 20, 17)
    elif name == "secret":
        oval(4, 8, 13, 17)
        line(13, 13, 25, 13)
        line(20, 13, 20, 18)
        line(24, 13, 24, 17)
    elif name == "testimony":
        rect(3, 4, 25, 20)
        line(8, 20, 6, 25, 14, 20)
        line(8, 9, 20, 9)
        line(8, 14, 17, 14)
    elif name == "evidence":
        rect(4, 4, 24, 24)
        line(8, 10, 11, 13, 17, 7)
        line(8, 18, 20, 18)
    elif name == "help":
        oval(4, 4, 24, 24)
        line(11, 10, 12, 8, 16, 8, 18, 10, 18, 12, 14, 15, 14, 17)
        oval(13, 21, 15, 23, fill=colour)
    else:
        oval(5, 5, 23, 23)
        line(14, 8, 14, 20)
        line(8, 14, 20, 14)


class IconActionButton(tk.Frame):
    """A high-contrast icon-and-label action tile."""

    def __init__(self, parent, text, command, icon="next", accent=False, enabled=True):
        bg = RED if accent else CARD
        fg = WHITE if accent else INK
        border = RED_DARK if accent else INK
        super().__init__(parent, bg=bg, highlightbackground=border,
                         highlightthickness=2, bd=0)
        self.command = command
        self.enabled = enabled
        self.normal_bg = bg
        self.hover_bg = RED_DARK if accent else "#dedcd6"
        self.icon = tk.Canvas(self, width=30, height=30, bg=bg,
                              highlightthickness=0, bd=0)
        self.icon.pack(side="left", padx=(12, 5), pady=7)
        draw_icon(self.icon, icon, fg if enabled else MUTED)
        self.label = tk.Label(self, text=text, bg=bg, fg=fg if enabled else MUTED,
                              font=("Arial Black", 12), anchor="w")
        self.label.pack(side="left", fill="both", expand=True, padx=(2, 12), pady=8)
        if enabled:
            for widget in (self, self.icon, self.label):
                widget.bind("<Button-1>", self._click)
                widget.bind("<Enter>", self._enter)
                widget.bind("<Leave>", self._leave)

    def _click(self, _event):
        if self.enabled:
            self.command()

    def _enter(self, _event):
        self.configure(bg=self.hover_bg)
        self.icon.configure(bg=self.hover_bg)
        self.label.configure(bg=self.hover_bg)

    def _leave(self, _event):
        self.configure(bg=self.normal_bg)
        self.icon.configure(bg=self.normal_bg)
        self.label.configure(bg=self.normal_bg)


class TextActionButton(tk.Frame):
    """A macOS-safe text button whose foreground and background stay legible."""

    def __init__(self, parent, text, command, accent=True):
        bg = RED_DARK if accent else CARD
        fg = WHITE if accent else INK
        hover = RED if accent else "#d5d2cb"
        super().__init__(parent, bg=bg, highlightbackground=INK,
                         highlightthickness=2, bd=0, cursor="hand2")
        self.command = command
        self.normal_bg = bg
        self.hover_bg = hover
        self.label = tk.Label(self, text=text, bg=bg, fg=fg,
                              font=("Arial Black", 12), padx=22, pady=11,
                              cursor="hand2")
        self.label.pack(fill="both", expand=True)
        for widget in (self, self.label):
            widget.bind("<Button-1>", lambda _event: self.command())
            widget.bind("<Enter>", self._enter)
            widget.bind("<Leave>", self._leave)

    def _enter(self, _event):
        self.configure(bg=self.hover_bg)
        self.label.configure(bg=self.hover_bg)

    def _leave(self, _event):
        self.configure(bg=self.normal_bg)
        self.label.configure(bg=self.normal_bg)


class ActionTile(tk.Frame):
    """Large two-part action card used in the central 2 x 2 command grid."""

    def __init__(self, parent, title, subtitle, command, icon, enabled=True):
        border = INK if enabled else LINE
        super().__init__(parent, bg=CARD, highlightbackground=border,
                         highlightthickness=3, bd=0,
                         cursor="hand2" if enabled else "arrow")
        self.command = command
        self.enabled = enabled
        self.header = tk.Frame(self, bg=RED if enabled else SILVER)
        self.header.pack(fill="x")
        self.icon = tk.Canvas(self.header, width=34, height=34,
                              bg=RED if enabled else SILVER,
                              highlightthickness=0, bd=0)
        self.icon.pack(side="left", padx=(15, 6), pady=12)
        draw_icon(self.icon, icon, WHITE if enabled else MUTED)
        self.title = tk.Label(
            self.header, text=title.upper(), bg=RED if enabled else SILVER,
            fg=WHITE if enabled else MUTED, font=("Arial Black", 18),
            anchor="w", justify="left",
        )
        self.title.pack(side="left", fill="both", expand=True, padx=(3, 12), pady=10)
        self.subtitle = tk.Label(
            self, text=subtitle, bg=CARD, fg=INK if enabled else MUTED,
            font=("Arial", 14), wraplength=300, justify="center",
        )
        self.subtitle.pack(fill="both", expand=True, padx=14, pady=9)
        if enabled:
            for widget in (self, self.header, self.icon, self.title, self.subtitle):
                widget.bind("<Button-1>", self._click)
                widget.bind("<Enter>", self._enter)
                widget.bind("<Leave>", self._leave)

    def _click(self, _event):
        if self.enabled:
            self.command()

    def _enter(self, _event):
        self.header.configure(bg=RED_DARK)
        self.icon.configure(bg=RED_DARK)
        self.title.configure(bg=RED_DARK)

    def _leave(self, _event):
        self.header.configure(bg=RED)
        self.icon.configure(bg=RED)
        self.title.configure(bg=RED)


# The interface keeps the side rails persistent while replacing only the
# central stage as the player progresses through the case.
class FifthAlibiGUI:
    """Present the shared Game rules in a staged Tkinter interface."""
    def __init__(self, root):
        self.root = root
        self.root.title("The Fifth Alibi")
        self.root.geometry("1500x960")
        self.root.minsize(1220, 780)
        self.root.configure(bg=BG)
        self.root.report_callback_exception = self.handle_callback_error

        # Draw a status message before building the full interface. This is
        # especially useful on macOS, where the window may appear before all
        # Tk widgets have finished initialising.
        self.loading_label = tk.Label(
            self.root,
            text="Loading The Fifth Alibi...",
            bg=BG,
            fg="white",
            font=("Arial", 16),
        )
        self.loading_label.pack(fill="both", expand=True)
        self.root.update_idletasks()

        self.case = None
        self.game = None
        self.action_points = 0
        self.limits = {}
        self.current_buttons = []
        self.portraits = {}
        self.portraits_tiny = {}
        self.portraits_small = {}
        self.portraits_card = {}
        self.portraits_medium = {}
        self.round_art = {}
        self.identity_art = {}
        self.death_scene_art = {}
        self.ui_phase = "START"
        self.player_unlocked = False
        self.suspects_unlocked = False
        self.victim_enabled = False
        self.action_layout_mode = "row"
        self.modal_overlay = None
        self.modal_card = None

        self._configure_styles()
        self._load_portraits()
        self._load_round_art()
        self._load_identity_art()
        self._load_death_scene_art()
        self.loading_label.destroy()
        self._build_layout()
        self.show_start_screen()

    def handle_callback_error(self, error_type, error, error_traceback):
        """Show GUI callback failures instead of leaving an unresponsive window."""
        details = "".join(traceback.format_exception(error_type, error, error_traceback))
        try:
            Path("fifth_alibi_gui_error.log").write_text(details, encoding="utf-8")
        except OSError:
            pass
        messagebox.showerror(
            "The Fifth Alibi - error",
            "An unexpected error occurred. The game has written details to "
            "fifth_alibi_gui_error.log.\n\n" + str(error),
            parent=self.root,
        )

    def _load_portraits(self):
        """Load packaged PNG portraits while keeping a safe text-only fallback."""
        portrait_dir = Path(__file__).resolve().parent / "assets" / "portraits"
        for key, filename in PORTRAIT_FILES.items():
            path = portrait_dir / filename
            if not path.exists():
                continue
            try:
                image = tk.PhotoImage(file=str(path))
                self.portraits[key] = image
                self.portraits_tiny[key] = image.subsample(6, 6)
                self.portraits_small[key] = image.subsample(4, 4)
                self.portraits_card[key] = image.subsample(3, 3)
                self.portraits_medium[key] = image.subsample(2, 2)
            except tk.TclError:
                continue

    def _load_round_art(self):
        """Keep Tk image references alive for each available display size."""
        art_dir = Path(__file__).resolve().parent / "assets" / "round_art"
        for stage_id, filename in ROUND_ART_FILES.items():
            for width in (240, 320, 400):
                path = art_dir / f"{width}" / filename
                try:
                    self.round_art[stage_id, width] = tk.PhotoImage(file=str(path))
                except tk.TclError:
                    pass

    def _load_identity_art(self):
        """Load Evelyn's illustrations at the sizes used by the identity view."""
        art_dir = Path(__file__).resolve().parent / "assets" / "identity_art"
        for width in IDENTITY_ART_WIDTHS:
            try:
                self.identity_art[width] = tk.PhotoImage(file=str(art_dir / f"evelyn_{width}.png"))
            except tk.TclError:
                pass

    def _load_death_scene_art(self):
        """Load proportional scene banners; missing files retain the placeholder."""
        art_dir = Path(__file__).resolve().parent / "assets" / "death_scenes"
        for method, filename in DEATH_SCENE_FILES.items():
            for width in DEATH_SCENE_WIDTHS:
                try:
                    self.death_scene_art[method, width] = tk.PhotoImage(
                        file=str(art_dir / str(width) / filename)
                    )
                except tk.TclError:
                    pass

    def _configure_styles(self):
        """Set readable fonts and native-themed controls for all game views."""
        style = ttk.Style()
        # Keep the operating system's native ttk theme. Forcing the "clam"
        # theme can stall during startup on some macOS builds of Tk 9.
        style.configure("Main.TFrame", background=PAPER)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Title.TLabel", background=PAPER, foreground=INK,
                        font=("Arial Black", 26))
        style.configure("Heading.TLabel", background=PAPER, foreground=RED_DARK,
                        font=("Arial Black", 10))
        style.configure("Body.TLabel", background=PAPER, foreground=INK,
                        font=("Arial", 12), wraplength=680)
        style.configure("Panel.TLabel", background=PANEL, foreground=INK,
                        font=("Arial", 11), wraplength=240)
        style.configure("Stat.TLabel", background=CARD, foreground=INK,
                        font=("Arial Black", 9))
        # Use the operating system's native button colours. macOS Aqua may
        # ignore a custom background while accepting a custom foreground,
        # which can make button text appear invisible.
        style.configure("Accent.TButton", font=("Arial Black", 10),
                        padding=(12, 8))
        style.configure("Action.TButton", font=("Arial", 11), padding=(10, 9))
        style.configure("TCombobox", padding=6)
        style.configure("Vote.TCombobox", padding=(12, 12), font=("Arial", 19))

    def _build_layout(self):
        """Build fixed side rails and a flexible centre area shared by every stage."""
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        # One compact global bar replaces the old oversized masthead, statistics
        # row and route strip. It remains visible during every stage of the case.
        header = tk.Frame(outer, bg=INK, height=78,
                          highlightbackground=INK, highlightthickness=2)
        header.pack(fill="x", pady=(0, 6))
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=INK, width=345)
        brand.pack(side="left", fill="y")
        brand.pack_propagate(False)
        logo = tk.Canvas(brand, width=60, height=60, bg=INK,
                         highlightthickness=0, bd=0)
        logo.pack(side="left", padx=(12, 8), pady=8)
        logo.create_rectangle(7, 7, 49, 49, fill=RED, outline=WHITE, width=3)
        logo.create_line(12, 17, 44, 17, fill=INK, width=3)
        logo.create_line(12, 41, 44, 41, fill=INK, width=3)
        logo.create_text(28, 29, text="V", fill=WHITE,
                         font=("Arial Black", 21))
        logo.create_line(47, 4, 56, 56, fill=RED, width=3)
        brand_title = tk.Frame(brand, bg=INK)
        brand_title.pack(side="left", fill="both", expand=True, pady=13)
        title_line = tk.Frame(brand_title, bg=INK)
        title_line.pack(anchor="w")
        tk.Label(title_line, text="THE FIFTH", bg=INK, fg=WHITE,
                 font=("Arial Black", 21)).pack(side="left")
        tk.Label(title_line, text=" ALIBI", bg=INK, fg=RED,
                 font=("Arial Black", 21)).pack(side="left")
        tk.Label(brand_title, text="RED NOIR CASE FILE", bg=INK, fg=SILVER,
                 font=("Courier New", 8, "bold")).pack(anchor="w", pady=(2, 0))

        status_bar = tk.Frame(header, bg=INK)
        status_bar.pack(side="left", fill="both", expand=True, pady=8, padx=(0, 8))
        self.status_vars = {}
        status_items = [
            ("seed", "CASE", 18),
            ("phase", "PHASE", 20),
            ("round_type", "ROUND TYPE", 27),
            ("status", "STATUS", 30),
        ]
        for key, title, width in status_items:
            box = tk.Frame(status_bar, bg=CARD, width=width * 8,
                           highlightbackground=INK, highlightthickness=1)
            box.pack(side="left", fill="both", expand=True)
            tk.Label(box, text=title, bg=CARD, fg=RED,
                     font=("Arial Black", 9)).pack(anchor="w", padx=10, pady=(7, 0))
            variable = tk.StringVar(value="—")
            tk.Label(box, textvariable=variable, bg=CARD, fg=INK,
                     font=("Arial Black", 11), anchor="w").pack(
                         fill="x", padx=10, pady=(1, 5)
                     )
            self.status_vars[key] = variable
        # Compatibility alias for older checks and helper code.
        self.stat_vars = self.status_vars
        self.meter_bars = {}

        body = tk.Frame(outer, bg=BG)
        self.body = body
        body.pack(fill="both", expand=True)
        # Content must never make a dossier rail wider and steal space from
        # the case page. Only the centre column receives extra window width.
        body.grid_propagate(False)
        body.grid_columnconfigure(0, weight=0, minsize=320)
        body.grid_columnconfigure(1, weight=1, minsize=620)
        body.grid_columnconfigure(2, weight=0, minsize=250)
        body.grid_rowconfigure(0, weight=1)

        self.left = tk.Frame(body, bg=PANEL,
                             width=320, highlightbackground=INK, highlightthickness=2)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.left.pack_propagate(False)
        dossier_head = tk.Frame(self.left, bg=INK)
        dossier_head.pack(fill="x")
        dossier_icon = tk.Canvas(dossier_head, width=30, height=30, bg=INK,
                                 highlightthickness=0)
        dossier_icon.pack(side="left", padx=(12, 4), pady=7)
        draw_icon(dossier_icon, "dossier", WHITE)
        tk.Label(dossier_head, text="CHARACTER DOSSIERS", bg=INK, fg=WHITE,
                 font=("Arial Black", 13)).pack(side="left")

        # Evelyn's portrait and all of the player's changing data now live in
        # one prominent card, preventing the identity/statistics split that
        # made the old interface feel like a detective dashboard.
        self.stat_progress = {}
        self.player_card = tk.Frame(
            self.left, bg=CARD, highlightbackground=RED, highlightthickness=3,
        )
        self.player_card.pack(fill="x", padx=9, pady=9)
        self.player_name_var = tk.StringVar(value="YOUR FILE")
        self.player_role_var = tk.StringVar(value="IDENTITY SEALED")
        self.player_name_label = tk.Label(
            self.player_card, textvariable=self.player_name_var, bg=CARD, fg=RED,
            font=("Arial", 19, "bold"), anchor="center",
        )
        self.player_name_label.pack(fill="x", padx=7, pady=(7, 0))
        self.player_row = tk.Frame(self.player_card, bg=CARD)
        self.player_row.pack(fill="x")
        self.player_portrait = tk.Label(self.player_row, bg=CARD, bd=0)
        self.player_portrait.pack(side="left", padx=6, pady=6)
        self.player_copy = tk.Frame(self.player_row, bg=CARD)
        self.player_copy.pack(side="left", fill="both", expand=True, padx=(4, 7), pady=7)
        player_copy = self.player_copy
        self.player_suspicion_var = tk.StringVar(value="SUSPICION  —")
        self.player_credibility_var = tk.StringVar(value="CREDIBILITY  —")
        self.player_actions_var = tk.StringVar(value="ACTIONS LEFT  —")
        for key, variable in (("suspicion", self.player_suspicion_var),
                              ("credibility", self.player_credibility_var),
                              ("actions", self.player_actions_var)):
            tk.Label(player_copy, textvariable=variable, bg=CARD, fg=INK,
                     font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(2, 0))
            bar = tk.Canvas(player_copy, height=11, bg="#d5d2cb",
                            highlightthickness=0, bd=0)
            bar.pack(fill="x", pady=(0, 3))
            self.stat_progress[key] = bar
            bar.bind("<Configure>", lambda _event: self.update_meters())

        suspects_head = tk.Frame(self.left, bg=CARD,
                                 highlightbackground=INK, highlightthickness=2)
        suspects_head.pack(fill="x", padx=9, pady=(0, 7))
        tk.Label(suspects_head, text="OTHER", bg=CARD, fg=INK,
                 font=("Arial Black", 13)).pack(side="left", padx=(8, 4), pady=6)
        tk.Label(suspects_head, text="SUSPECTS", bg=CARD, fg=RED,
                 font=("Arial Black", 13)).pack(side="left", pady=6)
        self.people_container = tk.Frame(self.left, bg=PANEL)
        self.people_container.grid_columnconfigure(0, weight=1, uniform="suspect")
        self.people_container.grid_columnconfigure(1, weight=1, uniform="suspect")
        self.people_container.grid_rowconfigure(0, weight=1, uniform="suspect", minsize=175)
        self.people_container.grid_rowconfigure(1, weight=1, uniform="suspect", minsize=175)

        # The victim file is anchored at the bottom and expands across the
        # complete remaining width, so the left rail never ends in dead space.
        self.victim_card = tk.Frame(
            self.left, bg=CARD, cursor="hand2",
            highlightbackground=INK, highlightthickness=2,
        )
        self.victim_card.configure(height=108)
        # Reserve the victim's full height before the flexible suspect grid.
        # Otherwise the four unlocked dossiers can consume its allotted space.
        self.victim_card.pack(side="bottom", fill="x", expand=False,
                              padx=9, pady=(0, 9))
        self.victim_card.pack_propagate(False)
        if "victim" in self.portraits_card:
            self.victim_portrait = tk.Label(
                self.victim_card, image=self.portraits_small["victim"],
                bg=CARD, bd=0, cursor="hand2",
            )
        else:
            self.victim_portrait = tk.Label(
                self.victim_card, text="CW", bg=CARD, fg=INK,
                font=("Arial Black", 18), cursor="hand2",
            )
        self.victim_portrait.pack(side="left", padx=7, pady=4)
        victim_copy = tk.Frame(self.victim_card, bg=CARD, cursor="hand2")
        victim_copy.pack(side="left", fill="both", expand=True, padx=(2, 8), pady=9)
        victim_name = tk.Label(victim_copy, text="VICTIM FILE\nCHARLES WHITMORE", bg=CARD,
                               fg=INK, font=("Arial Black", 12), anchor="w",
                               justify="left",
                               cursor="hand2")
        victim_name.pack(fill="x")
        victim_role = tk.Label(victim_copy, text="VICTIM // ESTATE OWNER", bg=CARD,
                               fg=RED_DARK, font=("Courier New", 10, "bold"),
                               anchor="w", cursor="hand2")
        victim_role.pack(fill="x", pady=(4, 0))
        self.victim_facts_var = tk.StringVar(value="CASE FILE SEALED")
        victim_facts = tk.Label(
            victim_copy, textvariable=self.victim_facts_var, bg=CARD, fg=MUTED,
            font=("Arial", 10), anchor="nw", justify="left", wraplength=190,
            cursor="hand2",
        )
        victim_facts.pack(fill="x", pady=(8, 0))
        self.victim_widgets = (self.victim_card, self.victim_portrait,
                               victim_copy, victim_name, victim_role, victim_facts)
        for widget in self.victim_widgets:
            widget.bind("<Button-1>", lambda _event: self.show_victim_profile())
        self.people_container.pack(side="top", fill="both", expand=True,
                                   padx=9, pady=(0, 7))
        self.center = tk.Frame(body, bg=PANEL,
                               highlightbackground=INK, highlightthickness=2)
        self.center.grid(row=0, column=1, sticky="nsew", padx=(0, 6))
        self.center.grid_propagate(False)
        self.center.grid_columnconfigure(0, weight=1)
        self.center.grid_rowconfigure(1, weight=1)
        self.center.grid_rowconfigure(2, weight=0)

        self.detective_frame = tk.Frame(self.center, bg=INK,
                                        highlightbackground=INK, highlightthickness=2)
        self.detective_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        tk.Frame(self.detective_frame, bg=RED, width=8).pack(side="left", fill="y")
        detective_inner = tk.Frame(self.detective_frame, bg=INK)
        detective_inner.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.detective_kicker = tk.Label(
            detective_inner, text="DETECTIVE ARTHUR REED // CASE BRIEFING",
            bg=INK, fg=RED, font=("Courier New", 10, "bold")
        )
        self.detective_kicker.pack(anchor="w")
        self.detective = tk.Label(detective_inner, bg=INK, fg=WHITE,
                                  font=("Arial", 14, "bold"), justify="left", anchor="nw",
                                  wraplength=720)
        self.detective.pack(fill="x", pady=(5, 0))

        self.stage = tk.Frame(self.center, bg=CARD,
                              highlightbackground=INK, highlightthickness=2)
        self.stage.grid(row=1, column=0, sticky="nsew", padx=10)
        self.stage.grid_columnconfigure(0, weight=1)
        self.stage.grid_rowconfigure(0, weight=1)
        # Compatibility name retained for external checks. Stage content is now
        # composed from real panels rather than a single oversized Text widget.
        self.content = self.stage

        self.actions = tk.Frame(self.center, bg=PANEL)
        self.actions.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.right = tk.Frame(body, bg=CARD,
                              width=250, highlightbackground=INK, highlightthickness=2)
        self.right.grid(row=0, column=2, sticky="nsew")
        self.right.pack_propagate(False)
        evidence_head = tk.Frame(self.right, bg=INK)
        evidence_head.pack(fill="x")
        evidence_icon = tk.Canvas(evidence_head, width=30, height=30, bg=INK,
                                  highlightthickness=0)
        evidence_icon.pack(side="left", padx=(12, 4), pady=7)
        draw_icon(evidence_icon, "evidence", RED)
        tk.Label(evidence_head, text="EVIDENCE BOARD", bg=INK, fg=WHITE,
                 font=("Arial Black", 13)).pack(side="left")
        tk.Label(self.right, text="COLLECTED REPORTS // TESTIMONY",
                 bg=CARD, fg=MUTED, font=("Courier New", 9, "bold")).pack(
                     anchor="w", padx=14, pady=(10, 7))
        tk.Label(self.right, text="Scroll to view all evidence ↓", bg=CARD, fg=RED_DARK,
                 font=("Arial", 12, "bold"), anchor="e").pack(
                     fill="x", padx=16, pady=(0, 6))
        evidence_frame = tk.Frame(self.right, bg=CARD)
        evidence_frame.pack(fill="both", expand=True, padx=(10, 8), pady=(0, 10))
        self.evidence_canvas = tk.Canvas(evidence_frame, bg=CARD, bd=0,
                                         highlightthickness=0)
        self.evidence_scroll = tk.Scrollbar(evidence_frame, orient="vertical", width=24,
                                       bg=RED, activebackground=RED_DARK,
                                       troughcolor="#d0cec7", relief="flat",
                                       command=self.evidence_canvas.yview)
        # Reserve the scrollbar's width before the canvas takes the rest.
        self.evidence_scroll.pack(side="right", fill="y")
        self.evidence_canvas.pack(side="left", fill="both", expand=True)
        self.evidence_canvas.configure(yscrollcommand=self.evidence_scroll.set)
        self.evidence_canvas.bind("<MouseWheel>", self._scroll_evidence)
        self.evidence_canvas.bind("<Button-4>", lambda event: self._scroll_evidence(event, -1))
        self.evidence_canvas.bind("<Button-5>", lambda event: self._scroll_evidence(event, 1))
        self.evidence_cards = tk.Frame(self.evidence_canvas, bg=CARD)
        self.evidence_window = self.evidence_canvas.create_window(
            (0, 0), window=self.evidence_cards, anchor="nw"
        )
        self.evidence_cards.bind(
            "<Configure>",
            lambda _event: self.evidence_canvas.configure(
                scrollregion=self.evidence_canvas.bbox("all")
            ),
        )
        self.evidence_canvas.bind(
            "<Configure>",
            lambda event: self.evidence_canvas.itemconfigure(
                self.evidence_window, width=event.width
            ),
        )

    def _scroll_evidence(self, event, direction=None):
        if direction is None:
            direction = -1 if event.delta > 0 else 1
        self.evidence_canvas.yview_scroll(direction, "units")
        return "break"

    def _bind_evidence_wheel(self, widget):
        """Receive wheel events even when the pointer is over a card label."""
        widget.bind("<MouseWheel>", self._scroll_evidence)
        widget.bind("<Button-4>", lambda event: self._scroll_evidence(event, -1))
        widget.bind("<Button-5>", lambda event: self._scroll_evidence(event, 1))
        for child in widget.winfo_children():
            self._bind_evidence_wheel(child)

    def set_content(self, parts, scrollable=False):
        """Render result/review copy as a structured, readable report.

        Onboarding and round screens use dedicated compositions below; this
        generic renderer is kept for variable-length evidence and vote results.
        """
        self.clear_stage()
        if scrollable:
            container = tk.Frame(self.stage, bg=CARD)
            container.grid(row=0, column=0, sticky="nsew", padx=26, pady=22)
            canvas = tk.Canvas(container, bg=CARD, highlightthickness=0)
            bar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=bar.set)
            bar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            report = tk.Frame(canvas, bg=CARD)
            window = canvas.create_window((0, 0), window=report, anchor="nw")
            report.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        else:
            report = tk.Frame(self.stage, bg=CARD)
            report.grid(row=0, column=0, sticky="nsew", padx=26, pady=22)
        report.grid_columnconfigure(0, weight=1)
        row = 0
        for raw_text, tag in parts:
            text = raw_text.strip()
            if not text:
                continue
            if tag == "title":
                font, colour, pady = ("Arial", 28, "bold"), INK, (0, 16)
            elif tag in ("heading", "gold"):
                font, colour, pady = ("Arial", 13, "bold"), RED_DARK, (12, 5)
            elif tag == "bold":
                font, colour, pady = ("Arial", 15, "bold"), INK, (2, 9)
            elif tag == "muted":
                font, colour, pady = ("Arial", 12), MUTED, (4, 9)
            else:
                font, colour, pady = ("Arial", 14), INK, (1, 7)
            label = tk.Label(
                report, text=text, bg=CARD, fg=colour, font=font,
                anchor="w", justify="left", wraplength=690,
            )
            label.grid(row=row, column=0, sticky="ew", pady=pady)
            if scrollable:
                label.bind("<MouseWheel>", lambda event: canvas.yview_scroll(
                    -1 if event.delta > 0 else 1, "units"))
                label.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
                label.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
            row += 1
        report.grid_rowconfigure(row, weight=1)

    def clear_stage(self):
        """Remove the previous centre view before rendering the next stage."""
        for widget in self.stage.winfo_children():
            widget.destroy()

    def _stage_heading(self, parent, eyebrow, title, body=None):
        tk.Label(parent, text=eyebrow.upper(), bg=CARD, fg=RED_DARK,
                 font=("Courier New", 11, "bold"), anchor="w").pack(fill="x")
        tk.Label(parent, text=title, bg=CARD, fg=INK,
                 font=("Arial", 29, "bold"), anchor="w", justify="left",
                 wraplength=590).pack(fill="x", pady=(7, 9))
        tk.Frame(parent, bg=RED, height=2).pack(fill="x", pady=(0, 12))
        if body:
            tk.Label(parent, text=body, bg=CARD, fg=INK,
                     font=("Arial", 14), anchor="nw", justify="left",
                     wraplength=590).pack(fill="x")

    def _image_panel(self, parent, portrait_key, fallback_text, bg=CARD):
        panel = tk.Frame(parent, bg=bg, highlightbackground=INK,
                         highlightthickness=2)
        if portrait_key in self.portraits:
            tk.Label(panel, image=self.portraits[portrait_key],
                     bg=bg, bd=0).pack(expand=True, padx=10, pady=10)
        else:
            tk.Label(panel, text=fallback_text, bg=bg, fg=INK,
                     font=("Arial", 18, "bold"), justify="center").pack(
                         fill="both", expand=True, padx=16, pady=16)
        return panel

    def _render_start_view(self):
        """Lay out the case-code form and introductory case information."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=32, pady=30)
        shell.grid_columnconfigure(0, weight=2, uniform="intake")
        shell.grid_columnconfigure(1, weight=5, uniform="intake")
        shell.grid_rowconfigure(0, weight=1)
        seal = tk.Frame(shell, bg="#ebe9e3", highlightbackground=INK, highlightthickness=2)
        seal.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        emblem = tk.Frame(seal, bg=RED, highlightbackground=INK, highlightthickness=3)
        emblem.pack(expand=True, padx=35, pady=(50, 16))
        tk.Label(emblem, text="V", bg=RED, fg=WHITE,
                 font=("Arial", 105, "bold"), padx=55, pady=25).pack()
        tk.Label(seal, text="SEALED CASE FILE", bg="#ebe9e3", fg=RED_DARK,
                 font=("Arial", 20, "bold")).pack(pady=(0, 48))
        copy = tk.Frame(shell, bg=CARD)
        copy.grid(row=0, column=1, sticky="new", pady=4)
        self._stage_heading(copy, "WHITMORE ESTATE // CASE OPENING", "There has been a murder at the estate!",
                            "Charles Whitmore has been killed. Every guest at the estate is now a suspect. "
                            "Enter a case code to uncover what happened tonight.")
        self.case_entry_area = tk.Frame(copy, bg="#ebe9e3", highlightbackground=RED,
                                        highlightthickness=2)
        self.case_entry_area.pack(fill="x", pady=(28, 18), ipady=18)
        tk.Label(self.case_entry_area, text="CASE CODE", bg="#ebe9e3", fg=RED_DARK,
                 font=("Arial", 21, "bold")).pack(anchor="w", padx=22, pady=(2, 10))
        self.case_entry_controls = tk.Frame(self.case_entry_area, bg="#ebe9e3")
        self.case_entry_controls.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(copy, text="Use the suggested code to start a new case. Save it to replay the same mystery later.",
                 bg=CARD, fg=INK, font=("Arial", 17), anchor="w",
                 wraplength=850, justify="left").pack(fill="x")
        next_steps = tk.Frame(copy, bg=CARD)
        next_steps.pack(fill="x", pady=(32, 0))
        for number, title, detail in (
            ("01", "The crime scene", "Find out who died and what is known about the scene."),
            ("02", "Your role", "Discover who you are and why the others suspect you."),
            ("03", "The investigation", "Choose leads, influence testimony, and vote each round."),
        ):
            step = tk.Frame(next_steps, bg="#ebe9e3", highlightbackground=SILVER,
                            highlightthickness=1)
            step.pack(fill="x", pady=(0, 9))
            tk.Label(step, text=number, bg=RED, fg=WHITE,
                     font=("Arial", 20, "bold"), width=3).pack(side="left", fill="y")
            tk.Label(step, text=title, bg="#ebe9e3", fg=INK,
                     font=("Arial", 17, "bold"), width=9, anchor="w").pack(
                         side="left", padx=(18, 8), pady=12)
            tk.Label(step, text=detail, bg="#ebe9e3", fg=INK,
                     font=("Arial", 15), anchor="w", justify="left").pack(
                         side="left", fill="x", expand=True, padx=(0, 12))

    def _render_incident_view(self):
        """Show the victim's details and the matching death-scene artwork."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(1, weight=1)
        top = tk.Frame(shell, bg=CARD)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        victim = self._image_panel(top, "victim", "CHARLES WHITMORE")
        victim.pack(side="left", padx=(0, 18))
        copy = tk.Frame(top, bg=CARD)
        copy.pack(side="left", fill="both", expand=True)
        self._stage_heading(copy, "Incident report // 10:47 pm", "A body has been found",
                            f"At 10:47 pm, Charles Whitmore was found dead in the "
                            f"{self.case.location}. Detective Arthur Reed has sealed the estate.")
        for label, value in (("VICTIM", "Charles Whitmore"), ("LOCATION", self.case.location),
                             ("ESTIMATED DEATH", self.case.time),
                             ("PRELIMINARY CAUSE", self.case.method["cause"])):
            row = tk.Frame(copy, bg="#ebe9e3", highlightbackground=SILVER, highlightthickness=1)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, bg="#ebe9e3", fg=RED_DARK,
                     font=("Arial", 13, "bold"), width=18, anchor="w").pack(side="left", padx=12, pady=5)
            tk.Label(row, text=value, bg="#ebe9e3", fg=INK,
                     font=("Arial", 15), anchor="w").pack(side="left", padx=12)
        photo = tk.Frame(shell, bg=CARD, highlightbackground=INK, highlightthickness=2)
        photo.grid(row=1, column=0, sticky="nsew")
        scene_image = tk.Canvas(photo, bg=CARD, bd=0, highlightthickness=0)
        scene_image.pack(fill="both", expand=True)
        method = self.case.method.get("art_id", self.case.method["name"])
        def fit_death_scene(event):
            scene_image.delete("all")
            images = [self.death_scene_art[method, width] for width in DEATH_SCENE_WIDTHS
                      if (method, width) in self.death_scene_art]
            images.sort(key=lambda item: item.width())
            image = next((item for item in images
                          if item.width() >= event.width and item.height() >= event.height),
                         images[-1] if images else None)
            if image:
                scene_image.create_image(event.width // 2, event.height // 2,
                                         image=image, anchor="center")
            else:
                scene_image.create_text(event.width // 2, event.height // 2,
                                        text="SCENE PHOTOGRAPH", fill=MUTED,
                                        font=("Arial", 22, "bold"))
        scene_image.bind("<Configure>", fit_death_scene)
        self.incident_continue = tk.Frame(photo, bg=CARD)
        self.incident_continue.place(relx=.985, rely=.98, anchor="se")

    def _render_identity_view(self):
        """Introduce Evelyn and her starting risks before opening the dossiers."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        shell.grid_columnconfigure(0, weight=5, uniform="identity")
        shell.grid_columnconfigure(1, weight=6, uniform="identity")
        shell.grid_rowconfigure(0, weight=1)
        portrait_panel = tk.Frame(shell, bg=CARD, highlightbackground=INK, highlightthickness=2)
        portrait_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        identity_image = tk.Canvas(portrait_panel, bg=CARD, bd=0, highlightthickness=0)
        identity_image.pack(fill="both", expand=True)
        def fit_identity_art(event):
            identity_image.delete("all")
            images = [self.identity_art[width] for width in IDENTITY_ART_WIDTHS
                      if width in self.identity_art]
            images.sort(key=lambda item: item.width())
            image = next((item for item in images
                          if item.width() >= event.width and item.height() >= event.height),
                         images[-1] if images else self.portraits.get(PLAYER_ID))
            if image:
                identity_image.create_image(event.width // 2, event.height // 2,
                                            image=image, anchor="center")
            else:
                identity_image.create_text(event.width // 2, event.height // 2,
                                           text="EVELYN HART", fill=INK)
        identity_image.bind("<Configure>", fit_identity_art)
        copy = tk.Frame(shell, bg=CARD)
        copy.grid(row=0, column=1, sticky="nsew")
        self._stage_heading(copy, "Your file // Identity confirmed", "You are Evelyn Hart",
                            "Charles Whitmore's fiancée — and one of five suspects.")
        for title, text in (("YOUR PUBLIC POSITION", "You denied involvement. The evidence will test your account while the other guests investigate you."),
                            ("WHAT CHANGES", "Every action affects suspicion, credibility and how each person sees you."),
                            ("IMMEDIATE RISK", "If suspicion reaches 90, you will be detained before the final verdict.")):
            block = tk.Frame(copy, bg="#ebe9e3", highlightbackground=SILVER, highlightthickness=1)
            block.pack(fill="x", pady=(12, 0))
            tk.Label(block, text=title, bg="#ebe9e3", fg=RED_DARK,
                     font=("Arial", 15, "bold"), anchor="w").pack(fill="x", padx=15, pady=(12, 4))
            tk.Label(block, text=text, bg="#ebe9e3", fg=INK,
                     font=("Arial", 15), justify="left", anchor="w",
                     wraplength=530).pack(fill="x", padx=15, pady=(0, 12))
        self.identity_continue = tk.Frame(copy, bg=CARD)
        self.identity_continue.pack(fill="x", pady=(18, 0))

    def _render_suspects_view(self):
        """Introduce the other four suspects without changing the side rails."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=22, pady=16)
        heading_row = tk.Frame(shell, bg=CARD)
        heading_row.pack(fill="x")
        heading_copy = tk.Frame(heading_row, bg=CARD)
        heading_copy.pack(side="left", fill="x", expand=True)
        self._stage_heading(heading_copy, "THE SOCIAL FIELD", "Five suspects",
                            "Each person has a reason to lie to Charles, and a reason to lie to you.")
        self.suspects_continue = tk.Frame(heading_row, bg=CARD)
        self.suspects_continue.pack(side="right", padx=(16, 0), anchor="n")
        tk.Label(shell, text="Select a portrait on the left to read that person's full dossier.", bg=CARD, fg=RED_DARK,
                 font=("Arial", 16, "bold"), anchor="w").pack(fill="x", pady=(10, 0))
        cards = tk.Frame(shell, bg=CARD)
        cards.pack(fill="both", expand=True, pady=(10, 0))
        for column in range(2):
            cards.grid_columnconfigure(column, weight=1, uniform="cast")
        for row in range(2):
            cards.grid_rowconfigure(row, weight=1, uniform="cast")
        others = [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]
        for index, person in enumerate(others):
            row, column = divmod(index, 2)
            card = tk.Frame(cards, bg="#ebe9e3", highlightbackground=INK,
                            highlightthickness=2)
            card.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            if person.character_id in self.portraits_medium:
                tk.Label(card, image=self.portraits_medium[person.character_id],
                         bg=CARD).pack(side="left", fill="y", padx=(10, 12), pady=10)
            info = tk.Frame(card, bg="#ebe9e3")
            info.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=12)
            tk.Label(info, text=person.name.upper(), bg="#ebe9e3", fg=INK,
                     font=("Arial", 13, "bold"), wraplength=190,
                     anchor="w").pack(fill="x")
            tk.Label(info, text=person.role.upper(), bg="#ebe9e3", fg=RED_DARK,
                     font=("Arial", 11), wraplength=190, justify="left",
                     anchor="w").pack(fill="x", pady=(6, 0))
            tk.Label(info, text=f"STARTING SUSPICION {person.public_suspicion}",
                     bg="#ebe9e3", fg=MUTED, font=("Arial", 10, "bold"),
                     anchor="w").pack(fill="x", pady=(10, 0))
            self._suspicion_bar(info, person.public_suspicion, "#ebe9e3")

    def _render_briefing_view(self):
        """Explain the four actions and the per-round action budget."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        top = tk.Frame(shell, bg=CARD)
        top.pack(fill="x", pady=(0, 16))
        heading = tk.Frame(top, bg=CARD)
        heading.pack(side="left", fill="both", expand=True)
        self._stage_heading(heading, "Detective Arthur Reed // Briefing", "How each round works",
                            "You have three rounds before the final assessment.")
        self.briefing_continue = tk.Frame(top, bg=CARD)
        self.briefing_continue.pack(side="right", padx=(20, 4))
        cards = tk.Frame(shell, bg=CARD)
        cards.pack(fill="both", expand=True)
        items = (("search", "Investigate", "Choose one lead from this round's investigation theme."),
                 ("persuade", "Persuade", "Defend yourself, redirect suspicion, or exchange information."),
                 ("deceive", "Deceive", "Make a claim that may be exposed later."),
                 ("vote", "Round vote", "After the actions, everyone makes a statement and votes."))
        for index, (icon_name, title, description) in enumerate(items):
            row, col = divmod(index, 2)
            cards.grid_columnconfigure(col, weight=1, uniform="rules")
            cards.grid_rowconfigure(row, weight=1, uniform="rules")
            card = tk.Frame(cards, bg="#ebe9e3", highlightbackground=INK, highlightthickness=2)
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            icon = tk.Canvas(card, width=90, height=90, bg="#ebe9e3", highlightthickness=0)
            icon.pack(side="left", padx=22)
            draw_icon(icon, icon_name, RED_DARK)
            icon.scale("all", 0, 0, 2.7, 2.7)
            copy = tk.Frame(card, bg="#ebe9e3")
            copy.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=20)
            tk.Label(copy, text=title, bg="#ebe9e3", fg=RED_DARK,
                     font=("Arial", 22, "bold"), anchor="w").pack(fill="x")
            label = tk.Label(copy, text=description, bg="#ebe9e3", fg=INK,
                             font=("Arial", 16), justify="left", anchor="w", wraplength=250)
            label.pack(fill="x", pady=(10, 0))
            copy.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(180, event.width-12)))

    def _render_round_view(self, round_number, stage_name, objective, stage_id=None):
        """Display the selected investigation theme and its illustration."""
        self.clear_stage()
        shell = tk.Frame(self.stage, bg=CARD)
        shell.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        shell.grid_columnconfigure(0, weight=2)
        shell.grid_columnconfigure(1, weight=5)
        shell.grid_rowconfigure(0, weight=1)
        visual = tk.Frame(shell, bg=CARD, highlightbackground=INK, highlightthickness=2)
        visual.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        art = tk.Label(visual, bg=CARD, bd=0)
        art.pack(fill="both", expand=True, padx=8, pady=8)
        def fit_round_art(event):
            # Choose the largest packaged portrait which fits the current pane.
            available = [width for width in (240, 320, 400)
                         if (stage_id, width) in self.round_art
                         and width <= event.width and round(width * 1626 / 967) <= event.height]
            image = self.round_art.get((stage_id, max(available))) if available else self.round_art.get((stage_id, 240))
            art.configure(image=image if image else "", text="" if image else self.short_stage_name(stage_name))
        art.bind("<Configure>", fit_round_art)
        copy = tk.Frame(shell, bg=CARD)
        copy.grid(row=0, column=1, sticky="nsew")
        self._stage_heading(copy, f"Round {round_number} // You are acting as Evelyn",
                            self.short_stage_name(stage_name), objective)
        tk.Label(copy,
                 text=f"You have {self.action_points} actions. Investigate lets you choose an available lead; "
                      "persuasion and deception may each be used once. Finish every action before voting.",
                 bg="#ebe9e3", fg=INK, font=("Arial", 12), justify="left",
                 wraplength=500, padx=14, pady=12).pack(fill="x", pady=(14, 0))

    def open_modal(self, title, kicker="ACTION", width=720, height=500):
        """Create a focused dialog while keeping the underlying game stage intact."""
        self.close_modal()
        overlay = tk.Frame(self.root, bg="#000000", highlightthickness=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        card = tk.Frame(overlay, bg=PAPER, highlightbackground=INK,
                        highlightthickness=3, width=width, height=height)
        card.place(relx=.5, rely=.5, anchor="center")
        card.pack_propagate(False)
        header = tk.Frame(card, bg=INK, height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Frame(header, bg=RED, width=8).pack(side="left", fill="y")
        hcopy = tk.Frame(header, bg=INK)
        hcopy.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        tk.Label(hcopy, text=kicker.upper(), bg=INK, fg=RED,
                 font=("Courier New", 11, "bold"), anchor="w").pack(fill="x")
        tk.Label(hcopy, text=title.upper(), bg=INK, fg=WHITE,
                 font=("Arial", 21, "bold"), anchor="w").pack(fill="x", pady=(3, 0))
        close = tk.Label(header, text="×", bg=INK, fg=WHITE,
                         font=("Arial", 22, "bold"), cursor="hand2")
        close.pack(side="right", padx=18)
        close.bind("<Button-1>", lambda _event: self.close_modal())
        body = tk.Frame(card, bg=PAPER)
        body.pack(fill="both", expand=True, padx=20, pady=18)
        self.modal_overlay, self.modal_card = overlay, card
        overlay.grab_set()
        return body

    def close_modal(self):
        """Dismiss the current dialog and release its focus."""
        if self.modal_overlay is not None and self.modal_overlay.winfo_exists():
            try:
                self.modal_overlay.grab_release()
            except tk.TclError:
                pass
            self.modal_overlay.destroy()
        self.modal_overlay = None
        self.modal_card = None

    def refresh_round_flow(self):
        """Compatibility hook; the current stage now lives in the top status bar."""
        return

    def clear_actions(self):
        for widget in self.actions.winfo_children():
            widget.destroy()
        self.current_buttons = []
        for column in range(2):
            self.actions.grid_columnconfigure(column, weight=0)
        for row in range(2):
            self.actions.grid_rowconfigure(row, weight=0)
        self.action_layout_mode = "row"
        self.center.grid_rowconfigure(1, weight=1)
        self.center.grid_rowconfigure(2, weight=0)

    def add_button(self, text, command, accent=False, enabled=True, icon=None):
        if icon is None:
            lower = text.lower()
            if "investigate" in lower:
                icon = "search"
            elif "persuade" in lower:
                icon = "persuade"
            elif "deceive" in lower or "statement" in lower:
                icon = "deceive"
            elif "vote" in lower:
                icon = "vote"
            elif "case" in lower or "generate" in lower:
                icon = "case"
            else:
                icon = "next"
        button = IconActionButton(
            self.actions, text.upper(), command, icon=icon,
            accent=accent, enabled=enabled,
        )
        button.pack(side="left", fill="x", expand=True, padx=(0, 9), pady=1)
        self.current_buttons.append(button)
        return button

    def add_action_tile(self, title, subtitle, command, icon, row, column,
                        enabled=True):
        """Place one large command card in the central round-action grid."""
        self.action_layout_mode = "grid"
        self.actions.grid_columnconfigure(0, weight=1, uniform="action")
        self.actions.grid_columnconfigure(1, weight=1, uniform="action")
        self.actions.grid_rowconfigure(0, weight=1, uniform="action")
        self.actions.grid_rowconfigure(1, weight=1, uniform="action")
        tile = ActionTile(
            self.actions, title, subtitle, command, icon, enabled=enabled,
        )
        tile.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        self.current_buttons.append(tile)
        return tile

    def set_detective(self, text):
        prefix = "Detective Arthur Reed\n"
        if text.startswith(prefix):
            text = text[len(prefix):]
        self.detective.configure(text=text)

    def dialog_button(self, parent, text, command):
        return TextActionButton(parent, text, command, accent=True)

    def capture_game_output(self, function, *args):
        """Run a core narration method and return its lines for the GUI."""
        messages = []
        original_output = self.game.output
        self.game.output = messages.append
        try:
            function(*args)
        finally:
            self.game.output = original_output
        return messages

    def update_stats(self):
        """Refresh case status and side panels after a game-state change."""
        if not self.game:
            self.status_vars["seed"].set("—")
            self.status_vars["phase"].set("NEW CASE")
            self.status_vars["round_type"].set("—")
            self.status_vars["status"].set("AWAITING CASE CODE")
            self.refresh_people()
            self.refresh_evidence()
            self.update_meters()
            return
        self.status_vars["seed"].set(self.case.seed)
        total_rounds = len(self.case.round_order)
        if 1 <= self.game.round_number <= total_rounds:
            self.status_vars["phase"].set(f"ROUND {self.game.round_number}/{total_rounds}")
            _stage_id, stage_name = self.case.round_order[self.game.round_number - 1]
            self.status_vars["round_type"].set(self.short_stage_name(stage_name).upper())
        elif self.game.round_number > total_rounds:
            self.status_vars["phase"].set("FINAL VERDICT")
            self.status_vars["round_type"].set("CASE THEORY")
        else:
            self.status_vars["phase"].set(self.ui_phase.replace("_", " "))
            self.status_vars["round_type"].set("—")
        self.status_vars["status"].set(self.current_status())
        self.refresh_people()
        self.refresh_evidence()
        self.update_meters()

    @staticmethod
    def short_stage_name(stage_name):
        replacements = {
            "Crime Scene I: Objects and Space": "Crime Scene I",
            "Crime Scene II: Forensic Traces": "Forensics",
            "Movements: Minute-by-Minute Timeline": "Movements",
            "Secrets: Conflict and Concealment": "Secrets",
            "Testimony: Contradictions and Relationships": "Testimony",
        }
        return replacements.get(stage_name, stage_name)

    def current_status(self):
        if self.ui_phase == "INCIDENT":
            return "CASE OPENED"
        if self.ui_phase == "YOUR_ROLE":
            return "IDENTITY OPENED"
        if self.ui_phase == "SUSPECTS":
            return "DOSSIERS OPENED"
        if self.ui_phase == "BRIEFING":
            return "AWAITING INVESTIGATION"
        if self.ui_phase == "ROUND":
            return "CHOOSE YOUR ACTION" if self.action_points else "READY TO VOTE"
        if self.ui_phase == "VOTE":
            return "ROUND VOTE"
        if self.ui_phase == "SUMMARY":
            return "ROUND REVIEW"
        if self.ui_phase == "FINAL":
            return "BUILD FINAL THEORY"
        if self.ui_phase == "VERDICT":
            return "CASE CLOSED"
        return "AWAITING CASE CODE"

    def update_meters(self):
        """Render suspicion, trust, and remaining actions as progress bars."""
        if not hasattr(self, "stat_progress"):
            return
        for key, canvas in self.stat_progress.items():
            value = (self.game.player_suspicion if key == "suspicion" else
                     self.game.credibility if key == "credibility" else
                     self.action_points) if self.game and self.player_unlocked else 0
            maximum = 3 if key == "actions" else 100
            width = max(1, canvas.winfo_width())
            canvas.delete("all")
            canvas.create_rectangle(0, 0, width * max(0, min(maximum, value)) / maximum,
                                    11, fill=RED if key == "suspicion" else INK,
                                    outline="")

    def _set_rails_visible(self, visible):
        """Keep side panels hidden only during the opening case views."""
        if visible:
            self.left.grid()
            self.right.grid()
            self.body.grid_columnconfigure(0, weight=0, minsize=320)
            self.body.grid_columnconfigure(1, weight=1, minsize=620)
            self.body.grid_columnconfigure(2, weight=0, minsize=250)
        else:
            self.left.grid_remove()
            self.right.grid_remove()
            self.body.grid_columnconfigure(0, weight=0, minsize=0)
            self.body.grid_columnconfigure(1, weight=1, minsize=0)
            self.body.grid_columnconfigure(2, weight=0, minsize=0)

    def show_start_screen(self):
        self.case = None
        self.game = None
        self.ui_phase = "START"
        self._set_rails_visible(False)
        self.player_unlocked = False
        self.suspects_unlocked = False
        self.victim_enabled = False
        self.clear_actions()
        self.detective_kicker.configure(text="WHITMORE ESTATE // SEALED CASE FILE")
        self.set_detective("Enter a case code to open a complete, reproducible mystery.")
        self._render_start_view()
        entry = ttk.Entry(self.case_entry_controls, width=18, font=("Arial", 22))
        entry.insert(0, f"WH-{random.SystemRandom().randint(10000, 99999)}")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=9)
        generate = IconActionButton(
            self.case_entry_controls, "START CASE",
            lambda: self.start_case(entry.get().strip()),
            icon="case", accent=True,
        )
        generate.pack(side="left", fill="y")
        self.update_stats()

    def start_case(self, seed):
        """Generate the case from the entered code and start the story."""
        if not seed:
            messagebox.showwarning("Case code", "Enter a case code first.")
            return
        self.case = CaseGenerator.generate(seed)
        self.game = Game(self.case, input_function=lambda _: "", output_function=lambda _: None)
        self.game.round_number = 0
        self.action_points = 0
        self.victim_enabled = True
        self.player_unlocked = False
        self.suspects_unlocked = False
        self.show_incident_screen()

    def show_incident_screen(self):
        """First onboarding page: what happened and why nobody may leave."""
        self.ui_phase = "INCIDENT"
        self._set_rails_visible(False)
        self.player_unlocked = False
        self.suspects_unlocked = False
        self.clear_actions()
        self.detective_kicker.configure(text="INCIDENT REPORT // 10:47 PM")
        self.set_detective(
            "Charles Whitmore has been found dead. I have sealed the estate; no guest may leave."
        )
        self._render_incident_view()
        IconActionButton(self.incident_continue, "How awful... Wait, who am I?",
                         self.show_identity_screen, icon="case", accent=True).pack()
        self.update_stats()

    def show_identity_screen(self):
        """Second onboarding page: connect the player directly to Evelyn."""
        self.ui_phase = "YOUR_ROLE"
        self._set_rails_visible(True)
        self.player_unlocked = True
        self.suspects_unlocked = False
        self.clear_actions()
        self.detective_kicker.configure(text="YOUR FILE // EVELYN HART")
        self.set_detective(
            "Your statement places you among the suspects. Every choice will change how the others see you."
        )
        self._render_identity_view()
        IconActionButton(self.identity_continue, "Meet the other suspects",
                         self.show_suspects_screen, icon="dossier", accent=True).pack(fill="x")
        self.update_stats()

    def show_suspects_screen(self):
        """Third onboarding page: unlock the social field before the rules."""
        self.ui_phase = "SUSPECTS"
        self.player_unlocked = True
        self.suspects_unlocked = True
        self.clear_actions()
        self.detective_kicker.configure(text="FIVE SUSPECTS // ONE HOUSE")
        self.set_detective(
            "Every person here had a reason to lie to Charles — and a reason to lie to you."
        )
        self._render_suspects_view()
        IconActionButton(self.suspects_continue, "Enter the investigation", self.show_briefing_screen,
                         icon="case", accent=True).pack(pady=8)
        self.update_stats()

    def show_briefing_screen(self):
        """Final onboarding page: concise rules in the same persistent shell."""
        self.ui_phase = "BRIEFING"
        self.player_unlocked = True
        self.suspects_unlocked = True
        self.clear_actions()
        self.detective_kicker.configure(text="DETECTIVE ARTHUR REED // CASE BRIEFING")
        self.set_detective(
            "You have three rounds before my final assessment. The others will investigate too."
        )
        self._render_briefing_view()
        IconActionButton(self.briefing_continue, "START CASE",
                         lambda: self.start_round(1), icon="case", accent=True).pack(pady=10)
        self.update_stats()

    def _suspicion_bar(self, parent, value, background=CARD):
        """Draw a suspect's suspicion on a shared zero-to-one-hundred scale."""
        track = tk.Canvas(parent, bg="#d5d2cb", height=11,
                          highlightthickness=0, bd=0)
        track.pack(fill="x", pady=(4, 8))
        def paint(event):
            track.delete("all")
            track.create_rectangle(0, 0, event.width * max(0, min(100, value)) / 100,
                                   11, fill=RED, outline="")
        track.bind("<Configure>", paint)
        return track

    def refresh_people(self):
        """Update the persistent dossier cards without changing their layout."""
        for widget in self.people_container.winfo_children():
            widget.destroy()
        if not self.case:
            self.player_name_var.set("YOUR FILE")
            self.player_role_var.set("IDENTITY SEALED")
            self.player_suspicion_var.set("SUSPICION  —")
            self.player_credibility_var.set("CREDIBILITY  —")
            self.player_actions_var.set("ACTIONS LEFT  —")
            self.player_portrait.configure(image="", text="SEALED", bg=CARD, fg=INK,
                                           font=("Arial Black", 12), width=10, height=7)
            self.victim_facts_var.set("CASE FILE SEALED")
            return

        player = self.case.characters[PLAYER_ID]
        if self.player_unlocked:
            if PLAYER_ID in self.portraits_medium:
                self.player_portrait.configure(
                    image=self.portraits_medium[PLAYER_ID], text="", bg=CARD,
                    width=0, height=0,
                )
            else:
                self.player_portrait.configure(
                    image="", text="EH\nYOU", bg=CARD, fg=INK,
                    font=("Arial Black", 15), width=9, height=6,
                )
            self.player_name_var.set("EVELYN HART")
            self.player_role_var.set("YOU // CHARLES'S FIANCÉE")
            self.player_suspicion_var.set(f"SUSPICION  {self.game.player_suspicion}")
            self.player_credibility_var.set(f"CREDIBILITY  {self.game.credibility}")
            self.player_actions_var.set(
                f"ACTIONS LEFT  {self.action_points}" if self.ui_phase == "ROUND" else
                "ACTIONS LEFT  —"
            )
            player_index = list(self.case.characters).index(PLAYER_ID)
            for widget in (self.player_card, self.player_name_label,
                           self.player_row, self.player_portrait, self.player_copy):
                widget.configure(cursor="hand2")
                widget.bind(
                    "<Button-1>",
                    lambda _event, selected=player_index: self.show_selected_profile(selected),
                )
        else:
            self.player_portrait.configure(image="", text="YOUR\nFILE", bg=CARD, fg=INK,
                                           font=("Arial Black", 13), width=9, height=5)
            self.player_name_var.set("YOUR FILE")
            self.player_role_var.set("IDENTITY SEALED // OPEN THE FILE")
            self.player_suspicion_var.set("SUSPICION  —")
            self.player_credibility_var.set("CREDIBILITY  —")
            self.player_actions_var.set("ACTIONS LEFT  —")

        self.victim_facts_var.set(
            f"FOUND 10:47 PM\n{self.case.location.upper()}\n"
            f"DEATH ≈ {self.case.time.upper()}"
        )

        others = [person for person in self.case.characters.values()
                  if person.character_id != PLAYER_ID]
        all_people = list(self.case.characters.values())
        for position, person in enumerate(others):
            row, column = divmod(position, 2)
            suspicion = person.public_suspicion
            card_bg = CARD
            card = tk.Frame(self.people_container, bg=card_bg,
                            highlightbackground=INK, highlightthickness=2)
            card.grid(row=row, column=column, sticky="nsew", padx=3, pady=3)
            if person.character_id in self.portraits_card:
                portrait = tk.Label(
                    card, image=self.portraits_card[person.character_id],
                    bg=CARD, bd=0,
                )
                portrait.pack(side="top", pady=(4, 1))
            else:
                portrait = tk.Label(card, text=person.name.split()[0][0], bg=CARD,
                                    fg=INK, font=("Arial Black", 18), width=6, height=5)
                portrait.pack(side="top", pady=(8, 3))
            info = tk.Frame(card, bg=card_bg)
            info.pack(side="top", fill="x", padx=7, pady=(0, 3))
            name_label = tk.Label(
                info, text=person.name.upper(), bg=card_bg, fg=INK,
                font=("Arial", 14, "bold"), anchor="center", justify="center",
                wraplength=145,
            )
            name_label.pack(fill="x")
            if self.suspects_unlocked:
                detail = f"{person.attitude_label().upper()}\nSUSPICION {suspicion}"
                detail_fg = MUTED
            else:
                detail = "LOCKED\nDOSSIER"
                detail_fg = RED_DARK
            detail_label = tk.Label(
                info, text=detail, bg=card_bg, fg=detail_fg,
                font=("Arial", 11, "bold"), justify="center", anchor="center",
                wraplength=145,
            )
            detail_label.pack(fill="x", pady=(1, 0))
            suspicion_bar = None
            if self.suspects_unlocked:
                suspicion_bar = self._suspicion_bar(info, suspicion, card_bg)
            if self.suspects_unlocked:
                index = all_people.index(person)
                for widget in (card, portrait, info, name_label, detail_label, suspicion_bar):
                    widget.configure(cursor="hand2")
                    widget.bind(
                        "<Button-1>",
                        lambda _event, selected=index: self.show_selected_profile(selected),
                    )

    def show_dossier_window(self, title, portrait_key, role, details, meters=None):
        """Open a suspect's full profile with current social statistics."""
        body = self.open_modal(title, f"Confidential dossier // {role}", 850, 625)
        portrait_panel = tk.Frame(body, bg=CARD, width=280, highlightbackground=INK, highlightthickness=2)
        portrait_panel.pack(side="left", fill="y")
        portrait_panel.pack_propagate(False)
        if portrait_key in self.portraits:
            tk.Label(portrait_panel, image=self.portraits[portrait_key], bg=CARD).pack(expand=True)
        information = tk.Frame(body, bg=CARD, highlightbackground=INK, highlightthickness=2)
        information.pack(side="left", fill="both", expand=True, padx=(14, 0))
        tk.Label(information, text="CASE NOTES", bg=CARD, fg=RED_DARK,
                 font=("Arial", 19, "bold")).pack(anchor="w", padx=22, pady=(20, 8))
        sections = details.split("\n\n")
        for section in sections:
            if not section.strip():
                continue
            heading, _, content = section.partition("\n")
            tk.Label(information, text=heading, bg=CARD, fg=RED_DARK,
                     font=("Arial", 15, "bold"), anchor="w").pack(fill="x", padx=22, pady=(12, 3))
            if heading == "TRUST IN EVELYN" and meters:
                continue
            label = tk.Label(information, text=content, bg=CARD, fg=INK,
                             font=("Arial", 15), anchor="w", justify="left")
            label.pack(fill="x", padx=22)
            label.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(160, event.width)))
        for label, value, maximum in meters or ():
            tk.Label(information, text=f"{label}  {value}/{maximum}", bg=CARD, fg=RED_DARK,
                     font=("Arial", 15, "bold"), anchor="w").pack(fill="x", padx=22, pady=(12, 4))
            track = tk.Canvas(information, height=12, bg="#d5d2cb", highlightthickness=0)
            track.pack(fill="x", padx=22)
            def paint(event, track=track, value=value, maximum=maximum):
                track.delete("all")
                track.create_rectangle(0, 0, event.width*max(0,min(maximum,value))/maximum,
                                       12, fill=RED, outline="")
            track.bind("<Configure>", paint)
        self.dialog_button(information, "CLOSE DOSSIER", self.close_modal).pack(
            side="bottom", anchor="e", padx=22, pady=15)

    def show_victim_profile(self):
        if not self.case or not getattr(self, "victim_enabled", False):
            return
        details = (
            f"LOCATION\n{self.case.location.title()}\n\n"
            f"PRELIMINARY CAUSE\n{self.case.method['cause'].capitalize()}\n\n"
            f"ESTIMATED TIME\nAround {self.case.time}\n\n"
            "BACKGROUND\nEstate owner whose control over money, careers and private "
            "information gave every suspect a reason to conceal something."
        )
        self.show_dossier_window(
            "Charles Whitmore", "victim", "Victim // Whitmore estate owner", details
        )

    def show_selected_profile(self, index=None):
        if not self.case or index is None:
            return
        person = list(self.case.characters.values())[index]
        extra = ""
        if person.character_id != PLAYER_ID:
            extra = (f"\n\nATTITUDE TO EVELYN\n{person.attitude_label().title()}")
        details = (
            f"TRAITS\n{', '.join(person.traits).title()}\n\n"
            f"RELATIONSHIP WITH CHARLES\n{person.relationship}\n\n"
            f"KNOWN PRESSURE\n{person.personal_pressure.capitalize()}."
            f"{extra}"
        )
        self.show_dossier_window(
            person.name, person.character_id, person.role, details,
            meters=(("TRUST IN EVELYN", person.trust_evelyn, 100),
                    ("SUSPICION", person.public_suspicion, 100)) if person.character_id != PLAYER_ID else
                   (("SUSPICION", self.game.player_suspicion, 100),
                    ("CREDIBILITY", self.game.credibility, 100),
                    ("ACTIONS LEFT", self.action_points, 3))
        )

    def refresh_evidence(self):
        """Rebuild the scrollable evidence rail from the current case record."""
        for widget in self.evidence_cards.winfo_children():
            widget.destroy()
        if not self.game:
            self._add_empty_evidence("OPEN A CASE TO BEGIN")
            return
        if not self.game.found_evidence and not self.game.public_information:
            self._add_empty_evidence("NO EVIDENCE COLLECTED")
        for evidence_id in self.game.found_evidence:
            item = self.game.evidence(evidence_id)
            self._add_evidence_card(
                item.category.upper(), item.title,
                item.detail, "VERIFIED FACT",
            )
        for source, text in self.game.public_information:
            self._add_evidence_card(
                "TESTIMONY", "Unverified testimony", text,
                f"SOURCE // {source}", unverified=True,
            )
        self._bind_evidence_wheel(self.evidence_cards)
        self.evidence_cards.update_idletasks()
        self.evidence_canvas.configure(scrollregion=self.evidence_canvas.bbox("all"))

    def _add_empty_evidence(self, text):
        tk.Label(self.evidence_cards, text=text, bg=RED, fg=WHITE,
                 font=("Arial Black", 11), justify="center",
                 wraplength=220).pack(fill="x", padx=3, pady=(3, 8))
        tk.Label(
            self.evidence_cards,
            text="Investigate during each round to add complete reports here.",
            bg=CARD, fg=INK, font=("Arial", 11), justify="center",
            wraplength=220,
        ).pack(fill="x", padx=8, pady=(0, 10))
        placeholder = tk.Frame(
            self.evidence_cards, bg="#ece9e2",
            highlightbackground=SILVER, highlightthickness=2, height=150,
        )
        placeholder.pack(fill="x", padx=3, pady=5)
        placeholder.pack_propagate(False)
        icon = tk.Canvas(placeholder, width=38, height=38, bg="#ece9e2",
                         highlightthickness=0)
        icon.pack(pady=(31, 6))
        draw_icon(icon, "evidence", SILVER)
        tk.Label(placeholder, text="REPORTS WILL APPEAR HERE",
                 bg="#ece9e2", fg=LINE,
                 font=("Arial", 9, "bold")).pack()

    def _add_evidence_card(self, category, title, detail, footer,
                           unverified=False, muted=False):
        card = tk.Frame(self.evidence_cards, bg=CARD,
                        highlightbackground=INK, highlightthickness=2)
        card.pack(fill="x", padx=3, pady=(3, 8))
        stripe = RED if not muted else LINE
        tk.Frame(card, bg=stripe, width=5).pack(side="left", fill="y")
        copy = tk.Frame(card, bg=CARD)
        copy.pack(side="left", fill="both", expand=True, padx=12, pady=11)
        category_label = tk.Label(copy, text=category, bg=CARD,
                 fg=RED_DARK if not muted else MUTED,
                 font=("Courier New", 10, "bold"), anchor="w",
                 justify="left", wraplength=140)
        category_label.pack(fill="x")
        title_label = tk.Label(copy, text=title, bg=CARD, fg=INK,
                 font=("Arial", 12, "bold"), anchor="w", justify="left",
                 wraplength=140)
        title_label.pack(fill="x", pady=(4, 6))
        detail_label = tk.Label(copy, text=detail, bg=CARD, fg=INK if not muted else MUTED,
                 font=("Arial", 11), anchor="w", justify="left",
                 wraplength=140)
        detail_label.pack(fill="x")
        footer_label = tk.Label(copy, text=footer, bg=CARD,
                 fg=RED_DARK if unverified else MUTED,
                 font=("Courier New", 9, "bold"), anchor="w", justify="left",
                 wraplength=140)
        footer_label.pack(fill="x", pady=(8, 0))
        labels = (category_label, title_label, detail_label, footer_label)
        def fit_evidence_text(event):
            available = max(40, event.width - 8)
            for label in labels:
                if label.cget("wraplength") != available:
                    label.configure(wraplength=available)
        copy.bind("<Configure>", fit_evidence_text)

    def start_round(self, round_number):
        """Load the next randomly selected theme and reset its action limits."""
        self.game.round_number = round_number
        self.ui_phase = "ROUND"
        self.player_unlocked = True
        self.suspects_unlocked = True
        if round_number > 1:
            for person in self.case.characters.values():
                if person.character_id != PLAYER_ID:
                    person.public_suspicion = max(0, int(person.public_suspicion * 0.92))
        self.action_points = 2 if self.game.player_suspicion >= 55 else 3
        self.limits = {"investigate": 0, "persuade": 0, "deceive": 0}
        self.game.assign_npc_investigations()
        stage_id, stage_name = self.case.round_order[round_number - 1]
        objectives = {
            "scene_a": "Examine how objects and positions connect each person to the scene.",
            "scene_b": "Compare forensic traces with the weapon and death interval.",
            "movement": "Compare exact times, locations and unexplained gaps.",
            "secret": "Separate murder motives from unrelated reasons to lie.",
            "testimony": "Cross-check statements without treating every contradiction as murder.",
        }
        self.detective_kicker.configure(
            text=f"ROUND {round_number} // {self.short_stage_name(stage_name).upper()}"
        )
        self.set_detective(
            "This round's theme was assigned by the case. Choose which available lead "
            "you want to examine; the other suspects investigate independently."
        )
        self._render_round_view(round_number, stage_name, objectives[stage_id], stage_id)
        self.show_action_buttons()
        self.update_stats()

    def show_action_buttons(self):
        """Enable only the actions still available in the current round."""
        self.clear_actions()
        self.center.grid_rowconfigure(1, weight=2)
        self.center.grid_rowconfigure(2, weight=3)
        investigate_left = 2 - self.limits["investigate"]
        persuade_left = 1 - self.limits["persuade"]
        deceive_left = 1 - self.limits["deceive"]
        self.add_action_tile(
            f"Investigate — {investigate_left} left",
            "Choose one available lead from this round's theme.",
            self.open_investigate, "search", 0, 0,
            enabled=self.action_points > 0 and investigate_left > 0,
        )
        self.add_action_tile(
            f"Persuade — {persuade_left} left",
            "Offer evidence, defend yourself or request information.",
            self.open_persuade, "persuade", 0, 1,
            enabled=self.action_points > 0 and persuade_left > 0,
        )
        self.add_action_tile(
            f"Deceive — {deceive_left} left",
            "Mislead one suspect, with a risk of later exposure.",
            self.open_deceive, "deceive", 1, 0,
            enabled=self.action_points > 0 and deceive_left > 0,
        )
        self.add_action_tile(
            "End actions" if self.action_points else "Proceed to vote",
            (f"Spend your remaining {self.action_points} action point(s) first."
             if self.action_points else "Begin statements and the mandatory round vote."),
            self.begin_vote, "vote", 1, 1,
            enabled=self.action_points <= 0,
        )

    def spend_action(self, action_type):
        """Deduct one action and refresh controls and status consistently."""
        self.limits[action_type] += 1
        self.action_points -= 1
        self.show_action_buttons()
        self.update_stats()

    def choice_window(self, title, options, callback):
        """Show a modal with selectable alternatives and one confirmation action."""
        if not options:
            messagebox.showinfo(title, "No options are currently available.")
            return
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("560x420")
        window.configure(bg=PAPER)
        window.transient(self.root)
        window.grab_set()
        tk.Label(window, text=title, bg=PAPER, fg=INK,
                 font=("Arial Black", 18)).pack(anchor="w", padx=20, pady=(18, 10))
        listbox = tk.Listbox(window, bg=CARD, fg=INK, font=("Arial", 11),
                             selectbackground=RED, selectforeground=WHITE, activestyle="none",
                             highlightbackground=INK, highlightthickness=2)
        listbox.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        for option in options:
            listbox.insert("end", option)
        listbox.selection_set(0)

        def confirm():
            if not listbox.curselection():
                return
            index = listbox.curselection()[0]
            window.destroy()
            callback(index)

        self.dialog_button(window, "CONFIRM", confirm).pack(pady=(0, 18))

    def open_investigate(self):
        """Let Evelyn choose one available lead for the current theme."""
        if self.limits["investigate"] >= 2:
            messagebox.showinfo("Investigation", "You have already investigated twice this round.")
            return
        leads = self.game.current_available_evidence()
        if not leads:
            messagebox.showinfo("Investigation", "No unexamined clues remain in this round.")
            return

        body = self.open_modal(
            "Choose an investigation lead",
            f"Evelyn's action // Round {self.game.round_number}", 760, 570,
        )
        tk.Label(
            body,
            text="Choose what you want to examine. The full finding is revealed only after you confirm.",
            bg=PAPER, fg=MUTED, font=("Arial", 12), anchor="w",
            wraplength=690, justify="left",
        ).pack(fill="x", pady=(0, 12))
        listbox = tk.Listbox(
            body, bg=CARD, fg=INK, font=("Arial", 29),
            selectbackground=RED, selectforeground=WHITE,
            activestyle="none", highlightbackground=INK,
            highlightthickness=2, bd=0,
        )
        listbox.pack(fill="both", expand=True)
        for number, item in enumerate(leads, start=1):
            subject = self.game.character(item.subject_id)
            listbox.insert(
                "end",
                f"  {number:02d}   {subject.name}  —  {item.category.title()}",
            )
        listbox.selection_set(0)
        listbox.configure(height=max(5, len(leads)))

        def confirm():
            if not listbox.curselection():
                return
            item = leads[listbox.curselection()[0]]
            self.close_modal()
            self._reveal_investigation(item)

        self.dialog_button(body, "INVESTIGATE SELECTED LEAD", confirm).pack(
            anchor="e", pady=(14, 0)
        )

    def _reveal_investigation(self, item):
        """Record the selected clue and display the resulting report."""
        self.game.add_evidence(item)
        self.detective_kicker.configure(text="INVESTIGATION REPORT // EVIDENCE COLLECTED")
        self.set_detective(
            "Your chosen search has produced a report. It is now pinned to the evidence board."
        )
        self.set_content([
            (item.title + "\n", "title"),
            ("INITIAL FINDING\n", "heading"), (item.summary + "\n\n", ""),
            ("FULL DETAIL\n", "heading"), (item.detail + "\n", ""),
        ])
        self.spend_action("investigate")

    def open_persuade(self):
        """Collect a conversation choice before applying the shared game rules."""
        if self.limits["persuade"] >= 1:
            messagebox.showinfo("Persuasion", "You have already used persuasion this round.")
            return
        people = [person for person in self.case.characters.values() if person.character_id != PLAYER_ID]
        body = self.open_modal("Persuade or exchange", "Evelyn's action", 690, 515)
        tk.Label(body,
                 text="Choose what you want from this conversation. Only the relevant fields are shown.",
                 bg=PAPER, fg=MUTED, font=("Arial", 12), anchor="w").pack(fill="x")
        form = tk.Frame(body, bg=PAPER)
        form.pack(fill="both", expand=True, pady=(8, 0))

        def row(label, values):
            holder = tk.Frame(form, bg=PAPER)
            tk.Label(holder, text=label.upper(), bg=PAPER, fg=RED_DARK,
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(6, 3))
            combo = ttk.Combobox(holder, values=values, state="readonly")
            combo.current(0)
            combo.pack(fill="x")
            return holder, combo

        person_row, person_box = row("Person", [f"{p.name} · trust {p.trust_evelyn}" for p in people])
        purpose_row, purpose_box = row("Purpose", [
            "Defend Evelyn - reduce suspicion",
            "Redirect suspicion to another person",
            "Exchange one known clue for information",
        ])
        tone_names = ["evidence", "emotion", "bargain", "pressure"]
        tone_row, tone_box = row("Approach", [
            "Evidence - use facts and contradictions",
            "Emotion - appeal to sympathy or loyalty",
            "Bargain - offer mutual help",
            "Pressure - confront them (can backfire)",
        ])
        targets = [p for p in people]
        target_row, target_box = row("Person to redirect suspicion toward", [p.name for p in targets])
        found = [self.game.evidence(item_id) for item_id in self.game.found_evidence]
        give_row, give_box = row(
            "Information offered",
            [f"{item.title} | concerns {self.game.character(item.subject_id).name}"
             for item in found] or ["No evidence available"],
        )
        person_row.pack(fill="x")
        purpose_row.pack(fill="x")

        def update_form(_event=None):
            tone_row.pack_forget()
            target_row.pack_forget()
            give_row.pack_forget()
            purpose = purpose_box.current()
            if purpose in (0, 1):
                tone_row.pack(fill="x")
            if purpose == 1:
                target_row.pack(fill="x")
            elif purpose == 2:
                give_row.pack(fill="x")

        purpose_box.bind("<<ComboboxSelected>>", update_form)
        update_form()

        def execute():
            person = people[person_box.current()]
            purpose = purpose_box.current()
            tone = tone_names[tone_box.current()] if purpose in (0, 1) else "bargain"
            fit = 18 if tone == person.preference else 0
            if tone == "pressure":
                fit -= 15
            persuasion_score = (
                person.trust_evelyn + fit + len(self.game.found_evidence) * 2
                + (self.game.credibility - 50) * 0.25
                - max(0, person.suspicion_evelyn - 40) * 0.15
            )
            success = persuasion_score >= 58
            if purpose == 0:
                if success:
                    person.suspicion_evelyn = max(0, person.suspicion_evelyn - 12)
                    person.trust_evelyn = min(100, person.trust_evelyn + 7)
                    result = f"{person.name} accepts part of Evelyn's explanation."
                else:
                    person.suspicion_evelyn = min(100, person.suspicion_evelyn + 6)
                    person.trust_evelyn = max(0, person.trust_evelyn - 4)
                    result = f"{person.name} remains unconvinced."
            elif purpose == 1:
                target = targets[target_box.current()]
                if target.character_id == person.character_id:
                    messagebox.showwarning("Target", "Choose someone other than the person being persuaded.")
                    return
                person.private_suspicion[target.character_id] = (
                    person.private_suspicion.get(target.character_id, 0) + (12 if success else 2)
                )
                result = f"{person.name} listens to Evelyn's argument about {target.name}."
            else:
                if not found:
                    messagebox.showwarning("Exchange", "You have no evidence to offer yet.")
                    return
                given = found[give_box.current()]
                before = len(self.game.public_information)
                self.game.exchange_information(person, given, success)
                if len(self.game.public_information) > before:
                    result = f"{person.name}: {self.game.public_information[-1][1]}"
                else:
                    result = f"{person.name} completes the exchange."
            self.close_modal()
            self.set_content([("Conversation result\n", "title"), (result + "\n", "")])
            self.spend_action("persuade")

        self.dialog_button(body, "PROCEED", execute).pack(anchor="e", pady=(10, 0))

    def open_deceive(self):
        """Offer a deceptive statement and record its later consequences."""
        if self.limits["deceive"] >= 1:
            messagebox.showinfo("Deception", "You have already attempted deception this round.")
            return
        people = [person for person in self.case.characters.values() if person.character_id != PLAYER_ID]
        lies = [
            ("I never went near the crime scene.", 70),
            ("I left long before the death.", 55),
            ("I concealed only a private argument.", 25),
            ("I saw another suspect leaving the area.", 45),
        ]
        body = self.open_modal("Create a statement", "Evelyn's action // Deception", 650, 420)
        tk.Label(
            body,
            text="Risk is the base discovery chance. Counter-evidence raises it; trust and credibility can lower it.",
            bg=PAPER, fg=MUTED, font=("Arial", 12), wraplength=580, justify="left",
        ).pack(anchor="w", pady=(0, 14))
        tk.Label(body, text="PERSON", bg=PAPER, fg=RED_DARK,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        person_box = ttk.Combobox(body, values=[p.name for p in people], state="readonly")
        person_box.current(0)
        person_box.pack(fill="x", pady=(3, 14))
        tk.Label(body, text="STATEMENT", bg=PAPER, fg=RED_DARK,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        lie_box = ttk.Combobox(body, values=[f"{text} (base risk {risk}%)" for text, risk in lies],
                               state="readonly")
        lie_box.current(0)
        lie_box.pack(fill="x", pady=(3, 14))

        def execute():
            person = people[person_box.current()]
            text, risk = lies[lie_box.current()]
            self.game.lies.append({"target": person.character_id, "text": text,
                                   "risk": risk, "checked": False})
            person.suspicion_evelyn = max(0, person.suspicion_evelyn - 8)
            self.game.player_suspicion = max(0, self.game.player_suspicion - 4)
            self.close_modal()
            self.set_content([("Statement delivered\n", "title"),
                              (f"Evelyn tells {person.name}: “{text}”\n\n", ""),
                              ("Its consequences will emerge through later evidence and reactions.\n", "muted")])
            self.spend_action("deceive")

        self.dialog_button(body, "DELIVER STATEMENT", execute).pack(anchor="e", pady=12)

    def begin_vote(self):
        """Collect Evelyn's suspect and supporting clue after actions end."""
        self.ui_phase = "VOTE"
        self.detective_kicker.configure(
            text=f"ROUND {self.game.round_number} // STATEMENTS AND VOTE"
        )
        exposed = self.game.check_lies()
        self.game.prepare_npc_investigations()
        self.action_points = 0
        self.set_detective(
            "The other suspects have completed their investigations. "
            "Everyone must now make a statement and cast one vote."
        )
        parts = [("Mandatory vote\n", "title")]
        if exposed:
            parts.append(("CONTRADICTIONS EXPOSED\n", "heading"))
            for line in exposed:
                parts.append(("• " + line + "\n", ""))
            parts.append(("\n", ""))
        parts.extend([
            ("EVELYN'S DECISION\n", "heading"),
            ("Choose one suspect and one item from your evidence board.\n", ""),
        ])
        self.set_content(parts)
        self.clear_actions()
        report = self.stage.winfo_children()[0]
        form_row = report.grid_size()[1]
        report.grid_rowconfigure(form_row, weight=0)
        form = tk.Frame(report, bg="#ebe9e3", highlightbackground=INK,
                        highlightthickness=2)
        form.grid(row=form_row, column=0, sticky="ew", pady=(18, 0))
        form.grid_columnconfigure(0, weight=2)
        form.grid_columnconfigure(1, weight=3)
        tk.Label(form, text="Who gets your vote?", bg="#ebe9e3", fg=RED_DARK,
                 font=("Arial", 16, "bold"), anchor="w").grid(
                     row=0, column=0, sticky="ew", padx=18, pady=(15, 6))
        tk.Label(form, text="Which evidence will you submit?", bg="#ebe9e3", fg=RED_DARK,
                 font=("Arial", 16, "bold"), anchor="w").grid(
                     row=0, column=1, sticky="ew", padx=18, pady=(15, 6))
        candidates = [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]
        evidence = [self.game.evidence(item_id) for item_id in self.game.found_evidence]
        target_box = ttk.Combobox(form, values=[p.name for p in candidates], state="readonly", width=18,
                                  font=("Arial", 19), style="Vote.TCombobox")
        target_box.current(0)
        target_box.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 22), ipady=11)
        proof_box = ttk.Combobox(form,
                                 values=[f"{item.title} | {self.game.character(item.subject_id).name}"
                                         for item in evidence] or ["No evidence"],
                                 state="readonly", width=32, font=("Arial", 19),
                                 style="Vote.TCombobox")
        proof_box.current(0)
        proof_box.grid(row=1, column=1, sticky="ew", padx=18, pady=(0, 22), ipady=11)
        submit_vote = IconActionButton(
            form, "SUBMIT VOTE",
            lambda: self.resolve_vote(candidates[target_box.current()],
                                      evidence[proof_box.current()] if evidence else None),
            icon="vote", accent=True,
        )
        submit_vote.grid(row=2, column=1, sticky="e", padx=18, pady=(0, 18))
        report.grid_rowconfigure(form_row + 1, weight=1)
        self.update_stats()

    def resolve_vote(self, target, proof):
        """Apply the five votes and their consequences using shared game state."""
        self.ui_phase = "SUMMARY"
        self.detective_kicker.configure(
            text=f"DETECTIVE ARTHUR REED // ROUND {self.game.round_number} REVIEW"
        )
        if proof:
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
            target.public_suspicion += 3
        target.retaliation += 10
        target.suspicion_evelyn = min(100, target.suspicion_evelyn + 5)
        votes = [{"round": self.game.round_number, "from": PLAYER_ID,
                  "to": target.character_id, "proof": proof.evidence_id if proof else None}]
        for voter in [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]:
            accused = self.game.npc_vote(voter)
            votes.append({"round": self.game.round_number, "from": voter.character_id,
                          "to": accused.character_id, "proof": None})
        self.game.votes.extend(votes)
        tally = {character_id: 0 for character_id in self.case.characters}
        for vote in votes:
            tally[vote["to"]] += 1
        for character_id, count in tally.items():
            if character_id == PLAYER_ID:
                self.game.player_suspicion = min(100, self.game.player_suspicion + count * 6)
            else:
                self.game.character(character_id).public_suspicion += count * 2

        reports = {report["speaker"]: report
                   for report in self.game.round_reports[self.game.round_number]}
        parts = [(f"Round {self.game.round_number} statements and votes\n", "title"),
                 ("STATEMENTS\n", "heading"),
                 (f"Evelyn Hart: “{target.name} must explain the contradictions in the evidence.”\n\n", "")]
        self.game.statements.append((self.game.round_number, PLAYER_ID,
                                     f"{target.name} must explain the contradictions in the evidence."))
        for person in [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]:
            statement = reports[person.character_id]["statement"]
            parts.append((f"{person.name}: “{statement}”\n\n", ""))
            self.game.statements.append((self.game.round_number, person.character_id, statement))
        parts.append(("VOTES\n", "heading"))
        for vote in votes:
            parts.append((f"{self.game.character(vote['from']).name} → "
                          f"{self.game.character(vote['to']).name}\n", ""))
        unanimous = next((character_id for character_id, count in tally.items() if count == 5), None)
        if unanimous:
            parts.append((f"\nAll five votes accuse {self.game.character(unanimous).name}.\n", "bold"))
        parts.append((f"\nEvelyn's suspicion is now {self.game.player_suspicion}.\n", "bold"))
        review = self.capture_game_output(self.game.detective_round_review, votes, tally, proof)
        parts.append(("\nDETECTIVE REED'S ROUND REVIEW\n", "heading"))
        for line in review:
            cleaned = line.strip()
            if cleaned and cleaned != "DETECTIVE REED'S ROUND REVIEW":
                parts.append((cleaned + "\n", ""))
        self.set_content(parts)
        self.clear_actions()
        for person in self.case.characters.values():
            if person.character_id != PLAYER_ID:
                person.retaliation = max(0, person.retaliation - 5)
        if self.game.player_suspicion >= 90:
            self.add_button("View detention result", self.show_early_arrest, True)
        elif self.game.round_number < len(self.case.round_order):
            self.add_button(f"Begin Round {self.game.round_number + 1}",
                            lambda: self.start_round(self.game.round_number + 1), True)
        else:
            self.add_button("Build final theory", self.show_final_phase, True)
        self.update_stats()

    def show_early_arrest(self):
        killer = self.game.character(self.case.killer_id)
        self.game.round_number = len(self.case.round_order) + 2
        self.ui_phase = "VERDICT"
        self.detective_kicker.configure(text="DETENTION NOTICE // CASE REMAINS OPEN")
        self.set_detective("Evelyn's public suspicion has reached the detention threshold.")
        self.set_content([
            ("Evelyn is detained\n", "title"),
            ("She can no longer influence the investigation.\n\n", ""),
            ("CASE FILE\n", "heading"),
            (f"The complete investigation later identifies {killer.name} as the true killer.\n", ""),
        ])
        self.clear_actions()
        self.add_button("New case", self.show_start_screen, True)
        self.game.write_history()
        self.update_stats()

    def show_final_phase(self):
        """Present the final theory builder after the three selected rounds."""
        self.game.round_number = len(self.case.round_order) + 1
        self.ui_phase = "FINAL"
        self.detective_kicker.configure(text="FINAL ASSESSMENT // BUILD YOUR THEORY")
        totals = self.game.vote_totals()
        parts = [("Final theory\n", "title"), ("ACCUMULATED VOTES\n", "heading")]
        for character_id, count in totals.items():
            parts.append((f"{self.game.character(character_id).name}: {count}\n", ""))
        parts.append(("\nChoose Evelyn's final suspect and two evidence items. Evidence that concerns "
                      "the accused is useful; two positive clues from different investigation "
                      "stages create a stronger chain.\n", "muted"))
        self.set_content(parts)
        self.clear_actions()
        self.add_button("Build final theory", self.open_final_builder, True)
        self.update_stats()

    def open_final_builder(self):
        """Gather the final accusation and evidence chain from the player."""
        candidates = [p for p in self.case.characters.values() if p.character_id != PLAYER_ID]
        evidence = [self.game.evidence(item_id) for item_id in self.game.found_evidence]
        body = self.open_modal("Evelyn's final theory", "Final assessment", 720, 500)
        tk.Label(body, text="Select the accused person and two different supporting clues.",
                 bg=PAPER, fg=MUTED, font=("Arial", 12)).pack(anchor="w", pady=(0, 8))
        form = tk.Frame(body, bg=PAPER)
        form.pack(fill="both", expand=True)

        def add_combo(label, values):
            tk.Label(form, text=label, bg=PAPER, fg=RED,
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 4))
            combo = ttk.Combobox(form, values=values, state="readonly")
            combo.current(0)
            combo.pack(fill="x", ipady=4)
            return combo

        target_box = add_combo("FINAL ACCUSATION", [p.name for p in candidates])
        labels = [self.game.evidence_option(item) for item in evidence]
        first_box = add_combo("FIRST EVIDENCE", labels or ["No evidence available"])
        second_box = None
        if len(evidence) >= 2:
            second_box = add_combo("SECOND EVIDENCE", labels)
            second_box.current(1)

        def submit():
            if len(evidence) >= 2:
                if first_box.current() == second_box.current():
                    messagebox.showwarning("Evidence", "Choose two different evidence items.")
                    return
                proof = [evidence[first_box.current()], evidence[second_box.current()]]
            else:
                proof = evidence
            theory = candidates[target_box.current()]
            self.close_modal()
            self.resolve_final(theory, proof)

        self.dialog_button(body, "DELIVER FINAL THEORY", submit).pack(anchor="e", pady=16)

    def resolve_final(self, theory, proof):
        """Calculate and display the verdict using the core scoring functions."""
        scores, ranking = self.game.calculate_final_scores(theory, proof)
        convicted, reason = self.game.decide_verdict(scores, ranking)
        killer = self.game.character(self.case.killer_id)
        correct = convicted is not None and convicted.character_id == killer.character_id
        if killer.character_id == PLAYER_ID:
            result = "Evelyn is exposed and loses." if correct else "Evelyn avoids conviction and wins."
        elif correct:
            result = "Evelyn identifies the real killer and wins."
        elif convicted and convicted.character_id == PLAYER_ID:
            result = "Evelyn is innocent but is wrongly convicted."
        else:
            result = "Evelyn fails to secure the correct conviction."

        self.game.round_number = len(self.case.round_order) + 2
        self.ui_phase = "VERDICT"
        self.detective_kicker.configure(text="DETECTIVE ARTHUR REED // FINAL VERDICT")
        self.set_detective("The social verdict is complete. The sealed case file may now be opened.")
        if killer.character_id == PLAYER_ID:
            headline = "You win: your identity remains concealed" if not correct else "You lose: your identity has been exposed"
        elif convicted and convicted.character_id == PLAYER_ID:
            headline = "You lose: you were wrongly convicted"
        else:
            headline = "You win: the real killer was found" if correct else "You lose: the real killer escaped conviction"
        verdict = convicted.name if convicted else "no one"
        parts = [(headline, "title"), (result, "bold"),
                 ("Your final accusation and the verdict", "heading"),
                 (f"You accused {theory.name}. Convicted: {verdict}. The real killer: {killer.name}.", "")]
        parts.append(("Votes and verdict scores", "heading"))
        for person in ranking:
            score = scores[person.character_id]
            parts.append((f"{person.name}: {score['votes']} votes; evidence {score['evidence']}; "
                          f"chain bonus {score['chain']}; accusation bonus {score['theory']}; "
                          f"total {score['total']}", ""))
        parts.append(("Your evidence and its connection", "heading"))
        if proof:
            for item in proof:
                subject = self.game.character(item.subject_id)
                effect = "raises suspicion" if item.points > 0 else "supports an alibi" if item.points < 0 else "is inconclusive"
                parts.append((f"{item.title}: concerns {subject.name} and {effect}.", ""))
        else:
            parts.append(("You submitted no evidence.", ""))
        linked = [item for item in proof if item.subject_id == theory.character_id and item.points > 0]
        if len({item.stage for item in linked}) >= 2:
            chain_text = "Two supporting clues about the person you accused came from different investigation stages, forming a strong evidence chain."
        elif linked:
            chain_text = "At least one clue supports your accusation, but the clues do not form a strong chain across investigation stages."
        else:
            chain_text = "The submitted clues do not form an evidence chain supporting your accusation."
        parts.append((chain_text, ""))
        parts.append(("Why the verdict was reached", "heading"))
        parts.append((reason, ""))
        parts.extend([
            ("What really happened", "heading"),
            (f"{killer.name} killed Charles Whitmore at {self.case.time} in the {self.case.location} "
             f"using {self.case.weapon}, in order to {self.case.motive}. Afterwards, the killer "
             f"{self.case.cover_up}.", ""),
        ])
        self.set_content(parts, scrollable=True)
        self.clear_actions()
        self.add_button("Generate another case", self.show_start_screen, True)
        self.game.write_history()
        self.update_stats()


def runtime_compatibility_error():
    """Return a clear explanation for unsupported macOS system Tk builds."""
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        return (
            "This Python uses the deprecated macOS system Tk 8.5. It can create "
            "a window frame, but complex controls may render as a blank window.\n\n"
            "Install Python 3.12 or later from python.org, select that interpreter "
            "in VS Code, open a new terminal, and run:\n"
            "python3 check_tkinter.py\n\n"
            "The command 'which python3' must not show /usr/bin/python3."
        )
    return None


def main():
    problem = runtime_compatibility_error()
    if problem:
        print("The Fifth Alibi GUI cannot start with this Python installation.\n")
        print(problem)
        return 2
    root = tk.Tk()
    root.withdraw()
    try:
        FifthAlibiGUI(root)
        root.update_idletasks()
        root.deiconify()
        root.lift()
    except Exception as error:
        details = traceback.format_exc()
        try:
            Path("fifth_alibi_gui_error.log").write_text(details, encoding="utf-8")
        except OSError:
            pass
        try:
            messagebox.showerror(
                "The Fifth Alibi - startup error",
                "The interface could not finish loading. Details were written to "
                "fifth_alibi_gui_error.log.\n\n" + str(error),
                parent=root,
            )
        except tk.TclError:
            print(details, file=sys.stderr)
        root.destroy()
        raise
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
