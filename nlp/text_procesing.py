import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
# nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize, sent_tokenize
# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import re
import pandas as pd

data = pd.read_csv(r"C:\Users\rajesh.narravula\OneDrive - Accenture\Documents\python\nlpl\tripadvisor_hotel_reviews.csv")

data['to_lower'] = data['Review'].str.lower()

en_stopwords = stopwords.words('english')
en_stopwords.remove("not")

data['review_no_stopwords'] = data['to_lower'].apply(lambda x: ' '.join([word for word in x.split() if word not in en_stopwords]))

data['review_no_stopwords_no_punct'] =  data['review_no_stopwords'].str.replace(r"[*]", "star", regex=True)

data['review_no_stopwords_no_punct'] = data.apply(lambda x: re.sub(r"([^\w\s])", "", x['review_no_stopwords_no_punct']), axis=1)

data['tokenized'] = data.apply( lambda x: word_tokenize(x['review_no_stopwords_no_punct']), axis =1)

lemmatizer = WordNetLemmatizer()
data['lemmatized'] = data['tokenized'].apply( lambda tokens: [lemmatizer.lemmatize(token) for token in tokens])

tokens_clean = sum(data['lemmatized'], [])

bigrams = pd.Series(nltk.ngrams(tokens_clean, 2)).value_counts()

print(bigrams)