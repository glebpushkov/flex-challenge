### How to start the app:

Download binary, place in the directory which you want to watch, launch it \
`./importer_darwin`

alternatively, provide directory as a flag
'./importer_darwin --path=/abs/path/to/directory'

check all flags `./importer_darwin -h`

To build win + linux + mac binaries: `make build VERSION=v0.0.1`

### Description
Despite in task requirements it's said 'batch importer', in provided openapi schema there is no batch url.

In this case, to make uploading as performant as possible (from importer side), 
idea is to spawn 4-8 goroutines which are listening for a channel, that receives Trades (row by row as they are read from csv).
We limit outbound concurrent requests to not overload api service.

