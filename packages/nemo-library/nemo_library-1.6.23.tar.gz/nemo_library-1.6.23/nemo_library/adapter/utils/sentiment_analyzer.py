from collections import defaultdict
import json
from pathlib import Path
import time

from bs4 import BeautifulSoup
from prefect import get_run_logger
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from nemo_library.adapter.gedys.gedys_object_type import GedysObjectType
from nemo_library.adapter.utils.recursive_json_flattener import RecursiveJsonFlattener
from nemo_library.core import NemoLibrary
import pandas as pd


class SentimentAnalyzer:

    def __init__(self):

        self.logger = get_run_logger()

        super().__init__()

    def analyze_sentiment(
        self, data: dict, sentiment_analysis_fields: list[str] | None
    ) -> dict:
        """
        Analyze the sentiment of the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: The sentiment of the text ('positive', 'negative', or 'neutral').
        """

        if not sentiment_analysis_fields:
            self.logger.warning(
                "No sentiment analysis fields provided. Skipping sentiment analysis."
            )
            return data

        model_name = "oliverguhr/german-sentiment-bert"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

        # Perform sentiment analysis
        start_time = time.time()
        total = len(data)
        idx = 0

        for element in data:
            idx += 1
            for field in sentiment_analysis_fields:

                # sometimes, a record does not have the field we want to analyze
                if field not in element:
                    continue

                html = element.get(field, {}).get("Value")
                if html:
                    # Extract plain text from HTML
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)
                    if text:
                        element[f"plain_html_{field.lower()}"] = text[
                            :512
                        ]  # Limit to 512 characters for storage in the database
                        # sentiment_analysis has a max length of 512 tokens
                        # so we split the text into chunks of 512 characters and peform sentiment analysis on each chunk
                        chunk_size = 512
                        chunks = [
                            text[i : i + chunk_size]
                            for i in range(0, len(text), chunk_size)
                        ]

                        sentiments = nlp(chunks)

                        # Initialize aggregators
                        label_scores = defaultdict(float)
                        label_counts = defaultdict(int)

                        # Tally scores and counts
                        for s in sentiments:
                            label = s["label"]
                            label_scores[label] += s["score"]
                            label_counts[label] += 1

                        # Compute average scores per label
                        average_scores = {
                            label: label_scores[label] / label_counts[label]
                            for label in label_scores
                        }

                        # Determine the most confident label
                        dominant_label = max(average_scores.items(), key=lambda x: x[1])

                        element[f"sentiment_field_{field.lower()}"] = {
                            "label": dominant_label[0],
                            "score": dominant_label[1],
                            "distribution": average_scores,  # optional: gives insights into all labels
                            "counts": label_counts,  # optional: how many chunks had each label
                        }

                        # remove original field
                        element.pop(field, None)

            if idx % 100 == 0 or idx == total:
                elapsed = time.time() - start_time
                percent = idx / total
                eta = (elapsed / idx) * (total - idx)

                self.logger.info(
                    f"[sentiment analysis] Processed {idx:,}/{total:,} "
                    f"({percent:.2%}) - ETA: {eta/60:.1f} min"
                )

        return data
