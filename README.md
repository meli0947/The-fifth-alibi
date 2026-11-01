# The Fifth Alibi

**COMP9001 Final Python Project**

## Project overview

*The Fifth Alibi* is a single-player, replayable murder mystery written in Python. You play Evelyn Hart, one of five suspects after Charles Whitmore is found dead at his estate. Investigate clues, interact with suspects, manage suspicion and trust, vote each round, and make a final accusation supported by evidence.

Each case has a code that can be reused to replay the same underlying mystery. The project has a fully playable terminal version and an illustrated Tkinter GUI. Both versions use the same game rules.

## Submission and complete project

The Python source files and this README are submitted to Ed's Code Submission. Because Ed has a 2 MB upload limit, the complete illustrated project is provided as a ZIP file on GitHub:

**The complete project download link:https: //github.com/meli0947/The-fifth-alibi/releases/download/v1.0/fifth_alibi_gui_MenghaoLi.zip
**

On the Release page, expand **Assets** and download **`The_Fifth_Alibi_MenghaoLi.zip`** (approximately 38 MB). Extract this file to obtain the Python scripts and the `assets/` folder. **Do not download GitHub's automatically generated “Source code (zip)”** for the illustrated version: the repository's source archive does not contain the illustration assets.

The terminal version does not require the illustrations. Ed's online runner cannot display a Tkinter window, so the tutor can run the terminal version on Ed and download the complete ZIP to try the GUI locally.

The hosted project will not be modified after the submission deadline.

## Requirements

- Python 3.12 or later.
- No third-party Python packages.
- A terminal for the text version.
- Tkinter with Tk 8.6 or later and a graphical desktop for the GUI.
- No network connection during play.

The GUI was tested on macOS. Its appearance may vary with the operating system, available fonts, screen size, and display scaling.

## How to run

Download and extract **`The_Fifth_Alibi_MenghaoLi.zip`** from the Release page. Open a terminal or command prompt and change into the extracted folder containing `fifth_alibi.py` and `fifth_alibi_gui.py`. Run the commands **from that folder**, not its parent.

| Version | macOS / Linux | Windows |
|---|---|---|
| Terminal game | `python3 fifth_alibi.py` | `py fifth_alibi.py` |
| Illustrated GUI | `python3 fifth_alibi_gui.py` | `py fifth_alibi_gui.py` |
| Check Tkinter | `python3 check_tkinter.py` | `py check_tkinter.py` |

The terminal game uses numbered text prompts. The GUI uses buttons, character dossiers, and a scrollable evidence board.

If Tkinter is unavailable, use the terminal game. If the GUI opens without illustrations, check that `assets/` is in the same folder as the Python scripts.

## How to play

1. Start a new case or enter an existing case code to replay it.
2. Read the incident report, Evelyn's identity, the other suspects' dossiers, and Detective Reed's briefing.
3. Play three distinct investigation themes randomly selected from five. Spend limited action points investigating leads or interacting with suspects.
4. At the end of each round, review the suspects' statements and cast Evelyn's vote with supporting evidence.
5. After three rounds, make a final accusation. The final report states the outcome first, then explains the votes, evidence chain, and actual events.

Evelyn may herself be the culprit. High suspicion can also lead to her arrest before the final verdict.

## Files

| File or folder | Purpose |
|---|---|
| `fifth_alibi.py` | Case generation, character and evidence data, game rules, voting, verdict calculation, history saving, and the terminal entry point. |
| `fifth_alibi_gui.py` | Tkinter interface using the shared rules in `fifth_alibi.py`. |
| `check_tkinter.py` | Checks whether Tkinter is available locally. |
| `test_game.py` | Automated tests for game rules. |
| `test_gui_compatibility.py` | GUI and illustration compatibility checks. |
| `assets/` | Character portraits and scene illustrations included in the complete Release ZIP. |

Completed cases may be recorded in `fifth_alibi_history.json` in the working directory.

## Optional checks

| Check | macOS / Linux | Windows |
|---|---|---|
| Non-interactive demonstration | `python3 fifth_alibi.py --demo` | `py fifth_alibi.py --demo` |
| Automated tests | `python3 -m unittest discover -p 'test_*.py' -v` | `py -m unittest discover -p "test_*.py" -v` |

These checks supplement a normal playthrough. They do not guarantee identical GUI display on every computer.

## How the project addresses the marking criteria

### A. Functionality

Both versions cover the complete game flow: case setup, character introductions, three investigation rounds, player actions, suspect statements, round votes, a final accusation, and an explained outcome. The terminal and GUI interfaces use the same game model. The included tests and `--demo` mode provide ways to check important game behaviour.

### B. Structure and documentation

The code separates case data, case generation, game rules, and presentation:

- `Evidence`, `Character`, and `Case` represent the mystery and its participants.
- `CaseGenerator` creates reproducible cases from case codes.
- `Game` manages actions, NPC behaviour, voting, scoring, and the terminal flow.
- `FifthAlibiGUI` handles graphical layout and input while calling the shared game rules.

Functions divide major tasks, and English comments and docstrings explain important classes, stage changes, and decisions. This README identifies the files, entry points, requirements, commands, and gameplay steps.

### C. Advanced Python concepts

1. **Object-oriented programming:** Classes separate evidence, characters, case generation, changing game state, and the graphical interface. The GUI reuses the game model instead of duplicating its rules.
2. **File I/O and exception handling:** Completed cases can be saved as JSON. The program handles problems such as a failed save or a missing optional illustration without silently discarding the game result.
3. **Seeded randomisation and nested data structures:** Case codes produce replayable mysteries while varying culprits, murder methods, clues, investigation themes, character beliefs, and votes. Lists and dictionaries organise the evidence and changing social state used in the final verdict.

### D. Creativity and originality

The player investigates a murder while also being a suspect and potentially the culprit. Limited actions, changing trust, deception, independent NPC decisions, and evidence-based voting make each case a social mystery. The final report explains how the votes and clues relate to the verdict. Original noir-inspired artwork, character dossiers, and a live evidence board present the story visually, while the terminal version remains fully playable without images.

## Padlet and presentation

The separate Padlet post includes the project title, a representative image, and a short description naming the target audience. The project will also be demonstrated in a three-minute tutorial presentation.
