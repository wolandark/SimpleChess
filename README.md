# SimpleChess

<div align="center">
  
  ### *Chess. Pure. Simple. Beautiful.*
  
  <img width="1024" height="1024" alt="1767863479715-65868660-9f20-45f9-9875-168be66d3586" src="https://github.com/user-attachments/assets/23c1a85c-4341-4707-888c-b5c9c0ee8840" />



**Finally, a chess game that doesn't look like it's from 1995.**

[![Downloads](https://img.shields.io/github/downloads/wolandark/SimpleChess/total?style=for-the-badge&color=success)](https://github.com/wolandark/SimpleChess/releases)
<!-- [![Release](https://img.shields.io/github/v/release/wolandark/SimpleChess?style=for-the-badge)](https://github.com/wolandark/SimpleChess/releases/)
[![License](https://img.shields.io/github/license/wolandark/SimpleChess?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/wolandark/SimpleChess/releases)
[Download Now](https://github.com/yourusername/SimpleChess/releases) • [Report Bug](https://github.com/yourusername/SimpleChess/issues) • [Request Feature](https://github.com/yourusername/SimpleChess/issues)
-->


---

## Why SimpleChess?

<table>
<tr>
<td width="50%">

### ❌ Other Chess Programs
- Cluttered interfaces from the 90s
- Hundreds of settings you'll never use
- Confusing menus and options
- Ugly, outdated graphics
- Complicated setup process
- Analysis paralysis before you even start

</td>
<td width="50%">

### ✅ SimpleChess
- **Clean, modern interface**
- **Just play chess**
- **Beautiful piece rendering**
- **Adjust difficulty, done**
- **Download and play instantly**
- **Zero bullshit**

</td>
</tr>
</table>

</div>

---

## Features

<div align="center">

| Feature | Description |
|---------|-------------|
| **Stockfish Integration** | Play against one of the world's strongest chess engines - bundled and ready |
| **Difficulty Settings** | From beginner to grandmaster - find your perfect challenge |
| **PGN/FEN Support** | Load and export games in standard formats |
| **Beautiful Design** | Custom chess fonts and clean, modern UI |
| **Sound Effects** | Satisfying audio feedback for moves |
| **Portable** | No installation required - just download and play |
| **Cross-Platform** | Windows and Linux builds available |

</div>

---

## Getting Started

### Download & Play

It's literally that simple.

#### Windows
```bash
1. Download SimpleChess-Windows.zip from Releases
2. Extract anywhere
3. Run SimpleChess.exe
4. Play chess
```

#### Linux
```bash
1. Download SimpleChess-Linux.tar.gz from Releases
2. Extract anywhere
3. Run ./SimpleChess
4. Play chess
```

No dependencies. No setup. No configuration files. **Just chess.**

---

## How to Use

<div align="center">

### It's chess. You know how to play chess.

</div>

1. **Launch the game**
2. **Select your difficulty** (or don't, the default is fine)
3. **Play chess**

Want to save a game? There's a button for that.  
Want to load a position? There's a button for that too.  

Everything else is just... playing chess.

---

## Technical Details

<div align="center">

**Built with Python** | **Powered by Pygame** | **UI with Tkinter**

</div>

### Stack
- **Python 3.x** - Core language
- **Pygame** - Graphics and game loop
- **Tkinter** - Clean dialog interfaces
- **Stockfish** - Chess engine (bundled)
- **Custom Chess Fonts** - Beautiful piece glyphs

### Why These Technologies?

Because they work. Because they're reliable. Because I wanted to make a chess game, not reinvent the wheel.

---

## Screenshots

<div align="center">

### Clean. Modern. Distraction-free.

<img width="839" height="669" alt="image" src="https://github.com/user-attachments/assets/7a49b007-9ac6-4c9e-aa4a-d1e22500600d" />

*The entire interface. That's it. That's the app.* 

Yes there is a hint system too, accessed by `h` or clicking on the light bulb 

---

<img width="838" height="668" alt="image" src="https://github.com/user-attachments/assets/67404382-ff31-428d-a373-9e5f1fa4e001" />

*Settings that actually matter*

</div>

---

## Philosophy

> "I just wanted to play chess against my computer without feeling like I'm using software from the Windows XP era."

This project exists because:

- Every chess program I tried looked ancient
- They all had 47 different analysis modes I didn't need
- I just wanted to play a game of chess
- I figured I couldn't be the only one

**SimpleChess is for people who want to play chess, not configure chess software.**

---

## Contributing

Found a bug? Want to add a feature that doesn't violate the "simple" philosophy?

1. Fork it
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Please keep it simple.** If your feature requires a manual, it probably doesn't belong here.

---

<!-- ## License

Distributed under the MIT License. See `LICENSE` for more information.

-->
---

## Acknowledgments

- **Stockfish** - For being an incredible open-source chess engine
- **Pygame Community** - For excellent documentation
- **Everyone tired of ugly chess software** - This is for you

---

<div align="center">

### If SimpleChess saved you from another ugly chess program, consider starring this repo

</div>

---

## FAQ

**Q: Why not just use chess.com/lichess?**  
A: Sometimes you want to play offline. Sometimes you don't want to be in a browser. Sometimes you just want a desktop app that doesn't suck.

**Q: Can you add [complex feature]?**  
A: Yes, but only if it fits the philosophy of the game. The point is simplicity. But feel free to fork it!

**Q: Why bundle Stockfish instead of making it a dependency?**  
A: Because "just download and play" means **just download and play**. Not "download, then install dependencies, then configure paths, then play."

**Q: Will you add online multiplayer?**  
A: Maybe, but there are plenty of places to play online, and why would I reinvent chess.com ?

**Q: Is this really better than [other chess program]?**  
A: Try it and see. If you like clean interfaces and just playing chess, probably yes.

---

<div align="center">

**SimpleChess** - *Because chess is complicated enough.*

</div>

---

## To Do:
- Issues:
  - improve tk file picker and mouse support
  - small menu fonts in windows
- Features:
  - Implement check visuals and sound
  - various chess board colors
  - change pieces glyphs in game
- score board and sqlite db
- package for linux distros
