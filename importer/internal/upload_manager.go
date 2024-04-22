package internal

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
)

type Uploader interface {
	Upload(context.Context, <-chan Trade, *sync.WaitGroup)
}

type UploadManager struct {
	logger        *slog.Logger
	uploader      Uploader
	numWorkers    int
	parseFileFunc func(ctx context.Context, logger *slog.Logger, filename string, tradesCh chan<- Trade) error
}

func NewUploadManager(
	logger *slog.Logger,
	uploader Uploader,
	numWorkers int,
	parseFileFunc func(ctx context.Context, logger *slog.Logger, filename string, tradesCh chan<- Trade) error,
) *UploadManager {
	return &UploadManager{
		logger:        logger,
		uploader:      uploader,
		numWorkers:    numWorkers,
		parseFileFunc: parseFileFunc,
	}
}

// ReadAndUpload reads csv and immediate uploads parsed rows via channel
func (um *UploadManager) ReadAndUpload(ctx context.Context, filename string) error {
	var wg sync.WaitGroup
	tradesCh := make(chan Trade)

	// spawn workers to listen channel
	for range um.numWorkers {
		wg.Add(1)
		go um.uploader.Upload(ctx, tradesCh, &wg)
	}

	// and now we can submit row by row into the channel
	err := ParseFile(ctx, um.logger, filename, tradesCh)
	if err != nil {
		close(tradesCh)
		return fmt.Errorf("failed to parse file %s: %w", filename, err)
	}

	// wait for finish before processing a new file
	wg.Wait()
	return nil
}
