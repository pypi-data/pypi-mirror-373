import shlex
import faulthandler
import tempfile
class StackParser:

    parsers = {}
    @staticmethod
    def onNewParser(parser):
        StackParser.parsers[parser.getThreadId()] =parser

    @staticmethod
    def listAll():
        for p in StackParser.parsers:
            yield p
    
    @classmethod
    def find(cls, thread_id):
        if thread_id in cls.parsers:
            p = cls.parsers.get(thread_id)
            return p.iterateStacks()
        else:
            return iter([])

    @staticmethod
    def parse():
        with tempfile.NamedTemporaryFile() as buf:
            faulthandler.dump_traceback(buf)
            if buf.tell() < 1:
                return
            buf.seek(0)
            stackdump = buf.read().decode("utf-8")
            stackParser = None
            for stack in stackdump.split('\n'):
                if not stack:
                    stackParser.onComplete()
                    stackParser = None
                    continue
                if not stackParser:
                    stackParser = StackParser(stack)
                else:
                    stackParser.add(stack)

    def __init__(self, threadBegin):
        self.__stacks = []
        tokens = shlex.split(threadBegin)
        if tokens and len(tokens) > 2:
            try:
                if 'Thread' == tokens[0] and int(tokens[1],0) > 0:
                    threadid = int(tokens[1],0)
                    self.__threadid = threadid

                    StackParser.onNewParser(self)
                elif 'Current' == tokens[0] and 'thread' == tokens[1] and int(tokens[2],0):
                    threadid = int(tokens[2],0)
                    self.__threadid = threadid
                
                    StackParser.onNewParser(self)
            except ValueError:
                pass

    def getThreadId(self):
        return self.__threadid
    
    def add(self, line):
        tokens = shlex.split(line)
        if len(tokens) == 6:
            _, module, _, lineno, _, method = tokens
            self.__stacks.append((module.strip(','), lineno, method))

    def iterateStacks(self):
        return iter(self.__stacks)

    def toString(self):
        return """Thread: {}
{}""".format(self.__threadid, "\n".join([ "{} {} {}".format(stack[0],stack[1],stack[2]) for stack in self.__stacks]))

    def onComplete(self):
        pass

def getThreadStackFaultHandler( thread_id):
    StackParser.parse()
    for line, line_num, method_name in StackParser.find(thread_id):
        if line.find('/whatap/trace') > -1 or line.find('/threading.py') > -1:
            continue
        yield '{} ({}:{})\n'.format(method_name, line, line_num)

