### How to start the app:

Download the binary, place it in the directory which you want to watch, and launch it \
`./importer_darwin`

alternatively, provide a directory as a flag
'./importer_darwin --path=/abs/path/to/directory'

check all flags `./importer_darwin -h`

To build win + linux + mac binaries: `make build VERSION=v0.0.1`

### Description
Despite in task requirements it's said 'batch importer', in the provided openapi schema there is no batch url.

In this case, to make uploading as performant as possible (from the importer side), 
idea is to spawn 4-8 goroutines that are listening for a channel, that receives Trades (row by row as they are read from csv).
We limit outbound concurrent requests to not overload api service.

(The original plan was to use a codegen to generate a client based on a schema, but missed that moment and started polishing a codebase / testing \
, so now it would require some time investments to replace, but I don't feel it's very important do, so just mentioning) 
