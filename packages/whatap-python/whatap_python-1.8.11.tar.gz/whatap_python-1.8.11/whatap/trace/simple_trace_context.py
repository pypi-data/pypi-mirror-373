import copy

from whatap.trace.trace_context import TraceContext


class SimpleTraceContext(TraceContext):
    def __init__(self, ctx: TraceContext):
        self.ctx = ctx

    """
    Replaced Python's built-in deepcopy function with a manual deep copy method in SimpleTraceContext.
    This change prevents potential pickle errors when serializing the TraceContext object.
    Each attribute is copied individually to ensure that complex objects within TraceContext are correctly handled.
    """
    def getDeepCopiedContext(self):
        for key, value in self.ctx.__dict__.items():
            setattr(self, key, value)
        return self