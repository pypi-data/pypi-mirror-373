import logging
import argparse
import torch
import torch.nn as nn
from torchvision import models
from torchvision import datasets
from torchvision.transforms import ToTensor
from multiprocessing import Process
from pyconlai import ConLArguments, ConLPoCArguments, DSgd, FedDatasetsClassification

formatter = '%(asctime)s [%(name)s] %(levelname)s :  %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)

batch_size = 100
num_rounds = 100

def run_client(args, client_id, train_data_loader, test_data_loader, device="cpu"):
    round_idx = 0

    model = models.resnet18()

    # Preliminary: Optimizer can be anything
    org_optimizer = torch.optim.SGD(filter(lambda p: p.requires_grad, model.parameters()), lr=0.01)
    optimizer = DSgd(args, org_optimizer, model.parameters())

    criterion = nn.CrossEntropyLoss()

    logger = logging.getLogger("ConLAi-Tra%02d" % client_id)
    logger.info("Training Start!!")

    model = model.to(device)

    while round_idx < num_rounds:
        round_idx += 1
        model.train()

        batch_loss = []
        for batch_idx, (x, labels) in enumerate(train_data_loader):
            x, labels = x.to(device), labels.to(device)
            optimizer.zero_grad()
            labels = labels.long()

            log_probs = model(x)
            loss = criterion(log_probs, labels)
            loss.backward()
            batch_loss.append(loss.item())

            optimizer.step()

        model.eval()
        class_correct = list(0. for _ in range(10))
        class_total = list(0. for _ in range(10))
        criterion = nn.CrossEntropyLoss().to(device)

        metrics = {"accuracy": 0., "loss": 0.}
        loss_ary = []
        with torch.no_grad():
            total = 0
            correct = 0
            batch_loss = []
            for batch_idx, (x, target) in enumerate(test_data_loader):
                x = x.to(device)
                target = target.to(device)
                pred = model(x)
                target = target.long()
                loss = criterion(pred, target)

                _, predicted = torch.max(pred, 1)
                c = (predicted == target).squeeze()
                for i in range(4):
                    label = target[i]
                    class_correct[label] += c[i].item()
                    class_total[label] += 1
                total += target.size(0)
                correct += (predicted == target).sum().item()

                batch_loss.append(loss.item())
                loss_ary.append(sum(batch_loss) / len(batch_loss))

            metrics["accuracy"] = correct / total
            metrics["loss"] = sum(loss_ary) / len(loss_ary)

        logger.info("Round= {:4d} \tAcc: {:.6f} \tLoss: {:.6f} \tDiff: {:.8f} \tK: {:2d}".format(
            round_idx, metrics["accuracy"], metrics["loss"], optimizer.diff, optimizer.inner_loop))

        # round update
        optimizer.round_update(metrics)

    # close
    logger.info("Training Finished!!")



def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("config_path", type=str, help="path of config file")
    args = arg_parser.parse_args()

    net_args = ConLArguments.from_yml(args.config_path)
    poc_args = ConLPoCArguments.from_yml(args.config_path)

    train_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=True, download=True, transform=ToTensor())
    valid_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=False, download=True, transform=ToTensor())
    # Split the CIFAR10 dataset for each client
    fed_datasets = FedDatasetsClassification(net_args, poc_args, batch_size,
                                             train_data, valid_data, class_num=10)

    clients = []
    for client_id in range(poc_args.worker_num):
        client = Process(target=run_client, args=(net_args, client_id,
                                                  fed_datasets.fed_dataset(client_id)["train"],
                                                  fed_datasets.fed_dataset(client_id)["valid"],
                                                  "cuda"))
        client.start()
        clients.append(client)

    for client in clients:
        client.join()


if __name__ == "__main__":
    main()
