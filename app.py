import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

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

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
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
        monthly_timeline = helper.monthly_timeliner(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.divider()
        st.subheader("Daily Timeline")
        daily_timeline = helper.daily_timeliner(selected_user, df)
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
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='pink')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.write("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Activity Heatmap
        st.divider()
        st.subheader("Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Finding the busiest person in the chat (Group Level)
        if selected_user == 'Overall':
            st.divider()
            st.subheader("Most Busy Users")
            x, new_df = helper.most_busy_user(df)
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
        df_wc = helper.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        st.divider()
        st.subheader(f"Most common words: {selected_user}")
        most_common_words_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()
        ax.barh(most_common_words_df[0], most_common_words_df[1], color="purple")
        st.pyplot(fig)

        # Emoji Analysis
        st.divider()
        st.subheader(f"Most common emojis: {selected_user}")
        emoji_df = helper.emoji_counter(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, use_container_width=True)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            # ax.bar(emoji_df[0].head(), emoji_df[1].head(), color="purple")
            st.pyplot(fig)
