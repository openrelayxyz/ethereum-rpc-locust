#Do a ton of this
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":64}'

#ER20 balanceOf - We'll need to mix this up
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_call","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0x70a08231000000000000000000000000aa934f0f7dc2f6b1a081839ab8a3b929d092356c"}, "latest"],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#ERC20 totalSupply - We'll want to vary target ERC20 address
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_call","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0x18160ddd"}, "latest"],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#ERC20 allowance(owner, spender) - We'll need to mix this up
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_call","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0xdd62ed3e000000000000000000000000aa934f0f7dc2f6b1a081839ab8a3b929d092356c000000000000000000000000258dd1b12d0e6f3e4010a1c6a80ff231536b1005"}, "latest"],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#ER20 balanceOf - We'll need to mix this up
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0x70a08231000000000000000000000000aa934f0f7dc2f6b1a081839ab8a3b929d092356c"}],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#ERC20 totalSupply - We'll want to vary target ERC20 address
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0x18160ddd"}],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#ERC20 allowance(owner, spender) - We'll need to mix this up
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to": "0xdde19c145c1ee51b48f7a28e8df125da0cc440be", "data": "0xdd62ed3e000000000000000000000000aa934f0f7dc2f6b1a081839ab8a3b929d092356c000000000000000000000000258dd1b12d0e6f3e4010a1c6a80ff231536b1005"}],"id":64}' https://mainnet.ethercattle.openrelay.xyz

#I'll provide a huge list of addresses to vary the address
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0xD224cA0c819e8E97ba0136B3b95ceFf503B79f53", "latest"],"id":64}' https://goerli-rpc.openrelay.xyz
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":64}' https://goerli-rpc.openrelay.xyz

#We'll need to vary the block number
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["0x1b4", true],"id":64}' https://goerli-rpc.openrelay.xyz

#We'll need to vary the block number
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getBlockByHash","params":["0xb0550d9b3033c5bc04407af24af13f943d5636e3674e1e93855219a6fe2ed885", false],"id":64}' https://goerli-rpc.openrelay.xyz

#We'll need to vary the block hash, maybe following the previous request
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByHash","params":["0xb0550d9b3033c5bc04407af24af13f943d5636e3674e1e93855219a6fe2ed885"],"id":64}' https://goerli-rpc.openrelay.xyz

#Vary block number
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByNumber","params":["0x25a99"],"id":64}' https://goerli-rpc.openrelay.xyz

#Change block ranges, get a list of topics
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getLogs","params":[{"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"], "fromBlock": "latest", "toBlock":"latest"}],"id":74}' https://mainnet.ethercattle.openrelay.xyz

#Change block ranges, get a list of topics NOT PROVIDED
# curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getStorage","params":["0xdde19c145c1eE51B48f7a28e8dF125da0Cc440be", "0x0"],"id":74}' https://mainnet.ethercattle.openrelay.xyz

#Vary block hash and index number
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockHashAndIndex","params":["0x324e6083db2899e9a55c77e519a89c76a86ed4edcdf79517c8bf4d1e58793c77", "0x0"],"id":64}' https://goerli-rpc.openrelay.xyz

#Maybe use tx hash from previous request
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["0x723e3c355d6c3a3f2eb36f47df6a1a31b724fb0ca5ce9abc8a584c457554f15b"],"id":64}' https://goerli-rpc.openrelay.xyz

#Maybe use tx hash from previous request
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["0x723e3c355d6c3a3f2eb36f47df6a1a31b724fb0ca5ce9abc8a584c457554f15b"],"id":64}' https://goerli-rpc.openrelay.xyz

#Maybe use tx hash from previous request
curl -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_getTransactionCount","params":["0x2b371c0262CEAb27fAcE32FBB5270dDc6Aa01ba4","latest"],"id":64}' https://goerli-rpc.openrelay.xyz
