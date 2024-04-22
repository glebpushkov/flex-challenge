package main

import (
	"context"
	"flag"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"regexp"
	"syscall"
	"time"

	"github.com/fsnotify/fsnotify"
	"importer/internal"
)

type config struct {
	basicAuthUsername string
	basicAuthPassword string
	tradesCreateUrl   string
	requestTimeout    time.Duration
	numberOfWorkers   int
}

func getConfig() config {
	// could be pulled from env, but hardcoding defaults for now
	return config{
		basicAuthUsername: "webapi",
		basicAuthPassword: "secret",
		tradesCreateUrl:   "http://localhost:8000/trades",
		requestTimeout:    3 * time.Second,
		numberOfWorkers:   4,
	}
}

func main() {
	var path string
	var url string
	var workers int
	flag.StringVar(&path, "path", ".", "path to directory to watch. By default, a current directory will be observed")
	flag.StringVar(&url, "url", "", "url which will be used along with POST request to create Trades")
	flag.IntVar(&workers, "workers", 0, "number of goroutines which also define number of outbound parallel requests")
	flag.Parse()

	cfg := getConfig()
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	httpClient := http.Client{Timeout: cfg.requestTimeout}

	if url == "" {
		url = cfg.tradesCreateUrl
	}
	if workers < 0 || workers > 16 {
		logger.Warn(
			"invalid parallel workers number. Going to use default",
			slog.Int("workers", workers),
			slog.Int("default", cfg.numberOfWorkers),
		)
		workers = 0
	}
	if workers == 0 {
		workers = cfg.numberOfWorkers
	}

	uploader := internal.NewUpload(logger, "basic", cfg.basicAuthUsername, cfg.basicAuthPassword, url, httpClient)
	uploadManager := internal.NewUploadManager(logger, uploader, cfg.numberOfWorkers, internal.ParseFile)
	os.Exit(runWatcher(context.Background(), logger, uploadManager, path))
}

// runWatcher start the loop which waits for fsnotify events in specified directory (`path`).
// If event type and filename pattern satisfy condition -> we trigger parse & upload logic.
func runWatcher(ctx context.Context, logger *slog.Logger, uploadManager *internal.UploadManager, path string) int {
	ctx, cancel := signal.NotifyContext(ctx, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)
	defer cancel()

	// Create a watcher
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		logger.Error("error creating file watcher", slog.Any("error", err))
		return 1
	}
	defer watcher.Close()

	// Start listening for events
	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Has(fsnotify.Create) && verifyFilename(event.Name) {
					logger.Info("Process file", slog.String("file", event.Name))
					err := uploadManager.ReadAndUpload(ctx, event.Name)
					if err != nil {
						logger.Info("Failed to process file", slog.String("file", event.Name), slog.Any("error", err))
					}
					logger.Info("Successfully processed", slog.String("file", event.Name))
					continue
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				logger.Error("unexpected error while waiting for file events", slog.Any("error", err))
			case <-ctx.Done():
				return
			}
		}
	}()

	// Add a path.
	err = watcher.Add(path)
	if err != nil {
		logger.Error("error adding a path to file watcher", slog.Any("error", err), slog.String("path", path))
		return 1
	}

	<-ctx.Done()
	return 0
}

// verifyFilename ensures that file name follows the format epex_trades_NNNNNNNN.csv, where N is any digit 0-9.
// for example, valid name is epex_trades_20230220.csv
func verifyFilename(filename string) bool {
	pattern := `^(.*/)?epex_trades_\d{8}\.csv$`
	match, _ := regexp.MatchString(pattern, filename)
	return match
}
