import os
import time
import logging
from threading import Thread
from .tasks.openfiledescriptor import OpenFileDescriptorTask

#현재 디렉토리 아래 tasks 가 있고 그안의 openfiledescriptor.py 파일에  OpenFileDescriptorTask 클래스를 import 하고싶어.

class CounterMgr(Thread):
    def __init__(self):
        super(CounterMgr, self).__init__()  # Thread 초기화
        self.tasks = list()
        self.last_executed = {}  # 각 task의 마지막 실행 시간을 기록하기 위한 딕셔너리
        
    def run(self):
        # OpenFileDescriptorTask 인스턴스 생성 후 tasks에 추가
        task = OpenFileDescriptorTask()
        self.tasks.append(task)
        self.last_executed[task.name()] = 0  # 각 task의 마지막 실행 시간을 초기화
        while True:
            current_time = time.time()  # 현재 시간을 초 단위로 가져옴
            time.sleep(1)  # 0.1초마다 확인 (부하 줄이기)
            for task in self.tasks:
                
                # 현재 시간과 마지막 실행 시간을 비교하여 task.interval() 초 만큼의 시간이 지났으면 실행
                last_executed_time = self.last_executed[task.name()]
                interval = task.interval()
                
                if current_time - last_executed_time >= interval:
                    try:
                        self.last_executed[task.name()] = current_time  # 마지막 실행 시간 업데이트
                        task.process()  # task 실행
                        
                    except Exception as e:
                        logging.debug(e, extra={'id': 'WA181'}, exc_info=True)
                        