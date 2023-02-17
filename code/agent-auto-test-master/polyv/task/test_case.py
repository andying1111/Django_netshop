from polyv.task.case_step import CaseStep


class TestCase(object):
    def __init__(self):
        self.taskId = None
        self.projectId = None
        self.projectSign = None
        self.projectName = None
        self.executor = None
        self.caseName = None
        self.caseId = None
        self.caseSign = None
        self.git = None
        self.hostStr = None
        self.caseCount = None
        self.caseIndex = None
        self.notify = None
        self.steps = []
        self.startTime = None

    def decode_step(self):
        _steps = []
        for step in self.steps:
            _step = CaseStep()
            _step.__dict__ = step
            _steps.append(_step)
        self.steps = _steps
