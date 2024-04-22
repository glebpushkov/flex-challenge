package internal

type Trade struct {
	ID            string `json:"id" validate:"required"`
	Price         int    `json:"price" validate:"required"`
	Quantity      int    `json:"quantity" validate:"required,gte=0"`
	Direction     string `json:"direction" validate:"oneof=buy sell"`
	DeliveryDay   string `json:"delivery_day" validate:"required"` // todo: we could also validate date/datetime format
	DeliveryHour  int    `json:"delivery_hour" validate:"required,gte=0,lte=23"`
	TraderId      string `json:"trader_id" validate:"required"`
	ExecutionTime string `json:"execution_time" validate:"required"`
}
