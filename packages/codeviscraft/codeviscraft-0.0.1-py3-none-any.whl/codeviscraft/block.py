class Block:
    def __init__(self, blockType, x, y, z):
        self.blockType = blockType
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "Block(%s,%s,%s,%s)"%(self.blockType, self.x,self.y,self.z)
