from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    # Exclude group notifications
    df = df[df['user'] != 'group_notification']
    x = df['user'].value_counts().head()
    percent_df = (
        (df['user'].value_counts() / df.shape[0]) * 100
    ).round(2).rename_axis('name').reset_index(name='percent')

    return x, percent_df


def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r', encoding='utf-8')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'].notna()]  # remove NaN if any

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    temp['clean_message'] = temp['message'].apply(remove_stop_words)

    # Check if there’s any valid text left
    all_text = temp['clean_message'].str.cat(sep=" ").strip()
    if not all_text:
        return None  # no text to generate a word cloud

    # Generate word cloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(all_text)
    return df_wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r', encoding='utf-8')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']
    temp = temp[temp['message'].notna()]

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words and not word.startswith("http"):
                words.append(word)

    # If no words found, return empty DataFrame
    if not words:
        return pd.DataFrame(columns=['word', 'count'])

    # Add column names
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        for c in message:
            if c in emoji.EMOJI_DATA:  # updated for latest emoji lib
                emojis.append(c)

    # If no emojis found, return empty dataframe
    if not emojis:
        return pd.DataFrame(columns=['emoji', 'count'])

    # Add column names explicitly
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['emoji', 'count'])
    return emoji_df
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    user_heatmap = user_heatmap.reindex(sorted(user_heatmap.columns, key=lambda x: int(x.split('-')[0])), axis=1)

    return user_heatmap
