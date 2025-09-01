import uiautomation as uia

class Window:
    @staticmethod
    def Close(target: str | uia.Control) -> None:
        """
        关闭窗口

        Window.Close(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: None
        """
    @staticmethod
    def GetActive(isReturnHwnd: bool = True) -> uia.Control | int:
        """
        获取活动窗口

        Window.GetActive(isReturnHwnd=True)

        :param isReturnHwnd: [可选参数]是否返回窗口句柄，True时函数返回窗口句柄，False时返回窗口元素对象。默认True
        :return:窗口句柄或者窗口元素对象
        """
    @staticmethod
    def SetActive(target: str | uia.Control) -> bool:
        """
        设置活动窗口

        Window.SetActive(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: bool。激活成功返回True，否则返回False
        """
    @staticmethod
    def Show(target: str | uia.Control, showStatus: str = 'show') -> bool:
        '''
        更改窗口显示状态

        Window.Show(target, showStatus="show")

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :param showStatus: [可选参数] 显示：\'show\' 隐藏：\'hide\' 最大化：\'max\' 最小化：\'min\' 还原：\'restore\'。默认\'show\'
        :return: bool。执行成功返回True，否则返回False
        '''
    @staticmethod
    def Exists(target: str | uia.WindowControl) -> bool:
        """
        判断窗口是否存在

        Window.Exists(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象
        :return: bool。窗口存在返回True,否则返回False
        """
    @staticmethod
    def GetSize(target: str | uia.Control) -> dict:
        '''
        获取窗口大小

        Window.GetSize(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: {"height":int, "width":int, "x":int, "y":int}
        '''
    @staticmethod
    def SetSize(target: str | uia.Control, width: int, height: int) -> None:
        """
        改变窗口大小

        Window.SetSize(target, 800, 600)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :param width: [必选参数]窗口宽度
        :param height: [必选参数]窗口高度
        :return: None
        """
    @staticmethod
    def Move(target: str | uia.Control, x: int, y: int) -> None:
        """
        移动窗口位置

        Window.Move(target, 0, 0)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :param x: [必选参数]移动到新位置的横坐标
        :param y: [必选参数]移动到新位置的纵坐标
        :return: None
        """
    @staticmethod
    def TopMost(target: str | uia.Control, isTopMost: bool = True) -> bool:
        """
        窗口置顶

        Window.TopMost(target, isTopMost=True)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :param isTopMost: [可选参数]是否使窗口置顶，窗口置顶:true 窗口取消置顶:false。默认True
        :return: bool值，设置成功返回True，否则返回False
        """
    @staticmethod
    def GetClass(target: str | uia.Control) -> str:
        """
        获取窗口类名

        Window.GetClass(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: 窗口的类名称
        """
    @staticmethod
    def GetPath(target: str | uia.Control) -> str:
        """
        获取窗口程序的文件路径

        Window.GetPath(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: 文件绝对路径
        """
    @staticmethod
    def GetPID(target: str | uia.Control) -> int:
        """
        获取进程PID

        Window.GetPID(target)

        :param target: [必选参数]tdRPA拾取器获取的目标窗口元素特征字符串或uia目标窗口元素对象，也可选取窗口内始终存在的元素。
        :return: PID
        """

class WinMouse:
    @staticmethod
    def Action(target: str | uia.Control, button: str = 'left', clickType: str = 'click', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, simulateType: str = 'simulate', moveSmoothly: bool = False) -> uia.Control:
        '''
        点击目标元素

        WinMouse.Action(target, button="left", clickType="click", searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, simulateType=\'simulate\', moveSmoothly=False)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param button: [可选参数]鼠标点击。鼠标左键:"left" 鼠标右键:"right" 鼠标中键:"middle"。默认"left"
        :param clickType: [可选参数]点击类型。单击:"click" 双击:"dblclick" 按下:"down" 弹起:"up"。默认"click"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param cursorPosition: [可选参数]光标位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX: [可选参数]横坐标偏移。默认0
        :param cursorOffsetY: [可选参数]纵坐标偏移。默认0
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"simulate"
        :param moveSmoothly: [可选参数]是否平滑移动鼠标。默认False
        :return:目标元素对象
        '''
    @staticmethod
    def Hover(target: str | uia.Control, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, simulateType: str = 'simulate', moveSmoothly: bool = True) -> uia.Control:
        '''
        移动到目标上

        WinMouse.Hover(target, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, simulateType=\'simulate\', moveSmoothly=False)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param cursorPosition: [可选参数]光标位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX: [可选参数]横坐标偏移。默认0
        :param cursorOffsetY: [可选参数]纵坐标偏移。默认0
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"simulate"
        :param moveSmoothly: [可选参数]平滑移动。默认True
        :return:目标元素对象
        '''
    @staticmethod
    def Click(button: str = 'left', clickType: str = 'click', keyModifiers: list = None, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        模拟点击

        WinMouse.Click(button="left", clickType="click", keyModifiers=None, delayAfter=100, delayBefore=100)

        :param button: [可选参数]鼠标点击。鼠标左键:"left" 鼠标右键:"right" 鼠标中键:"middle"。默认"left"
        :param clickType: [可选参数]点击类型。单击:"click" 双击:"dblclick" 按下:"down" 弹起:"up"。默认"click"
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''
    @staticmethod
    def Move(x: int, y: int, isRelativeMove: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        # 模拟移动

        WinMouse.Move(0, 0, isRelativeMove=False, delayAfter=100, delayBefore=100)

        :param x: [必选参数]横坐标
        :param y: [必选参数]纵坐标
        :param isRelativeMove: [可选参数]是否相对目前位置移动。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        """
    @staticmethod
    def GetPos() -> tuple[int, int]:
        """
        获取鼠标位置

        WinMouse.GetPos()

        :return:pointX, pointY
        """
    @staticmethod
    def Drag(x1: int, y1: int, x2: int, y2: int, button: str = 'left', keyModifiers: list = None, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        模拟拖动

        WinMouse.Drag(0, 0, 0, 0, button=\'left\', keyModifiers=None, delayAfter=100, delayBefore=100)

        :param x1: [必选参数]起始横坐标
        :param y1: [必选参数]起始纵坐标
        :param x2: [必选参数]结束横坐标
        :param y2: [必选参数]结束纵坐标
        :param button: [可选参数]鼠标按键。鼠标左键:"left" 鼠标右键:"right" 鼠标中键:"middle"。默认"left"
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''
    @staticmethod
    def Wheel(scrollNum: int, scrollDirection: str = 'down', keyModifiers: list = None, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        模拟滚轮

        WinMouse.Wheel(1, scrollDirection="down", keyModifiers=None, delayAfter=100, delayBefore=100)

        :param scrollNum: [必选参数]滚动次数
        :param scrollDirection: [可选参数]滚动方向。向上:"up" 向下:"down"。默认"down"
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''

class WinKeyboard:
    @staticmethod
    def InputText(target: str | uia.Control, content: str, clearOldText: bool = True, inputInterval: int = 50, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, simulateType: str = 'message', validate: bool = False, clickBeforeInput: bool = False) -> uia.Control:
        '''
        在目标中输入

        WinKeyboard.InputText(target, \'\', clearOldText=True, inputInterval=50, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, simulateType=\'message\', validate=False, clickBeforeInput=False)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param content: [必选参数]写入文本
        :param clearOldText: [可选参数]是否清空原内容。默认True
        :param inputInterval: [可选参数]键入间隔(毫秒)。默认50
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"message"
        :param validate: [可选参数]验证写入文本。默认False
        :param clickBeforeInput: [可选参数]输入前点击。默认False
        :return: 目标元素对象
        '''
    @staticmethod
    def PressKey(target: str | uia.Control, button: str, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, keyModifiers: list = None, simulateType: str = 'message', clickBeforeInput: bool = False) -> uia.Control:
        '''
        在目标中按键

        WinKeyboard.PressKey(target, "Enter", searchDelay=10000, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, keyModifiers=None, simulateType=\'message\', clickBeforeInput=False)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param button: [必选参数]键盘按键上的符号。如"Enter"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param keyModifiers: [可选参数]辅助按键[\'Alt\',\'Ctrl\',\'Shift\',\'Win\']可多选。默认None
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"message"
        :param clickBeforeInput: [可选参数]输入前点击。默认False
        :return: 目标元素对象
        '''
    @staticmethod
    def Input(content: str, inputInterval: int = 50, delayAfter: int = 100, delayBefore: int = 100, simulateType: str = 'message') -> None:
        '''
        输入文本

        WinKeyboard.Input(\'\', inputInterval=50, delayAfter=100, delayBefore=100, simulateType=\'message\')

        :param content: [必选参数]输入内容
        :param inputInterval: [可选参数]键入间隔(毫秒)。默认50
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"message"
        :return: None
        '''
    @staticmethod
    def Press(button: str, pressType: str = 'press', keyModifiers: list = None, delayAfter: int = 100, delayBefore: int = 100, simulateType: str = 'message') -> None:
        '''
        模拟按键

        WinKeyboard.Press(\'Enter\', pressType=\'press\', keyModifiers=None, delayAfter=100, delayBefore=100, simulateType=\'message\')

        :param button: [必选参数]键盘按键上的符号，如“Enter”
        :param pressType: [可选参数]点击类型。单击:"press" 按下:"down" 弹起:"up"。默认"press"
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 消息操作:"message"。默认"message"
        :return: None
        '''

class WinElement:
    @staticmethod
    def FindElementByTd(tdTargetStr: str = None, anchorsElement: uia.Control = None, searchDelay: int = 10000, continueOnError: bool = False):
        """
        依据tdrpa拾取器获取的元素特征码查找元素

        WinElement.FindElementByTd('', anchorsElement=None, searchDelay=10000, continueOnError=False)

        :param tdTargetStr: 目标元素特征码(tdrpa拾取器获取)
        :param anchorsElement: 从哪个元素开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param searchDelay: 查找延时（豪秒）。默认10000
        :param continueOnError: 错误继续执行。默认False
        :return: 目标元素 or None
        """
    @staticmethod
    def GetChildren(target: str | uia.Control, searchType: str = 'all', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> list | uia.Control:
        '''
        获取子元素

        WinElement.GetChildren(target, searchType=\'all\', searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param searchType: [可选参数]搜索方式。全部子元素:"all" 首个子元素:"first" 最后一个子元素:"last"。默认"all"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 目标元素对象的子元素列表 或 首个子元素 或 最后一个子元素
        '''
    @staticmethod
    def GetParent(target: str | uia.Control, upLevels: int = 1, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> uia.Control:
        """
        获取父元素

        WinElement.GetParent(target, upLevels=1, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param upLevels: [可选参数]父元素层级，1为父元素，2为祖父元素，3为曾祖父元素，以此类推，0为当前元素的顶层窗口元素。默认1
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 目标元素对象的上一层父级元素 或 顶层父级元素
        """
    @staticmethod
    def GetSibling(target: str | uia.Control, position: str = 'next', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> uia.Control | None:
        '''
        获取相邻元素

        WinElement.GetSibling(target, position="next", searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param position: [可选参数]相邻位置。下一个："next"  上一个："previous"。默认"next"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 目标元素对象的下一个相邻元素对象 或 上一个相邻元素对象，没有返回None
        '''
    @staticmethod
    def Exists(target: str | uia.Control, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool:
        """
        判断元素是否存在

        WinElement.Exists(target, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: bool
        """
    @staticmethod
    def GetCheck(target: str | uia.Control, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool:
        """
        获取元素勾选

        WinElement.GetCheck(target, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: bool
        """
    @staticmethod
    def SetCheck(target: str | uia.Control, isCheck: bool = True, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool:
        """
        设置元素勾选

        WinElement.SetCheck(target, isCheck=True, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param isCheck: [可选参数]设置勾选:True 设置取消勾选:False。默认True
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 执行成功返回True，执行失败返回False
        """
    @staticmethod
    def GetSelect(target: str | uia.Control, mode: str = 'text', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | int:
        '''
        获取元素选择

        WinElement.GetSelect(target, mode=\'text\', searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param mode: [可选参数]获取文本："text" 获取序号：“index” 获取值：“value”。默认"text"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 已选项的文本 或 序号 或 值，没有则返回None
        '''
    @staticmethod
    def SetSelect(target: str | uia.Control, option: str | int, mode: str = 'text', searchDelay: int = 10000, anchorsElement: uia.Control = None, setForeground: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, simulateType: str = 'simulate', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        设置元素选择

        WinElement.SetSelect(target, \'\', mode="text", searchDelay=10000, anchorsElement=None, setForeground=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, simulateType=\'simulate\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param option: [必选参数]选择选项的文本或者序号
        :param mode: [可选参数]选择文本："text" 选择序号：“index” 选择值：“value”。默认"text"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param setForeground: [可选参数]激活窗口。默认True
        :param cursorPosition: [可选参数]光标在选中项的位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX: [可选参数]横坐标偏移。默认0
        :param cursorOffsetY: [可选参数]纵坐标偏移。默认0
        :param simulateType: [可选参数]鼠标点击选中项时的模式。模拟操作:"simulate" 消息操作:"message"。默认"simulate"
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''
    @staticmethod
    def GetValue(target: str | uia.Control, getMethod: str = 'auto', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str:
        '''
        获取元素文本

        WinElement.GetValue(target, getMethod="auto", searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param getMethod: [可选参数]获取方式。自动方式："auto" 获得元素Name方式："name" 获得元素Value方式："value" 获得元素Text方式："text"。默认"auto"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 元素文本
        '''
    @staticmethod
    def SetValue(target: str | uia.Control, value: str, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        设置元素文本

        WinElement.SetValue(target, "", searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param value: [必选参数]要写入元素的文本内容
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''
    @staticmethod
    def GetRect(target: str | uia.Control, relativeType: str = 'parent', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> dict:
        '''
        获取元素区域

        WinElement.GetRect(target, relativeType="parent", searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param relativeType: [可选参数]返回元素位置是相对于哪一个坐标而言的。 相对父元素:"parent" 相对窗口客户区:"root" 相对屏幕坐标:"screen"。默认"parent"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: {"height" : int, "width" : int, "x" : int, "y" : int}
        '''
    @staticmethod
    def ScreenCapture(target: str | uia.Control, filePath: str, rect: dict = None, searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool:
        '''
        元素截图

        WinElement.ScreenCapture(target, \'D:/1.png\', rect=None, searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param filePath: [必选参数]图片存储的绝对路径。如 \'D:/1.png\'(支持图片保存格式：bmp、jpg、jpeg、png、gif、tif、tiff)
        :param rect: [可选参数]对指定界面元素截图的范围，若传None，则截取该元素的全区域。若传{"x":int,"y":int,"width":int,"height":int}，则以该元素左上角位置偏移x,y的坐标为原点，根据高宽进行截图。默认None
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: bool(截图成功返回True，否则返回假)
        '''
    @staticmethod
    def Wait(target: str | uia.Control, waitType: str = 'show', searchDelay: int = 10000, anchorsElement: uia.Control = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        等待元素（等待元素显示或消失）

        WinElement.Wait(target, waitType=\'show\', searchDelay=10000, anchorsElement=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]tdRPA拾取器获取的目标元素特征字符串或uia目标元素对象
        :param waitType: [可选参数]等待方式。 等待显示："show" 等待消失:"hide"。默认"show"
        :param searchDelay: [可选参数]超时时间(毫秒)。默认10000
        :param anchorsElement: [可选参数]锚点元素，从它开始找，不传则从桌面顶级元素开始找（有值可提高查找速度）。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: None
        '''
