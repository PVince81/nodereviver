'''
Node Reviver

@author: Vincent Petry <PVince81@yahoo.fr>
'''
from game import Game
from editor import Editor
from config import Config
import optparse

def main():
    
    parser = optparse.OptionParser(description='Node Reviver')
    parser.add_option('--enable-sound', action="store_true",
                        dest='enableSound',
                        default=False, help='enable sound (ugly)')
    parser.add_option('--game', action="store_true", default=True,
                        dest='game',
                        help='runs the game (default)')
    parser.add_option('--editor', action="store_true", default=False,
                        dest='editor',
                        help='runs the level editor (buggy)')
    parser.add_option('--fullscreen', action="store_true", default=False,
                        dest='fullScreen',
                        help='runs the game in full screen mode')
    parser.add_option('--startlevel', action="store", default=1,
                        dest='startLevel', type=int,
                        help='specifies the start level number (cheat mode)')
    parser.add_option('--datapath', action="store", default='data/',
                        dest='dataPath', type=str,
                        help='specifies the data path')
    (args, rest) = parser.parse_args()
    
    config = Config()
    config.startLevel = args.startLevel
    config.sound = args.enableSound
    config.dataPath = args.dataPath
    config.fullScreen = args.fullScreen
    if args.editor:
        editor = Editor(config)
        editor.run()
    elif args.game:
        game = Game(config)
        game.run()

if __name__ == '__main__':
    main()
