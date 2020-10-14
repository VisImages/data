# VisImages Data

<b>VisImages</b> is a high-quality dataset with large scale of visualization publication images and comprehensive categories 
of visualizations, which contains 12,267 visualization publication images with captions. Each image is annotated by the 
visualization types and locations (represented as bounding boxes).<br>

The extracted images, annotations, and metadata can be downloaded directly from [google drive](https://drive.google.com/drive/folders/1p00qs7PXCpbxhcaeDeYV4bENh8Jmn53r?usp=sharing).<br>

In addition, following the steps below, you are able to download all the PDF documents of VIS paper through your access to the IEEE, and extract images and captions from those PDF documents easily.<br>


## 1. Download Papers
### Requirements
The following packages should be installed:
* `bs4`
* `requests`
* `Pillow`

### Installing Requirements
Install the required python packages with
```
pip install -r requirements.txt
```

### Usage
To collect all the PDF documents, simply run:<br>
```
cd 1_crawler
python PaperScrapy.py
```
The PDF files will be stored in `/vis_data/papers`. We borrow a paper list from [Vispubdata](https://sites.google.com/site/vispubdata/home) and index the papers with a number (please refer to `1_crawler/list.csv` for more details).

## 2. Extract Images
### Requirements
The following packages should be installed:
* `pdf2image`
* `opencv-python`

### Usage
To extract images from PDF documents, simply run:<br>
```
cd ..
python 2_extract_images/extract_images.py
```
The default path of PDF files is `/vis_data/papers`, and the extracted images will be stored in `/vis_data/images`.
You can specify the source directory for PDF files and target directory for images using `--src` and `--dst`
<br>

## 3. Extract Captions
We use [pdffigures](http://pdffigures.allenai.org/) to extract captions from PDF documents.

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

## 4. Caption Matching
Match the extracted captions to the images in VisImages according to the distance of the bounding boxes. If accurate captions are required, please contact us.

### Usage
Simply run:
```
cd ..
python 4_match_captions/match_captions.py
```
You can use option '--help' for more information


