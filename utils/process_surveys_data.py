import pandas as pd
from utils.process_data import get_continent_name, country_code_to_continent_name
from utils.ga_utils import clean_duplicated_columns

DATA_PATH = 'data/surveys'


def process_and_clean_survey_data():

    # TRAITEMENT DES APPROCHES EN MATIÈRE D'ANXIÉTÉ ET DE DÉPRESSION
    approaches_df = pd.read_csv(f'{DATA_PATH}/dealing-with-anxiety-depression-approaches.csv')
    approaches_df['Continent'] = approaches_df['Code'].apply(country_code_to_continent_name)
    approaches_df.rename(columns={
        'Share - Question: mh8b - Engaged in religious/spiritual activities when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'Engagé dans des activités religieuses ou spirituelles lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8e - Improved healthy lifestyle behaviors when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'Amélioré les comportements de mode de vie sain lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8f - Made a change to work situation when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A fait un changement dans sa situation professionnelle lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8g - Made a change to personal relationships when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A fait un changement dans ses relations personnelles lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8c - Talked to friends or family when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A parlé à des amis ou à sa famille lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8d - Took prescribed medication when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A pris des médicaments prescrits lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8h - Spent time in nature/the outdoors when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A passé du temps dans la nature ou à l\'extérieur lorsqu\'il est anxieux ou déprimé',
        'Share - Question: mh8a - Talked to mental health professional when anxious/depressed - Answer: Yes - Gender: all - Age_group: all': 'A parlé à un professionnel de la santé mentale lorsqu\'il est anxieux ou déprimé'
    }, inplace=True)

    # TRAITEMENT DE L'INCONFORT À PARLER DE L'ANXIÉTÉ ET DE LA DÉPRESSION
    discomfort_df = pd.read_csv(f'{DATA_PATH}/discomfort-speaking-anxiety-depression.csv')
    discomfort_df.rename(columns={
        'Share - Question: mh5 - Someone local comfortable speaking about anxiety/depression with someone they know - Answer: Not at all comfortable - Gender: all - Age_group: all': 'Pas à l\'aise pour parler de l\'anxiété/de la dépression avec des connaissances'
    }, inplace=True)
    discomfort_df['Continent'] = discomfort_df['Code'].apply(country_code_to_continent_name)

    # TRAITEMENT DU FINANCEMENT DE LA RECHERCHE SUR L'ANXIÉTÉ ET LA DÉPRESSION
    fund_df = pd.read_csv(f'{DATA_PATH}/fund-research-anxiety-depression.csv')
    fund_df.rename(columns={
        'Share - Question: mh4b - Important for national government to fund research on anxiety/depression - Answer: Extremely important - Gender: all - Age_group: all': 'Opinion sur le financement par le gouvernement national de la recherche sur l\'anxiété et la dépression comme extrêmement important'
    }, inplace=True)
    fund_df['Continent'] = fund_df['Code'].apply(country_code_to_continent_name)

    fund_df = fund_df.dropna(subset=[
        'Opinion sur le financement par le gouvernement national de la recherche sur l\'anxiété et la dépression comme extrêmement important',
    ])
    fund_df = fund_df.drop(columns=[
        'Population (historical estimates)',
        'GDP per capita, PPP (constant 2017 international $)'
    ])

    return approaches_df, discomfort_df, fund_df


approaches_df, discomfort_df, fund_df = process_and_clean_survey_data()
merged_survey_df = clean_duplicated_columns(approaches_df.merge(discomfort_df, on='Entity', how='inner'))
merged_survey_df = clean_duplicated_columns(merged_survey_df.merge(fund_df, on='Entity', how='inner'))
