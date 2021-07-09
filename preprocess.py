from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
from datetime import datetime
import pandas as pd
import re
import pickle

import nltk

nltk.download('stopwords')
mystem = Mystem()
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['лента', 'ассорт', 'разм', 'арт', 'что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на'])

with open('model.pickle', 'rb') as f:
    model_test = pickle.load(f)
    print(model_test)


def create_df_by_dict(receipt_dict):
    print(receipt_dict)
    products_df = pd.DataFrame(receipt_dict['ticket']['document']['receipt']['items'])
    products_len = len(products_df)
    products_df['date'] = datetime.strptime(re.findall(r't=(\w+)', receipt_dict["qr"])[0], '%Y%m%dT%H%M')
    products_df['processed'] = products_df['name'].apply(preprocess_text)
    products_df['fiscal_sign'] = receipt_dict['ticket']['document']['receipt']['fiscalSign'] * products_len
    products_df['fiscal_document_number'] = receipt_dict['ticket']['document']['receipt']['fiscalDocumentNumber']
    products_df['fiscal_drive_number'] = receipt_dict['ticket']['document']['receipt']['fiscalDriveNumber']
    products_df['store_inn'] = receipt_dict['ticket']['document']['receipt']['userInn'] * products_len
    products_df['store_name'] = receipt_dict['ticket']['document']['receipt'].get('user', '-')
    print(products_df['store_name'])
    # products_df['nds10'] = receipt_dict['ticket']['document']['receipt']['nds10']
    prediction = model_test.predict(products_df['processed'])
    products_df['prediction'] = prediction
    return products_df


def get_info_about_receipt(products_df):
    message = f""
    message += f"Магазин: {products_df['store_name'].loc[0]}\n"
    message += f"Число покупок: {len(products_df)}\n"
    message += f"Сумма покупок: {round((products_df['sum'] / 100).sum())}\n"
    message += f"Самая дорогая покупка: {products_df[products_df['sum'] == max(products_df['sum'])].name.iloc[0]}, сумма: {products_df[products_df['sum'] == max(products_df['sum'])]['sum'].iloc[0] / 100}\n"
    return message


def preprocess_text(text):
    text=str(text)
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in russian_stopwords\
              and token != " "\
              and len(token) >= 3\
              and token.strip() not in punctuation\
              and not token.isdigit()]
    text = " ".join(tokens)
    return text
