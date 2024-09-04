# Project: YouTube Data Harvesting and Warehousing

Problem Statement: The project aims to develop a Streamlit application that allows users to access, analyze, and store data from multiple YouTube channels. The application should enable users to retrieve comprehensive data from YouTube using a channel ID and store this data in a MongoDB data lake. Additionally, users should be able to migrate data from the data lake to a SQL database, perform complex queries, and visualize the data within the Streamlit app.

Features:

YouTube Channel Data Retrieval:
Input a YouTube channel ID to retrieve data such as channel name, subscribers, video count, playlist ID, video ID, likes, dislikes, and comments using the Google API.
Data Storage in MongoDB:
Store retrieved YouTube channel data in a MongoDB database, functioning as a data lake for up to 10 different channels.
Data Migration to SQL:
Select a channel name and migrate its data from MongoDB to a SQL database, creating structured tables for easier querying.
Data Search and Analysis:
Perform searches and retrieve data from the SQL database using different options, including joining tables to get detailed channel information.
Approach:

Set up a Streamlit App:
Develop the user interface and backend logic using Streamlit to handle data retrieval, storage, and visualization.
Connect to the YouTube API:
Utilize the Google API to fetch YouTube channel data based on the channel ID.
Store Data in MongoDB:
Store the collected YouTube data in a MongoDB database, enabling scalable storage and retrieval.
Query the SQL Data Warehouse:
Migrate data from MongoDB to a SQL database and perform queries to retrieve and analyze the data.
Display Data in the Streamlit App:
Use Streamlit to visualize the data, allowing users to explore YouTube channel metrics and insights.
Methodology:

Environment Setup:

Ensure all necessary tools and libraries are installed, including Python, Pandas, Google API Client, MongoDB, MySQL, and Streamlit.
YouTube API Key Generation:

Generate an API key using the Google Developer Console to retrieve data from YouTube.
Data Retrieval:

Use the YouTube API to fetch data using the channel ID and service object.
Data Storage:

Store the retrieved data in MongoDB Compass, which acts as the data lake.
SQL Database Connection:

Establish a connection to a MySQL database and migrate data from MongoDB for structured storage.
Streamlit Visualization:

Visualize the data within the Streamlit app, allowing users to interact with the data and perform custom searches.
Functionality in the Streamlit App:

Retrieve YouTube Channel Data: Fetch and store data in MongoDB using the channel ID.
Data Migration to MySQL: Upload data from MongoDB to MySQL for analysis.
View Tables: Display channel, video, and comments tables.
Search Options: Provide search functionalities with pre-defined queries and allow users to generate custom column views based on channel ID or name.
This project showcases the full lifecycle of data from retrieval, storage, migration, and analysis, offering valuable insights into YouTube channels and their performance.

## Feel free to reach me on my linkedin Profile:> https://www.linkedin.com/in/sabreena-gulzar-5a0227176/





