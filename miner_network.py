import sys, flask, random, json, requests
from flask    import Flask, request
from requests_futures.sessions import FuturesSession

app = Flask(__name__)
addresses = { }

def randomized_nodes():
  nodes = addresses.keys()
  random.shuffle(nodes)
  for id in nodes: 
  	yield (id, addresses[id])

def success(message):
  return app.response_class(response=json.dumps({ "status" : message }), status=200, mimetype='application/json')

@app.route('/nodes/register', methods=["POST"])
def register():
  id 	  		      = request.form["id"] 
  address 		    = request.form["address"]
  addresses[ id ] = address
  print("NODE:{0} has come online at {1}".format(id, address))
  return success("NODE Registered")

@app.route('/nodes/unregister', methods=["DELETE"])
def unregister():
  id = request.form["id"]
  del addresses[id]
  print("NODE:{0} offline".format(id))
  return success("NODE offline")

@app.route('/nodes', methods=["GET"])
def list():
  payload = json.dumps(addresses.values())
  return app.response_class(response=payload, status=200, mimetype='application/json')

@app.route('/transactions/new', methods=["POST"])
def new_transaction():
  sender    = request.form["sender"] 
  recipient = request.form["recipient"]
  amount    = request.form["amount"]
  session       = FuturesSession()
  (id, address) = next(randomized_nodes())
  session.post(address + "/transactions/new", data={ "sender": sender, "recipient": recipient, "amount": amount })
  
  return success("TRANSACTION submitted into miner network")

@app.route('/chain', methods=["PUT"])
def update_chain():
  chain     = request.form["chain"]
  publisher = request.form["publisher"]
  session   = FuturesSession()
  
  for (id, address) in randomized_nodes():
    session.put(address + "/chain", data={ "chain": chain, "publisher": publisher });

  return success("PUBLISHING updated chain")

if __name__ == '__main__':
  app.run(host="localhost", port=9999)