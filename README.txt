THE FIFTH ALIBI — COMP9001 Final Project
========================================

1. PROJECT OVERVIEW
-------------------
The Fifth Alibi is a single-player, replayable murder mystery written in
Python. You play Evelyn Hart, one of five suspects after Charles Whitmore
is found dead at his estate. Investigate clues, speak to suspects, manage
suspicion and trust, vote each round, and make a final accusation supported
by evidence. A case code reproduces the same underlying mystery for replay
or demonstration.

The project includes a fully playable terminal version and an illustrated
Tkinter GUI. Both versions use the same game rules.


2. SUBMISSION AND COMPLETE PROJECT
----------------------------------
All Python source files and this README.txt are submitted to Ed's Code
Submission. Ed has a 2 MB upload limit, so the complete illustrated project
is available as a ZIP file on GitHub:

https://github.com/meli0947/The-fifth-alibi/releases/latest

On that page, expand "Assets" and download:

The_Fifth_Alibi_MenghaoLi.zip

This is the complete project ZIP, approximately 38 MB. Extract it to obtain
the Python scripts and the assets/ folder. Do not use GitHub's automatically
generated "Source code (zip)" for the illustrated version, because that
archive does not contain the illustration assets.

The terminal version, fifth_alibi.py, does not need the image assets or a
Tkinter window. Ed's online runner cannot display the GUI, so the tutor can
run the terminal version on Ed and download the complete ZIP to try the GUI
locally. The hosted project will not be modified after the submission
deadline.


3. REQUIREMENTS
---------------
- Python 3.12 or later.
- No third-party Python packages are required.
- The terminal version needs a command-line terminal.
- The GUI needs Tkinter with Tk 8.6 or later and a graphical desktop.
- The game does not require network access during play.

The GUI has been tested on macOS. Its layout may vary with the operating
system, available fonts, screen size, and display scaling.


4. EXACT RUN INSTRUCTIONS
-------------------------
Download and extract The_Fifth_Alibi_MenghaoLi.zip. Open a terminal or
command prompt and change into the extracted folder containing
fifth_alibi.py and fifth_alibi_gui.py. Run the commands from that folder,
not its parent directory.

Terminal version:

    macOS / Linux:  python3 fifth_alibi.py
    Windows:        py fifth_alibi.py

Illustrated GUI version:

    macOS / Linux:  python3 fifth_alibi_gui.py
    Windows:        py fifth_alibi_gui.py

The terminal version uses numbered text prompts. The GUI uses buttons,
character dossiers, and a scrollable evidence board.

If the GUI does not open, check Tkinter with:

    macOS / Linux:  python3 check_tkinter.py
    Windows:        py check_tkinter.py

If Tkinter is unavailable, use fifth_alibi.py. If the GUI opens but images
are missing, check that assets/ is inside the same folder as the scripts.


5. HOW TO PLAY
--------------
1. Start a new case or enter an earlier case code to replay the same
   underlying mystery.
2. Read the incident report, Evelyn's identity, the other suspects'
   dossiers, and Detective Reed's briefing.
3. Play three distinct investigation themes randomly selected from five.
   In each round, spend limited action points investigating leads or
   interacting with suspects. Suspicion, trust, and evidence can change.
4. After each round, review the other suspects' statements and cast
   Evelyn's vote for one suspect with supporting evidence.
5. After three rounds, make a final accusation and select supporting
   evidence. The final report states the outcome first, then explains
   the votes, evidence chain, and actual events.

Evelyn herself may be the culprit. High suspicion may also cause her
arrest before the final verdict.


6. FILE GUIDE
-------------
fifth_alibi.py
    Case generation, character and evidence data, game rules, voting,
    verdict calculation, history saving, and the terminal entry point.

fifth_alibi_gui.py
    Tkinter interface using the shared rules in fifth_alibi.py.

check_tkinter.py
    Local Tkinter compatibility check.

test_game.py
    Automated game-rule tests.

test_gui_compatibility.py
    GUI and illustration compatibility checks.

assets/
    Character portraits and scene illustrations in the complete
    Release ZIP.

Completed cases may write fifth_alibi_history.json in the working
directory.


7. OPTIONAL CHECKS
------------------
To run a non-interactive terminal demonstration:

    macOS / Linux:  python3 fifth_alibi.py --demo
    Windows:        py fifth_alibi.py --demo

To run the included automated tests:

    macOS / Linux:
        python3 -m unittest discover -p 'test_*.py' -v

    Windows:
        py -m unittest discover -p "test_*.py" -v

These checks supplement a normal playthrough. They cannot guarantee
identical GUI display on every computer.


8. HOW THE PROJECT ADDRESSES THE MARKING CRITERIA
-------------------------------------------------

(A) FUNCTIONALITY

The terminal and GUI versions cover the complete game flow: case setup,
character introductions, three investigation rounds, player actions,
suspect statements, round votes, a final accusation, and an explained
outcome. Both interfaces use the same game model. The included tests and
--demo mode provide ways to check important game behaviour.


(B) STRUCTURE AND DOCUMENTATION

The code separates case data, case generation, game rules, and
presentation. Evidence, Character, and Case represent the mystery.
CaseGenerator creates reproducible cases from case codes. Game manages
player actions, NPC behaviour, voting, scoring, and the terminal flow.
FifthAlibiGUI handles graphical layout and input while calling the shared
game rules.

Functions divide major tasks. English comments and docstrings explain
important classes, stage changes, and decisions. This README identifies
the files, entry points, requirements, commands, and gameplay steps.


(C) ADVANCED PYTHON CONCEPTS

1. Object-oriented programming:
   Classes separate evidence, characters, case generation, changing game
   state, and the graphical interface. The GUI reuses the game model
   instead of duplicating its rules.

2. File I/O and exception handling:
   Completed cases can be saved as JSON. The program handles problems
   such as a failed save or a missing optional illustration without
   silently discarding the game result.

3. Seeded randomisation and nested data structures:
   Case codes produce replayable mysteries while varying culprits,
   murder methods, clues, investigation themes, character beliefs, and
   votes. Lists and dictionaries organise evidence and changing social
   information used in the final verdict.


(D) CREATIVITY AND ORIGINALITY

The player investigates a murder while also being a suspect and
potentially the culprit. Limited actions, changing trust, deception,
independent NPC decisions, and evidence-based voting make each case a
social mystery. The final report explains how votes and clues relate to
the verdict.

The optional GUI presents the story through character dossiers, a live
evidence board, and original noir-inspired illustrations. The terminal
version remains fully playable without images.


9. PADLET AND PRESENTATION
--------------------------
The separate Padlet post includes the project title, a representative
image, and a short description naming the target audience. The project
will also be demonstrated in a three-minute tutorial presentation.
