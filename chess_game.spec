# chess_game.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('engine/stockfish/win/stockfish-windows-x86-64-avx2.exe', 'stockfish'),  # Windows
        ('engine/stockfish/linux/stockfish-ubuntu-x86-64-avx2', 'stockfish'),        # Linux
    ],
    datas=[
        ('fonts/', ','),
        ('img/', '.'),
        ('sfx/', '.'),
    ],
    hiddenimports=['pygame', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
)

