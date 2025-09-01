import sys, os

try:
    from whatap import agent
    agent()
except ModuleNotFoundError:
    pythonpath = os.environ.get('PYTHONPATH')
    if pythonpath.endswith("/bootstrap"):
        pythonpath,_ = os.path.split(pythonpath)
        pythonpath,_ = os.path.split(pythonpath)
        
        sys.path.append(pythonpath)
        try:
            from whatap import agent
            agent()
        except ModuleNotFoundError:
            #final fail
            pass
            