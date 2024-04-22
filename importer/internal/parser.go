package internal

import (
	"context"
	"encoding/csv"
	"fmt"
	"io"
	"log/slog"
	"os"
	"strconv"

	"github.com/go-playground/validator/v10"
)

// ParseFile is responsible to:
// - open file
// - validate header
// - start loop for reading & validation rows, submitting valid Trades to channel as soon as they're read
// - close channel at the end to notify goroutine workers that we're done
func ParseFile(ctx context.Context, logger *slog.Logger, filename string, tradesCh chan<- Trade) error {
	file, err := os.Open(filename)
	if err != nil {
		return fmt.Errorf("rrror opening the file: %w", err)
	}
	defer file.Close()

	parser := csv.NewReader(file)

	// Validate headers
	hRow, err := parser.Read()
	if err != nil {
		return fmt.Errorf("error reading headers: %w", err)
	}
	if !isValidHeader(hRow) {
		return fmt.Errorf("invalid headers or headers order") // todo: improve msg with expected headers
	}

	lineNum := 0
loop:
	for {
		select {
		case <-ctx.Done():
			break loop
		default:
			rec, err := parser.Read()
			if err == io.EOF {
				break loop
			}
			if err != nil {
				logger.Warn(fmt.Sprintf("Can't parse line %d", lineNum))
				continue
			}
			if len(rec) < 8 {
				logger.Warn(fmt.Sprintf("Not enough fields to create Trade object"), slog.Any("record", rec))
				continue
			}
			trade, errs := tradeFromRecord(rec)
			if len(errs) > 0 {
				logger.Warn(fmt.Sprintf("Invalid Trade object"), slog.Any("errors", errs))
				continue
			}
			// success! push to channel, now workers can process it
			tradesCh <- trade
			lineNum++
		}
	}
	close(tradesCh)
	return nil
}

// tradeFromRecord tries to convert string values to specific types, and then invokes Trade object struct tags validation
func tradeFromRecord(rec []string) (Trade, []error) {
	var errs []error
	price, err := strconv.Atoi(rec[1])
	if err != nil {
		errs = append(errs, fmt.Errorf("can't parse 'Price' value: %w", err))
	}
	quantity, err := strconv.Atoi(rec[2])
	if err != nil {
		errs = append(errs, fmt.Errorf("can't parse 'Quantity' value: %w", err))
	}
	deliveryHour, err := strconv.Atoi(rec[5])
	if err != nil {
		errs = append(errs, fmt.Errorf("can't parse 'delivery_hour' value: %w", err))
	}
	trade := Trade{
		ID:            rec[0],
		Price:         price,
		Quantity:      quantity,
		Direction:     rec[3],
		DeliveryDay:   rec[4],
		DeliveryHour:  deliveryHour,
		TraderId:      rec[6],
		ExecutionTime: rec[7],
	}

	validate := validator.New(validator.WithRequiredStructEnabled())
	err = validate.Struct(trade)
	if err != nil {
		errs = append(errs, err.(validator.ValidationErrors))
	}
	return trade, errs
}

func isValidHeader(rec []string) bool {
	if len(rec) >= 8 || (rec[0] == "ID" && rec[1] == "Price" && rec[2] != "Quantity" && rec[3] != "Direction" &&
		rec[4] != "delivery_day" && rec[5] != "delivery_hour" && rec[6] != "trader_id" && rec[7] != "execution_time") {
		return true
	}
	return false
}
