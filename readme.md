# My-Py-BlockChain

Custom block chain implementation inspired by [Daniel Van Flymen](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46).

[How block chains work?](https://www.youtube.com/watch?v=bBC-nXj3Ng4&t=1283s)

```
# Start the miner network
# This is a communcation stream handling message pub-sub between miners
python miner_network.py 

########################################################################

# Create multiple miners
python miner_node.py localhost 3000 # Miner 1
python miner_node.py localhost 3001 # Miner 2
python miner_node.py localhost 3002 # Miner 3
```

## Transaction
A [genesis block](https://en.bitcoin.it/wiki/Genesis_block) is hard-coded into the code. User 'satoshi' gets 100,000 Coins from the earth. A miner is rewared by 100 Coins on successful addtion of a block to the block chain.

1) Transaction are published to the network of miners
```
curl -XPOST localhost:9999/transactions/new --data "sender=satoshi&recipient=A&amount=10"
curl -XPOST localhost:9999/transactions/new --data "sender=satoshi&recipient=B&amount=20"
curl -XPOST localhost:9999/transactions/new --data "sender=satoshi&recipient=C&amount=30"
```
2) The miners compete to validate the transaction and add it to the block chain. They ensure that a user has sufficient funds to transfer
3) The updated chain is published through the network
4) A node chooses to update it's copy of the block chain through a defined notion of consensus


## Account balances
Over multiple transactions we see that each miner's ledger is synchronized.
```
curl localhost:3000/transactions/balance
curl localhost:3001/transactions/balance
[
    ["A", 10.0],								  # User Coinage
    ["C", 30.0],
    ["B", 20.0],
    ["3d333dea82e748c889fe675ff232ae32", 200.0],  # Miner Coinage 
    ["29e477eb4e6c428abbeebee444de2648", 100.0],  
    ["EARTH", -100300.0], 						  # Total Coinage in the system
    ["satoshi", 99640.0],						  # First user (ICO)
]

```