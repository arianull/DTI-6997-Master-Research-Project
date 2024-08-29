inference-finviz-mock:
	python3 finviz_scrapper.py --username "abc@abc.abc" --password "---"
	python3 screener_formula.py
	python3 latest_news_embedding.py --mock
	python3 sentiment_inference.py --model "mock_wrapper"

inference-finviz-generate:
	python3 finviz_scrapper.py --username "abc@abc.abc" --password "---"
	python3 screener_formula.py
	python3 latest_news_embedding.py
	python3 sentiment_inference.py

dashboard-mock: inference-finviz-mock
	python3 dashboard.py

dashboard-generate: inference-finviz-generate
	python3 dashboard.py