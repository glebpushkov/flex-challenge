### How to use a cli:

`docker build -t pyreporter .`\
`docker run --rm pyreporter` \
`docker run --rm -v $PWD/epex_trades_good.csv:/app/epex_trades_good.csv pyreporter python main.py epex_trades_good.csv`

### Description

Not much to describe. Just Pandas, and I was consulting with chatGPT to build it. \
Perhaps it could be structured better - steps broken into functions, which would allow unit-test, but due to time reasons decided to stop on a current state
