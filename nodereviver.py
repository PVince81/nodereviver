'''
Node Reviver

@author: Vincent Petry <PVince81@yahoo.fr>
'''
from game import Game
from editor import Editor
from config import Config
import argparse

def main():
    
    parser = argparse.ArgumentParser(description='Node Reviver')
    parser.add_argument('--enable-sound', action="store_true",
                        dest='enableSound',
                        default=False, help='enable sound (ugly)')
    parser.add_argument('--game', action="store_true", default=True,
                        dest='game',
                        help='runs the game (default)')
    parser.add_argument('--editor', action="store_true", default=False,
                        dest='editor',
                        help='runs the level editor (buggy)')
    parser.add_argument('--fullscreen', action="store_true", default=False,
                        dest='fullScreen',
                        help='runs the game in full screen mode')
    parser.add_argument('--startlevel', action="store", default=1,
                        dest='startLevel', type=int,
                        help='specifies the start level number (cheat mode)')
    parser.add_argument('--datapath', action="store", default='data/',
                        dest='dataPath', type=str,
                        help='specifies the data path')
    args = parser.parse_args()
    
    config = Config()
    config.startLevel = args.startLevel
    config.sound = args.enableSound
    config.dataPath = args.dataPath
    config.fullScreen = args.fullScreen
    if config.startLevel > 1:
        config.cheat = True
    if args.editor:
        config.cheat = True
        editor = Editor(config)
        editor.run()
    elif args.game:
        game = Game(config)
        game.run()

if __name__ == '__main__':
    main()
