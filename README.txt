THE FIFTH ALIBI — COMP9001 Final Project
========================================

1. PROJECT OVERVIEW
-------------------
The Fifth Alibi is a single-player, replayable murder mystery written in
Python. You play Evelyn Hart, one of five suspects after Charles Whitmore is
found dead. Investigate clues, speak to suspects, manage suspicion, and vote
before presenting a final accusation supported by evidence. A case code
reproduces the same underlying mystery for replay or demonstration.

2. SUBMISSION AND WHICH VERSION TO RUN
--------------------------------------
Submit all Python source files in Ed's Code Submission. The illustration
folder cannot be uploaded there. The complete project folder, including this
README and assets/, will be sent separately to the tutor by email. The two
versions use the same game rules:

* On Ed or in a terminal, run fifth_alibi.py. It needs no image files,
  Tkinter window, or third-party packages. This is the version to use if the
  GUI cannot be displayed.
* On a desktop computer, run fifth_alibi_gui.py from the complete emailed
  folder. Keep assets/ beside the Python files to see the illustrations.
  Ed's code runner cannot display a Tkinter window.

Use Python 3.12 or later. The GUI also needs Tkinter with Tk 8.6 or later and
a graphical desktop. No third-party packages, network access, or audio/video
tools are required. The GUI has been tested on macOS; its layout can vary with
the operating system, font availability, and display scaling.

3. EXACT RUN INSTRUCTIONS
-------------------------
Download or extract the complete emailed folder, open a terminal or command
prompt, and change into the directory containing fifth_alibi.py. Do not run
the commands from the parent directory.

macOS / Linux:
    python3 fifth_alibi.py
    python3 fifth_alibi_gui.py

Windows (with the Python launcher):
    py fifth_alibi.py
    py fifth_alibi_gui.py

For example, after extracting a folder named fifth_alibi_gui_english, change
into that folder first. If a computer uses a different Python command, replace
python3 or py with that command. The program creates a case code when you
start; follow the numbered prompts in the terminal or the buttons in the GUI.

To check Tkinter if the GUI does not open, run the appropriate command:
macOS / Linux:
    python3 check_tkinter.py
Windows:
    py check_tkinter.py

If Tkinter is unavailable, use fifth_alibi.py. If the GUI launches but images
are missing, check that assets/ is inside the same folder as the scripts.

4. HOW TO PLAY
--------------
1. Generate a new case code, or enter an earlier code to replay the same
   killer, murder method, location, evidence, and investigation order.
2. Read the incident report, Evelyn's identity, the other four suspects'
   profiles, and Detective Reed's briefing.
3. Play three distinct investigation themes randomly selected from five:
   two crime-scene themes, a movement timeline, secrets, and testimony.
   In each round, spend action points to investigate leads, persuade someone,
   or deceive someone. Investigations and conversations have per-round limits.
4. After the actions, review the suspects' statements and cast Evelyn's vote
   for one suspect, selecting supporting evidence from any clues found.
5. After three rounds, accuse a suspect and select up to two evidence items.
   The report first states the outcome, then explains votes, scores, evidence
   connections, and what actually happened. Evelyn can be the killer, and
   high suspicion may cause her early arrest.

In the GUI, the left rail holds character dossiers and the right rail is a
scrollable evidence board. Death-scene and round illustrations are selected
to match the generated case. The terminal version presents the same game
rules through numbered text choices.

5. FILE GUIDE
-------------
fifth_alibi.py            Case generation, domain classes, game rules,
                          scoring, verdict, and terminal entry point.
fifth_alibi_gui.py        Tkinter interface using the same game rules.
check_tkinter.py          Local Tkinter compatibility check.
test_game.py              Automated game-rule tests.
test_gui_compatibility.py GUI and illustration compatibility checks.
assets/                   Portraits and scene illustrations (emailed package).

Completed cases write fifth_alibi_history.json in the working directory.

6. OPTIONAL CHECKS
------------------
From the folder containing the Python files:

macOS / Linux:
    python3 fifth_alibi.py --demo
    python3 -m unittest discover -p 'test_*.py' -v

Windows:
    py fifth_alibi.py --demo
    py -m unittest discover -p "test_*.py" -v

--demo runs a non-interactive three-round smoke test; it is not the normal
play mode. The unittest command runs the packaged automated checks. GUI
compatibility checks need Tkinter; use the terminal game if the environment
cannot provide it. Automated checks do not replace a manual GUI playthrough
on the tutor's computer.

7. HOW THE PROJECT ADDRESSES THE MARKING CRITERIA
-------------------------------------------------

(A) FUNCTIONALITY
The playable terminal entry point is fifth_alibi.py; the illustrated entry
point is fifth_alibi_gui.py. Both run the case model in fifth_alibi.py. The
case progresses from setup and character introductions through three rounds,
mandatory votes, a final theory, and an explained outcome. Game.run controls
the terminal sequence; the GUI calls the same Game methods and shared verdict
functions. Limited actions, early arrest, and missing evidence have explicit
paths rather than leaving the player in an incomplete round. test_game.py
checks deterministic generation, distinct rounds, evidence exchanges,
deception, and final scoring; test_gui_compatibility.py checks key GUI stages
and packaged assets. The --demo command exercises three rounds without
manual input. These checks support the functionality claim; they cannot
guarantee identical display behaviour on every operating system.

(B) STRUCTURE AND DOCUMENTATION
Evidence, Character, and Case hold the case data. CaseGenerator creates a
reproducible mystery; Game owns actions, NPC behaviour, voting, scoring, and
the terminal flow. DemoGame provides a non-interactive check. The separate
FifthAlibiGUI class handles Tkinter layout, dialogs, image display, and input
while calling the shared rules. Functions separate case generation, clue
selection, social interactions, verdict calculation, and history saving.
English comments and docstrings explain the important classes, stage changes,
and decisions. This README identifies the entry points, files, requirements,
commands, and gameplay so the project can be run without reading the source.

(C) ADVANCED PYTHON CONCEPTS
1. Object-oriented programming: Evidence, Character, Case, CaseGenerator,
   and Game separate the fixed case solution from changing character beliefs
   and player actions. The GUI reuses those objects instead of duplicating
   the rules.
2. File I/O and exception handling: Game.write_history serialises the case
   result, discovered evidence, and votes to fifth_alibi_history.json. It
   catches OSError and tells the player if saving fails, without discarding
   the game result. The GUI also reports callback errors to a log; missing
   optional illustration files leave a usable text or placeholder view.
3. Reproducible randomisation and nested data structures: CaseGenerator uses
   a local random.Random instance seeded by the case code. It selects the
   culprit, method, location, clues, and three of five investigation topics.
   Dictionaries and lists hold characters' private suspicion, evidence, and
   votes; these data feed the evidence-chain and final-score calculations.

(D) CREATIVITY AND ORIGINALITY
The player is both an investigator and a possible suspect. Each case code
creates a replayable social mystery with a different culprit, murder method,
clue set, and selection of investigation themes. NPCs investigate and vote
independently; trust, deception, retaliation, and evidence sharing can change
their views of Evelyn and of one another. The final decision combines votes,
clue relevance, and evidence from different investigation stages, then
explains the result and reveals the actual events. The optional GUI presents
the same mystery through character dossiers, an evidence board, and original
red-and-black scene illustrations; the terminal version remains fully
playable without images.

Padlet and presentation: The separate Padlet post needs the project title,
a representative image, and a short description naming the target audience.
The in-class presentation is three minutes. Those submission activities
cannot be established by the program files alone.
