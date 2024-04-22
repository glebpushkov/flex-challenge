EXECUTABLE=importer
OUTPUT_DIR=bin
WINDOWS=$(OUTPUT_DIR)/$(EXECUTABLE).exe
LINUX=$(OUTPUT_DIR)/$(EXECUTABLE)_linux
DARWIN=$(OUTPUT_DIR)/$(EXECUTABLE)_darwin
VERSION=?dev

build: windows linux darwin
	@echo version: $(VERSION)

windows: $(WINDOWS)

linux: $(LINUX)

darwin: $(DARWIN)

$(WINDOWS):
	env GOOS=windows GOARCH=amd64 go build -v -o $(WINDOWS) -ldflags="-s -w -X main.version=$(VERSION)"  ./cmd/importer/main.go

$(LINUX):
	env GOOS=linux GOARCH=amd64 go build -v -o $(LINUX) -ldflags="-s -w -X main.version=$(VERSION)"  ./cmd/importer/main.go

$(DARWIN):
	env GOOS=darwin GOARCH=amd64 go build -v -o $(DARWIN) -ldflags="-s -w -X main.version=$(VERSION)"  ./cmd/importer/main.go
