from whatap.trace.trace_context import TraceContext
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from whatap.net.packet_type_enum import PacketTypeEnum
from whatap.conf.configure import Configure as conf
from whatap.trace.mod.application.wsgi import interceptor_step_error
import whatap.net.async_sender as async_sender
import re


def extract_db_error_message(e):
    try:
        # PostgreSQL (psycopg2)
        if hasattr(e, 'pgcode') and hasattr(e, 'pgerror'):
            return str(e.pgerror)

        # MySQL (PyMySQL, mysql-connector-python)
        if hasattr(e, 'args') and len(e.args) > 1 and isinstance(e.args[1], str):
            return e.args[1]

        # 기본 에러 메시지
        if hasattr(e, 'args') and len(e.args) > 0:
            if isinstance(e.args[0], str):
                return e.args[0]
            return str(e.args[0])

        return str(e)
    except:
        return "Unknown database error"



def addQuoteDict(arg_dict):
    quoted_dict = dict()

    for k, v in arg_dict.items():
        if isinstance(v, str):
            quoted_dict[k] = "'" + v.replace("'", "\\'") + "'"
        else:
            quoted_dict[k] = v

    return quoted_dict

def addQuoteList(arg_list):
    quoted_list = list()

    for v in arg_list:
        if isinstance(v, str):
            quoted_list.append("'" + v.replace("'", "\\'") + "'")
        else:
            quoted_list.append("'" + str(v) + "'")

    return tuple(quoted_list)

def addQuoteMany(arg_list, query_template=None):
    """
    executemany용 파라미터 리스트를 쿼리 문자열로 변환

    Args:
        arg_list: [(val1, val2, val3), (val4, val5, val6), ...] 형태의 리스트
        query_template: 쿼리 템플릿 (제공되면 개별 쿼리들 생성)

    Returns:
        str: 포매팅된 문자열
    """
    if not arg_list:
        return ""

    try:
        if query_template is None:
            # 기존 방식: VALUES 절용 포맷
            formatted_rows = []
            for row in arg_list:
                if isinstance(row, (list, tuple)):
                    quoted_values = []
                    for value in row:
                        if value is None:
                            quoted_values.append("NULL")
                        elif isinstance(value, str):
                            escaped = value.replace("'", "''")
                            quoted_values.append(f"'{escaped}'")
                        else:
                            quoted_values.append("'" + str(value) + "'")

                    formatted_row = "({})".format(", ".join(quoted_values))
                    formatted_rows.append(formatted_row)

            result = ", ".join(formatted_rows)
        else:
            # 개별 쿼리 생성 방식
            queries = []
            for row in arg_list:
                if isinstance(row, (list, tuple)):
                    try:
                        quoted_values = []
                        for value in row:
                            if value is None:
                                quoted_values.append("NULL")
                            elif isinstance(value, str):
                                escaped = value.replace("'", "''")
                                quoted_values.append(f"'{escaped}'")
                            else:
                                quoted_values.append(str(value))

                        individual_query = query_template % tuple(quoted_values)
                        queries.append(individual_query)
                    except:
                        queries.append(f"{query_template} [failed to format row: {row}]")

            result = ";\n".join(queries)

        return result

    except Exception as e:
        return f"[{len(arg_list)} rows]"



def neo4jQuery(query,paremeter):
    neo4j_query = query

    for key, value in paremeter.items():
        placeholder = f"${key}"
        replacement = f"'{str(value)}'"
        neo4j_query = neo4j_query.replace(placeholder, replacement)

    return neo4j_query

def sqliteQuery(query, paremeter):
    sqlite_query = query

    def quote(v):
        if v is None: return "NULL"
        if isinstance(v, (bytes, bytearray)): return "X'" + v.hex() + "'"
        return "'" + str(v).replace("'", "''") + "'"

    # 이름 기반: :name / @name / $name (단일 세트)
    if isinstance(paremeter, dict):
        for pfx in (':', '@', '$'):
            for k, v in paremeter.items():
                sqlite_query = sqlite_query.replace(f"{pfx}{k}", quote(v))
        return sqlite_query

    # 포지셔널 + executemany 분기
    if isinstance(paremeter, (list, tuple)):
        # ── executemany: [tuple|dict, ...] ──
        if isinstance(paremeter, list) and paremeter and isinstance(paremeter[0], (tuple, dict)):
            stmts = []
            for params in paremeter:
                sqlite_query = query
                if isinstance(params, dict):
                    for pfx in (':', '@', '$'):
                        for k, v in params.items():
                            sqlite_query = sqlite_query.replace(f"{pfx}{k}", quote(v))
                else:  # tuple
                    for i, v in enumerate(params, 1):
                        sqlite_query = sqlite_query.replace(f"?{i}", quote(v))
                    for v in params:
                        sqlite_query = sqlite_query.replace('?', quote(v), 1)
                stmts.append(sqlite_query)
            return ";\n".join(stmts)

        # ── 단일 포지셔널 세트 (tuple 또는 스칼라 list) ──
        seq = paremeter if isinstance(paremeter, tuple) else tuple(paremeter)
        for i, v in enumerate(seq, 1):
            sqlite_query = sqlite_query.replace(f"?{i}", quote(v))
        for v in seq:
            sqlite_query = sqlite_query.replace('?', quote(v), 1)
        return sqlite_query

    return sqlite_query

def interceptor_db_con(fn, db_info, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return fn(*args, **kwargs)

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    ctx.db_opening = True
    try:
        callback = fn(*args, **kwargs)
    finally:
        ctx.db_opening = False

    if not kwargs:
        kwargs = dict(
            x.split('=') for x in re.sub(r'\s*=\s*', '=', args[0]).split())

    db_type = db_info.get('type')

    if db_type == "sqlite":
        text = "sqlite:"

    elif db_type == "neo4j":
        text = "neo4j"
        text += "@"
        text += db_info.get('uri','')
        text += "/"
        text += db_info.get('user', '')

    else:
        text = '{}://'.format(db_type)
        text += kwargs.get('user', '')
        text += "@"
        text += kwargs.get('host', kwargs.get('dsn', ''))
        text += '/'

    text += kwargs.get('database', kwargs.get('db', kwargs.get('dbname', '')))
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    ctx.active_dbc = 0

    datas = [text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    async_sender.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)

    return callback


def interceptor_db_execute(fn, db_info, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    # sendDebugProfile(ctx, 'interceptor_db_execute step -1')
    self = args[0]
    db_type = db_info.get('type')
    query = None
    if db_type == "neo4j":
        try:
            query = neo4jQuery(args[1], kwargs)
        except Exception as e:
            pass

    elif db_type == "sqlite" and len(args) > 2:
        try:
            query = sqliteQuery(args[1],args[2])
        except Exception as e:
            pass

    else:
        if (len(args) > 2 and
                isinstance(args[2], (list, tuple)) and
                len(args[2]) > 0 and
                isinstance(args[2][0], (list, tuple))):
            try:
                query_str = args[1]
                if isinstance(query_str, bytes):
                    query_str = query_str.decode()

                query_upper = query_str.upper()

                if 'VALUES' in query_upper:
                    # INSERT 처리
                    values_pos = query_upper.find('VALUES')
                    before_values = query_str[:values_pos + 6]
                    query = f"{before_values} {addQuoteMany(args[2])}"
                else:
                    # UPDATE, DELETE 등 처리 - 개별 쿼리로 표시
                    query = addQuoteMany(args[2], query_str)
            except Exception as e:
                pass

        elif len(args) > 2 and type(args[2]) == dict and args[2]:
            try:
                query = args[1] % addQuoteDict(args[2])
            except Exception as e:
                pass
        elif len(args) > 2 and type(args[2]) in (list, tuple) and args[2]:
            try:
                query = args[1] % addQuoteList(args[2])
            except Exception as e:
                pass
    try:
        if not query:
            query = args[1].decode()
    except Exception as e:
        query = args[1]

    if not query:
        return fn(*args, **kwargs)

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    ctx.active_sqlhash = query
    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        datas = [ctx.lctx.get('dbc', ''), query, str(self.rowcount)]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        async_sender.send_packet(PacketTypeEnum.TX_SQL, ctx, datas)
        count = self.rowcount

        if (count is not None) and (count > -1):
            desc = '{0}: {1}'.format('Fetch count', count)
            datas = [' ', ' ', desc]
            ctx.elapsed = 0
            async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

        ctx.active_sqlhash = 0


def interceptor_db_close(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    ctx.db_opening = False

    if not conf.profile_dbc_close:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            interceptor_step_error(e)
        finally:
            return
    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    try:
        callback = fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
    finally:
        text = 'DB: Close Connection.'
        datas = [' ', ' ', text]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)


async def async_interceptor_db_con(fn, db_info, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return await fn(*args, **kwargs)

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    ctx.db_opening = True
    try:
        callback = await fn(*args, **kwargs)
    finally:
        ctx.db_opening = False

    if not kwargs:
        kwargs = dict(
            x.split('=') for x in re.sub(r'\s*=\s*', '=', args[0]).split())

    db_type = db_info.get('type')

    if db_type == "sqlite":
        text = "sqlite:"
    else:
        text = '{}://'.format(db_type)
        text += kwargs.get('user', '')
        text += "@"
        text += kwargs.get('host', kwargs.get('dsn', ''))
        text += '/'

    text += kwargs.get('database', kwargs.get('db', kwargs.get('dbname', '')))
    ctx.active_dbc = text
    ctx.lctx['dbc'] = text

    ctx.active_dbc = 0

    datas = [text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    async_sender.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)

    return callback


async def async_interceptor_db_execute(fn, db_info, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    self = args[0]
    db_type = db_info.get('type')
    query = None
    if db_type == "neo4j":
        try:
            query = neo4jQuery(args[1], kwargs)
        except Exception as e:
            pass

    elif db_type == "sqlite" and len(args) > 2:
        try:
            query = sqliteQuery(args[1], args[2])
        except Exception as e:
            pass

    else:
        if (len(args) > 2 and
                isinstance(args[2], (list, tuple)) and
                len(args[2]) > 0 and
                isinstance(args[2][0], (list, tuple))):
            try:
                # VALUES 절을 찾아서 전체를 교체
                query_str = args[1]
                if isinstance(query_str, bytes):
                    query_str = query_str.decode()

                # VALUES (...) 부분을 찾아서 교체
                query_upper = query_str.upper()
                if 'VALUES' in query_upper:
                    values_pos = query_upper.find('VALUES')
                    before_values = query_str[:values_pos + 6]  # "VALUES" 까지
                    query = f"{before_values} {addQuoteMany(args[2])}"
                else:
                    # VALUES가 없으면 단순 치환 시도
                    query = query_str.replace('%s', addQuoteMany(args[2]), 1)
            except Exception as e:
                pass

        elif len(args) > 2 and type(args[2]) == dict and args[2]:
            try:
                query = args[1] % addQuoteDict(args[2])
            except Exception as e:
                pass
        elif len(args) > 2 and type(args[2]) in (list, tuple) and args[2]:
            try:
                query = args[1] % addQuoteList(args[2])
            except Exception as e:
                pass

    try:
        if not query:
            if hasattr(args[1], 'decode'):
                query = args[1].decode()
            else:
                query = args[1]
    except Exception as e:
        query = args[1]

    if not query:
        return await fn(*args, **kwargs)

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time
    ctx.active_sqlhash = query

    try:
        callback = await fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
        raise
    finally:
        datas = [ctx.lctx.get('dbc', ''), query, str(self.rowcount)]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        async_sender.send_packet(PacketTypeEnum.TX_SQL, ctx, datas)
        count = self.rowcount

        if (count is not None) and (count > -1):
            desc = '{0}: {1}'.format('Fetch count', count)
            datas = [' ', ' ', desc]
            ctx.elapsed = 0
            async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)

        ctx.active_sqlhash = 0


async def async_interceptor_db_close(fn, *args, **kwargs):
    ctx = TraceContextManager.getLocalContext()
    ctx.db_opening = False

    if not conf.profile_dbc_close:
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            interceptor_step_error(e)
            raise
        finally:
            return

    start_time = DateUtil.nowSystem()
    ctx.start_time = start_time

    try:
        callback = await fn(*args, **kwargs)
        return callback
    except Exception as e:
        interceptor_step_error(e)
        raise
    finally:
        text = 'DB: Close Connection.'
        datas = [' ', ' ', text]
        ctx.elapsed = DateUtil.nowSystem() - start_time
        async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)


def interceptor_pool_get(db_info):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return

    start_time = DateUtil.nowSystem()

    db_type = db_info.get('type', 'db')
    text = f"{db_type}://{db_info.get('user', '')}@{db_info.get('host', '')}/{db_info.get('dbname', '')}"

    ctx.active_dbc = text
    ctx.lctx['dbc'] = text
    ctx.active_dbc = 0

    datas = [text]
    ctx.elapsed = DateUtil.nowSystem() - start_time

    async_sender.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)


def interceptor_pool_release():
    ctx = TraceContextManager.getLocalContext()
    if not ctx or not conf.profile_dbc_close:
        return

    start_time = DateUtil.nowSystem()
    text = 'DB: Close Connection.'
    datas = [' ', ' ', text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)


async def async_interceptor_pool_get(db_info):
    ctx = TraceContextManager.getLocalContext()
    if not ctx:
        return

    start_time = DateUtil.nowSystem()

    db_type = db_info.get('type', 'db')
    text = f"{db_type}://{db_info.get('user', '')}@{db_info.get('host', '')}/{db_info.get('dbname', '')}"

    ctx.active_dbc = text
    ctx.lctx['dbc'] = text
    ctx.active_dbc = 0

    datas = [text]
    ctx.elapsed = DateUtil.nowSystem() - start_time

    async_sender.send_packet(PacketTypeEnum.TX_DB_CONN, ctx, datas)

async def async_interceptor_pool_release():
    ctx = TraceContextManager.getLocalContext()
    if not ctx or not conf.profile_dbc_close:
        return

    start_time = DateUtil.nowSystem()
    text = 'DB: Close Connection.'
    datas = [' ', ' ', text]
    ctx.elapsed = DateUtil.nowSystem() - start_time
    async_sender.send_packet(PacketTypeEnum.TX_MSG, ctx, datas)