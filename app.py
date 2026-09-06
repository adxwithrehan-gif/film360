import requests
import json
import os
import time

TMDB_API_KEY = "b08b360b32514449d5f98ff244e62b1b"
TRACKER_FILE = "progress.json"

LANG_CATEGORIES = {
    "Hollywood": "en",
    "Bollywood": "hi",
    "Tollywood": "te",
    "Kollywood": "ta",
    "Lollywood": "ur"
}

PAGES_TO_FETCH_PER_RUN = 50 

def load_progress():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {
        "category_pages": {cat: 1 for cat in LANG_CATEGORIES},
        "data": []
    }

def save_progress(progress):
    with open(TRACKER_FILE, "w") as f:
        json.dump(progress, f, indent=4)

def fetch_all_deep_data():
    progress = load_progress()
    existing_data = progress.get("data", [])
    existing_ids = {item["id"] for item in existing_data}
    category_pages = progress["category_pages"]
    
    brand_new_items = []

    for category, lang in LANG_CATEGORIES.items():
        start_page = category_pages.get(category, 1)
        end_page = start_page + PAGES_TO_FETCH_PER_RUN
        print(f"\n--- Fetching {category} from Page {start_page} to {end_page - 1} ---")
        
        for page in range(start_page, end_page):
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language={lang}&primary_release_date.gte=2020-01-01&primary_release_date.lte=2026-12-31&sort_by=popularity.desc&page={page}"
            
            try:
                response = requests.get(url)
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                    
                if response.status_code == 200:
                    res = response.json()
                    results = res.get("results", [])
                    if not results:
                        break
                        
                    for item in results:
                        title = item.get("title")
                        poster_path = item.get('poster_path')
                        backdrop_path = item.get('backdrop_path')
                        overview = item.get('overview', 'No description available.')
                        release_date = item.get('release_date', '2026')
                        year = release_date.split('-')[0] if release_date else '2026'
                        
                        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750"
                        backdrop = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else poster
                        tmdb_id = item.get("id")
                        
                        time.sleep(0.05)
                        ext_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
                        ext_res = requests.get(ext_url).json()
                        imdb_id = ext_res.get("imdb_id")
                        
                        if imdb_id and tmdb_id not in existing_ids:
                            # 100% WORKING & ACTIVE MULTI-AUDIO / MULTI-SERVER CONFIG
                            stream_url = f"https://multiembed.mov/?video_id={imdb_id}&tmdb=1"
                            alt_url = f"https://vidsrc.su/embed/movie/{imdb_id}"
                            third_url = f"https://embed.su/embed/movie/{imdb_id}"
                            
                            newItem = {
                                "id": tmdb_id,
                                "title": title,
                                "year": year,
                                "overview": overview,
                                "poster": poster,
                                "backdrop": backdrop,
                                "stream_url": stream_url,
                                "alt_url": alt_url,
                                "third_url": third_url,
                                "category": category,
                                "type": "MOVIE"
                            }
                            brand_new_items.append(newItem)
                            existing_ids.add(tmdb_id)
                            
                    category_pages[category] = page + 1
            except Exception as e:
                print(f"Error: {e}")
                
    updated_data = brand_new_items + existing_data
    progress["category_pages"] = category_pages
    progress["data"] = updated_data
    save_progress(progress)
    return updated_data

existing_data = fetch_all_deep_data()
movies_json = json.dumps(existing_data)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Film360 - Multi-Audio Streaming Portal</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23E50914'/><text x='50%' y='55%' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='70' font-family='Arial, sans-serif' font-weight='bold'>F</text></svg>">
    <style>
        body {{ background-color: #141414; color: white; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 15px; }}
        h1 {{ color: #E50914; margin: 0; font-size: 30px; }}
        .search-box {{ padding: 10px 15px; width: 280px; background: #222; border: 1px solid #444; color: white; border-radius: 4px; }}
        .categories {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
        .cat-btn {{ background: #222; color: white; border: 1px solid #444; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
        .cat-btn.active, .cat-btn:hover {{ background: #E50914; border-color: #E50914; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }}
        .card {{ background: #222; border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform 0.2s; }}
        .card:hover {{ transform: scale(1.05); }}
        .card img {{ width: 100%; height: 230px; object-fit: cover; }}
        .card-info {{ padding: 10px; font-size: 13px; text-align: center; }}
        .badge {{ background: #E50914; font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }}
        .load-more-container {{ text-align: center; margin: 30px 0; }}
        .load-btn {{ background: #E50914; color: white; border: none; padding: 12px 30px; font-size: 16px; font-weight: bold; border-radius: 4px; cursor: pointer; }}
        .load-btn:hover {{ background: #b20710; }}

        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); overflow-y: auto; }}
        .modal-content {{ background: #181818; margin: 40px auto; width: 90%; max-width: 850px; border-radius: 8px; overflow: hidden; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }}
        .close {{ position: absolute; right: 15px; top: 15px; color: white; font-size: 30px; cursor: pointer; z-index: 10; background: rgba(0,0,0,0.5); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
        
        .modal-banner {{ position: relative; width: 100%; height: 400px; background-size: cover; background-position: center; }}
        .modal-banner::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 150px; background: linear-gradient(to top, #181818, transparent); }}
        .modal-banner-content {{ position: absolute; bottom: 20px; left: 30px; z-index: 2; }}
        .modal-title {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }}
        
        .play-btn {{ background: white; color: black; border: none; padding: 10px 25px; font-size: 16px; font-weight: bold; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }}
        .play-btn:hover {{ background: rgba(255,255,255,0.75); }}

        .modal-body {{ padding: 30px; }}
        .meta-row {{ display: flex; gap: 15px; align-items: center; font-size: 14px; margin-bottom: 15px; color: #46d369; font-weight: bold; }}
        .overview {{ font-size: 15px; line-height: 1.6; color: #d2d2d2; margin-bottom: 25px; }}

        .similar-section {{ margin-top: 30px; }}
        .similar-title {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
        .similar-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; }}
        .similar-card {{ background: #222; border-radius: 4px; overflow: hidden; cursor: pointer; transition: 0.2s; }}
        .similar-card:hover {{ transform: scale(1.05); }}
        .similar-card img {{ width: 100%; height: 180px; object-fit: cover; }}
        .similar-info {{ padding: 8px; font-size: 12px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

        .player-modal {{ display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); }}
        .player-content {{ position: relative; margin: 3% auto; width: 90%; max-width: 900px; }}
        .player-close {{ position: absolute; right: -15px; top: -35px; color: white; font-size: 35px; cursor: pointer; z-index: 10; }}
        .server-btns {{ margin-bottom: 10px; text-align: center; }}
        .server-btn {{ background: #333; color: white; border: none; padding: 8px 15px; margin: 0 5px; cursor: pointer; border-radius: 4px; font-weight: bold; }}
        .server-btn.active {{ background: #E50914; }}
        
        .player-wrapper {{ position: relative; width: 100%; padding-bottom: 56.25%; height: 0; }}
        
        .click-shield {{ 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; 
            background: rgba(0,0,0,0.6); display: flex; flex-direction: column; 
            align-items: center; justify-content: center; cursor: pointer; 
            text-align: center; transition: background 0.3s;
        }}
        .click-shield:hover {{ background: rgba(0,0,0,0.4); }}
        .shield-btn {{
            background: #E50914; color: white; border: none; padding: 14px 28px;
            font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.6); pointer-events: none;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>FILM360</h1>
        <input type="text" id="searchInput" class="search-box" placeholder="Search movies..." onkeyup="filterContent()">
    </div>

    <div class="categories">
        <button class="cat-btn active" onclick="setCategory('All', this)">All (Latest on Top)</button>
        <button class="cat-btn" onclick="setCategory('Hollywood', this)">Hollywood</button>
        <button class="cat-btn" onclick="setCategory('Bollywood', this)">Bollywood</button>
        <button class="cat-btn" onclick="setCategory('Tollywood', this)">Tollywood</button>
        <button class="cat-btn" onclick="setCategory('Kollywood', this)">Kollywood</button>
        <button class="cat-btn" onclick="setCategory('Lollywood', this)">Lollywood</button>
    </div>

    <div class="grid" id="movieGrid"></div>

    <div class="load-more-container" id="loadMoreContainer">
        <button class="load-btn" onclick="loadMore()">Load More</button>
    </div>

    <div id="detailsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeDetails()">&times;</span>
            <div id="modalBanner" class="modal-banner">
                <div class="modal-banner-content">
                    <div id="modalTitle" class="modal-title"></div>
                    <button class="play-btn" onclick="playCurrentMovie()">&#9658; Play</button>
                </div>
            </div>
            <div class="modal-body">
                <div class="meta-row">
                    <span id="modalYear"></span>
                    <span class="badge" id="modalCategoryBadge" style="font-size: 11px;"></span>
                </div>
                <div class="overview" id="modalOverview"></div>
                <div class="similar-section">
                    <div class="similar-title">More Like This</div>
                    <div class="similar-grid" id="similarGrid"></div>
                </div>
            </div>
        </div>
    </div>

    <div id="playerModal" class="player-modal">
        <div class="player-content">
            <span class="player-close" onclick="closePlayer()">&times;</span>
            <div class="server-btns">
                <button class="server-btn active" id="btn1" onclick="switchServer(currentUrl1, 'btn1')">Server 1 (MultiEmbed)</button>
                <button class="server-btn" id="btn2" onclick="switchServer(currentUrl2, 'btn2')">Server 2 (Vidsrc.su)</button>
                <button class="server-btn" id="btn3" onclick="switchServer(currentUrl3, 'btn3')">Server 3 (Embed.su)</button>
            </div>
            <div class="player-wrapper">
                <div id="clickShield" class="click-shield" onclick="removeShield()">
                    <button class="shield-btn">&#9658; Click to Watch Movie</button>
                    <p style="color: #fff; font-size: 13px; margin-top: 10px; text-shadow: 1px 1px 2px #000;">Click anywhere to start player</p>
                </div>
                <iframe id="videoIframe" src="" style="position:absolute; top:0; left:0; width:100%; height:100%;" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
            </div>
        </div>
    </div>

    <script>
        const allMovies = {movies_json};
        let currentMovie = null;
        let currentUrl1 = '';
        let currentUrl2 = '';
        let currentUrl3 = '';
        let itemsToShow = 36;
        let currentCategory = 'All';

        function renderGrid() {{
            const grid = document.getElementById('movieGrid');
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            
            let filtered = allMovies.filter(m => {{
                let matchesCategory = (currentCategory === 'All' || m.category === currentCategory);
                let matchesSearch = m.title.toLowerCase().includes(searchInput);
                return matchesCategory && matchesSearch;
            }});

            let paginated = filtered.slice(0, itemsToShow);
            
            grid.innerHTML = paginated.map(m => `
                <div class="card" onclick='openDetails({{JSON.stringify(m).replace(/'/g, "&#39;")}})'>
                    <img src="${{m.poster}}" alt="${{m.title}}" loading="lazy">
                    <div class="card-info">
                        <span class="badge">${{m.category}}</span><br>
                        <strong style="margin-top:5px; display:block;">${{m.title}}</strong>
                    </div>
                </div>
            `).join('');

            let loadBtn = document.getElementById('loadMoreContainer');
            if (filtered.length > itemsToShow && searchInput === '') {{
                loadBtn.style.display = 'block';
            }} else {{
                loadBtn.style.display = 'none';
            }}
        }}

        function loadMore() {{
            itemsToShow += 36;
            renderGrid();
        }}

        function setCategory(cat, btn) {{
            currentCategory = cat;
            itemsToShow = 36;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderGrid();
        }}

        function filterContent() {{
            itemsToShow = 36;
            renderGrid();
        }}

        function openDetails(movie) {{
            currentMovie = movie;
            document.getElementById('modalBanner').style.backgroundImage = `url('${{movie.backdrop}}')`;
            document.getElementById('modalTitle').innerText = movie.title;
            document.getElementById('modalYear').innerText = movie.year;
            document.getElementById('modalCategoryBadge').innerText = movie.category;
            document.getElementById('modalOverview').innerText = movie.overview;

            let similarContainer = document.getElementById('similarGrid');
            let filteredSimilar = allMovies.filter(m => m.category === movie.category && m.id !== movie.id).slice(0, 6);
            
            similarContainer.innerHTML = filteredSimilar.map(sim => `
                <div class="similar-card" onclick='openDetails({{JSON.stringify(sim).replace(/'/g, "&#39;")}})'>
                    <img src="${{sim.poster}}" alt="${{sim.title}}" loading="lazy">
                    <div class="similar-info">${{sim.title}}</div>
                </div>
            `).join('');

            document.getElementById('detailsModal').style.display = 'block';
        }}

        function closeDetails() {{
            document.getElementById('detailsModal').style.display = 'none';
        }}

        function playCurrentMovie() {{
            if (!currentMovie) return;
            
            currentUrl1 = currentMovie.stream_url;
            currentUrl2 = currentMovie.alt_url;
            currentUrl3 = currentMovie.third_url;
            
            document.getElementById('clickShield').style.display = 'flex';
            switchServer(currentUrl1, 'btn1');
            document.getElementById('playerModal').style.display = 'block';
        }}

        function removeShield() {{
            document.getElementById('clickShield').style.display = 'none';
        }}

        function switchServer(url, btnId) {{
            document.getElementById('clickShield').style.display = 'flex';
            document.getElementById('videoIframe').src = url;
            document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(btnId).classList.add('active');
        }}

        function closePlayer() {{
            document.getElementById('videoIframe').src = '';
            document.getElementById('playerModal').style.display = 'none';
        }}

        renderGrid();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated server links successfully!")
