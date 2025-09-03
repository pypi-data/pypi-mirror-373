===============
 pubtools-sign
===============

Set of scripts used for signing artifacts via configured signers 


Requirements
============

* Python 3.7+

Setup
=====

.. code-block:: bash

  $ pip install -r requirements.txt
  $ pip install . 
  or
  $ python setup.py install

For specific signers you may also need to install some additional dependencies.
Cosign signer requires `cosign` binary to be installed and available in PATH.
MsgSigner requires following python packages to be installed:

- pyOpenSSL
- python-qpid-proton

  note that for ssl support python-qpid-proton must be compiled with ssl support,
  it might be better to install it via system package manager

Supported signers
=================
* Cosign
* MsgSigner

Usage
=====

.. code-block:: bash

  $ pubtools-sign --help
  $ pubtools-sign cosign-container-sign --help
  $ pubtools-sign msg-clear-sign --help
  $ pubtools-sign msg-container-sign --help


Cosign container signing
========================

Cosign container signier sign provided container images and digests with `cosign`.
Example of usage:

.. code-block:: bash

  $ pubtools-sign cosign-container-sign --signing-key signing-key \
      --config-file ~/.config/pubtools-sign/conf.yaml \
      --reference internal-registry/prod/repository:latest \
      --digest sha256:1a452c013d37a60014c5506c4230d5b85686b106f1b7dbd9b93fc44f87a12643 \
      --identity public-registry.com/repository:latest \
      --task-id t-1

Output:

.. code-block:: none

  {"signer_result": {"status": "ok", "error_message": ""},
   "operation_results": ["Pushing signature to: internal-registry/prod/repository:latest\n"],
   "operation": {
      "digests": ["sha256:1a452c013d37a60014c5506c4230d5b85686b106f1b7dbd9b93fc44f87a12643"],
      "references": ["internal-registry/prod/repository:latest"],
      "signing_key": "signing-key",
      "task_id": "t-1"}, 
   "signing_key": "signing-key"}

The command will sign mentioned container image provided by reference and digest with provided key.
Produced signature will be pushed to the same registry as the image. Credentials which are use to 
authenticate to the registry are taken from standard container configuration files (e.i. `~/.docker/config.json`). Identity set in the command will be stored in the signature itself. With that container images can be verified against public registry.

Verification
------------
To verify the signature, adjust container configuration in `/etc/containers/registries.d/registry.yaml` to 
have `use-sigstore-attachments: true`. Example:

.. code-block:: yaml

  docker:
    example-registry.com:
      use-sigstore-attachments: true

Then in `/etc/containers/policy.json` add following policy:

.. code-block:: none

  {
    "default": [
      {
        "type": "insecureAcceptAnything"
      }
    ],
    "transports": {
      "docker": {
        "example-registry.com": [
          {
            "type": "sigstoreSigned",
            "keyPath": "path-to-public-key",
            "signedIdentity": {
              "type": "matchRepoDigestOrExact"
            }
          }
        ]
      }
    }
  }

More info about policy file can be found here:
https://github.com/containers/image/blob/main/docs/containers-policy.json.5.md

Messaging signing
=================
Example of usage:

.. code-block:: bash
  
  $ pubtools-sign-msg-container-sign --digest sha256:123456 \
    --reference registry.com/repository:latest \
    --signing-key signing-key \
    --task-id task-1 \
    --digest sha256:123456

Output:

.. code-block:: none

  {"signer_result": {"status": "ok", "error_message": ""},
   "operation_results": [
      [
        <message>,
        <message-headers>
      ]
  ],
  "operation": {
    "digests": ["sha256:123456"],
    "references": ["registry.com/repository:latest"],
    "signing_key": "signing-key",
    "task_id": "task-1"
  },
  "signing_key": "signing-key"
  }

Messaging signer is used to send requests to signing server via messaging brorker. Every reference + digest is send in separate message with following format:

.. code-block:: none

  {
    "sig_key_id": <signing-key>,
    "request_id": <request-id>,
    "created": <timestamp>,
    "requested_by": <requester-id>,
    "repo": <repository>,
    "data": <base64-encoded-data-to-be-signed>, # in the case of container signing
    "claim-file": <base64-encoded-data-to-be-signed>, # in the case of clear signing
  }


For clearsign signing, data is base64 content you want to sign. For container signing, data is base64 encoded 
json with following structure:

.. code-block:: none

  {
    "critical": {
      "type": "atomic container signature",
      "image": {"docker-manifest-digest": <digest>},
      "identity": {"docker-reference": <reference>},
    },
    "optional": {"creator": "pubtools-sign"},
  }


Messages are sent senquantially to the topic `topic_send_to` specified in the configuration file. After then msg signer listen for response on the queue `topic_listen_to`. Configuration variable `topic_listen_to` can contain following templating variables:
- {creator} - UID from client certificate
- {task_id} - task_id from signing request
When messages are sent, their request_ids are stored in mapping which determines whether reply the to message was received or not. When msg signer receives a message, it uses <message_id_key> attribute from the message to identify messages expected to be received.
Receiving happens in a loop with configured timeout `timeout`. If no message from the expected messages is received within the `tiemout` period, receiving is considered as failed. If any expected message is received, timeout time is reset. On the timeout event, receving is restarted.
If number of receiving retries is bigger then `retries`, the whole process is considered as failed. Process is considered as failed and messages which haven't been received are sent again. This keeps happening until number of attempts to send and received messages is not greater than `send_retries`.

Configuration
=============

Configuration is done via a yaml file. The default location is `~/.config/.pubtools-sign/conf.yaml` or `/etc/pubtools-sign/conf.yaml`. You can also specify a custom location via the `--config` argument. The configuration file is divided into sections, each section is a signer. Each signer has a set of attributes that are used to configure the signer
Conf.yaml has following structure:::

  msg_signer:
    messaging_brokers:
      - <protocol://<host>:<port> for messaging broker
    messaging_cert_key: <path to messaging client key + certificate in PEM format>
    messaging_ca_cert: <path to CA certificate bundle>
    topic_send_to: topic://<topic> - topic where to send signing requests
    topic_listen_to: queue://<queue> - queue where to listen for answers from signing server. Supported templating variables: {creator - UID from client cert}, {task_id}
    environment: <env> - environment attribute which is included in signing request
    service: <service> - service attribute which is included in signing request
    timeout: <int> - timeout for signing request
    retries: <int> - number of retries for receiving signing responses from messaging brokers
    send_retries: <int> - number of retries for whole send + receive cycle
    message_id_key: <id> - attribute in message response used as unique identifier for signing request
    log_level: <level> - log level for pubtools-sign
  cosign_signer:
    rekor_url: <rekor-url>
    upload_tlog: <true|false>
    registry_user: <user> - used to login to registry where images will be signed
    registry_password: <password>
    env_variables:
      <key>: <val> - mapping of environment variables used in signing process. This can be used for example for AWS setup
    key_aliases:
      <alias>: <key> - mapping of key aliases to actual keys. When passing alias as signing key, <key> is used instead. This
                       way you cna define for example "prod-key" alias and have different real keys for different signers
