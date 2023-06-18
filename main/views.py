import os
from django.shortcuts import get_object_or_404
from .models import Review
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from pytube import YouTube
def youtube(url):
    try:        
        yt = YouTube(url)
        if yt.title:
            lens= yt.length/60
            lengtha =str(lens).split(".")
            a = lengtha[0]
            b=str(int(lengtha[1])*6)
            b = int(str(b)[:2])
            length = f'{a}:{b}'

            alla = [yt.title,yt.thumbnail_url,yt.views,yt.description,yt.author,yt.publish_date,length]
    except:
        redirect("home")
    return alla
# Create your views here.
def home1(response):
    try:
        data = None
        if "url" in response.GET:
            url= response.GET.get('url')
            alls = youtube(url)

            

            data = dict()
            data["title"] = alls[0]
            data["thumbnail"] = alls[1]
            data["views"]=alls[2]
            data["details"] = alls[3]
            data["author"] = alls[4]
            data["date"] = alls[5]
            data["length"] = alls[6]
    except:
        return render(response, 'main/home.html', {'msg':'VideoBro advices you to check your internet connection'})
        

    return render(response, "main/home.html", {"data":data})

def audio(responses):
    try:
        for fname in os.listdir():
            if fname.endswith('.mp3'):
                os.remove(fname)    
        if responses.method == 'POST':
            link = responses.POST['links']
            video = YouTube(link)

            stream = video.streams.filter(only_audio=True).first()
            if stream.filesize < 1000000000:
                size= dict()
                size["file"]= stream.filesize_mb
                out_file = stream.download()
                # save the file
                base, ext= os.path.splitext(out_file)
                new_file = base + "-VideoBro-" + '.mp3'
                os.rename(out_file, new_file)
                from django.http import FileResponse
            
                return  FileResponse(open(new_file,'rb'), as_attachment=True)
            else:
                return render(responses, 'main/audio.html', {'msg':'The Audio was too big for VideoBro'})
    except:
        return render(responses, 'main/audio.html', {'msg':'The Last Audio was not Downloaded'}) 
    return render(responses, 'main/audio.html')
def video(request):
    try:
        for fname in os.listdir():
            if fname.endswith('.mp4'):
                os.remove(fname)
        if request.method == 'POST':
            link = request.POST['link']

            
            
            from django.http import FileResponse
            stream=YouTube(link).streams.get_highest_resolution()
            if stream.filesize < 1000000000:
                
                out_file = stream.download(skip_existing=True)
                base, ext= os.path.splitext(out_file)
                new_file = base + "-VideoBro-" + '.mp4'
                os.rename(out_file, new_file)
                return FileResponse(open(new_file,'rb'), as_attachment=True)
            else:
                return render(request, 'main/video.html', {'msg':'The Video was too big for VideoBro'}) 
    except:
        return render(request, 'main/video.html', {'msg':'The Last Video was not Downloaded'})  
    return render(request, 'main/video.html')
from pytube import Playlist, YouTube
from django.http import FileResponse
def playlist(request):
    data = None
    # Remove the directory and all its contents
    try:
        if request.method == "POST": 
            link = request.POST['linkPlay']
            playlist = Playlist(link)   
            import re
            
                
            if len(playlist)<17:
                # Get the URLs of the videos to download
                import zipfile
                    # Create a list to store the downloaded files
                downloaded_files = []

                playlist._video_regex = re.compile(r'\"url\":\"(/watch\?v=[\w-]*)')
                    # Download the videos and store them in the list
                directorys = 'playlist/'
                os.makedirs(directorys, exist_ok=True)
                for url in playlist:
                    yt = YouTube(url)
                    video = yt.streams.filter(type='video', progressive=True, file_extension='mp4').order_by('resolution').desc().\
                            first()
                    file_path = os.path.join(directorys, f'{video.title}-VideoBro-.mp4')  # Set the desired file path and format
                    video.download(output_path='', filename=file_path)
                    downloaded_files.append(file_path)
                    # Create a zip file containing the downloaded files
                zip_file_path = os.path.join(directorys, 'VideoBro-Download.zip')  # Set the path for the ZIP file
                with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                    for file_path in downloaded_files:
                        zip_file.write(file_path)

                    # Send the zip file as a response
                response = FileResponse(open(zip_file_path, 'rb'), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="VideoBro-Download.zip"'
                return response
            else:
                return  render(request, 'main/playlist.html',{'msg': 'The Playlist is too long for VideoBro'})   
        if "linkPlay" in request.GET:
            url= request.GET.get('linkPlay')
            from bs4 import BeautifulSoup
            import requests
            import re
            import json
            
            links = Playlist(url)
            link = YouTube(url)
            url_pic = link.channel_url
            soup = BeautifulSoup(requests.get(url_pic, cookies={'CONSENT':'YES+1'}).text, 'html.parser')
            data = re.search(r"var ytInitialData = ({.*});", str(soup.prettify())).group(1)
            json_data = json.loads(data)
            channel_logo = json_data['header']['c4TabbedHeaderRenderer']['avatar']['thumbnails'][2]['url']
            urls= [links.title,links.owner,links.length,channel_logo,url_pic]
            video=[]
            for x in links:
                all = YouTube(x)
                data={
                    'title':all.title,
                    'author':all.author,
                    'x':all.thumbnail_url,
                    'link':all.watch_url,
                    'views':all.views,
                }
                video.append(data)
            data = dict()
            data["title"]=urls[0]
            data["length"]=urls[2]
            data["owner"]=urls[1]
            data["pic"]=urls[3]
            data["link"]=urls[4]
            return  render(request, 'main/playlist.html',{"data":data,'video':video})
    except:
        return render(request, 'main/playlist.html',{"msg":"VideoBro encountered a network error"})
    return  render(request, 'main/playlist.html')
def Explore(req):
    try:
        if req.method == 'POST':

            from isodate import parse_duration
            import requests
            
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            search_params = {
                'part':'snippet',
                'q': req.POST['real'],
                'key':'AIzaSyCjHpieWDVllIFCFC2yzgTbrSCNBYwpwk8',
                'maxResults':9,
                'type':'video',
                'chart':'mostPopular',
            }
            response = requests.get(search_url, params=search_params)

            ans = response.json()['items']
            long=[]
            for answers in ans:
                long.append(answers['id']['videoId'])
            video_url = 'https://www.googleapis.com/youtube/v3/videos'
            video_params={
            'key':'AIzaSyCjHpieWDVllIFCFC2yzgTbrSCNBYwpwk8',
            'part':'snippet,contentDetails',
            'id':','.join(long),
            'maxResults':9,
            }
            r = requests.get(video_url, params=video_params)
            res = r.json()['items']

            videos = []
            for result in res:
                video_data = {
                    'title':result['snippet']['title'],
                    'id':result['id'],
                    'url': f'https://www.youtube.com/watch?v={ result["id"] }',
                    'duration': parse_duration(result['contentDetails']['duration']),
                    'thumbnail':result['snippet']['thumbnails']['high']['url'],
                    'description': result['snippet']['description'],
                    'owner':result['snippet']['channelTitle'],     
                }
                videos.append(video_data)
            context ={
                'videos':videos
            }
            return render(req, 'main/explore.html', context)
    except:
        return render(req, 'main/explore.html', {'msg': "VideoBro couldn't connect to Youtube"})
    return render(req, 'main/explore.html')
    
def help(sos):
    return render(sos, 'main/Help.html')
def instagram(request):
    try:
        for fname in os.listdir():
            if fname.endswith('.mp4'):
                os.remove(fname)
        if request.method == "POST":
            directory = 'IG'
            os.makedirs(directory, exist_ok=True)
            import instaloader
            loader = instaloader.Instaloader()
            url = request.POST['answers']

            post_id = url.split("/")[-2]
            post = instaloader.Post.from_shortcode(loader.context, post_id)
            if post.get_is_videos():
                loader.download_post(post, target=directory)

                # Set the video file path
                for files in os.listdir():
                    if files=='IG':
                        for f in os.listdir(files):
                            if f.endswith('_UTC.mp4'):
                                all = os.path.join(os.getcwd(),f'IG\{f}')
                                video_file = open(all, 'rb')
                                response = FileResponse(video_file, content_type='video/mp4')
                                response['Content-Disposition'] = 'attachment; filename="VideoBro-Instagram.mp4"'
                                return response
    except:
        return render(request, 'main/instagram.html', {'msg':"Error in downloading Instagram Video"})
    return render(request, 'main/instagram.html')
#*j,Qgdei2RR?PR7
from django.shortcuts import render, redirect
from .models import Review
from .forms import ReviewForm

def review_page(request):
    try:
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('review')
        else:
            form = ReviewForm()
        reviews = Review.objects.order_by('-created_at')
        context = {'form': form, 'reviews': reviews}
    except:
        context = {'form': form, 'reviews': reviews, 'msg':'VideoBro encountered an Internal Server Error'}
        return render(request, 'main/review.html', context)
    return render(request, 'main/review.html', context)
def tiktok(requests1):
    try:
        if "answer" in requests1.POST:
            url = requests1.POST['answer']
            from urllib.request import urlopen
        
            import time
            from bs4 import BeautifulSoup
            import requests

            cookies = {
                '_gid': 'GA1.2.945598809.1686700245',
                '__gads': 'ID=bdf077c205c0e73a-22af5b8b30e00027:T=1686700249:RT=1686700249:S=ALNI_MZ1bGt6_uN_sOsrQ--HBityQpM2qA',
                '__gpi': 'UID=00000c4e9f6f9854:T=1686700249:RT=1686700249:S=ALNI_MZYhhWHiM8LDiqxUT5AJXylv5lyJw',
                '__cflb': '0H28v8EEysMCvTTqtu4kewtscz2STFoq6qG8bN6EZYH',
                '_ga': 'GA1.2.764753617.1686700245',
                '_gat_UA-3524196-6': '1',
                '_ga_ZSF3D6YSLC': 'GS1.1.1686700244.1.1.1686700385.0.0.0',
            }

            headers = {
                'authority': 'ssstik.io',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'cookie': '_gid=GA1.2.945598809.1686700245; __gads=ID=bdf077c205c0e73a-22af5b8b30e00027:T=1686700249:RT=1686700249:S=ALNI_MZ1bGt6_uN_sOsrQ--HBityQpM2qA; __gpi=UID=00000c4e9f6f9854:T=1686700249:RT=1686700249:S=ALNI_MZYhhWHiM8LDiqxUT5AJXylv5lyJw; __cflb=0H28v8EEysMCvTTqtu4kewtscz2STFoq6qG8bN6EZYH; _ga=GA1.2.764753617.1686700245; _gat_UA-3524196-6=1; _ga_ZSF3D6YSLC=GS1.1.1686700244.1.1.1686700385.0.0.0',
                'hx-current-url': 'https://ssstik.io/en',
                'hx-request': 'true',
                'hx-target': 'target',
                'hx-trigger': '_gcaptcha_pt',
                'origin': 'https://ssstik.io',
                'referer': 'https://ssstik.io/en',
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }

            params = {
                'url': 'dl',
            }

            data = {
                'id': url,
                'locale': 'en',
                'tt': 'VndnSko1',
            }

            response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)

            downloadSoup = BeautifulSoup(response.text,"html.parser")
            downloadlink = downloadSoup.a["href"]
        
            data = dict()
            data['link']=downloadlink
            return render(requests1, 'main/tiktok.html',{'data':data})
    except:        
        return render(requests1, 'main/tiktok.html',{'msg':'Error in downloading Tiktok Video'})
    return render(requests1, 'main/tiktok.html')

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('review')


      		