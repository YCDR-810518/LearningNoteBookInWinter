# block
# chain
import hashlib


# 包导入区


# 区块的构成
# data（数据区）
# 之前区块的哈希值
# 自己的哈希值

class Block:
    def __init__(self, pre_hash,data):
        self.data = data
        self.pre_hash = pre_hash
        # 这里是将sha-256算出来的data数据进行转换为16进制，方便打印
        self.hash = self.calculate_text_hash()

    def calculate_text_hash(self):
        # 初始化哈希
        hasher = hashlib.sha256()
        hash_data = str(self.data) + str(self.pre_hash)
        # 用数据&前哈希更新哈希值
        hasher.update(hash_data.encode('utf-8'))
        # 返回十六进制哈希
        return hasher.hexdigest()

# 区块的链
class Chain:
    def __init__(self):
        self.chain = [self.generate_genesis_block()]

    def generate_genesis_block(self):
        genesis_block = Block(0, "本区块为祖先区块")
        return genesis_block

    def append_block(self, block):
        self.chain.append(block)
        return block

    def search_hash(self):
        latest_block = self.chain[-1]
        return latest_block.hash

# 实例化测试
data = 'YC666'
pre_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
print(pre_hash)
testBlock = Block(pre_hash,"test")
print(testBlock.hash)

data = 'YCDR666'
YC  = Chain()
YC666 = Block(YC.search_hash(),data)
YC.append_block(YC666)
