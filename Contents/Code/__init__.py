# Icon and Code by Ryan McNally. Art by jpmatth on flicker http://www.flickr.com/photos/jpmatth/979337931/
import string

BASE = 'http://www.hd-trailers.net'
TOP_10 = '%s/TopMovies/' % BASE
LATEST = '%s/Page/%%d' % BASE
LIBRARY = '%s/PosterLibrary/%%s' % BASE
OPENING = '%s/OpeningThisWeek/' % BASE
COMING_SOON = '%s/ComingSoon/' % BASE
BLU_RAY = '%s/BluRay/' % BASE
ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/hdtrailers', MainMenu, 'HD Trailers.net', ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

  MediaContainer.art = R(ART)
  MediaContainer.title1 = 'HD Trailers.net'
  MediaContainer.userAgent = 'Apple Mac OS X v10.6.7 CoreMedia v1.0.0.10J869'
  MediaContainer.viewGroup = 'List'
  DirectoryItem.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'

####################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(Videos, title='Top 10'), url=TOP_10))
  dir.Append(Function(DirectoryItem(Latest, title='Latest')))
  dir.Append(Function(DirectoryItem(Videos, title='Opening'), url=OPENING))
  dir.Append(Function(DirectoryItem(Videos, title='Coming Soon'), url=COMING_SOON))
  dir.Append(Function(DirectoryItem(Videos, title='Blu-Ray'), url=BLU_RAY))
  dir.Append(Function(DirectoryItem(Library, title='Library')))
  dir.Append(PrefsItem(title='Preferences...', thumb=R('icon-prefs.png')))
  return dir

####################################################################################################
def Latest(sender, page=1):
  dir = Videos(sender, url=LATEST % page)
  dir.Append(Function(DirectoryItem(Latest, title='More...'), page=page+1))
  return dir

####################################################################################################
def Library(sender):
  dir = MediaContainer(title=sender.itemTitle)
  for page in list(string.uppercase):
    dir.Append(Function(DirectoryItem(Videos, title=page), url=LIBRARY % page))
  return dir

####################################################################################################
def Videos(sender, url):
  dir = MediaContainer(title=sender.itemTitle)
  for poster in HTML.ElementFromURL(url).xpath('//td[@class="indexTableTrailerImage"]/a'):
    if len(poster.xpath('./img')) > 0:
      url = BASE + poster.get('href')
      thumb = poster.xpath('./img')[0].get('src')
      title = poster.xpath('./img')[0].get('alt')
      dir.Append(Function(PopupDirectoryItem(VideosMenu, title=title, thumb=Function(GetThumb, url=thumb)), url=url))
  return dir

####################################################################################################
def VideosMenu(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)
  defaultRes = Prefs['resolution']

  for row in HTML.ElementFromURL(url).xpath('//table[@class="bottomTable"]//tr'):
    baseTitleItems = row.xpath('./td[@class="bottomTableName"]')
    baseTitle = None
    if len(baseTitleItems) > 0:
      baseTitle = baseTitleItems[0].xpath('./span')[0].text
    if baseTitle is not None:
      for res in row.xpath('./td[@class="bottomTableResolution"]/a'):
        resTitle = res.text
        videoUrl = res.get('href')
        if defaultRes == 'Prompt' or defaultRes == resTitle:
          dir.Append(VideoItem(videoUrl, title='%s %s' % (baseTitle, resTitle)))

  if len(dir) == 0:
    return MessageContainer('Empty', "There aren't any items to display")
  else:
    return dir

####################################################################################################
def GetThumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH)
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))
