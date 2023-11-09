from pytube import YouTube

# URL of the video to download
video_url = 'https://www.youtube.com/watch?v=qmpUfWN7hh4&list=LL&index=24'

# Create a YouTube object
yt = YouTube(video_url)

print("Title: ", yt.title)
print("Number of views: ", yt.views)
print("Length of video: ", yt.length)


# Select the highest quality stream that is mp4
stream = yt.streams.filter(
    progressive=True, file_extension='mp4').get_highest_resolution()  # .order_by(
# 'resolution').desc().first()


print("Downloading...", stream.title, stream.resolution)

exit()
# Download the video
stream.download("/data/")

print("Download complete!")
