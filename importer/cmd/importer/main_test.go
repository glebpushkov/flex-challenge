package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"importer/internal"
)

const TEST_CSV_FILE_PATH string = "../../test_artifacts/test_upload.csv"

// Each test have to use own instance, not thread-safe
type MockedRoundTripper struct {
	wg            *sync.WaitGroup
	roundTripMock func(*http.Request) (*http.Response, error)
}

func (mrt *MockedRoundTripper) RoundTrip(r *http.Request) (*http.Response, error) {
	mrt.wg.Done()
	if mrt.roundTripMock != nil {
		return mrt.roundTripMock(r)
	}
	return nil, nil
}

// Test_runWatcher performs end-to-end tests, with no mocks except httpClient to track outgoing requests
func Test_runWatcher(t *testing.T) {
	t.Run("Success upload with skipped rows", func(t *testing.T) {
		// prepare directory to track
		testDirName := "TEMP_" + strings.Split(t.Name(), "/")[1] // name is Test_runWatcher/Success_upload_with_skiped_rows
		err := os.Mkdir(testDirName, 0700)
		require.NoError(t, err)
		defer os.RemoveAll(testDirName)

		// prepare app
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		logger := slog.Default()
		wg := sync.WaitGroup{}
		wg.Add(2) // based on test_upload.csv we expect 2 API calls
		client := http.Client{
			Transport: &MockedRoundTripper{wg: &wg},
			Timeout:   3 * time.Second,
		}
		uploader := internal.NewUpload(logger, "basic", "username", "password", "https://example.com/trades", client)
		uploadManager := internal.NewUploadManager(logger, uploader, 2, internal.ParseFile)
		go runWatcher(ctx, logger, uploadManager, testDirName)

		// start test!
		err = exec.Command("cp", TEST_CSV_FILE_PATH, testDirName+"/epex_trades_20230225.csv").Run()
		require.NoError(t, err)

		wgDoneCh := make(chan struct{})
		go func() {
			wg.Wait()
			close(wgDoneCh)
		}()
		select {
		case <-wgDoneCh:
			// success, nothing to do (but ideally check deeply which data was sent in requests)
		case <-time.After(2 * time.Second):
			t.Errorf("Timeout error, not enough outbound API calls")
		}
	})
	t.Run("File open error", func(t *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		logger := slog.Default()
		client := http.Client{ // not supposed to be called
			Transport: &MockedRoundTripper{},
			Timeout:   3 * time.Second,
		}
		uploader := internal.NewUpload(logger, "basic", "username", "password", "https://example.com/trades", client)
		uploadManager := internal.NewUploadManager(logger, uploader, 2, internal.ParseFile)
		errCode := runWatcher(ctx, logger, uploadManager, "/not/existing/dir/at/all")
		require.Equal(t, 1, errCode)
	})
}
