from textblob import TextBlob
import pandas as pd

df = pd.read_excel('synthetic_reviews.xlsx')

def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

df['Sentiment'] = df['Review_Text'].apply(get_sentiment)
df.to_excel('reviews_with_sentiment.xlsx', index=False)
