### How to use a cli:

`docker build -t pyreporter .`\
`docker run --rm pyreporter` \
`docker run --rm -v $PWD/epex_trades_good.csv:/app/epex_trades_good.csv pyreporter python main.py epex_trades_good.csv`

### Description

Not much to describe. Just Pandas, and was consulting with chatGPT to build it 
Initially tried with go & https://github.com/go-gota/gota, just to be able to ship a nice binary,
but it was a horrible experience comparing to smooth and easy-to-use/iterate pandas. 

Perhaps it could be structured better - steps broken to functions, which would allow to unit-test, but due to time reasons decided to stop on a current state
