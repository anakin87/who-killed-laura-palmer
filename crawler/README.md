# Twin Peaks crawler

This crawler download texts and metadata from [Twin Peaks Fandom Wiki](https://twinpeaks.fandom.com/wiki/Twin_Peaks_Wiki). The output format is JSON. The crawler is based on the combination of [Scrapy](https://github.com/scrapy/scrapy) and [fandom-py](https://github.com/NikolajDanger/fandom-py).

*Several wiki pages are discarded, since they are not related to Twin Peaks plot and create noise in the Question Answering index.*

## Installation
- copy this folder (if needed, see [stackoverflow](https://stackoverflow.com/questions/7106012/download-a-single-folder-or-directory-from-a-github-repo))
- `pip install -r requirements.txt`

## Usage
- (if needed, activate the virtual environment)
- `cd tpcrawler`
- `scrapy crawl tpcrawler`
- you can find the downloaded pages in `data` subfolder
