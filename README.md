# music-visualizer
A music visualizer compatibile with .mp3 or .wav files with two seperate modes of visualization.

## Instructions
Press space bar to pause, left and right arrow keys will skip 10 seconds forward or backward in the song. Press the m key to change visualization mode.

## Installing
Install python 3 from the official website.
Also install ffmpeg from their official website.

Run the following in the terminal to install all necessary libraries:
```
pip3 install pygame
pip3 install numpy
pip3 install pydub
```
## Running the application
Clone the repo and run the main.py file.
```
python3 main.py 
```

## Screenshots

![1](https://github.com/schmanub/music-visualizer/blob/main/screenshots/main-menu.png)
*Written using PyCharm*

![2](https://github.com/schmanub/music-visualizer/blob/main/screenshots/line.png)
*Line mode, visualizes the wave form of the audio*

![3](https://github.com/schmanub/music-visualizer/blob/main/screenshots/bars.png)
*Bar mode, visualizes the energy of the audio*

## Prerequisites
* [Python](https://www.python.org)
* [Pygame](https://www.pygame.org) Used to create all graphics and sound.
* [Numpy](https://numpy.org/) Used to process data in arrays.
* [Pydub](https://github.com/jiaaro/pydub) Used for MP3 support.
* [ffmpeg](https://ffmpeg.org/) or [avconv](https://github.com/libav/libav) required for pydub for file conversion.

## Authors

* **Manuel Marchand** - *File processing and menu system*
* **Ethan Dunn** - *Graphics*
