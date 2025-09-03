from .counter_manager import CounterMgr  # CounterMgr 클래스 import
from whatap import preview_whatap_conf

open_file_descriptor_enabled = preview_whatap_conf("open_file_descriptor_enabled")

if open_file_descriptor_enabled != 'false':
    mgr = CounterMgr()
    mgr.setDaemon(True)
    mgr.start()