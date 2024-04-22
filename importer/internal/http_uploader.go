package internal

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"sync"
)

type httpUploader struct {
	logger       *slog.Logger
	authType     string
	authUsername string
	authPassword string
	url          string
	client       http.Client
}

func NewUpload(
	logger *slog.Logger,
	authType string,
	authUsername string,
	authPassword string,
	url string,
	client http.Client,
) *httpUploader {
	return &httpUploader{
		logger:       logger,
		authType:     authType,
		authUsername: authUsername,
		authPassword: authPassword,
		url:          url,
		client:       client,
	}
}

// Upload takes care about creating and sending http requests to the Trades server.
// Supports non-auth and basic-auth POST requests.
func (u *httpUploader) Upload(ctx context.Context, tradesCh <-chan Trade, wg *sync.WaitGroup) {
	defer wg.Done()

	for trade := range tradesCh {
		slog.Info(fmt.Sprintf("Uploading %s", trade.ID))

		body, err := json.Marshal(trade)
		if err != nil {
			u.logger.Warn("Can't create json body, skipping", slog.Any("trade", trade))
			continue
		}

		req, err := http.NewRequestWithContext(ctx, http.MethodPost, u.url, bytes.NewBuffer(body))
		if err != nil {
			u.logger.Warn("Can't create a request, skipping", slog.Any("trade", trade))
			continue
		}

		if u.authType == "basic" {
			authCreds := u.prepareBasicAuthCreds(u.authUsername, u.authPassword)
			req.Header.Add("Authorization", "Basic "+authCreds)
		}

		resp, err := u.client.Do(req)
		if err != nil {
			u.logger.Warn("Failed to send http request, skipping", slog.Any("trade", trade), slog.Any("error", err))
			continue
		}

		if resp.StatusCode != http.StatusOK {
			respBody, err := io.ReadAll(resp.Body)
			if err != nil {
				u.logger.Warn(
					"Can't create Trade. Failed to read response body, skipping",
					slog.Any("trade", trade),
					slog.Int("statusCode", resp.StatusCode),
				)
				continue
			}
			resp.Body.Close()
			u.logger.Warn(
				"Can't create Trade",
				slog.Any("trade", trade),
				slog.String("responseBody", string(respBody)),
				slog.Int("statusCode", resp.StatusCode),
			)
		}
	}
}

func (u *httpUploader) prepareBasicAuthCreds(username string, password string) string {
	auth := username + ":" + password
	return base64.StdEncoding.EncodeToString([]byte(auth))
}
