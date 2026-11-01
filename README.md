# The Fifth Alibi

**COMP9001 Final Python Project**

## Project overview

*The Fifth Alibi* is a single-player, replayable murder mystery written in Python. You play Evelyn Hart, one of five suspects after Charles Whitmore is found dead at his estate. Investigate clues, interact with suspects, manage suspicion and trust, vote each round, and make a final accusation supported by evidence.

Each case has a code that can be reused to replay the same underlying mystery. The project has a fully playable terminal version and an illustrated Tkinter GUI. Both use the same game rules.

## Submission and complete project

The Python source files and this README are submitted to Ed's Code Submission. Because Ed has a 2 MB upload limit, the complete project, including illustrations, is also hosted here:

**[Download the complete project from GitHub](https://github.com/meli0947/The-fifth-alibi)**

To play the illustrated GUI, download the complete project and keep `assets/` beside the Python files. The terminal version does not require illustrations. Ed's online runner cannot display a Tkinter window, so the tutor can run the terminal version on Ed and download the complete project to try the GUI locally.

The hosted project will not be modified after the submission deadline.

## Requirements

- Python 3.12 or later.
- No third-party Python packages.
- A terminal for the text version.
- Tkinter with Tk 8.6 or later and a graphical desktop for the GUI.
- No network connection during play.

The GUI was tested on macOS. Its appearance may vary with the operating system, fonts, screen size, and display scaling.

## How to run

Download and extract the complete project. Open a terminal or command prompt **inside the folder containing `fifth_alibi.py` and `fifth_alibi_gui.py`**.

| Version | macOS / Linux | Windows |
|---|---|---|
| Terminal game | `python3 fifth_alibi.py` | `py fifth_alibi.py` |
| Illustrated GUI | `python3 fifth_alibi_gui.py` | `py fifth_alibi_gui.py` |
| Check Tkinter | `python3 check_tkinter.py` | `py check_tkinter.py` |

The terminal game uses numbered prompts. The GUI uses buttons, character dossiers, and a scrollable evidence board.

If Tkinter is unavailable, use the terminal game. If the GUI opens without illustrations, check that `assets/` is in the same folder as the Python scripts.

## How to play

1. Start a new case or enter an existing case code to replay it.
2. Read the incident report, Evelyn's identity, the other suspects' dossiers, and Detective Reed's briefing.
3. Play three distinct investigation themes randomly selected from five. Spend limited action points investigating leads or interacting with suspects.
4. At the end of each round, review the suspects' statements and cast Evelyn's vote with supporting evidence.
5. After three rounds, make a final accusation. The report states the outcome first, then explains the votes, evidence chain, and actual events.

Evelyn may herself be the culprit. High suspicion can also lead to her arrest before the final verdict.

## Files

| File or folder | Purpose |
|---|---|
| `fifth_alibi.py` | Case generation, data classes, rules, voting, verdict, history saving, and terminal entry point. |
| `fifth_alibi_gui.py` | Tkinter interface using the shared rules in `fifth_alibi.py`. |
| `check_tkinter.py` | Checks whether Tkinter is available locally. |
| `test_game.py` | Automated game-rule tests. |
| `test_gui_compatibility.py` | GUI and illustration compatibility checks. |
| `assets/` | Character portraits and scene illustrations for the GUI. |

Completed cases may be recorded in `fifth_alibi_history.json` in the working directory.

## Optional checks

| Check | macOS / Linux | Windows |
|---|---|---|
| Non-interactive demonstration | `python3 fifth_alibi.py --demo` | `py fifth_alibi.py --demo` |
| Automated tests | `python3 -m unittest discover -p 'test_*.py' -v` | `py -m unittest discover -p "test_*.py" -v` |

These checks supplement a normal playthrough. They do not guarantee identical GUI display on every computer.

## How the project addresses the marking criteria

### A. Functionality

Both versions cover the complete flow: case setup, character introductions, three investigation rounds, actions, statements, round votes, a final accusation, and an explained outcome. They use the same game model. The tests and `--demo` mode provide ways to check important behaviour.

### B. Structure and documentation

The code separates case data, generation, game rules, and presentation. `Evidence`, `Character`, and `Case` represent the mystery; `CaseGenerator` builds reproducible cases; `Game` manages actions, NPC behaviour, voting, and verdicts. `FifthAlibiGUI` handles the interface while calling the shared rules. Functions, English comments, and this README explain the program's structure and operation.

### C. Advanced Python concepts

1. **Object-oriented programming:** Evidence, characters, case generation, changing game state, and the GUI have separate responsibilities.
2. **File I/O and exception handling:** Completed cases can be saved as JSON. The program handles problems such as a failed save or missing optional illustration.
3. **Seeded randomisation and nested data structures:** Case codes create replayable mysteries with varying culprits, murder methods, clues, investigation themes, character beliefs, and votes.

### D. Creativity and originality

The player investigates a murder while also being a suspect and potentially the culprit. Limited actions, changing trust, deception, independent NPC decisions, and evidence-based voting make the social mystery vary between cases. The verdict explains the relationship between votes and clues. Original noir-inspired artwork, dossiers, and a live evidence board present the story visually, while the terminal version remains fully playable without images.

## Padlet and presentation

The separate Padlet post includes the project title, a representative image, and a short description naming the target audience. The project will also be demonstrated in a three-minute tutorial presentation.
