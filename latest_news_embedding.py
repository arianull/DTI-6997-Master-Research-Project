import os
import pandas as pd
import numpy as np
from yahoo_fin import news
from finvizfinance.quote import finvizfinance
from openai import OpenAI
from loguru import logger
import argparse
import datetime


def get_latest_news(ticker: str, source: str = 'yf') -> list:
    """
    Fetches the latest news for a given stock ticker using either the yahoo_fin or finviz library.
    
    :param ticker: The stock ticker symbol.
    :param source: The news source to fetch from. Options are 'yf' for yahoo_fin and 'finviz' for finvizfinance.
                   Default value is 'yf'.
    :return: A list of latest news articles with their titles and URLs.
    """
    news_list = []
    try:
        if source == 'yf':
            logger.info(f'Fetching latest news for {ticker} from Yahoo! Finance')
            news_data = news.get_yf_rss(ticker)
            for article in news_data:
                news_list.append({
                    "ticker": ticker,
                    "title": article["title"],
                    "summary": article["summary"],
                    "url": article["link"],
                    "time": article["published"]
                })
        elif source == 'finviz':
            logger.info(f'Fetching latest news for {ticker} from Finviz')
            news_data = finvizfinance(ticker).ticker_news()
            news_list = []
            for index, row in news_data.iterrows():
                news_list.append({
                    "ticker": ticker,
                    "title": row["Title"],
                    "summary": None,
                    "url": row["Link"],
                    "time": row["Date"]
                })
        else:
            raise ValueError("Invalid news source. Please choose either 'yf' or 'finviz'.")
        
        return news_list

    except Exception as e:
        logger.error(f"An error occurred: {e}")


def get_gpt_embeddings(client, text: str, model: str = "text-embedding-ada-002", mock: bool = False):
    """
    Get embeddings for a given text using OpenAI API.
    
    Args:
        client (object): OpenAI client object.
        text (str): The text to get embeddings for.
        model (str): The embedding model to use (default is "text-embedding-ada-002").
        mock (bool): If True, return a mock embedding with shape of 100 and all 0 values.
    
    Returns:
        list: The embeddings for the given text.
    """
    if mock:
        return [0] * 100
    
    if text:
        text = text.replace("\n", " ")
        try:
            response = client.embeddings.create(
                input=[text],
                model=model
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None
    else:
        return None


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


def main():
    parser = argparse.ArgumentParser(description="Fetch latest news data from Yahoo Finance or Finviz and generate embeddings.")
    parser.add_argument("--input-path", required=False, default="data/inference/in/screener", help="Path to the screener output.")
    parser.add_argument("--output-path", required=False, default="data/inference/in/news", help="Path to the news embedding output.")
    parser.add_argument("--news-source", required=False, default="yf", help="Source of the news. 'yf' or 'finviz'")
    parser.add_argument("--embedding-key", required=False, default="last_summary", help="Choosing what to create embedding. Finviz source does not have summary. Options: last_summary, last_title, latest_title_concat, latest_summary_concat")
    parser.add_argument("--model", required=False, default="text-embedding-ada-002", help="GPT embedding model.")
    parser.add_argument("--mock", action="store_true", help="To run the script without calling OpenAI while testing.")
    args = parser.parse_args()

    logger.info('Loading latest screener downloaded file...')
    screener_df = load_latest_screener(args.input_path)


    logger.info('News module running...')
    screener_df['latest_news_list'] = screener_df['Ticker'].apply(lambda x: get_latest_news(x, source=args.news_source))
    screener_df['last_news_title'] = screener_df['latest_news_list'].apply(lambda x: x[0]['title'] if x else None)
    screener_df['last_news_summary'] = screener_df['latest_news_list'].apply(lambda x: x[0]['title'] if x else None)
    screener_df['last_news_time'] = screener_df['latest_news_list'].apply(lambda x: x[0]['title'] if x else None)
    screener_df['latest_news_title_concat'] = screener_df['latest_news_list'].apply(lambda x: ' - '.join([news['summary'] for news in x]))
    screener_df['latest_news_summary_concat'] = screener_df['latest_news_list'].apply(lambda x: ' - '.join([news['summary'] for news in x]))

    embedding_key = args.embedding_key

    if args.mock == False:
        client = OpenAI()
        logger.success("OpenAI client connected")
        logger.info(f'Generating embeddings for {embedding_key} using {args.model} from OpenAI')
    else:
        client = None

    
    if embedding_key == "last_summary":
        if args.news_source == 'finviz':
            logger.error('Finviz does not support news summary.')
        else:
            screener_df['last_summary_embedding'] = screener_df['last_news_summary'].apply(lambda x: get_gpt_embeddings(client, x, model=args.model, mock=args.mock))
    elif embedding_key == "last_title":
        screener_df['last_title_embedding'] = screener_df['last_news_title'].apply(lambda x: get_gpt_embeddings(clent, x, model=args.model, mock=args.mock))
    elif embedding_key == "latest_title_concat":
        screener_df['latest_title_concat_embedding'] = screener_df['latest_news_title_concat'].apply(lambda x: get_gpt_embeddings(client, x, model=args.model, mock=args.mock))
    elif embedding_key == "latest_summary_concat":
        if args.news_source == 'finviz':
            logger.error('Finviz does not support news summary.')
        else:
            screener_df['latest_summary_concat_embedding'] = screener_df['latest_news_summary_concat'].apply(lambda x: get_gpt_embeddings(client, model=args.model, mock=args.mock))
    else:
        logger.error("Invalid embedding key. Please choose one of: last_summary, last_title, latest_title_concat, latest_summary_concat")

    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"screener_embeddings_{current_time}.csv"
    file_path = os.path.join(args.output_path, file_name)
    screener_df.to_csv(file_path)
    logger.success(f'Screener with news and embeddings saved in {file_path}')
    

if __name__ == "__main__":
    main()