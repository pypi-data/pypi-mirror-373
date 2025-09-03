import traceback


class DummyNativeAPI:
    def LogInfo(self, *args, **kwargs):
        pass

    def LogWarning(self, *args, **kwargs):
        pass

    def LogError(self, *args, **kwargs):
        pass

    BREAKPOINT_EVENT_ERROR = "1"
    BREAKPOINT_EVENT_GLOBAL_CONDITION_QUOTA_EXCEEDED = "2"
    BREAKPOINT_EVENT_BREAKPOINT_CONDITION_QUOTA_EXCEEDED = "3"
    BREAKPOINT_EVENT_CONDITION_EXPRESSION_MUTABLE = "4"
    BREAKPOINT_EVENT_CONDITION_EXPRESSION_EVALUATION_FAILED = "5"


try:
    from . import cdbg_native as native
except Exception as e:
    print("Google Cloud Debugger Import Exception: %s, stacktrace: %s" % (e, traceback.format_exc()))
    native = DummyNativeAPI()
