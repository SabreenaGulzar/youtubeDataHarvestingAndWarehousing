#***********************Import Section***********************
from googleapiclient.discovery import build
import isodate
import mysql.connector
from pymongo import MongoClient
import streamlit as st
import pandas as pd 
import time
import numpy as np
import altair as alt 

#******************api connection************************

def apiConnection():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyBMUD52Jov6a1LBkSCvZvyay4Ih0-7GPPk"   
    #create a service object
    youtube = build(api_service_name, api_version, developerKey = api_key)
    return youtube
youtube = apiConnection()

def isChannelValid(youtube, channel_id):
    
    channelInfo = []
    
    request = youtube.channels().list(
        id=channel_id,
        part='snippet,statistics,contentDetails'
        )
    response = request.execute()
    if (response["pageInfo"]["totalResults"] == 0):

        st.write("Channel Id is invalid")
        return False
    return True


# '''Function Description: This function scraps channel data from youtube
#    Arguments: Youtube as Service Object, channel_id as String
#    Returns: Data as JSON'''

def ftg_channelDetails(youtube, channel_id):
    
    channelInfo = []
    
    request = youtube.channels().list(
        id=channel_id,
        part='snippet,statistics,contentDetails'
        )

    response = request.execute()
    if (response["pageInfo"]["totalResults"] == 0):
         st.write("Channel Id is invalid")
         InvalidchannelId=True
         return "Error"
    
    else:
        
        for i in range(len(response["items"])):
            data = dict(channelId = response["items"][i]["id"],
                        channelName = response["items"][i]["snippet"]["title"],
                        channelDescription = response["items"][i]["snippet"]["description"],
                        channelPublishedAt = response["items"][i]["snippet"]["publishedAt"],
                        channelSubscribers = response["items"][i]["statistics"]["subscriberCount"],
                        channelViewCount = response["items"][i]["statistics"]["viewCount"],
                        channelVideoCount = response["items"][i]["statistics"]["videoCount"],
                        channelPlaylistId = response["items"][i]["contentDetails"]["relatedPlaylists"]["uploads"])
            channelInfo.append(data)
  
    return channelInfo
    
# '''Function Description: This function scraps video Ids from youtube
#    Arguments: Youtube as Service Object, channelPlaylistID as String
#    Returns: Data as JSON'''

def ftg_videoIds(youtube,channelPlaylistId):
    
    allVideoIds = []
    
    token = None
    while True:
       
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50,
            playlistId= channelPlaylistId,
            pageToken = token
            )

        response = request.execute()
        token = response.get("nextPageToken")
        
        for i in range(len(response["items"])):
            video_data = response["items"][i]["contentDetails"]["videoId"]
            allVideoIds.append(video_data) 
            
        token = response.get("nextPageToken")
        if token is None:
            break
      
    return allVideoIds

# '''Function Description: This function scraps video data from youtube
#    Arguments: Youtube as Service Object, Video Ids as List
#    Returns: Data as JSON'''

def ftg_videoDetails(youtube,video_ids):

    videoDuration = ""
    videoInformation = []
    def getVideoDuration(videoDu):
        videoDuration = str(isodate.parse_duration(videoDu))
        print(videoDuration)
        print(type(videoDuration))
        vdX = videoDuration.split(":")
        hh=vdX[0]
        mm = vdX[1]
        ss = vdX[2]
        totalDuration = int(hh)*60 + int(mm)*60*60 + int(ss)
        return totalDuration
    
    for i in video_ids:
        request = youtube.videos().list(
            part = "snippet, contentDetails, statistics",
            id = i
            )
        
        response = request.execute()
        
        for item in response["items"]:
            
            d = dict(
                    channelId = item["snippet"]["channelId"],
                    channelName = item["snippet"]["channelTitle"],
                    videoId = item["id"],
                    videoName = item["snippet"]["title"],
                    videoDuration = getVideoDuration(item["contentDetails"]["duration"]),
                    videoDescription = item["snippet"]["localized"]["description"],
                    publishedAt = item["snippet"]["publishedAt"],
                    tags = ",".join(item["snippet"].get("tags",[])),
                    thumbnail = item["snippet"]["thumbnails"]["default"]["url"],
                    videoLikeCount = item["statistics"].get("likeCount"),
                    videoViewCount = item["statistics"]["viewCount"],
                    favoriteCount = item["statistics"]["favoriteCount"],
                    commentCount = item["statistics"].get("commentCount"),
                    videoDislikeCount = item["statistics"].get("dislikeCount"),
                    videoCaption = item["contentDetails"]["caption"])

            videoInformation.append(d)

    return videoInformation

# '''Function Description: This function scraps comments data from youtube
#    Arguments: Youtube as Service Object, Video Ids as List
#    Returns: Data as JSON'''

def ftg_commentDetails(youtube, video_ids):
    
    commentData = []
  
    try:
        
        for i in video_ids:
            request = youtube.commentThreads().list(
                part = "snippet",
                videoId = i,
                maxResults = 20
                )
            response = request.execute()
            
            for item in response["items"]:
                print('$$$$$$$$in second for of COMMENT DETAILS FUNC$$$$$$$$$$$$')
                
                data = {
                    'commentId' : item["snippet"]["topLevelComment"]["id"],
                    'commentText' :  item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                    'commentAuthor' :  item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                    'commentPublishedAt' :  item["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                    'videoId': item["snippet"]["videoId"]
                    }

                commentData.append(data)  

    except:
        pass
                
    return commentData

#*****************MongoDB Connection*********************

client = MongoClient("mongodb://localhost:27017/")
db = client['youtubeDataHarvesting']
collection = db['youtube']

# '''Function Description: This function scraps data from youtube and stores to MongoDB 
#    Arguments: channelId as String
#    Return: String'''

def data_to_mongo(channelId):
    channelData = ftg_channelDetails(youtube, channelId)
    if channelData == "Error":
       st.write("channel data not available")
       return "Error1"
    videoIds = ftg_videoIds(youtube,channelData[0]['channelPlaylistId'])
    videoData = ftg_videoDetails(youtube,videoIds)
    commentData = ftg_commentDetails(youtube, videoIds)
        
    collection.insert_one({"ChannelInfo": channelData, "videoIds" : videoIds,
                           "VideoInfo": videoData, "CommentInfo":commentData})
    return  "YouTube data has Uploaded To MongoDB Successfully"

 
#***********************MySQL DB Connection*******************************************

username = 'root'
password = '255244'
host = 'localhost'
database_name = 'Youtube'

mydb = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database_name,
    )

cursor = mydb.cursor()

# '''Function Description: This function upload channel data to MySQL DB
#    Arguments: MySQL connection
#    Return: NA'''
    
def channels_table(cursor):
    sqlChName = []
    username = 'root'
    password = '255244'
    host = 'localhost'
    database_name = 'Youtube'
    
    mydb = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database_name
        )
    cursor = mydb.cursor()
    create_query = ( """CREATE TABLE IF NOT EXISTS channelsTable (Channel_Name varchar(100),Channel_Id varchar(80) primary key,
                        Subscriber_Count bigint,View_Count bigint, Total_videos int, Channel_Description TEXT,
                        Channel_Published_At TEXT, Channel_Playlist_Id varchar(50))""")

    cursor.execute(create_query)
    mydb.commit()

    ch_list = []
    db = client["youtubeDataHarvesting"]
    coll1 = db["youtube"]
    for c_data in coll1.find({},{"_id":0,"ChannelInfo":1}):
        for i in range(len(c_data["ChannelInfo"])):
             ch_list.append(c_data["ChannelInfo"][i])
    df = pd.DataFrame(ch_list)
    for index, row in df.iterrows():
        insert_query = """INSERT INTO channelsTable (Channel_Name, Channel_Id,Subscriber_Count,View_Count,Total_videos,Channel_Description,
                        Channel_Published_At,Channel_Playlist_Id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (
                row["channelName"],
                row["channelId"],
                row["channelSubscribers"],
                row["channelViewCount"],
                row["channelVideoCount"],
                row["channelDescription"],
                row["channelPublishedAt"],
                row["channelPlaylistId"])
        
        try:
            cursor = mydb.cursor()
            cursor.execute(insert_query, values)
            mydb.commit()

        except Exception as e:
            print("Channels values are already inserted")

    cursor.close()
    mydb.close()

# '''Function Description: This function upload video data to MySQL DB
#    Arguments: MySQL connection
#    Return: NA'''

def videos_table(cursor):
    sqlChName = []
    username = 'root'
    password = '255244'
    host = 'localhost'
    database_name = 'Youtube'
    
    mydb = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database_name
        )
    cursor = mydb.cursor()
    try:    
        create_query = ("""CREATE TABLE IF NOT EXISTS videosTable(channelId varchar(50), channelName varchar(80),
                        videoId varchar(50) primary key,videoName varchar(150),
                        videoDuration varchar(50),videoDescription TEXT,publishedAt TEXT,tags TEXT,
                        thumbnail TEXT, videoLikeCount bigint, videoViewCount bigint,
                        favoriteCount int, commentCount int,videoDislikeCount int, videoCaption varchar(50))""")
        cursor.execute(create_query)
        mydb.commit()
        
    except:
        print("Videos Table already created")

    vi_list = []
    db = client["youtubeDataHarvesting"]
    coll1 = db["youtube"]
    for vi_data in coll1.find({},{"_id":0,"VideoInfo":1}):
        for i in range(len(vi_data["VideoInfo"])):
            vi_list.append(vi_data["VideoInfo"][i])
    df2 = pd.DataFrame(vi_list)

    for index, row in df2.iterrows():
        insert_query = """INSERT INTO videosTable(channelId, 
                                            channelName,       
                                            videoId,
                                            videoName,
                                            videoDuration,
                                            videoDescription,
                                            publishedAt, 
                                            tags,
                                            thumbnail,
                                            videoLikeCount,
                                            videoViewCount,
                                            favoriteCount,
                                            commentCount,
                                            videoDislikeCount,
                                            videoCaption)
                                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (
                    row["channelId"],
                    row["channelName"],
                    row["videoId"],
                    row["videoName"],
                    row["videoDuration"],
                    row["videoDescription"],
                    row["publishedAt"],
                    row["tags"],
                    row["thumbnail"],
                    row["videoLikeCount"],
                    row["videoViewCount"],
                    row["favoriteCount"],
                    row["commentCount"],
                    row["videoDislikeCount"],
                    row["videoCaption"]
                    )
    
        try:
            cursor = mydb.cursor()
            cursor.execute(insert_query, values)
            mydb.commit()
            
        except Exception as e:
            print("Videos data already inserted")

    cursor.close()
    mydb.close()

# '''Function Description: This function upload comment data to MySQL DB
#    Arguments: MySQL connection
#    Return: NA'''

def comments_table():
    username = 'root'
    password = '255244'
    host = 'localhost'
    database_name = 'Youtube'

    mydb = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database_name,
        )

    cursor = mydb.cursor()

    create_query = """CREATE TABLE IF NOT EXISTS commentsTable(comment_id varchar(200) primary key,comment_text TEXT,
                       comment_author varchar(50),comment_publishedAt Text,video_id varchar(100))"""

    cursor.execute(create_query)
    mydb.commit()

    com_list = []
    db = client["youtubeDataHarvesting"]
    coll1 = db["youtube"]
    for com_data in coll1.find({},{"_id":0,"CommentInfo":1}):
        for i in range(len(com_data["CommentInfo"])):
            com_list.append(com_data["CommentInfo"][i])
    df3 = pd.DataFrame(com_list)
   
    for index, row in df3.iterrows():
        insert_query = """INSERT INTO commentsTable (comment_id, comment_text,comment_author,comment_publishedAt,video_id) 
                            VALUES(%s,%s,%s,%s,%s)"""
        values = (
                row["commentId"],
                row["commentText"],
                row["commentAuthor"],
                row["commentPublishedAt"],
                row["videoId"])
                     
        try:
            print("in try of comment details")
            cursor = mydb.cursor()
            cursor.execute(insert_query, values)
            mydb.commit()
        except Exception as e:
            print("comments data already added")

    cursor.close()
    mydb.close()

# '''Streamlit page configuration'''

st.set_page_config(page_title='YouTube Data Harvesting and Warehousing',
                    page_icon=':apple:', layout="wide")
page_background_color = """
<style>

[data-testid="stHeader"] 
{
background: rgba(0,1,0,0);
}

</style>
"""
st.markdown(page_background_color, unsafe_allow_html=True)

st.markdown(f'<h1 style="text-align: center;">YouTube Data Harvesting and Warehousing </h1>',
            unsafe_allow_html=True)
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by <a style='display: block; right-align: right;' href="https://www.linkedin.com/in/sabreena-gulzar-5a0227176" target="_blank" = blank>©Sabreena Gulzar</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

# '''Function Description: This function creates MySQL tables
#    Arguments: NONE
#    Returns: String'''

def tables():
    channels_table()
    videos_table()
    comments_table()
    return "Tables Created Successfully"

# '''Function Description: This function shows MongoDB channel data as Dataframe
#    Arguments: NONE
#    Returns: Dataframe'''

def showChannelTable():
    cList = []
    db = client["youtubeDataHarvesting"]
    coll1 = db["youtube"]
    for c_data in coll1.find({},{"_id":0,"ChannelInfo":1}):
        for i in range(len(c_data["ChannelInfo"])):
            cList.append(c_data["ChannelInfo"][i])
    channelTable = st.dataframe(cList)
    return channelTable

# '''Function Description: This function shows MongoDB video data as Dataframe
#    Arguments: NONE
#    Returns: Dataframe'''

def showVideoTable():
    vList = []
    db = client["youtubeDataHarvesting"]
    coll2 = db["youtube"]
    for vData in coll2.find({},{"_id" : 0, "VideoInfo" : 1}):
        for i in range(len(vData["VideoInfo"])):
            vList.append(vData["VideoInfo"][i])
    videoTable = st.dataframe(vList)
    return videoTable

# '''Function Description: This function shows MongoDB comments data as Dataframe
#    Arguments: NONE
#    Returns: Dataframe'''

def showCommentTable():
    comList = []
    db = client["youtubeDataHarvesting"]
    coll1 = db["youtube"]
    for comData in coll1.find({},{"_id":0,"CommentInfo":1}):
        for i in range(len(comData["CommentInfo"])):
            comList.append(comData["CommentInfo"][i])
    commentTable = st.dataframe(comList)
    return commentTable 

#Gets the input from user

channelId = st.text_input(":blue[Enter the channel ID 👇]")

#*****************************Data retrieval and Store To MongoDB Button********************************


if st.button("Collect and Store Data in MongoDb"): 

    chIds = []
    db = client["youtubeDataHarvesting"]
    coll = db["youtube"]

    for chData in coll.find({},{"_id" : 0, "ChannelInfo" : 1}):
        chIds.append(chData["ChannelInfo"][0]["channelId"])

    if channelId in chIds:
        st.success("Channel details of the given channel ID:"+"---" + channelId + " ---"+ " already exists")
        st.empty()

    else:
        getData = data_to_mongo(id)
        if getData == "Error1":
            st.write("There was some error in getting the data, please check your input")
        else:
            st.write(getData)
                
#***********************************SQL BUTTON******************
if st.button("Data Migration to MySQL"):
    username = 'root'
    password = '255244'
    host = 'localhost'
    database_name = 'Youtube'

    mydb = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database_name
        )
    cursor = mydb.cursor()
    flag = False
    chIds = []
    e = "Select Channel_Id from channelstable;"
    cursor.execute(e)
    chIds = cursor.fetchall()

    for i in range(len(chIds)):

        if channelId == chIds[i][0]:
            flag = True
            st.write("Data of this channel"+" "+ channelId + " "+"already exists in MySQL DB")
    if flag == False: 

        if isChannelValid(youtube,channelId)==False:
            st.write("Channel Invalid please try again with proper channel id.")
        else:

            display = tables()
            st.success(display)
        

#------------------------------Sidebar Items-----------------------------------------------------
with st.sidebar:
    st.subheader("**Choose table to view**")
    show_table = st.selectbox("",("---select---","Channels","Videos","Comments"))
if show_table == "---select---":
    pass
elif show_table == "Channels":
    st.write("**Channel Table**")
    showChannelTable()
elif show_table =="Videos":
    st.write("**Video Table**")
    showVideoTable()
elif show_table == "Comments":
    st.write("**Comment Table**")
    showCommentTable()

#-------------------------------QUESTIONS SECTION--------------------------------
st.sidebar.subheader("**Select questions from below**")
question = st.sidebar.selectbox("",
                        ("---select---",
                        '1. What are the names of all the videos and their corresponding channels?',
                        '2. Which channels have the most number of videos, and how many videos do they have?',
                        '3. What are the top 10 most viewed videos and their respective channels?',
                        '4. How many comments were made on each video, and what are their corresponding video names?',
                        '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                        '6. What is the total number of likes and dislikes for each video, and what aretheir corresponding video names?',
                        '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                        '8. What are the names of all the channels that have published videos in the year 2022?',
                        '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                        '10.Which videos have the highest number of comments, and what are their corresponding channel names?')
                        )
if question == "---select---":
    pass
if question == '1. What are the names of all the videos and their corresponding channels?':
    query1 = 'SELECT channelName, videoName from videosTable;'
    cursor.execute(query1)
    ans1 = cursor.fetchall()
    st.write("**Names of all Videos and thier corresponding Channels**")
    st.write(pd.DataFrame(ans1, columns = ["Channel Name", "Video Name"]))
    
elif question =='2. Which channels have the most number of videos, and how many videos do they have?':
    query2 = "SELECT Channel_Name, Total_Videos from channelsTable order by Total_Videos desc;"
    cursor.execute(query2)
    ans2 = cursor.fetchall()
    df = pd.DataFrame(ans2, columns = ["Channel Name", "Total Videos"])
    st.write("**Channels with most number of videos**")
    st.write(pd.DataFrame(ans2, columns = ["Channel Name", "Total Videos"]))
    c = alt.Chart(df).mark_circle().encode(x = "Channel Name", y = "Total Videos")
    st.write(c)

elif question =='3. What are the top 10 most viewed videos and their respective channels?':
    query3 = "SELECT channelName, videoName, videoViewCount from videosTable order by videoViewCount desc limit 10;"
    cursor.execute(query3)
    ans3 = cursor.fetchall()
    st.write("**Top 10 viewed videos & thier Channel Names**")
    st.write(pd.DataFrame(ans3, columns = ["Channel Name", "Top 10 Videos", "Views"]))

elif question =='4. How many comments were made on each video, and what are their \
    corresponding video names?':
    query4 = "SELECT commentCount, videoName from videosTable order by commentCount desc;"
    cursor.execute(query4)
    ans4 = cursor.fetchall()
    st.write("**Comment Counts with corresponding Channel Names**")
    st.write(pd.DataFrame(ans4, columns = ["Comment Count", "Video Name"]))

elif question =='5. Which videos have the highest number of likes, and what are their corresponding channel names?':
    query5 = "SELECT channelName, videoName, videoLikeCount from videosTable order by videoLikeCount desc;"
    cursor.execute(query5)
    ans5 = cursor.fetchall()
    st.write("**Videos with high like count and their Channel Names**")
    st.write(pd.DataFrame(ans5, columns = ["Channel Name", "Video Name", "Likes"]))

elif question =='6. What is the total number of likes and dislikes for each video, and what aretheir corresponding video names?':
    query6 = "SELECT videoName, videoLikeCount, videoDislikeCount FROM videosTable;"
    cursor.execute(query6)
    ans = cursor.fetchall()
    st.write("**Like and Dislike Count & their channel Names**")
    st.write(pd.DataFrame(ans, columns =["Video Name", "Likes", "Dislikes"]))

elif question =='7. What is the total number of views for each channel, and what are their corresponding channel names?':
    query7 = "SELECT Channel_Name, View_Count FROM channelsTable;"
    cursor.execute(query7)
    ans7 = cursor.fetchall()
    st.write("**Number of Views of each Channel**")
    st.write(pd.DataFrame(ans7, columns = ["Channel Name", "Views"]))

elif question =='8. What are the names of all the channels that have published videos in the year 2022?':
    query8 = "SELECT Channel_Name, Channel_Published_At FROM channelsTable where Channel_Published_At = 2022 group by Channel_Name;"
    cursor.execute(query8)
    ans8 = cursor.fetchall()
    st.write("**Channels published in the year 2022**")
    st.write(pd.DataFrame(ans8, columns = ["Channel Name", "Publish Date"]))

elif question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
    query9 = "SELECT channelName, avg(videoDuration) from videosTable group by channelName;"
    cursor.execute(query9)
    ans9 = cursor.fetchall()
    st.write("**Avrage duration (in seconds) of all videos & their channel Names**")
    st.write(pd.DataFrame(ans9, columns = ["Channel Name", "AVG-Duration-in-seconds"]))
 

elif question == '10.Which videos have the highest number of comments, and what are their corresponding channel names?':
    query10 = "SELECT channelName, videoName, commentCount FROM videosTable;"
    cursor.execute(query10)
    ans10 = cursor.fetchall()
    df = pd.DataFrame(ans10)
    st.write("**Videos with high count of comments**")
    st.write(pd.DataFrame(ans10, columns = ["Channel Name", "Video Name", "Number of Comments"]))

#------------------------------------------Search Option------------------------------

st.sidebar.subheader("**Search Options**")
sqlChName = []
username = 'root'
password = '255244'
host = 'localhost'
database_name = 'Youtube'

mydb = mysql.connector.connect(
    user=username,
    password=password,
    host=host,
    database=database_name
    )
cursor = mydb.cursor()

queryOptions = st.sidebar.radio("Choose primary search option",
                                    ("---select---",
                                    "1. Channel Name",
                                    "2. Channel Id"))
if queryOptions == "---select---":
    pass

elif queryOptions == "1. Channel Name":
    channelName = st.text_input("**Enter the channel name 👇**")
    found = False
    emstring = False
    if channelName == "":
        st.write("You have not entered channel name yet.")
        emstring = True

    else:
        q11 = "select Channel_Name from channelsTable;"
        cursor.execute(q11)
        sqlChName = cursor.fetchall()
    
        for i in range(len(sqlChName)):

            if channelName == sqlChName[i][0]:
                found = True
                st.write("Channel is in Database, you can choose the options from sidebar.")
    
                st.sidebar.subheader('Select Columns for Tabular View')
                option_1 = st.sidebar.checkbox('Channel Name', value = True, disabled=False)
                option_1 = "Channel_Name,"
                option_3 = st.sidebar.checkbox("Subscriber Count",disabled=False)

                if option_3 == True:
                    option_3 = "Subscriber_Count,"

                else:
                    option_3 = ""
                option_4 = st.sidebar.checkbox('Channel Views',disabled=False)

                if option_4 == True:
                    option_4 = "View_Count,"

                else:
                    option_4 = ""
                option_5 = st.sidebar.checkbox('Total Videos',disabled=False)

                if option_5 == True:
                    option_5 = "Total_Videos,"    

                else:
                    option_5 = ""
       
                option_9 = st.sidebar.checkbox('Channel ID',disabled=False)

                if option_9 == True:
                    option_9 = "Channel_Id,"

                else:
                    option_9 = ""
       
                option_list=option_1+option_3+option_4+option_5+option_9
                option_list = option_list[:-1]
                option_list=option_list+" "
                x= "select "+option_list+" from channelsTable where Channel_Name = '"+channelName+"';"

                cursor.execute(x)
                q = cursor.fetchall()
                st.write(pd.DataFrame(q), columns=[option_list])

            else:
                continue
        if nor found and not emstring:
            st.write("invalid Channel Name, please re-enter")
            st.sidebar.checkbox('Channel Name', value = False, disabled= True)

elif queryOptions == "2. Channel Id":

    sqlChIds = []
    channelId = st.text_input("Enter the channel ID 👇")
    found = False
    emstring = False
    if channelId == "":
        st.write("You have not entered channel ID yet.")

    else:
        q11 = "select channelId from videosTable;"
        cursor.execute(q11)
        sqlChIds = cursor.fetchall()
    
        for i in range(len(sqlChIds)):

            if channelId == sqlChIds[i][0]:
                found = True
                st.write("Channel Id is in Database, you can choose the options from sidebar.")
                st.sidebar.subheader('Select Columns for Tabular View')
                option_1 = st.sidebar.checkbox('Channel Id', value = True, disabled=False)
                
                option_1 = "channelId,"
                
                option_2 =st.sidebar.checkbox("Video Name",disabled=False)

                if option_2 == True:
                    option_2 = "videoName,"

                else:
                    option_2 = ""

                option_3 = st.sidebar.checkbox("Video Duration(in sec)",disabled=False)

                if option_3 == True:
                    option_3 = "videoDuration,"

                else:
                    option_3 = ""

                option_4 = st.sidebar.checkbox('Video Description',disabled=False)

                if option_4 == True:
                    option_4 = "videoDescription,"

                else:
                    option_4 = ""

                option_5 = st.sidebar.checkbox('Published Date',disabled=False)

                if option_5 == True:
                    option_5 = "publishedAt,"
                
                else:
                    option_5 = ""

                option_6 = st.sidebar.checkbox("Likes",disabled=False)

                if option_6 == True:
                    option_6 = "videoLikeCount,"

                else:
                    option_6 = ""
                option_7 = st.sidebar.checkbox("Video Views",disabled=False)

                if option_7 == True:
                    option_7 = "videoViewCount,"

                else:
                    option_7 = ""
                option_8 = st.sidebar.checkbox("Comment Author",disabled=False)

                if option_8 == True:
                    option_8 = "comment_author,"

                else:
                    option_8 = ""
                option_9 = st.sidebar.checkbox("Comment Text",disabled=False)

                if option_9 == True:
                    option_9 = "comment_text,"

                else:
                    option_9 = ""

                option_10 = st.sidebar.checkbox('Comment Count',disabled=False)

                if option_10 == True:
                    option_10 = "commentCount,"

                else:
                    option_10 = ""

                option_11 = st.sidebar.checkbox('Tags',disabled=False)

                if option_11 == True:
                    option_11 = "tags,"

                else:
                    option_11 = ""

                option_list=option_1+option_2+option_3+option_4+option_5+option_6+option_7+option_8+option_9+option_10+option_11
                option_list = option_list[:-1]
                option_list=option_list+" "
                x= "select "+option_list+" from videosTable join commentsTable \
                    on videosTable.videoId = commentsTable.video_id \
                        where channelId = '"+channelId+"';"
                cursor.execute(x)
                y = cursor.fetchall()
                st.write(pd.DataFrame(y))

            else:
                continue
        if not found and not emstring:
            st.write("invalid Channel Id, please re-enter")
            st.sidebar.checkbox('Channel Id', value = False, disabled= True)





