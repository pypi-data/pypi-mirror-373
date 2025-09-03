from whatap.pack.pack import Pack
from whatap.pack.pack_enum import PackEnum
from whatap.value.map_value import MapValue
from whatap.io.data_outputx import DataOutputX
from whatap.util.hash_util import HashUtil as hashutil

class TagCountPack(Pack):
    def __init__(self):
        super(TagCountPack, self).__init__()
        self.tagHash = 0 #  int64
        self.tags = MapValue()
        self.fields = MapValue()   
        
    def getPackType(self):
        return PackEnum.TAG_COUNT

    def write(self, dout):
        super(TagCountPack, self).write(dout)

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
        dout.writeValue(self.fields)
        
    def resetTagHash(self) :
        dout = DataOutputX()
        dout.writeValue(self.tags)
        tagBytes = dout.toByteArray()
        tagHash = hashutil.hash(tagBytes)
        return tagHash, tagBytes
        
    def read(self, din):
        super(TagCountPack, self).read(din)
        din.readByte()
        self.Category = din.readText()
        self.tagHash = din.ReadDecimal()
        self.tags = din.readValue()
        self.fields = din.readValue()
        
        return self

def getTagCountPack( t = 0,
        category = None,
        tags = {},
        fields = {}):
    pack = TagCountPack()
    pack.time = t
    pack.Category = category
    for k, v in tags.items():
        pack.tags.putAuto(k, v)
    for k, v in fields.items():
        pack.fields.putAuto(k, v)
    return pack
    