import json, hashlib, time
from transaction import Transaction
from block       import Block
from urlparse import urlparse
import requests

class Blockchain(object):
  def __init__(self, chain=[]):
    self.chain = [ ]
    if len(chain) == 0:
      self.new_block(Transaction.genesis_transaction())
    else:
      for block in chain:
        t = block['transaction']
        transaction = Transaction(t["sender"], t["recipient"], t["amount"])
        b = Block(transaction, block["proof"], block["previous_hash"], block["index"], block["timestamp"])
        self.chain.append(b)

  def resolve_conflicts(self, conflicting_chains):
    new_chain = None
    max_length = len(self.chain)

    for blockchain in conflicting_chains:
      chain = blockchain.chain
      if len(chain) > max_length and Blockchain.valid(blockchain):
        max_length = len(chain)
        new_chain = chain

    if new_chain:
      self.chain = new_chain

    return self.chain

      
  def new_block(self, transaction):
    if len(self.chain) == 0: #genesis_transaction
      previous_hash = proof = int(round(time.time() * 1000))
      block = Block(transaction, previous_hash, proof)
    else:
      proof = Blockchain.proof_of_work(self.last_block().proof)
      previous_hash = Blockchain.hash(self)
      if not Transaction.valid(transaction, self):
        return False
      block = Block(transaction, proof, previous_hash)

    self.chain.append(block)
    print("CHAIN APPENDED : {0}".format(len(self.chain)))

    return block

  def last_block(self):
    return self.chain[-1]

  def chain_users(self):
    users = [ ]
    for c in self:
      users.append(c.transaction.sender)
      users.append(c.transaction.recipient)
    return set(users)

  def to_hash(self):
    return map(lambda b: b.to_hash(), self)

  def __iter__(self):
    for c in self.chain:
      yield c

  @classmethod
  def valid(self, blockchain):
    chain      = blockchain.chain
    last_block = chain[0]
    for c in range(1, len(chain)):
      subchain = map(lambda b: b.to_hash(), chain[0:c])

      if chain[c].previous_hash != Blockchain.hashStr( subchain ):
        return False
      
      if not self.valid_proof(last_block.proof, chain[c].proof):
        return False

      last_block = chain[c]
    return True

  @classmethod
  def valid_proof(self, last_proof, proof):
    guess = str(last_proof) + str(proof)
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

  @classmethod
  def hash(self, chain):
    block_string = json.dumps(chain.to_hash(), sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  @classmethod
  def hashStr(self, chain):
    block_string = json.dumps(chain, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  @classmethod
  def proof_of_work(self, last_proof):
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
      proof += 1
    return proof
  
  