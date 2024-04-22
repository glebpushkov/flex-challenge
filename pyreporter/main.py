import argparse
import pandas as pd


col_id = 'id'
col_price = 'price'
col_quantity = 'quantity'
col_direction = 'direction'
col_delivery_day = 'delivery_day'
col_delivery_hour = 'delivery_hour'
col_trader_id = 'trader_id'
col_execution_time = 'execution_time'

col_names = {
    col_id,
    col_price,
    col_quantity,
    col_direction,
    col_delivery_day,
    col_delivery_hour,
    col_trader_id,
    col_execution_time
}

direction_sell = 'sell'
direction_buy = 'buy'


def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print('Error: File not found.')
        return None
    except pd.errors.ParserError:
        print('Error: Failed to parse CSV file')
        return None
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def run(path, trader_id):
    df = load_csv_to_dataframe(path)

    # filter by trader_id if provided
    if trader_id:
        df = df[df['trader_id'] == trader_id]
        if len(df) == 0:
            print(f"No records found for trader_id {trader_id}")

    # convert datetime to hours, to group by hour later. E.g. 2023-02-28T12:20:35Z -> 12
    try:
        df[col_execution_time] = pd.to_datetime(df[col_execution_time])
    except ValueError:
        print("File contains invalid values in 'execution_time' column, aborting")
    df['execution_hour'] = df[col_execution_time].dt.hour.astype(str)

    # group and apply aggregations
    is_sell_col = df[col_direction] == direction_sell
    is_buy_col = df[col_direction] == direction_buy
    total_df = df.groupby('execution_hour').agg(
        records_count=('execution_hour', 'count'),
        total_sell_quantity=(col_quantity, lambda q: q[is_sell_col].sum()),
        total_buy_quantity=(col_quantity, lambda q: q[is_buy_col].sum()),
        sell_pnl=(col_quantity, lambda q: (q * df.loc[q.index, col_price])[is_sell_col].sum()),
        buy_pnl=(col_quantity, lambda q: (q * df.loc[q.index, col_price])[is_buy_col].sum())
    )
    total_df['pnl'] = total_df['buy_pnl'] - total_df['sell_pnl']

    # output results
    print(total_df)
    total_df.sort_values(by='execution_hour')
    print(total_df)


def main():
    parser = argparse.ArgumentParser(description='Cli to build a report based on daily CSV file with exported trades')
    parser.add_argument('path', type=str, help='Path to the CSV file to load.')
    parser.add_argument('--trader_id', type=str, default='', help='Trader id')
    args = parser.parse_args()
    run(args.path, args.trader_id)


if __name__ == '__main__':
    main()
