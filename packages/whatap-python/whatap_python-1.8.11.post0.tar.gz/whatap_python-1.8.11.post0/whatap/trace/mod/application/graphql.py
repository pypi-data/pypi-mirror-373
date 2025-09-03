from whatap.trace import get_dict
from whatap.trace.mod.application.wsgi import trace_handler, \
    interceptor_step_error, start_interceptor, end_interceptor
from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
import whatap.net.async_sender as async_sender
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.util.date_util import DateUtil
import pkg_resources
from graphql.language.ast import OperationDefinitionNode


def parseServiceName(graphql_doc):
    # GraphQL-core 버전 확인
    graphql_core_version = pkg_resources.get_distribution("graphql-core").version

    # GraphQL-core 3.x 이상 버전일 경우
    if graphql_core_version.startswith("3") or graphql_core_version.startswith("4"):
        try:
            # OperationDefinitionNode 타입의 노드 필터링 (3.x 이상 버전 로직)
            op_def = [
                i for i in graphql_doc.definitions
                if isinstance(i, OperationDefinitionNode)
            ][0]
        except (IndexError, KeyError):
            return "GraphQL unknown operation"

        # operation의 타입이 OperationType Enum인 경우
        op = op_def.operation.value  # Enum 값을 문자열로 변환
    else:
        try:
            # 이전 버전 로직 (OperationDefinition 사용)
            op_def = [
                i for i in graphql_doc.definitions
                if type(i).__name__ == "OperationDefinition"
            ][0]
        except (IndexError, KeyError):
            return "GraphQL unknown operation"

        # operation의 타입이 문자열인 경우
        op = op_def.operation  # 문자열 그대로 사용

    name = op_def.name
    fields = op_def.selection_set.selections if op_def.selection_set else []

    return "/GraphQL %s %s" % (op.upper(), name.value if name else "+".join([f.name.value for f in fields]))


def intercept_execute(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        ctx = TraceContext()
        is_transaction_started = False
    else:
        is_transaction_started = not ctx.is_ignored
    if not is_transaction_started:
        if len(args) > 1 and hasattr(args[1],"definitions"):
            name = parseServiceName(args[1])
            if name:    
                ctx.service_name =  name
        start_interceptor(ctx)
    start_time = DateUtil.nowSystem()
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        if not is_transaction_started:
            end_interceptor()
        else:
            text = "graphql.execute"
            payloads = [text, '']
            ctx.elapsed = DateUtil.nowSystem() - start_time
            async_sender.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)

def parseDocumentName(op_def):
    op = op_def.operation
    name = op_def.name
    fields = op_def.selection_set.selections
    if not fields:
        fields = []
    return "GraphQL %s %s" % (op.upper(), name if name else "+".join([f.name.value for f in fields]))  


def parseSelectionSet(gnode, tokens = [], indent=0):
    nameFound = False
    
    if hasattr(gnode, "selection_set"):
        if hasattr(gnode, "name") and hasattr(gnode, "selection_set"): 
            if gnode.selection_set:
                tokens.append("  "*indent+gnode.name.value+"{")
                nameFound = True
            else:
                tokens.append("  "*indent+gnode.name.value)

    if hasattr(gnode, "selection_set"):
        if gnode.selection_set:
            if gnode.selection_set.selections:
                for sel in gnode.selection_set.selections:
                    parseSelectionSet(sel, tokens, indent = indent+1)
    if nameFound:
        tokens.append("  "*indent+"}")

def parseDocument(defi):
    tokens = []
    if hasattr(defi, "name"):
        tokens.append(defi.name.value+"{")
    
    if hasattr(defi, "selection_set"):
        if defi.selection_set:
            if defi.selection_set.selections:
                for sel in defi.selection_set.selections:
                    if sel:
                        parseSelectionSet(sel, tokens, 1)

    if hasattr(defi, "name"):
        tokens.append("}")
    tokens.reverse()
    return "\n".join(tokens)

def intercept_execute_method( fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    start_time = DateUtil.nowSystem()
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        if ctx:
            interceptor_step_error(e)
    finally:
        if ctx and len(args) > 4 and not args[4] and args[3]:
            operation_definition = args[3][0]
            text = operation_definition.name.value
            arg = parseDocument(operation_definition)
            
            payloads = [text, arg]
            ctx.elapsed = DateUtil.nowSystem() - start_time
            async_sender.send_packet(PacketTypeEnum.TX_METHOD, ctx, payloads)
        
def instrument_graphql(module):
    def wrapper(fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_execute(fn, *args, **kwargs)
            return callback

        return trace
    if hasattr(module, 'execute'):
        module.execute = wrapper(module.execute)

    def wrapper( fn):
        @trace_handler(fn, start=True)
        def trace(*args, **kwargs):
            callback = intercept_execute_method( fn, *args, **kwargs)
            return callback
        return trace

    # if hasattr(module, 'execute_operation'):
    #    module.execute_operation = wrapper(module.execute_operation)
        
    if hasattr(module, 'resolve_field'):
       module.resolve_field = wrapper(module.resolve_field)