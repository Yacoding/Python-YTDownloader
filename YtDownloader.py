import urllib2
import time
from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Regex import Regex
from utils.Utils import Utils
import os

__author__ = 'Rabbi'


class YoutubeScrapper(object):
    def __init__(self):
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        self.utils = Utils()


    def scrapVideoDownloadUrl(self, url, filename=None):
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            title = self.scrapTitle(url)
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            dlUrlChunk = self.regex.getSearchedData('(?i)"url_encoded_fmt_stream_map": "([^"]*)"', data)
            dlUrlChunk = self.regex.replaceData('(?i)\\\\u0026', ' ', dlUrlChunk)
            dlUrlParts = dlUrlChunk.split(',')
            sig = ''
            video = ''
            videoUrl = ''
            print dlUrlParts
            for dlUrlPart in dlUrlParts:
                dlUrlPart = urllib2.unquote(dlUrlPart)
                print dlUrlPart

                ## TODO
                if self.regex.isFoundPattern('(?i)itag=22', dlUrlPart) or self.regex.isFoundPattern('(?i)itag=18',
                                                                                                    dlUrlPart):
                    urlPart = dlUrlPart.split(' ')
                    for part in urlPart:
                        print part
                        if self.regex.isFoundPattern('(?i)sig=.*?', part):
                            sig = self.regex.getSearchedData('(?i)sig=(.*?)$', part)

                        if self.regex.isFoundPattern('(?i)url=.*?', part):
                            video = self.regex.getSearchedData('(?i)url=(.*?)$', part)
                            print video

                    videoUrl = video + '&signature=' + sig
                    self.downloadDir = './natok.mp4'

                    print 'Video URL= ' + videoUrl
                    print self.downloadDir
                    break

            # dlPath = './natok.mp4' if filename is None else filename
            fname = self.regex.replaceData('\s+', '_', title)
            dlPath = './' + fname  + '.mp4' if filename is None else filename
            print dlPath
            print '\n\n'
            if self.downloadFile(videoUrl, dlPath) is True:
                print 'Download complete'
        else:
            print 'No data found.'

    def scrapTitle(self, url):
        #        https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v=9bZkp7q19f0&format=xml
        xmlUrl = 'https://www.youtube.com/oembed?url=' + str(url) + '&format=xml'
        data = self.spider.fetchData(xmlUrl)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            print data
            return self.regex.getSearchedData('(?i)<title>([^<]*)</title>', data)

    def downloadFile(self, url, downloadPath, retry=0):
        try:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                          urllib2.HTTPHandler(debuglevel=0),
                                          urllib2.HTTPSHandler(debuglevel=0))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'),
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                ('Connection', 'keep-alive')]
            #            resp = opener.open(url, timeout=10)
            resp = urllib2.urlopen(url, timeout=60)
            print 'ok'

            print resp.info()
            contentLength = resp.info()['Content-Length']
            contentLength = self.regex.getSearchedData('(?i)^(\d+)', contentLength)
            totalSize = float(contentLength)
            directory = os.path.dirname(downloadPath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            currentSize = 0
            dl_file = open(downloadPath, 'ab')
            try:
                if os.path.getsize(downloadPath):
                    start = os.path.getsize(downloadPath)
                    currentSize = start
                    opener.addheaders.append(('Range', 'bytes=%s-' % (start)))
            except Exception, x:
                print x

            res = opener.open(url, timeout=60)
            CHUNK_SIZE = 256 * 1024
            while True:
                data = res.read(CHUNK_SIZE)
                # data = resp.read(CHUNK_SIZE)
                if not data:
                    break
                currentSize += len(data)
                dl_file.write(data)

                print('============> ' + \
                      str(round(float(currentSize * 100) / totalSize, 2)) + \
                      '% of ' + str(totalSize / (1024 * 1024)) + ' Mega Bytes')
                notifyDl = '===> Downloaded ' + str(round(float(currentSize * 100) / totalSize, 2)) + '% of ' + str(
                    totalSize) + ' KB.'
            if currentSize >= totalSize:
                dl_file.close()
                return True
        except Exception, x:
            error = 'Error downloading: '
            print x
            if retry < 20:
                time.sleep(30)
                return self.downloadFile(url, downloadPath, retry + 1)
        return False

if __name__ == '__main__':
    var = YoutubeScrapper()
    ## http://www.youtube.com/watch?v=WzKMa9HNu-s  m-part2
    # var.scrapVideoDownloadUrl('http://www.youtube.com/watch?v=C6iuDz7-oRw', './Jamai-Daoat-Paise-HD.mp4')
    var.scrapVideoDownloadUrl('http://www.youtube.com/watch?v=C6iuDz7-oRw')
