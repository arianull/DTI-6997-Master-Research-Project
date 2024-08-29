import os
import pandas as pd
import datetime
import argparse
from loguru import logger
import dash
from dash import html
from dash import dash_table



def load_latest_screener(input_path: str):
    files = os.listdir(input_path)
    csv_files = [file for file in files if file.endswith('.csv')]
    if not csv_files:
        logger.error("No CSV files found in the provided path.")
        return pd.DataFrame()
    latest_file = max(csv_files, key=lambda x: int(x.split('_')[2].split('.')[0]))
    file_path = os.path.join(input_path, latest_file)
    df = pd.read_csv(file_path, index_col='No.')
    logger.success(f'Latest screener download file {latest_file} loaded.')
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shows result in a dashboard.")
    parser.add_argument("--input-path", required=False, default="data/inference/out/result", help="Path to the model output.")
    args = parser.parse_args()

    app = dash.Dash()

    result_df = load_latest_screener(args.input_path)

    app.layout = html.Div(
        style={'font-family': 'Arial, sans-serif', 'margin': '50px'},
        children=[
            html.H1('Screener Dashboard', style={'text-align': 'center', 'margin-bottom': '30px'}),
            dash_table.DataTable(
                id='table',
                columns=[{'name': col, 'id': col} for col in result_df.columns],
                data=result_df.to_dict('records'),
                style_table={'width': '100%', 'margin-bottom': '30px'},
                style_header={'background-color': '#f2f2f2', 'font-weight': 'bold'},
                style_cell={'padding': '10px', 'text-align': 'left'},
                style_data={'whiteSpace': 'normal', 'height': 'auto'}
            )
        ]
    )

    app.run_server()