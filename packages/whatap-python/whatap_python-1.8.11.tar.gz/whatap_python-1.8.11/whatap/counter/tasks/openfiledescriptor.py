import whatap.net.async_sender as async_sender
from whatap.pack import tagCountPack
from whatap import DateUtil, conf
import whatap.io as whatapio
import os, resource

currentpid = os.getpid()

soft_limit, _= resource.getrlimit(resource.RLIMIT_NOFILE)

class OpenFileDescriptorTask:
    def name(self):

        return "OpenFileDescriptorTask"
    
    def interval(self):
        from whatap.conf.configure import Configure as conf
        return conf.open_file_descriptor_interval
    
    def process(self):
        from whatap.conf.configure import Configure as conf
        if not conf.open_file_descriptor_enabled:
            return

        currentnofile = self.currentNofile()
        if soft_limit:
            current_nofile_pct = float(currentnofile) / float(soft_limit) * float(100)
        else:
            current_nofile_pct = "N/A"
        category = "app_filedescriptor"
        tags = dict(pid=currentpid)
        fields = dict(max_nofile = soft_limit,
                      currnet_nofile=currentnofile,
                      current_nofile_pct=current_nofile_pct )

        p = tagCountPack.getTagCountPack(
            t=DateUtil.now(),
            category=f"{category}",
            tags=tags,
            fields=fields
        )

        p.pcode = conf.PCODE
        bout = whatapio.DataOutputX()
        bout.writePack(p, None)
        packbytes = bout.toByteArray()

        async_sender.send_relaypack(packbytes)

    def currentNofile(self):
        fd_directory = f'/proc/{currentpid}/fd'  # 현재 프로세스의 파일 디스크립터가 있는 디렉터리
        try:
            fd_count = len(os.listdir(fd_directory))  # fd 디렉터리 안의 파일 목록 개수
            return fd_count
        except FileNotFoundError:
            #print("이 시스템에서는 /proc 파일 시스템이 지원되지 않습니다.")
            return "N/A"