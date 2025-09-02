from txhttputil.util.ModuleUtil import filterModules


def loadGridTuples():
    for mod in filterModules(__name__, __file__):
        __import__(mod, locals(), globals())
