# ConLAi CIFAR10

## How to start
The following command will run one server and two clients and start learning.  

```shell
# Run 
python run.py ./conf/dsgd_cifar10_mobilenet.yaml
```

## Config file and Python script

### Config file
This example uses the following configuration file:
```yaml
# Settings for connecting to the server
net:
  server_url: "localhost:9200"
  repo_name: "cifar10_resnet18"

  # Communication frequency during learning
  inner_loop: 10

# PoC mode settings
poc:
  # Data settings for CIFAR10
  data_cache_dir: "./.data_cache"
  partition_method: "hetero"
  partition_alpha: 100.
  random_seed: 42

  # Number of clients to launch
  worker_num: 2
```

### About run.py
#### 1. Load config
Call the above configuration file using the following steps:
```python
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("config_path", type=str, help="path of config file")
    args = arg_parser.parse_args()

    net_args = ConLArguments.from_yml(args.config_path)
    poc_args = ConLPoCArguments.from_yml(args.config_path)
```

#### 2. Prepare datasets
Splitting the CIFAR10 dataset for a client:
```python
    train_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=True, download=True, transform=ToTensor())
    valid_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=False, download=True, transform=ToTensor())
    # Split the CIFAR10 dataset for each client
    fed_datasets = FedDatasetsClassification(net_args, poc_args, batch_size,
                                             train_data, valid_data, class_num=10)
```

and, run each client in multiple processes.  

#### 3. Optimizer setting
Configure the Optimizer to communicate with the server:
```python
    # Preliminary: Optimizer can be anything
    org_optimizer = torch.optim.SGD(filter(lambda p: p.requires_grad, model.parameters()), lr=0.01)
    optimizer = DSgd(args, org_optimizer, model.parameters())
    # (args = net_args)
```

#### 4. Start Training
Start training using the same procedure as normal PyTorch training.
