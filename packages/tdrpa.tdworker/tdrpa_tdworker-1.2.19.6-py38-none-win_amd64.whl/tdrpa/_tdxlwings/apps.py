from .main import Apps, Books, App
from . import _xlwindows

class AppsEx(Apps):
    _name = 'AppsEx'

    @property
    def activeapps(self):
        applist = []
        for app in self.impl:
            tmp = App(impl=app)
            if tmp not in applist:
                applist.append(App(impl=app))
        return applist

appsex = AppsEx(impl=_xlwindows.Apps())

class ActiveApps(Books):

    def __init__(self):
        pass

    _name = 'Apps'

    @property
    def impl(self):
        impllist = []
        for appbooks in appsex.activeapps:
            for impl in appbooks.books.impl:
                impllist.append(impl)

        for impl in impllist:
            yield impl

AppsBooks = ActiveApps()