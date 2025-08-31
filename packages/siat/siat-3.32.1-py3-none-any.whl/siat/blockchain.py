# -*- coding: utf-8 -*-
"""
本模块功能：区块链的创建与查询，仅限测试使用
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年9月18日
最新修订日期：2020年2月7日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

import hashlib as hasher
class Block:
    """
    定义一个区块链中的区块:
    为了保证整个区块链的完整性，每一个区块都有一个唯一的哈希值，用于自我标识。
    比如比特币，每一个区块的哈希值是由区块的索引、时间戳、数据以及前一个区块的哈希，
    经过加密后得到的。其中，数据可以选取任意值。    
    """
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update((str(self.index) + 
                   str(self.timestamp) + 
                   str(self.data) + 
                   str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()


import datetime as date
def create_genesis_block():
    """
    创建一个区块链中的创世区块：即第一个区块
    这个区块的索引为0，此外，它所包含的数据以及前一个区块的哈希值都是一个任意的值。
    """ 
    # Manually construct ablock with
    # index zero and arbitrary previous hash
    return Block(0, date.datetime.now(), "RootBlock", "0")


def next_block(last_block,this_data):
    """
    增加一个区块：
    还需要一个函数来生成链上更多的区块。该函数将链上前一个区块作为参数，
    为后面的区块生成数据，并返回具有带有数据的新区块。
    当生成的新区块包含了前一个区块的哈希值，区块链的完整性就会随着每个区块的增加而增加。
    这样的操作虽然看起来有点复杂，但如果不这么做，其他人就会很容易篡改链上的数据，
    甚至把整条链都给换了。所以，链上区块的哈希值就充当了密码证明，
    确保区块一旦被添加到区块链上，就不能被替换或者删除。
    """
    this_index =last_block.index + 1
    this_timestamp =date.datetime.now()
    #this_data = "Hey! I'm block " +str(this_index)
    this_hash = last_block.hash
    return Block(this_index, this_timestamp, this_data, this_hash)


def create_block_chain(transactions):
    """
    创建一个实际的区块链例子并打印出来
    """
    # Create the blockchain and add the genesis block
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]
    # How many blocks should we add to the chain after the genesis block
    num_of_blocks_to_add= len(transactions)
    # Add blocks to the chain
    for i in range(0, num_of_blocks_to_add):
        block_to_add= next_block(previous_block,transactions[i])
        blockchain.append(block_to_add)
        previous_block = block_to_add
        # Tell everyone about it!
        print ("#{}区块已加入区块链!".format(block_to_add.index))
        print ("上家哈希值:{}".format(block_to_add.previous_hash))
        print ("区块哈希值:{}".format(block_to_add.hash))
        print ("本区块内容:{}".format(block_to_add.data))
        print ("本块时间戳:{}\n".format(block_to_add.timestamp))
    
    return blockchain

if __name__=='__main__':
    transactions=["交易1：开户","交易2：存款1万元","交易3：取款5千元"]
    blockchain=create_block_chain(transactions)


def append_block_chain(blockchain,transactions):
    """
    增加区块至现有的一个区块链
    """
    l = len(blockchain)
    previous_block = blockchain[l-1]
    # How many blocks should we add to the chain after the genesis block
    num_of_blocks_to_add= len(transactions)
    # Add blocks to the chain
    for i in range(0, num_of_blocks_to_add):
        block_to_add= next_block(previous_block,transactions[i])
        blockchain.append(block_to_add)
        previous_block = block_to_add
        # Tell everyone about it!
        print ("#{}区块已加入区块链!".format(block_to_add.index))
        print ("上家哈希值:{}".format(block_to_add.previous_hash))
        print ("区块哈希值:{}".format(block_to_add.hash))
        print ("本区块内容:{}".format(block_to_add.data))
        print ("本块时间戳:{}\n".format(block_to_add.timestamp))
    
    return blockchain

if __name__=='__main__':
    transactions2=["交易A：转账3千元","交易B：取款1千元"]
    blockchain=append_block_chain(blockchain,transactions2)


def search_block_chain(blockchain,word):
    """
    搜索一个区块链的数据内容
    """
    found=0
    # 遍历整个区块链
    for i in range(0, len(blockchain)):
        data=blockchain[i].data
        if data.find(word) != -1:
            found=found+1
            print ("找到区块#{}".format(blockchain[i].index))
            #print ("上家哈希值:{}".format(blockchain[i].previous_hash))
            #print ("区块哈希值:{}".format(blockchain[i].hash))
            print ("本区块内容:{}".format(blockchain[i].data))
            print ("本块时间戳:{}\n".format(blockchain[i].timestamp))
    if found == 0: print("抱歉，区块链中未能找到搜索关键字："+word)
    else: print("共找到"+str(found)+"个区块含有搜索关键字："+word) 
    
    return

if __name__=='__main__':
    search_block_chain(blockchain,"万元")
