import requests
import json
import os
import time

TMDB_API_KEY = "b08b360b32514449d5f98ff244e62b1b"

def fetch_media_with_rate_limit(media_type="movie", pages=10):
    media_list = []
    
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/{media_type}/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        
        try:
            response = requests.get(url)
            
            # Agar API rate limit hit ho jaye (HTTP 429)
            if response.status_code == 429:
                print("Rate limit hit! Script 5 seconds ke liye pause ho rahi hai...")
                time.sleep(5)
                continue
                
            res = response.json()
            
            if "results" in res:
                for item in res["results"]:
                    title = item.get("title") or item.get("name")
                    poster_path = item.get('poster_path')
                    poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750"
                    tmdb_id = item.get("id")
                    
                    # External ID request se pehle chota delay
                    time.sleep(0.25) # 250ms delay (safely stays under 40 reqs / 10 sec)
                    
                    ext_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
                    ext_res = requests.get(ext_url).json()
                    imdb_id = ext_res.get("imdb_id")
                    
                    if imdb_id:
                        if media_type == "movie":
                            stream_url = f"https://vidsrc.to/embed/movie/{imdb_id}"
                        else:
                            stream_url = f"https://vidsrc.to/embed/tv/{imdb_id}/1/1"
                            
                        media_list.append({
                            "title": title,
                            "poster": poster,
                            "stream_url": stream_url,
                            "type": media_type.upper()
                        })
                        
            print(f"Fetched Page {page} of {media_type}s successfully.")
            time.sleep(0.3) # Extra delay between pages
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            time.sleep(2)
            
    return media_list

# Main Execution
print("Rate-limited fetching started...")
movies = fetch_media_with_rate_limit("movie", pages=10) # 10 Pages = ~200 Movies
series = fetch_media_with_rate_limit("tv", pages=10)    # 10 Pages = ~200 Shows
all_data = movies + series

# HTML Generation Logic
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Film360 - Large Catalogue</title>
    <style>
        body {{ background-color: #141414; color: white; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        h1 {{ color: #E50914; margin-bottom: 20px; font-size: 32px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }}
        .card {{ background: #222; border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform 0.2s; }}
        .card:hover {{ transform: scale(1.05); }}
        .card img {{ width: 100%; height: 240px; object-fit: cover; }}
        .card-info {{ padding: 10px; font-size: 13px; text-align: center; }}
        .badge {{ background: #E50914; font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); }}
        .modal-content {{ position: relative; margin: 5% auto; width: 90%; max-width: 850px; }}
        .close {{ position: absolute; right: -15px; top: -35px; color: white; font-size: 35px; cursor: pointer; }}
    </style>
</head>
<body>

    <h1>FILM360 ({len(all_data)} Items)</h1>
    <div class="grid">
"""

for item in all_data:
    html_content += f"""
        <div class="card" onclick="openPlayer('{item['stream_url']}')">
            <img src="{item['poster']}" alt="{item['title']}">
            <div class="card-info">
                <span class="badge">{item['type']}</span><br>
                <strong style="margin-top:5px; display:block;">{item['title']}</strong>
            </div>
        </div>
    """

html_content += """
    </div>

    <div id="playerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closePlayer()">&times;</span>
            <div style="position:relative; padding-bottom:56.25%; height:0;">
                <iframe id="videoIframe" src="" style="position:absolute; top:0; left:0; width:100%; height:100%;" frameborder="0" allowfullscreen></iframe>
            </div>
        </div>
    </div>

    <script>
        function openPlayer(url) {
            document.getElementById('videoIframe').src = url;
            document.getElementById('playerModal').style.display = 'block';
        }
        function closePlayer() {
            document.getElementById('videoIframe').src = '';
            document.getElementById('playerModal').style.display = 'none';
        }
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

os.system("git add .")
os.system('git commit -m "Updated Film360 with rate limiting control"')
os.system("git push origin main")
print("Process completed successfully!")