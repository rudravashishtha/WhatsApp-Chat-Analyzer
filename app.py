import streamlit as st
import preprocessor
import matplotlib.pyplot as plt
import seaborn as sns


from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract_url = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetching number of messages
    num_messages = df.shape[0]

    # Fetching number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract_url.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'user': 'Name', 'count': 'Percent'})

    return x, df


def create_word_cloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp_df = df[df['message'] != '<Media omitted>\n']
    temp_df = temp_df[temp_df['message'] != 'You deleted this message\n']
    temp_df = temp_df[temp_df['message'] != 'This message was deleted\n']
    temp_df = temp_df[temp_df['user'] != 'group_notification\n']

    def remove_stop_words(message):
        words = []
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
        return " ".join(words)

    wc = WordCloud(width=500, height=250, min_font_size=10, background_color='white')
    temp_df['message'] = temp_df['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp_df['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp_df = df[df['message'] != '<Media omitted>\n']
    temp_df = temp_df[temp_df['message'] != 'You deleted this message\n']
    temp_df = temp_df[temp_df['message'] != 'This message was deleted\n']
    temp_df = temp_df[temp_df['user'] != 'group_notification\n']

    words = []
    for message in temp_df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_words_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_words_df


def emoji_counter(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeliner(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count().reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeliner(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


st.set_page_config(
    page_title="Whatsapp Chat Analysis",
    page_icon="👀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.sidebar.title("Whatsapp Chat Analyzer")
st.title("Whatsapp Chat Analysis Project")
st.divider()
# st.markdown("Made with :heart: by Rudra Vashishtha")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    try:
        user_list.remove('group_notification')
    except ValueError:
        link = "https://faq.whatsapp.com/1180414079177245/"
        st.title(f"Please, input a valid file!")
        st.link_button(url=link, label=":orange[Visit for more] :cyclone:")

    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox("Show analysis with respect to:", user_list)

    if st.sidebar.button("Show Analysis"):
        st.header(f"Analysing {selected_user}")
        st.markdown("""<style>.font {font-size:30px !important;}</style>""", unsafe_allow_html=True)

        num_messages, words, num_media_messages, num_links = fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Total Messages")
            st.markdown(f'<p class="font">{num_messages}</p>', unsafe_allow_html=True)

        with col2:
            st.subheader("Total Words")
            st.markdown(f'<p class="font">{words}</p>', unsafe_allow_html=True)

        with col3:
            st.subheader("Media Shared")
            st.markdown(f'<p class="font">{num_media_messages}</p>', unsafe_allow_html=True)

        with col4:
            st.subheader("Links Shared")
            st.markdown(f'<p class="font">{num_links}</p>', unsafe_allow_html=True)

        # Monthly Timeline
        st.divider()
        st.subheader("Monthly Timeline")
        monthly_timeline = monthly_timeliner(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.divider()
        st.subheader("Daily Timeline")
        daily_timeline = daily_timeliner(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='orange')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.divider()
        st.subheader("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Most busy day")
            busy_day = week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='pink')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.write("Most busy month")
            busy_month = month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Activity Heatmap
        st.divider()
        st.subheader("Activity Heatmap")
        user_heatmap = activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Finding the busiest person in the chat (Group Level)
        if selected_user == 'Overall':
            st.divider()
            st.subheader("Most Busy Users")
            x, new_df = most_busy_user(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            # remove row which contains group_notifications as user
            new_df = new_df[df['user'] == 'group_notification']

            with col1:
                ax.bar(x.index, x.values, color='brown')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df, use_container_width=True)

        # WordCloud
        st.divider()
        st.subheader(f"Wordcloud: {selected_user}")
        df_wc = create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        st.divider()
        st.subheader(f"Most common words: {selected_user}")
        most_common_words_df = most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.barh(most_common_words_df[0], most_common_words_df[1], color="purple")
        st.pyplot(fig)

        # Emoji Analysis
        st.divider()
        st.subheader(f"Most common emojis: {selected_user}")
        emoji_df = emoji_counter(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, use_container_width=True)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            # ax.bar(emoji_df[0].head(), emoji_df[1].head(), color="purple")
            st.pyplot(fig)
