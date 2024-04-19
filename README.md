# Second Chance
This is a platformer-style video game with a mechanic of always giving the user a second chance. The base game functions like any normal platformer, but when the player dies to an enemy, they are given a second chance. These second chances will function as minigames within the base game. After dying to an enemy, the player’s second chance could be a memory game, trivia, a logic puzzle, or any other number of short challenges. If the player succeeds (and passes/beats the challenge), they will respawn just ahead of the enemy whose challenge they passed. The second chance’s will be consistent with the enemy type (If an enemy gives a second chance challenge of trivia, they will always give a second chance challenge of trivia, but the questions may change). As the player progresses throughout the game, the enemies and their second chance challenges will get more difficult. Skilled players may attempt to beat the game through just the platformer elements, while others may try to beat the game by winning their second chance challenges.

# How to run

## Windows executable
- Download and extract the `SecondChance.zip` file from the latest
[release](https://github.com/cis3296s24/02_Second_Chance/releases).
- Run the `SecondChance.exe` executable to launch the game. 

## Windows source
- Follow [instructions for MacOS](#macos).

## MacOS
- Use this github repository: https://github.com/cis3296s24/Second_Chance
- Open the Terminal.
- Clone this repository with:
  - `git clone https://github.com/cis3296s24/Second_Chance.git`
- Change your current directory into the Second Chance Github repository you just cloned.
- Run `pip3 install -r requirements.txt` to install `pygame` and other necessary dependencies.
- Run `python3 SecondChance.py` to launch the game. 
- Afterwards, the game window opens and you can play the game. 

## Controls
- `LeftArrow`/`a`: Move left
- `RightArrow`/`d`: Move right
- `UpArrow`/`Spacebar`/`w`: Jump
- `LeftClick`/`q`: Melee attack
- `o`: Ranged attack

# How to contribute
Follow this project board to know the latest status of the project: https://github.com/orgs/cis3296s24/projects/71

### Requirements
Requires Python 3.0+, Pygame, and Git.

Download the latest version of Python [here](https://www.python.org/downloads/)
and the latest version of git [here](https://git-scm.com/downloads).
