# YoutubeDataHarvestingAndWarehousing
**Problem Statement:**

The problem statement is to create a Streamlit application that allows users to access
and analyze data from multiple YouTube channels. The application should have the
following features:
1. Ability to input a YouTube channel ID and retrieve all the relevant data
(Channel name, subscribers, total video count, playlist ID, video ID, likes,
dislikes, comments of each video) using Google API.
2. Option to store the data in a MongoDB database as a data lake
3. Ability to collect data for up to 10 different YouTube channels and store them in
the data lake by clicking a button.
4. Option to select a channel name and migrate its data from the data lake to a
SQL database as tables.
5. Ability to search and retrieve data from the SQL database using different
search options, including joining tables to get channel details.

**Approach:**
1. Set up a Streamlit app
2. Connect to the YouTube API
3. Store data in a MongoDB data lake
5. Query the SQL data warehouse
6. Display data in the Streamlit app

**Project Description:**

Pre requisites:

1. Install visual studio.
2. Install Python and Pandas.
3. Install Google API Client.
4. Install MongoDB and MySQL.
5. Install Streamlit Application.

**Methodology:**

Set up the environment of project and make sure all pre requisites are met.

Generate API key in order to retrieve data from youtube using google console API's.

Retrieve the data from the youtube using the API key and service object of youtube.

Store the data to Mongo DB compass.

Create the connect using SQL and load the data to MySQL database.

Using Streamlit application visualize output of the project.

**Functionality available on streamlit app:**

1. Retreive the data of any youtube channel using channel ID and storing it to mongoDB.
2. Uploading the data to MySQL from mongoDB.
3. View the channel table , video table , comments table.
4. Search 10 questions provided with the Project.
5. Generate column view at runtime using search options based on channel ID and channel name.

Feel free to reach me on my linkedin Profile:> https://www.linkedin.com/in/sabreena-gulzar-5a0227176/





