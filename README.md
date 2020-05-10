# VisImages Data

<b>VisImages</b> is a high-quality dataset with large volume of visualization publication images and comprehensive categories 
of visualizations, which contains 12267 visualization publication images with captions. Each image is annotated by the 
visualization types and locations (represented as bounding boxes).<br>

However, due to copyright restrictions, we couldn't supply image and caption data directly. Instead, we provide annotation 
file `vis_data/visimages_data.json` and this work. 
Follow the steps below, you'll download all the PDF documents of VIS paper, and extract image and caption from those PDF documents easily.<br>
<br>

## 1. Download Papers
### Requirements
The following package should installed:
* `bs4`
* `pypiwin32`
* `requests`
* `Pillow`

### Usage
To collect all the PDF documents, simply run:<br>
```
cd 1_crawler
python PaperScrapy.py
```

## 2. Extract Images
### Requirements
The following package should installed:
* `pdf2image`
* `opencv-python`

### Usage
To extract images from PDF documents, simply run:<br>
```
cd ..
python 2_extract_images/extract_images.py
```
You can use option '--help' for more information
<br>

## 3. Extract Captions
We use [pdffigures](http://pdffigures.allenai.org/) to extract caption from PDF documents.

### Usage

1. Compile the command line tools:

```
cd 3_extract_captions
make DEBUG=0
```

2. Run on all the PDF documents and gain the results, and modify the file path in `shell.sh` if you need:

```
sh shell.sh
```

See ```pdffigures -help``` for a list of additional command line arguements.

### Dependencies
pdffigures requires [leptonica](http://www.leptonica.com/) and [poppler](http://poppler.freedesktop.org/) to be installed.
On MAC both of these dependencies can be installed through homebrew:

```
brew install leptonica poppler
```

On Ubuntu 14.04 these dependencies can be installed through apt-get:

```
sudo apt-get install libpoppler-dev libleptonica-dev
```

On Ubuntu >= 15.04:

```
sudo apt-get install libpoppler-private-dev libleptonica-dev
```

pdffigures has been tested with poppler 3.0,3.4,3.7, although I expect most other versions to be compatible, and leptonica 1.72

pdffigures uses std::regex, therefore compiling on Ubuntu requires g++ >= 4.9

### Support
pdffigures has been tested on MAC OS X 10.9 and 10.10, Ubuntu 14.04, 15.04, and 15.10, Windows is not supported.
<br>

## 4. Match Captions
Match the extracted captions to visimages.

### Usage
Simply run:
```
cd ..
python 4_match_captions/match_captions.py
```
You can use option '--help' for more information


