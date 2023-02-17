class CaseStep(object):
    def __init__(self):
        self.caseType = None  # 类型：1=web,2=android,3=ios,4=win,5=http
        self.caseIndex = None
        self.packPath = None
        self.function = None
        self.parameters = None
        self.expectResult = None
