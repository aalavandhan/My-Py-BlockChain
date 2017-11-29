import datetime

class Block(object):
  index = 0
  @staticmethod
  def getIndex():
    Block.index = Block.index + 1
    return Block.index

  def __init__(self, transaction, proof, previous_hash, index=None, timestamp=None):
    self.index         = ( index or Block.getIndex() )
    self.timestamp     = ( timestamp or str(datetime.datetime.utcnow()) )
    self.proof         = proof
    self.previous_hash = previous_hash
    self.transaction   = transaction

  def to_hash(self):
    return {
      "transaction"  : self.transaction.to_hash(),
      "index"        : self.index,
      "timestamp"    : self.timestamp,
      "proof"        : self.proof,
      "previous_hash": self.previous_hash,
    }
    