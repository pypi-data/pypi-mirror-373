from whatap.pack.pack import Pack
from whatap.pack.pack_enum import PackEnum
from whatap.value.map_value import MapValue
from whatap.io.data_outputx import DataOutputX
from whatap.util.hash_util import HashUtil as hashutil

class LogSinkPack(Pack):
    def __init__(self):
        super(LogSinkPack, self).__init__()
        self.tagHash = 0 #  int64
        self.tags = MapValue()
        self.line = 0 #     int64
        self.content = None # string
        self.fields = MapValue()   
        
    def getPackType(self):
        return PackEnum.LOGSINK

    def write(self, dout):
        super(LogSinkPack, self).write(dout)

        dout.writeByte(0)
        dout.writeText(self.Category)
        if self.tagHash == 0 and self.tags.size() > 0:
            tagHash, tagBytes = self.resetTagHash()
            self.tagHash = tagHash
            dout.writeDecimal(tagHash)
            dout.write(tagBytes)
        else:
            dout.writeDecimal(self.tagHash)
            dout.writeValue(self.tags)
        dout.writeDecimal(self.line)
        dout.writeText(self.content)
        if self.fields and self.fields.size() > 0:
            dout.writeBoolean(True)
            dout.writeValue(self.fields)
        else:
            dout.writeBoolean(False)

    def resetTagHash(self) :
        dout = DataOutputX()
        dout.writeValue(self.tags)
        tagBytes = dout.toByteArray()
        tagHash = hashutil.hash(tagBytes)
        return tagHash, tagBytes
        
    def read(self, din):
        super(LogSinkPack, self).read(din)
        din.readByte()
        self.Category = din.readText()
        self.tagHash = din.ReadDecimal()
        self.tags = din.readValue()
        self.line = din.readDecimal()
        self.content = din.readText()
        if din.readBool():
            self.fields = din.readValue()
        
        return self


def getLogSinkPack( t = 0,
        category = None,
        tags = {},
        fields = {},
        line=0,
        content = None):
    pack = LogSinkPack()
    pack.time = t
    pack.Category = category
    for k, v in tags.items():
        pack.tags.putString(k, str(v))
    for k, v in fields.items():
        pack.fields.putString(k, str(v))
    pack.line = line
    pack.content = content
    return pack
    