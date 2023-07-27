
# AIHELPME

This is a simple core-lightning plugin that, using the L402 (LSAT) standard, that uses AI to help the user in the node administration.

Please remember that it is a draft so __DO NOT USE IT WITH REAL SATS__. Instead, use it in some test environments.


### Load plugin
To load the plugin in an already-running core-lightning node
```
lightning-cli -k plugin subcommand=start plugin=/lightningd/cln-plugins/aihelpme/aihelpme.py endpoint='http://<yourendpoint.some>:<port>/<path>'
```

If you have an endpoint that uses tor, add the option `torproxy=true`.

By default, the plugin will require the user actually to make the payment. If you want the plugin to automatically pay the invoice provided by the endpoint, add the option `pay1shot=true`.

### Usage
```
lightning-cli aihelpme '<question>'
```
If the flag  `pay1shot=true` is not set, the command will ask to pay the L402 invoice by copy/paste a command (`lightning-cli pay402 <invoice>`). After the payment, the response from AI is returned.

There are a lot of improvements to make. Again, this is only a draft, __DO NOT USE WITH REAL SATS__.
