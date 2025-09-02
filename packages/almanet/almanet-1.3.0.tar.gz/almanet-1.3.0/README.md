# almanet

Web Messaging Protocol is an open application level protocol that provides two messaging patterns:
- Routed Remote Procedure Calls (RPC)
- Produce & Consume

Almanet uses NSQ to exchange messages between different sessions. [NSQ](https://nsq.io/) is a realtime distributed queue like message broker.

## Installation

Before install NSQD [using this instruction](https://nsq.io/deployment/installing.html).

And run it [(configuration options)](https://nsq.io/components/nsqd.html):
```sh
nsqd --max-msg-timeout=1h
```

Then install [`almanet` PyPI package](https://pypi.org/project/almanet/):
```sh
pip install almanet
```

## Usage

- [How to build microservices?](guide/microservice/README.md)
- [How to call remote procedure?](guide/calling/README.md)
