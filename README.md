# Bad Songs  
<br />

Music can be a fascinating topic. So many different genres with several adoring fans, lots of whom think a particular one is best.
All too often there are discussions and arguments on why or if a certain genre should be classified as terrible.
An apt encapsulation of "one man's meat is another man's poison".
This got us thinking, what if we could get both men to see what the other sees?<br />  
Spotify, the number one music-streaming service worldwide, became the $20 billion company that it is today when Daniel Ek and Martin Lorentzon, two Swedish entrepreneurs, decided they could make a way for people to find and listen to new music in an era of declining CD sales and illegal music pirating.
Their method?  Big data.  
Ipshita Sen, internet blogger, puts it best when [she writes](https://outsideinsight.com/insights/how-ai-helps-spotify-win-in-the-music-streaming-world/), “The firm has a record of pushing boundaries in technology by using AI and machine learning … Machine learning, fueled both by user data and by external data, has become core to Spotify’s offering.”  Indeed, the streaming giant made headlines when it purchased Seed Scientific, a leading music analytics startup.  
One of Spotify’s signature services is their Discover Weekly playlist.  Each week, users get a personalized playlist of music they’ve never streamed before – like a modern-day mixtape from a friend who knows your taste.  
With such an investment in predicting what users will like, our team decided to take on a query that the Spotify data analytics team has yet to pose.  An analysis yet to be done.  A solution yet to be implemented.  
That is, a personalized playlist of songs that you’re guaranteed NOT to like
<br /><br />
## Method
After granting permissions, our web app queries the spotify API for a user's top 10 recent tracks. The model considers each track's audio features such as "speechiness", "loudness", "danceability" then generates 10 dissimilar tracks using sklearn's KNN algorithm.  
For students of several genres, note that our model uses the top 10 recent tracks so it's possible to get a dissimilar genre on the other side of the spectrum that you listen to sometimes, albeit not in a while.  
Be aware that the more further out of the norm your bad suggestions are, the longer it could take to generate. Please be a bit patient

The app also queries the Genius API to retrieve the lyrics of all suggested songs. A spaCy algorithm is then used to comb through the lyrics to come up with a playlist name.  
Our app also has a mini player embedded so you can listen to the songs right within the app.

When you've had enough of the bad songs, get some reprieve by getting a playlist of good suggestions. Simply click the checkbox for "Good Suggestions" and get 10 songs you should like. This feature is only available after running the model at least once to get a playlist of bad songs.  
All the properties of the bad playlists apply to the good playlist suggestions, right down to naming the playlists.  
Want to add a particular song to your liked songs? Click the Spotify logo in the mini player to be redirected to its Spotify page.  

<br /><br />
### Check out our web app at https://bad-songs.herokuapp.com/ and have some fun with it!  

<br />

#### Music Data Source:
[Kaggle dataset](https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks) used for KNN algorithm.<br /><br />

### 3rd Party Packages:
* flask
* jinja2
* lyricsgenius
* pandas
* python-dotenv
* sklearn
* spacy
* spotipy

### APIs:
* Spotify API
* Genius API

### Python version:
Python 3.8

<br />

Brought to you by Reid Harris, Treay Heaney, Christopher Lee, Laurence Obi, and Ik Okoro
