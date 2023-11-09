# ---------------------------------------------------------------------------- #
#                      Language Model Service                 #
# ---------------------------------------------------------------------------- #
# This section contains API entpoints for generating responses from the model.

from pathlib import Path
from fastapi import APIRouter, Body, status, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi import HTTPException, status
from app.schemas.userRequest import UserRequest, SystemResponse
from concurrent.futures import ThreadPoolExecutor
from app.schemas.key import APIKey
from app.auth import get_api_key
from pytube import YouTube
import subprocess
import datetime
import shutil
import os
import re

router = APIRouter(responses={404: {"description": "Not Found"}})

data_dir = "data"  # TODO: Move this to config file

# ---------------------------- Helpers --------------------------- #


@router.get("/hello")
async def hello_world():
    return {"message": "Hello World"}

# ---------------------------- Add Video --------------------------- #


def normalize_name(name):
    """Normalize the channel name to be file-system friendly."""
    # Remove invalid file name characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Convert to lowercase
    name = name.lower()
    return name


def download_video_async(video_url: str, channel_name: str):
    """Asynchronous video download task."""
    yt = YouTube(video_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
        'resolution').desc().first()
    data_dir = Path('data') / channel_name
    data_dir.mkdir(parents=True, exist_ok=True)
    stream.download(output_path=str(data_dir))


@router.post("/videos/")
async def download_video_endpoint(background_tasks: BackgroundTasks, video_url: str):
    """Endpoint to trigger the asynchronous download of a YouTube video."""
    try:
        # Create a YouTube object to extract video details
        yt = YouTube(video_url)
        # Normalize the channel name
        channel_name = normalize_name(yt.author)

        # Add the video download task to the background
        background_tasks.add_task(
            download_video_async, video_url, channel_name)

        # Return the response immediately without waiting for the download to complete
        return {
            "status": "download started",
            "title": yt.title,
            "video_url": video_url,
            "channel": yt.author,
            "normalized_channel_name": channel_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
