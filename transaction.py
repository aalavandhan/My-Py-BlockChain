EARTH = "EARTH"

class Transaction(object):
  def __init__(self, sender, recipient, amount):
    self.sender = sender
    self.recipient = recipient
    self.amount = float(amount)

  def to_hash(self):
    return {
      "sender"    : self.sender,
      "recipient" : self.recipient,
      "amount"    : self.amount,
    }

  @classmethod
  def genesis_transaction(self):
    return Transaction(EARTH, "satoshi", 100000)

  @classmethod
  def mining_reward(self, id):
    return Transaction(EARTH, id, 100)

  @classmethod
  def amountOwnedBy(self, person, blockchain):
    total = 0
    for block in blockchain:
      if person == block.transaction.recipient:
        total = total + block.transaction.amount
      if person == block.transaction.sender:
        total = total - block.transaction.amount
    return total

  @classmethod
  def balance(self, blockchain):
    for p in blockchain.chain_users():
      yield (p, self.amountOwnedBy(p, blockchain))

  @classmethod
  def valid(self, transaction, blockchain):
    return (transaction.sender == EARTH) or self.amountOwnedBy(transaction.sender, blockchain) >= transaction.amount