# Original Icon and Code by Ryan McNally. Art by jpmatth on flicker http://www.flickr.com/photos/jpmatth/979337931/
# 2.1 rewrite, URL service by Mike McCurdy June 2012.

# TODO: 
# Make Yahoo! quality selection work (right now it will play 1080p or the first available quality failing that).
# Library alphabetical section calls are slow, but mostly because the underlying pages are huge.
# Thumbnails from the site are poster aspect ratio, which looks awful in the VideoClipObject list previews in mediastream.

TITLE			= 'HD Trailers'
BASE_URL		= 'http://www.hd-trailers.net'
LATEST			= '%s/Page/%%d' % BASE_URL
LIBRARY			= '%s/PosterLibrary/%%s' % BASE_URL
MOST_WATCHED	= '%s/most-watched/' % BASE_URL
TOP_10			= '%s/TopMovies/' % BASE_URL
OPENING			= '%s/OpeningThisWeek/' % BASE_URL
COMING_SOON		= '%s/ComingSoon/' % BASE_URL
NEW_AT_NETFLIX	= '%s/netflix-new-releases/' % BASE_URL
ART				= 'art-default.jpg'
ICON			= 'icon-default.png'
USER_AGENT		= 'Apple Mac OS X v10.6.7 CoreMedia v1.0.0.10J869'
	
SOURCES		= {	
				'apple.com'			: 'Apple',
				'yahoo.com'			: 'Yahoo!',
				'moviefone.com'		: 'Moviefone',
				'youtube.com'		: 'YouTube',
				'hd-trailers.net' 	: 'HD Trailers',
				'wdmp.rd.llnwd.net' : 'HD Trailers',
				'disney.com' 		: 'HD Trailers'
			  }

####################################################################################################
def Start():

	Plugin.AddPrefixHandler('/video/hdtrailers', MainMenu, 'HD Trailers.net', ICON, ART)

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE

	HTTP.CacheTime = 300
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:12.0) Gecko/20100101 Firefox/12.0'

####################################################################################################
def MainMenu():
	
	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=LATEST, title='Latest'), title='Latest', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(LibraryAlphaList), title='Library', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=MOST_WATCHED, title='Most Watched This Week'), title='Most Watched', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=TOP_10, title='Box OfficeTop 10'), title='Box Office Top 10', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=OPENING, title='Opening This Week'), title='Opening This Week', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=COMING_SOON, title='Coming Soon'), title='Coming Soon', thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=NEW_AT_NETFLIX, title='New @ Netflix'), title='New @ Netflix', thumb=R(ICON)))
	return oc


####################################################################################################
def LibraryAlphaList():

	oc = ObjectContainer(title2='Library')
	oc.add(DirectoryObject(key=Callback(MoviesMenu, url=LIBRARY % '0', title='Library - #', page=0), title="#"))
	for page in map(chr, range(65, 91)):
		oc.add(DirectoryObject(key=Callback(MoviesMenu, url=LIBRARY % page, title='Library - ' + page, page=page), title=page))
	return oc


####################################################################################################
def MoviesMenu(url, title, page=1):

	oc = ObjectContainer(title2=title)
	
	if title == 'Latest':
		url = LATEST % page

	for movie in HTML.ElementFromURL(url).xpath('//td[@class="indexTableTrailerImage"]'):
		movie_url = BASE_URL + movie.xpath('./a')[0].get('href')

		try:
			movie_title = movie.xpath('./a/img')[0].get('title')
		except:
			movie_title = ''.join(movie.xpath('.//text()')).strip()
		
		try:
			thumb_url = movie.xpath('./a/img')[0].get('src')
		except:
			thumb_url = None

		oc.add(DirectoryObject(key = Callback(MovieMenu, url=movie_url, title=movie_title, thumb_url=thumb_url), title=movie_title, thumb=Callback(Thumb, url=thumb_url)))

	if title == 'Latest':
		oc.add(DirectoryObject(key=Callback(MoviesMenu, url=url, title=title, page=page+1), title="More..."))

	return oc	


####################################################################################################
def MovieMenu(url, title, thumb_url, section=None):
	
	oc = ObjectContainer(title2=title)
	trailers = BuildTrailerDict(url)

	if trailers['Trailers'] and trailers['Clips'] and section == None:
		Log('canonical url is -----> ' + trailers['Trailers'][0]['item_urls']['source_url'])
		latest = SanitizeSourceVideo(trailers['Trailers'][0], trailers['description'], thumb_url)
		if latest:
			oc.add(VideoClipObject(url = latest.url,thumb=thumb_url, title='Latest Trailer'))
		oc.add(DirectoryObject(key = Callback(MovieMenu, url=url, title=title, thumb_url=thumb_url, section='Trailers'), title='Trailers', thumb=Callback(Thumb, url=thumb_url)))
		oc.add(DirectoryObject(key = Callback(MovieMenu, url=url, title=title, thumb_url=thumb_url, section='Clips'), title='Clips', thumb=Callback(Thumb, url=thumb_url)))
	else:
		if not section:
			section = 'Trailers'
		for item in trailers[section]:
			video_clip = None
			video_clip = SanitizeSourceVideo(item,trailers['description'],thumb_url)
			if video_clip:
				oc.add(video_clip)

	return oc
	


####################################################################################################
# BuildTrailerDic builds a dictionary of clips parsed from the page.  
# Probably reasonable to assume there will always be at least one (latest) Trailer.

def BuildTrailerDict(url):
	
	trailers = { 'Trailers': [], 'Clips': [] } 
	movie_page = HTML.ElementFromURL(url)

	trailers['description'] = movie_page.xpath('//span[@itemprop="description"]')[0].text
	
	current_section = 'Trailers'

	rows = movie_page.xpath('//table[@class="bottomTable"]/tr')
	for row in rows:
		if 'Trailers' in row.xpath('.//text()')[0]:
			pass
		elif 'Clips' in row.xpath('.//text()')[0]:
			current_section = 'Clips'
		elif row.xpath('.//@itemprop="trailer"'):
			item_urls = {}
			for res in row.xpath('./td[@class="bottomTableResolution"]/a'):
				item_urls[res.text] = res.get('href')
			item_urls['source_url'] = row.xpath('./td[@class="bottomTableIcon"]/a')[0].get('href')
			trailer = {
				'item_title' : row.xpath('./td[@class="bottomTableName"]/span')[0].text,
				'item_date' : Datetime.ParseDate(row.xpath('./td[@class="bottomTableDate"]')[0].text).date(),
				'item_urls' : item_urls
			}
			trailers[current_section].append(trailer)
		else:
			pass
		
	return trailers

####################################################################################################
# Returns a sanitized VideoClipObject from a Trailers dict line item

def SanitizeSourceVideo(item, description, thumb_url):
	item_url = item['item_urls']['source_url']
	video_clip = None
		
	# Sources known to have good URL services that we can rely on instead of our own.
	if 'apple.com' in item_url or 'youtube.com' in item_url:
		try:
			video_clip = URLService.MetadataObjectForURL(item_url)
		except:
			Log('Error loading medata from service for url: ' + item_url)
			return None

	# Annotate the title with the source of the underlying clip in the spirit of the original site.
	# Determine if we can play this source file, filter out and log if not (should be rare).
	playable = False
	for pattern in SOURCES.iterkeys():
		if pattern in item_url:
			item_title = item['item_title'] + ' - ' + SOURCES[pattern]
			if video_clip:
				video_clip.title = item_title
			playable = True
	
	if not video_clip and playable:
		try:
			url = item['item_urls']['1080p']
		except:
			url = item['item_urls'].itervalues().next()
	
		video_clip = VideoClipObject(url = url, title = item_title, summary = description, thumb=Callback(Thumb, url=thumb_url))
	
	if not video_clip:
		Log('Don\'t know how to play source video at URL: %s' % item_url)

	return video_clip

####################################################################################################
def Thumb(url):

  if url:
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      return Redirect(R('icon-default.png'))
  return None