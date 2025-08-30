from _typeshed import Incomplete

class Web:
    @staticmethod
    def ChangeBrowser(browserType: str) -> None:
        """
        切换浏览器

        Web.ChangeBrowser('360')

        :param browserType: [必选参数]浏览器类型。"chrome":Chrome浏览器；"chromium":Chromium浏览器；"360":360安全浏览器。
        """
    @staticmethod
    def Click(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, button: str = 'left', clickType: str = 'click', delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, checkElementShow: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, simulateType: str = 'simulate', moveSmoothly: bool = False) -> str | None:
        '''
        点击元素

        tdrpa_element_id = Web.Click(target, onlyvis=False, index=None, fromElementTdid=None, button="left", clickType="click", delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, checkElementShow=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, simulateType=\'simulate\', moveSmoothly=False)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param button: [可选参数]鼠标点击。鼠标左键:"left" 鼠标右键:"right" 鼠标中键:"middle"。默认"left"
        :param clickType: [可选参数]点击类型。单击:"click" 双击:"dblclick" 按下:"down" 弹起:"up"。默认"click"
        :param delayTime: [可选参数]超时时间(毫秒)。默认10000
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param checkElementShow: [可选参数]检查元素是否可见。默认True
        :param cursorPosition: [可选参数]光标位置。中心:"center" 左上角:"topLeft" 右上角:"topRight" 左下角:"bottomLeft" 右下角:"bottomRight"。默认"center"
        :param cursorOffsetX: [可选参数]横坐标偏移。默认0
        :param cursorOffsetY: [可选参数]纵坐标偏移。默认0
        :param keyModifiers: [可选参数]辅助按键["Alt","Ctrl","Shift","Win"]可多选。默认None
        :param simulateType: [可选参数]操作类型。模拟操作:"simulate" 接口操作:"api"。默认"simulate"
        :param moveSmoothly: [可选参数]是否平滑移动鼠标（simulateType为api时会忽略此参数）。默认False
        :return: tdrpa_element_id
        '''
    @staticmethod
    def CloseBrowser(tryClose: int = 3, userData: str = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        关闭浏览器

        Web.CloseBrowser(tryClose=3, userData=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param tryClose:[可选参数]尝试关闭浏览器的次数。默认值为 3。如果在指定次数内无法成功关闭浏览器，则会抛出异常。
        :param userData:[可选参数]用户数据目录的路径。如果未提供，则使用默认路径。
        :param continueOnError:[可选参数]是否在发生错误时继续执行。默认值为 False。
        :param delayAfter:[可选参数]延迟关闭浏览器的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]延迟关闭浏览器之前的时间（毫秒）。默认值为 100。
        :return: None
        """
    @staticmethod
    def CloseTab(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        """
        关闭当前标签页

        closeResult = Web.CloseTab(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 关闭成功返回True，失败返回False。只有一个标签页时不能关闭，会返回False
        """
    @staticmethod
    def CreateBrowser(url: str = None, browserExePath: str = None, isMaximize: bool = True, supportMode: str = 'web', userData: str = None, clearBrowser: bool = True, otherStartupParam: Incomplete | None = None, waitPage: bool = True, delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, debugPort: int = 9222) -> None:
        """
        创建浏览器

        Web.CreateBrowser(url='https://www.baidu.com', browserExePath=None, isMaximize=True, supportMode='web', userData=None, clearBrowser=True, otherStartupParam=None, waitPage=True, delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100, debugPort=9222)

        :param url:[可选参数]启动浏览器后打开的链接，字符串类型。默认None
        :param browserExePath:[可选参数]浏览器可执行程序的绝对路径，字符串类型，填写None时会自动寻找本地安装的路径。默认None
        :param isMaximize:[可选参数]浏览器启动后是否最大化显示，选择True时最大化启动，选择False默认状态。默认True
        :param supportMode:[可选参数]浏览器元素拾取模式，'web':网页模式, 'uia':客户端模式。默认'web'
        :param userData:[可选参数]浏览器用户数据存放路径，字符串类型。默认None
        :param clearBrowser:[可选参数]是否在打开新浏览器之前清理浏览器进程。默认值为 True。
        :param otherStartupParam:[可选参数]其他启动浏览器的参数，如：['--xxx', '--xxx']。默认None
        :param waitPage:[可选参数]是否等待页面加载完成。默认True
        :param delayTime: 超时时间(毫秒)。默认60000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :param debugPort:[可选参数]调试端口。默认9222
        :return:None
        """
    @staticmethod
    def CreateTab(url: str = None, tabActive: bool = True, waitPage: bool = True, delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> int | None:
        '''
        新建标签页

        urlResult = Web.CreateTab(url="https://www.baidu.com", tabActive=True, waitPage=True, delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param url:[可选参数]要加载的 URL(注意：url需要保留 "https://" 或 "http://" )。如果为 None，加载默认页面。
        :param tabActive:[可选参数]是否激活新标签页。默认值为 True。
        :param waitPage:[可选参数]是否等待页面加载完成。True：等待页面加载完毕，False：不等待页面加载完毕。默认值为 True。
        :param delayTime: [可选参数]waitPage为True时，网页等待超时时间，默认为 60000 毫秒（60秒）
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:url是None时，返回None，url有具体链接时，返回True或False，代表是否打开了目标链接
        '''
    @staticmethod
    def Exists(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, returnType: str = 'id', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | str | None:
        '''
        元素是否存在

        tdrpa_element_id = Web.Exists(target, onlyvis=False, index=None, fromElementTdid=None, returnType=\'id\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param returnType:[可选参数]返回值的类型。设为\'bool\'时:网页元素存在，结果返回True，否则返回False，设为\'id\'时:网页元素存在，返回tdrpa_element_id，否则返回None.默认id
        :param continueOnError:[可选参数]是否在发生错误时继续执行。默认为False。
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100。
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100。
        :return:元素存在返回tdrpa_element_id或True，不存在返回None或False（返回类型根据returnType字段设置值而定）。
        '''
    @staticmethod
    def GetAllElements(target: str | dict, onlyvis: bool = False, getMode: str = None, cssTargetFaster: bool = False, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> list | None:
        '''
        获取指定特征所有元素（tdrpa_element_id列表或指定模式的值列表）

        tdrpa_elements = Web.GetAllElements(target, onlyvis=False, getMode=None, cssTargetFaster=False, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：css选择器，或xpath。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param getMode: [可选参数]获取值的模式。\'autoText\':自动获取文本内容（可能是text、innerText、value其一），\'text\':获取元素内所有文本内容，\'innerText\':获取元素内可见文本内容，\'value\':获取元素值。其他字符视为元素属性值，例如:\'href\'、\'class\'等等。None:获取tdrpa_element_id。默认None
        :param cssTargetFaster: [可选参数]是否使用css选择器更快的方式获取目标元素。默认False
        :param continueOnError:[可选参数]是否在发生错误时继续执行。默认为False。
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100。
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100。
        :return:所有目标元素的tdrpa_element_id列表 或 指定模式的值列表。
        '''
    @staticmethod
    def GetAttribute(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, attrname: str | list | None = 'class', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None | dict:
        '''
        获取网页元素属性值

        attrValue = Web.GetAttribute(target, onlyvis=False, index=None, fromElementTdid=None, attrname=\'class\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param attrname: [可选参数]属性名。str类型时：指定单个属性值，list类型时：指定多个属性名，None时：所有属性名。默认\'class\'
        :param continueOnError:[可选参数]是否在发生错误时继续执行。默认为False。
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100。
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100。
        :return:属性值字符串或属性键值字典, 没有指定属性名时，其值是None
        '''
    @staticmethod
    def GetCheck(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        '''
        获取元素勾选状态(radio或checkbox)

        isCheck = Web.GetCheck(target, onlyvis=False, index=None, fromElementTdid=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素选中返回True,否则返回False
        '''
    @staticmethod
    def GetChildren(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> list | None:
        '''
        获取子元素

        tdrpa_element_ids = Web.GetChildren(target, onlyvis=False, index=None, fromElementTdid=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的子元素的tdrpa_element_id列表
        '''
    @staticmethod
    def GetHTML(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        """
        读取网页源码

        htmlCode = Web.GetHTML(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:当前浏览器页面的 HTML 内容，无法获取时返回None
        """
    @staticmethod
    def GetParent(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, upLevels: int = 1, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        获取父元素

        tdrpa_element_id = Web.GetParent(target, onlyvis=False, index=None, fromElementTdid=None, upLevels=1, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param upLevels: [可选参数]向上查找的层级数。默认1
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的父元素的tdrpa_element_id，没有父元素时返回None
        '''
    @staticmethod
    def GetRect(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, relative: str = 'screen', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> dict | None:
        '''
        获取元素位置大小

        rectInfo = Web.GetRect(target, onlyvis=False, index=None, fromElementTdid=None, relative=\'screen\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param relative: [可选参数]相对坐标系。screen:相对屏幕坐标，parent:相对父级元素坐标。root:相对浏览器窗口内坐标。默认screen
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: {\'x\':int, \'y\':int, \'width\':int, \'height\':int}
        '''
    @staticmethod
    def GetScroll(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> dict | None:
        """
        获取滚动条位置(像素)

        location = Web.GetScroll(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return:返回当前页面的滚动条位置，如 {'ScrollLeft': 20, 'ScrollTop': 1054}，没有则返回None
        """
    @staticmethod
    def GetSelect(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, selectMode: str = 'text', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> list | None:
        '''
        获取元素选中项(select)

        selectedList = Web.GetSelect(target, onlyvis=False, index=None, fromElementTdid=None, selectMode="text", continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param selectMode: [可选参数]获取选中项的模式。\'text\':获取选中项的文本内容。\'value\':获取选中项的值。\'index\':获取选中项的索引。默认\'text\'
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的选中项的文本内容或值列表，没有选中项时返回空列表
        '''
    @staticmethod
    def GetSibling(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, position: str = 'next', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        获取兄弟元素

        tdrpa_element_id = Web.GetSibling(target, onlyvis=False, index=None, fromElementTdid=None, position=\'next\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param position: [可选参数]兄弟元素的位置。\'next\':下一个兄弟元素。\'prev\':上一个兄弟元素。默认\'next\'
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的兄弟元素的tdrpa_element_id，没有兄弟元素时返回None
        '''
    @staticmethod
    def GetTdElementId(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        获取元素tdrpa_element_id

        tdrpa_element_id = Web.GetTdElementId(target, onlyvis=False, index=None, fromElementTdid=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的tdrpa_element_id，没有找到时返回None
        '''
    @staticmethod
    def GetActiveElement(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100):
        """
        获取焦点元素

        tdrpa_element_id = Web.GetActiveElement(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 返回焦点元素的tdrpa_element_id
        """
    @staticmethod
    def GetElementByXY(x: int, y: int, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100):
        """
        根据坐标获取元素

        tdrpa_element_id = Web.GetElementByXY(x, y, continueOnError=False, delayAfter=100, delayBefore=100)

        :param x: [必选参数]相对于浏览器视窗左边缘的距离，为非负整数。
        :param y: [必选参数]相对于浏览器视窗顶部边缘的距离，为非负整数。
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 返回元素的tdrpa_element_id
        """
    @staticmethod
    def GetTitle(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        """
        获取网页标题

        title = Web.GetTitle(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 网页标题
        """
    @staticmethod
    def GetURL(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        """
        获取网页URL

        url = Web.GetURL(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 网页链接
        """
    @staticmethod
    def GetValue(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, getMode: str = 'auto', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        获取元素的文本值

        text = Web.GetValue(target, onlyvis=False, index=None, fromElementTdid=None, getMode=\'auto\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param getMode: [可选参数]获取文本值的方式。\'auto\':自动获取，\'text\':获取元素内所有文本内容，\'innerText\':获取元素内可见文本内容，\'value\':获取元素值。默认\'auto\'
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: 网页元素的文本值
        '''
    @staticmethod
    def GoBack(waitPage: bool = True, delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        执行后退操作(与浏览器工具栏的后退按钮功能相同)

        Web.GoBack(waitPage=True, delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param waitPage:[可选参数]是否等待页面加载完成。True：等待页面加载完毕，False：不等待页面加载完毕。默认值为 True。
        :param delayTime:[可选参数]waitPage为True时，网页等待超时时间，默认为 60000 毫秒（60秒）
        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return:None
        """
    @staticmethod
    def GoForward(waitPage: bool = True, delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        执行前进操作(与浏览器工具栏的前进按钮功能相同)

        Web.GoForward(waitPage=True, delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param waitPage:[可选参数]是否等待页面加载完成。True：等待页面加载完毕，False：不等待页面加载完毕。默认值为 True。
        :param delayTime:[可选参数]waitPage为True时，网页等待超时时间，默认为 60000 毫秒（60秒）
        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: None
        """
    @staticmethod
    def GoURL(url: str, waitPage: bool = True, delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        '''
        跳转至新网址

        goResult = Web.GoURL(\'https://www.baidu.com\', waitPage=True, delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param url:[必选参数]要加载的 URL(注意：url需要保留 "https://" 或 "http://" )。
        :param waitPage:[可选参数]是否等待页面加载完成。True：等待页面加载完毕，False：不等待页面加载完毕。默认值为 True。
        :param delayTime:[可选参数]waitPage为True时，网页等待超时时间，默认为 60000 毫秒（60秒）
        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 跳转链接正确返回True，否则返回False
        '''
    @staticmethod
    def Hover(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, checkElementShow: bool = True, cursorPosition: str = 'center', cursorOffsetX: int = 0, cursorOffsetY: int = 0, keyModifiers: list = None, simulateType: str = 'simulate', moveSmoothly: bool = False) -> str | None:
        '''
        鼠标悬停到元素上

        tdrpa_element_id = Web.Hover(target, onlyvis=False, index=None, fromElementTdid=None, delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, checkElementShow=True, cursorPosition=\'center\', cursorOffsetX=0, cursorOffsetY=0, keyModifiers=None, simulateType=\'simulate\', moveSmoothly=False)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param delayTime: [可选参数]超时时间(毫秒)。默认10000
        :param continueOnError: [可选参数]错误继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :param setForeground: [可选参数]激活窗口。默认True
        :param checkElementShow: [可选参数]检查元素是否可见。默认True
        :param cursorPosition: [可选参数]鼠标位置。"center"：元素中心，"left"：元素左边界，"right"：元素右边界，"top"：元素上边界，"bottom"：元素下边界。默认"center"
        :param cursorOffsetX: [可选参数]鼠标偏移量X。默认0
        :param cursorOffsetY: [可选参数]鼠标偏移量Y。默认0
        :param keyModifiers: [可选参数]键盘修饰符。默认None
        :param simulateType: [可选参数]模拟类型。"simulate"：模拟悬浮，"api"：接口悬浮。默认"simulate"
        :param moveSmoothly: [可选参数]移动平滑（simulateType为api时会忽略此参数）。默认False。
        :return: tdrpa_element_id
        '''
    @staticmethod
    def InputText(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, content: str = '', clearOldText: bool = True, inputInterval: int = 50, delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100, setForeground: bool = True, validate: bool = False, simulateType: str = 'simulate', checkClickNum: int = 3, checkElementShow: bool = True, endToDo: str = None) -> str | None:
        '''
        填写输入框

        tdrpa_element_id = Web.InputText(target, onlyvis=False, index=None, fromElementTdid=None, content=\'tdrpa\', clearOldText=True, inputInterval=50, delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=100, setForeground=True, validate=False, simulateType=\'simulate\', checkClickNum=3, checkElementShow=True, endToDo=None)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param content: [必选参数]输入的内容
        :param clearOldText: [可选参数]是否先清空原内容。True:清空原有内容，False:在末尾追加录入。默认True
        :param inputInterval: [可选参数]输入间隔，单位毫秒。默认50
        :param delayTime: [可选参数]超时时间，单位毫秒。默认10000
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]延迟时间，单位毫秒。默认100
        :param delayBefore: [可选参数]延迟时间，单位毫秒。默认100
        :param setForeground: [可选参数]是否将元素置于前台。默认True
        :param validate: [可选参数]是否验证输入内容。默认False
        :param simulateType: [可选参数]输入前点击方式。\'simulate\'：模拟点击，\'api\'：接口点击。默认\'simulate\'
        :param checkClickNum: [可选参数]检查点击次数。默认3
        :param checkElementShow: [可选参数]是否检查元素是否在屏幕上。默认True
        :param endToDo: [可选参数]输入完成后执行的操作。None:什么都不做。\'enter\'：按回车键。\'blur\'：使操作元素失去焦点。默认None
        :return: tdrpa_element_id
        '''
    @staticmethod
    def IsRunning(continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        """
        检查浏览器是否运行

        isRun = Web.IsRunning(continueOnError=False, delayAfter=100, delayBefore=100)

        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 正在运行返回True，否则返回False
        """
    @staticmethod
    def MoveElementToScreen(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, moveMode: str = 'smoothCenter', delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        将元素移动到屏幕中央

        tdrpa_element_id = Web.MoveElementToScreen(target, onlyvis=False, index=None, fromElementTdid=None, moveMode=\'smoothCenter\', delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param moveMode: [可选参数]移动方式。\'smoothCenter\'：平滑移动到元素中央。\'ifNeed\':如果元素不在浏览器可见区域再移动。\'fastCenter\'：快速移动到元素中央。默认\'smoothCenter\'
        :param delayTime: [可选参数]超时时间，单位毫秒。默认10000
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行后延时(毫秒)。默认100
        :param delayBefore: [可选参数]执行前延时(毫秒)。默认100
        :return: tdrpa_element_id
        '''
    @staticmethod
    def Refresh(waitPage: bool = True, delayTime: int = 60000, passCache: bool = False, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        刷新

        Web.Refresh(waitPage=True, delayTime=60000, passCache=False, continueOnError=False, delayAfter=100, delayBefore=100)

        :param waitPage:[可选参数]是否等待页面加载完成。True：等待页面加载完毕，False：不等待页面加载完毕。默认值为 True。
        :param delayTime:[可选参数]waitPage为True时，网页等待超时时间，默认为 60000 毫秒（60秒）
        :param passCache:[可选参数]是否要绕过本地缓存。默认为 False。
        :param continueOnError:[可选参数]是否继续执行后续步骤。默认值为 False。
        :param delayAfter:[可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore:[可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return:None
        """
    @staticmethod
    def RunJS(js_str: str, isSync: bool = True, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100):
        """
        执行JS脚本

        jsResult = Web.RunJS(js_str, isSync=True, continueOnError=False, delayAfter=100, delayBefore=100)

        :param js_str:[必选参数]要执行的JS脚本内容
        :param isSync:[可选参数]是否同步执行，True：等待JS运行完成后才返回继续执行，传递为 false：JS开始执行立即返回
        :param continueOnError:[可选参数]指定即使活动引发错误，自动化是否仍应继续。该字段仅支持布尔值（True，False）。默认值为False
        :param delayAfter:[可选参数]执行活动后的延迟时间（以毫秒为单位）。默认时间为100毫秒
        :param delayBefore:[可选参数]活动开始执行任何操作之前的延迟时间（以毫秒为单位）。默认的时间量是100毫秒
        :return:js运行结果
        """
    @staticmethod
    def ScreenShot(imgPath: str, imgName: str, rect: Incomplete | None = None, continueOnError: bool = False, delayAfter: int = 300, delayBefore: int = 100) -> None:
        '''
        网页截图

        Web.ScreenShot("d:/", "test.png", rect=None, continueOnError=False, delayAfter=300, delayBefore=100)

        :param imgPath:[必须参数]图片保存路径，如"d:/"
        :param imgName:[必选参数]图片名称，如"test.png"
        :param rect:[可选参数]截图的矩形范围，如：{"x": 0, "y": 0, "width": 200, "height": 200}。传递为 None 则截取整个标签页的显示区域。默认None
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认300
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:None
        '''
    @staticmethod
    def SetAttribute(target: str | dict, attrname: str, value: str, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        '''
        设置元素属性值

        setResult = Web.SetAttribute(target, attrname, value, onlyvis=False, index=None, fromElementTdid=None, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param attrname: [必选参数]属性名称。
        :param value: [必选参数]属性值。
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore: [可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 设置成功返回True，否则返回False
        '''
    @staticmethod
    def SetCheck(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, isCheck: bool = True, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        设置元素勾选状态(radio或checkbox)

        setResult = Web.SetCheck(target, onlyvis=False, index=None, fromElementTdid=None, isCheck=True, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param isCheck: [可选参数]是否勾选。True:勾选，False:不勾选。默认True
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore: [可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 设置成功返回True，否则返回False
        '''
    @staticmethod
    def SetFocus(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, setForeground: bool = True, checkElementShow: bool = True, focusMode: str = 'focus', delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        设置元素焦点

        tdrpa_element_id = Web.SetFocus(target, onlyvis=False, index=None, fromElementTdid=None, setForeground=True, checkElementShow=True, focusMode=\'focus\', delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param setForeground: [可选参数]是否将元素设置为前台窗口。默认True
        :param checkElementShow: [可选参数]是否检查元素是否可见。默认True
        :param focusMode: [可选参数]焦点模式。\'focus\'：获得焦点。\'blur\'：离开焦点。默认\'focus\'
        :param delayTime: [可选参数]等待元素出现的超时时间（毫秒）。默认10000
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore: [可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: tdrpa_element_id
        '''
    @staticmethod
    def SetScroll(scrollPostion: dict, smooth: bool = True, waitTime: int = 2000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> dict | None:
        '''
        设置滚动条位置(像素)

        position = Web.SetScroll({"ScrollLeft": 0, "ScrollTop": 500}, smooth=True, waitTime=2000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param scrollPostion:[可选参数]滚动条位置。如：{"ScrollLeft": 0,"ScrollTop": 0}
        :param smooth:[可选参数]是否平滑滚动。True:平滑滚动到指定位置。False:迅速滚动到指定位置。默认True
        :param waitTime:[可选参数]等待多长时间（毫秒）后返回滚动条位置，不能超过5000（毫秒）。默认2000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:返回当前页面的滚动条位置 如{\'ScrollLeft\': 0, \'ScrollTop\': 0}，没有则返回None
        '''
    @staticmethod
    def SetSelect(target: str | dict, selected: str | list | int, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, selectMode: str = 'text', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        '''
        设置元素选中项(select)

        Web.SetSelect(target, selected, onlyvis=False, index=None, fromElementTdid=None, selectMode="text", continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param selected: [必选参数]选中的值。str类型时：选中的值。list类型时：选中的值列表。int类型时：选中的值索引。
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param selectMode: [可选参数]设置选中项的模式。\'index\':根据索引选中。\'value\':根据值选中。\'text\':根据文本选中。默认\'text\'
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore: [可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: None
        '''
    @staticmethod
    def SetValue(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, value: str = '', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        设置元素的值

        setResult = Web.SetValue(target, onlyvis=False, index=None, fromElementTdid=None, value=\'\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param value: [可选参数]要设置的值。默认\'\'
        :param continueOnError: [可选参数]是否继续执行。默认False
        :param delayAfter: [可选参数]执行步骤后等待的时间（毫秒）。默认值为 100。
        :param delayBefore: [可选参数]执行步骤前等待的时间（毫秒）。默认值为 100。
        :return: 返回设置完成的值
        '''
    @staticmethod
    def Stop(delayTime: int = 10000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 1000) -> bool | None:
        """
        停止网页加载

        stopResult = Web.Stop(delayTime=10000, continueOnError=False, delayAfter=100, delayBefore=1000)

        :param delayTime:[可选参数]超时时间(毫秒)。默认10000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认1000
        :return:页面停止成功返回True，失败返回False
        """
    @staticmethod
    def SwitchTab(matchTabContent: str = '', matchTabType: str = 'title', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> bool | None:
        '''
        切换浏览器标签页(可通过地址栏、标题栏进行匹配，支持包含匹配)

        switchResult = Web.SwitchTab(\'百度\', matchTabType=\'title\', continueOnError=False, delayAfter=100, delayBefore=100)

        :param matchTabContent: [必选参数]标签页匹配的内容，标题支持包含匹配，例如“百度”，链接支持包含匹配，例如“baidu”
        :param matchTabType:[可选参数]标签页匹配的类型，\'title\':匹配标题。\'url\':匹配链接。默认"title"
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return: 切换成功返回True，失败返回False
        '''
    @staticmethod
    def SetWindowState(browserWinState: str = 'topmost', continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> None:
        """
        设置浏览器窗口状态

        Web.SetWindowState(browserWinState='topmost', continueOnError=False, delayAfter=100, delayBefore=100)

        :param browserWinState:[可选参数]浏览器窗口状态。'activate': 激活。'topmost':置顶并激活。'untop':取消置顶并移到底层显示。默认'topmost'
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:None
        """
    @staticmethod
    def WaitElement(target: str | dict, onlyvis: bool = False, index: int = None, fromElementTdid: str = None, waitType: str = 'show', delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100) -> str | None:
        '''
        等待元素

        tdrpa_element_id = Web.WaitElement(target, onlyvis=False, index=None, fromElementTdid=None, waitType=\'show\', delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param target: [必选参数]网页元素特征码。str类型时：tdSelector拾取的特征码，或css选择器，或xpath，或tdrpa_element_id。dict类型时：{"selector":css选择器, "txt": 网页元素上的文字}
        :param onlyvis: [可选参数]仅匹配可见元素。默认False
        :param index: [可选参数]元素索引。None:忽略索引，int:索引为整数时，从1开始算索引。 target为tdrpa_element_id时会自动忽略此参数。默认None
        :param fromElementTdid: [可选参数]从哪个元素开始查找（注意：当target为tdSelector获取的特征码时该参数才有效）。None:从当前页面开始查找。tdrpa_element_id:从该元素开始查找。默认None
        :param waitType: [可选参数]等待元素方式。\'show\':等待元素出现。\'hide\':等待元素消失。默认\'show\'
        :param delayTime:[可选参数]超时时间(毫秒)。默认60000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:tdrpa_element_id
        '''
    @staticmethod
    def WaitPage(delayTime: int = 60000, continueOnError: bool = False, delayAfter: int = 100, delayBefore: int = 100):
        """
        等待网页加载完成

        waitResult = Web.WaitPage(delayTime=60000, continueOnError=False, delayAfter=100, delayBefore=100)

        :param delayTime:[可选参数]超时时间(毫秒)。默认60000
        :param continueOnError:[可选参数]错误继续执行。默认False
        :param delayAfter:[可选参数]执行后延时(毫秒)。默认100
        :param delayBefore:[可选参数]执行前延时(毫秒)。默认100
        :return:页面加载完成返回True，未加载完成返回False
        """
