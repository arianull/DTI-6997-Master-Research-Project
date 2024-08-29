# DTI-6997-Master-Research-Project

## Overview
This repository contains the code for a research project that involves designing and implementing a software tool for stock market news analysis and screening. The project utilizes a large language model-based approach to analize based on news embeddings.

## Data
The collected data for this project is not uploaded to this repository due to its size and privacy considerations. However, the models trained on this data are available in the repository.

### Data Sources
If you need to train the models again, please download the required datasets from the following sources and add them to the corresponding directories in your local setup:

- **Stock News Data**:  
  [Massive stock news analysis DB for NLP/backtests by Enlle, M.](https://www.kaggle.com/datasets/miguelaenlle/massive-stock-news-analysis-db-for-nlpbacktests/data?select=raw_partner_headlines.csv)  
  Place the downloaded data in the `data/news` directory.

- **Stock Prices Data**:  
  [World stock prices: Daily updating by Withana, N.](https://www.kaggle.com/datasets/nelgiriyewithana/world-stock-prices-daily-updating/data)  
  Place the downloaded data in the `data/prices` directory.

## Usage

### Environment Setup
To install the required libraries, run the following command:

```bash
pip install -r requirements.txt
```

### Configuration
Before running the code, you need to set the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key for processing requests.
- Finviz account credentials (username and password) should be set in your environment or configuration file used by the makefile.

### Running the Code
To execute the inference software, use the provided makefile. An example command to generate the dashboard end-to-end is:

```bash
make dashboard-generate
```