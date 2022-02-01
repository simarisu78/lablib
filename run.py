from lablib.app.app import app
import sys

if __name__ == "__main__":
    debug = False
    
    if len(sys.argv) >= 2 and sys.argv[1] == "DEBUG":
        debug = True
        
    app.run(host='127.0.0.1', debug=debug)
    
