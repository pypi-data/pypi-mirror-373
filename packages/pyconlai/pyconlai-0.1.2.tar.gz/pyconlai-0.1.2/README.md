# pyConLAi
Client optimizer for use with ConLAi which is ledger type federated learning framework

## What's ConLAi?
Con(sensus)L(erning) Ai is server module for Ledger type federated learning.
Ledger type federated learning achieves federated learning in a way that feels like Git.

![features](https://github.com/rosso-ai/pyConLAi/blob/main/docs/images/conlai_features.png?raw=true)

## How to Install
from PyPi:  
```shell
pip install pyconlai
```

## How to Start
Here is how to run the CIFAR10 example:

#### 1. Server-side execution
This Python module is a client module. The ConLAi service requires the server to be started.  
Docker makes it easy to start a server.

```shell
docker pull ghcr.io/rosso-ai/conlai:latest
docker run -d -p 9200:9200 ghcr.io/rosso-ai/conlai
```

See also the server module README for more information.  
https://github.com/rosso-ai/conlai

#### 2. Client-side execution
Next, start the client side. This sample runs two client nodes in multi-process mode.  

```shell
cd examples/cifar10
python run.py conf/dsgd_cifar10.yml
```

For details, please see [CIFAR10 example README](https://github.com/rosso-ai/pyConLAi/tree/main/examples/cifar10).


## License
This client software is Apache-2.0 license.  

[Server-side software](https://github.com/rosso-ai/conlai) is dual licensed under AGPL-3.0 and commercial license.  
If you would like to use a commercial license, please contact [Rosso inc](https://www.rosso-tokyo.co.jp/contact/).


## Authors
ConLAi is developed by [Rosso inc](https://www.rosso-tokyo.co.jp/).
