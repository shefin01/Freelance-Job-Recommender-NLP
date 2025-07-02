import streamlit as st
import pandas as pd
import numpy as np
import sklearn 
import spacy
import pickle
from sklearn.metrics.pairwise import cosine_similarity

with open(r'C:\Users\mail4\Documents\luminar\ML\Main project\upwork-jobs.csv\upwork.pkl','rb') as obj1:
    dict1 = pickle.load(obj1)

if 'tfidf' not in st.session_state:
    st.session_state['df']=dict1['dataset']
    st.session_state['tfidf'] = dict1['tfidf']
    st.session_state['tfidf_matrix'] = dict1['tfidf_matrix']
lst=list(st.session_state['df']['country'].unique())
nlp = spacy.load('en_core_web_lg')
def clean_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return ' '.join(tokens)

def recommend_filtered_jobs(user_input, country, job_type, tfidf, tfidf_matrix, df, top_n=5):
    # Filter by job type
    if job_type.lower() == 'hourly':
        filtered_df = df[df['is_hourly'] == True]
    elif job_type.lower() == 'fixed':
        filtered_df = df[df['is_hourly'] == False]
    else:
        filtered_df = df.copy()

    # Filter by country
    if country.lower() != 'anywhere':
        filtered_df = filtered_df[filtered_df['country'].str.lower() == country.lower()]

    # Re-vectorize only the filtered jobs
    tfidf_filtered = tfidf.transform(filtered_df['clean_text'])
    
    # Process user input
    user_input_clean = clean_text(user_input)
    user_vec = tfidf.transform([user_input_clean])

    # Cosine similarity
    similarities = cosine_similarity(user_vec, tfidf_filtered).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]

    results = filtered_df.iloc[top_indices][['title', 'description', 'country', 'is_hourly', 'hourly_low', 'hourly_high', 'budget']].copy()

    # Add a new column for pay info
    def pay_info(row):
        if row['is_hourly']:
            return f"Hourly Rate: {row['hourly_low']} - {row['hourly_high']}"
        else:
            return f"Budget: {row['budget']}"

    results['pay'] = results.apply(pay_info, axis=1)

    return results[['title', 'description', 'country', 'pay']]



st.title('Freelance Job Recommendation')
user_input=st.text_input('Job')
country=st.selectbox('Country',lst)
job_type=st.selectbox('Pay type',['Fixed','Hourly'])

button=st.button('Submit')
if button:
    res = recommend_filtered_jobs(
        user_input=user_input,
        country=country,
        job_type=job_type,
        tfidf=st.session_state['tfidf'],
        tfidf_matrix=st.session_state['tfidf_matrix'],
        df=st.session_state['df']
    )

    st.subheader("Recommended Jobs")
    for index, row in res.iterrows():
        st.markdown(f"### {row['title']}")
        st.write(row['description'])
        st.write(f"**Country:** {row['country']}")
        st.write(f"**{row['pay']}**")
        st.markdown("---")
