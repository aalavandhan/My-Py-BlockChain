import sys, requests, json, flask, random
from uuid        import uuid4
from flask       import Flask, request
from blockchain  import Blockchain
from transaction import Transaction

NETWORK_PATH = "http://localhost:9999"

class MinerNode(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.id = str(uuid4()).replace('-', '')
    self.nodes = set()
    self.address = "http://{0}:{1}".format(host, port)

    self.app = Flask(__name__)

  def run(self):
    self.app.add_url_rule('/chain', 'full_chain', self.full_chain, methods=['GET'])
    self.app.add_url_rule('/chain', 'update_chain', self.update_chain, methods=['PUT'])
    self.app.add_url_rule('/transactions', 'ledger', self.ledger, methods=['GET'])
    self.app.add_url_rule('/transactions/balance', 'balance', self.balance, methods=['GET'])
    self.app.add_url_rule('/transactions/new', 'new_transaction', self.new_transaction, methods=['POST'])

    try:
      self.app.run(host=self.host, port=self.port, threaded=True)
    finally:
      self.__del__()
    
  def __json(self, data, msg):
    print(msg)
    response = self.app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
    return response

  def __error(self, msg):
    print(msg)
    error_msg = json.dumps({ "error" : msg })
    response = self.app.response_class(response=error_msg, status=500, mimetype='application/json')
    return response

  def mine(self):
    block = self.blockchain.new_block( Transaction.mining_reward(self.id) )
    return block
      
  def full_chain(self):
    return self.__json(self.blockchain.to_hash(), "FULL CHAIN RETURNED")

  def ledger(self):
    transactions = map(lambda b: b.transaction.to_hash(), self.blockchain)
    return self.__json(transactions, "RETURNED ALL TRANSACTIONS")

  def balance(self):
    balances = list(Transaction.balance(self.blockchain))
    return self.__json(balances, "RETURNED ALL TRANSACTIONS")

  def new_transaction(self):
    transaction = Transaction(request.form["sender"], request.form["recipient"], request.form["amount"])
    block = self.blockchain.new_block( transaction )

    if block and self.mine() and Blockchain.valid(self.blockchain):
      ch = json.dumps(self.blockchain.to_hash())
      requests.put(NETWORK_PATH + "/chain", data={ "chain": ch, "publisher": self.id })
      return self.__json( block.to_hash(), msg="TRANSACTION PROCESSED, UPDATING CHAIN" )
    else: 
      return self.__error(msg="TRANSACTION FAILED : {0}".format(str(transaction.to_hash())))

  def register(self):
    # Get a random chain  and Instantiate the Blockchain
    self.blockchain = Blockchain(chain=self.get_random_chain())
    requests.post(NETWORK_PATH + "/nodes/register", data={ "id": self.id, "address": self.address })

  def __del__(self):
    requests.delete(NETWORK_PATH + "/nodes/unregister", data={ "id": self.id })
  
  def get_random_chain(self):
    response = requests.get(NETWORK_PATH + "/nodes")
    node_addresses = json.loads(response.text)

    if len(node_addresses) == 0:
      return [ ]

    random.shuffle(node_addresses)
    address = node_addresses[0]
    response = requests.get(address + "/chain")
    return json.loads(response.text)

  # conflict resolution
  def update_chain(self):
    chain        = json.loads(request.form["chain"])
    blockchain   = Blockchain(chain)
    publisher    = request.form["publisher"]

    if publisher == self.id:
      return self.__error(msg="CHAIN: Loop back")

    if not Blockchain.valid(blockchain):
      import pdb; pdb.set_trace()
      return self.__error(msg="CHAIN: Invalid")

    self.blockchain.resolve_conflicts([ blockchain ])
    return self.__json(self.blockchain.to_hash(), "CHAIN: UPDATED")


if __name__ == '__main__':
  node = MinerNode(host=sys.argv[1], port=sys.argv[2])
  node.register()
  node.run()