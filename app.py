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

PAGES_TO_FETCH_PER_RUN = 30 

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
                        
                        time.sleep(0.02)
                        ext_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
                        ext_res = requests.get(ext_url).json()
                        imdb_id = ext_res.get("imdb_id")
                        
                        if imdb_id and tmdb_id not in existing_ids:
                            # HIGH SPEED DOWNLOAD SOURCES (TORRENT / FAST DL LINKS)
                            dl_url_1 = f"https://vidsrc.cc/v2/embed/movie/{imdb_id}"
                            dl_url_2 = f"https://embed.su/embed/movie/{imdb_id}"
                            
                            newItem = {
                                "id": tmdb_id,
                                "title": title,
                                "year": year,
                                "overview": overview,
                                "poster": poster,
                                "backdrop": backdrop,
                                "imdb_id": imdb_id,
                                "dl_url_1": dl_url_1,
                                "dl_url_2": dl_url_2,
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
    <title>Film360 - Movie Download Portal</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23E50914'/><text x='50%' y='55%' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='70' font-family='Arial, sans-serif' font-weight='bold'>F</text></svg>">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ background-color: #0b0b0b; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; }}
        
        .header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 25px; gap: 15px; }}
        h1 {{ color: #E50914; margin: 0; font-size: 30px; letter-spacing: 1px; font-weight: 800; }}
        .search-box {{ padding: 12px 20px; width: 320px; background: #161616; border: 1px solid #282828; color: white; border-radius: 8px; font-size: 14px; outline: none; transition: all 0.3s; }}
        .search-box:focus {{ border-color: #E50914; box-shadow: 0 0 10px rgba(229,9,20,0.2); }}

        .categories {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 30px; overflow-x: auto; padding-bottom: 5px; }}
        .cat-btn {{ background: #161616; color: #aaa; border: 1px solid #282828; padding: 9px 18px; border-radius: 25px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s; }}
        .cat-btn.active, .cat-btn:hover {{ background: #E50914; color: white; border-color: #E50914; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }}
        .card {{ background: #161616; border-radius: 10px; overflow: hidden; cursor: pointer; transition: transform 0.25s, box-shadow 0.25s; position: relative; border: 1px solid #222; }}
        .card:hover {{ transform: translateY(-6px); box-shadow: 0 10px 25px rgba(0,0,0,0.8); border-color: #444; }}
        .card img {{ width: 100%; height: 230px; object-fit: cover; display: block; background: #222; }}
        .card-info {{ padding: 12px; font-size: 12px; }}
        .badge {{ background: #E50914; font-size: 9px; padding: 3px 7px; border-radius: 4px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-title {{ margin-top: 8px; display: block; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #eaeaea; font-size: 13px; }}

        .load-more-container {{ text-align: center; margin: 40px 0; }}
        .load-btn {{ background: #161616; color: white; border: 1px solid #333; padding: 12px 40px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.2s; }}
        .load-btn:hover {{ background: #E50914; border-color: #E50914; }}

        /* Modal Details & Download Center */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.88); overflow-y: auto; backdrop-filter: blur(6px); }}
        .modal-content {{ background: #141414; margin: 30px auto; width: 92%; max-width: 850px; border-radius: 12px; overflow: hidden; position: relative; box-shadow: 0 20px 40px rgba(0,0,0,0.9); border: 1px solid #262626; }}
        .close {{ position: absolute; right: 18px; top: 18px; color: white; font-size: 22px; cursor: pointer; z-index: 10; background: rgba(0,0,0,0.7); width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: 0.2s; }}
        .close:hover {{ background: #E50914; }}
        
        .modal-banner {{ position: relative; width: 100%; height: 380px; background-size: cover; background-position: center; }}
        .modal-banner::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 160px; background: linear-gradient(to top, #141414, transparent); }}
        .modal-banner-content {{ position: absolute; bottom: 20px; left: 25px; z-index: 2; width: calc(100% - 50px); }}
        .modal-title {{ font-size: 28px; font-weight: bold; margin-bottom: 12px; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); }}
        
        /* Download Action Buttons Deck */
        .download-deck {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }}
        .download-btn {{ background: #E50914; color: white; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; text-decoration: none; transition: 0.2s; box-shadow: 0 4px 15px rgba(229,9,20,0.4); }}
        .download-btn:hover {{ background: #b20710; transform: translateY(-2px); }}
        .download-btn.secondary {{ background: #222; border: 1px solid #444; box-shadow: none; }}
        .download-btn.secondary:hover {{ background: #333; }}

        .modal-body {{ padding: 25px; }}
        .meta-row {{ display: flex; gap: 15px; align-items: center; font-size: 13px; margin-bottom: 15px; color: #46d369; font-weight: bold; }}
        .overview {{ font-size: 14px; line-height: 1.6; color: #b8b8b8; margin-bottom: 25px; }}

        .similar-section {{ margin-top: 25px; border-top: 1px solid #222; padding-top: 20px; }}
        .similar-title {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
        .similar-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }}
        .similar-card {{ background: #1a1a1a; border-radius: 6px; overflow: hidden; cursor: pointer; transition: 0.2s; border: 1px solid #2a2a2a; }}
        .similar-card:hover {{ transform: scale(1.04); }}
        .similar-card img {{ width: 100%; height: 160px; object-fit: cover; }}
        .similar-info {{ padding: 6px; font-size: 11px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>FILM360</h1>
        <input type="text" id="searchInput" class="search-box" placeholder="Search movies to download..." onkeyup="filterContent()">
    </div>

    <div class="categories">
        <button class="cat-btn active" onclick="setCategory('All', this)">All Movies</button>
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
                    <div class="download-deck">
                        <a id="dlLink1" href="#" target="_blank" class="download-btn">&#11015; High Speed Download (Server 1)</a>
                        <a id="dlLink2" href="#" target="_blank" class="download-btn secondary">&#11015; Mirror Download (Server 2)</a>
                    </div>
                </div>
            </div>
            <div class="modal-body">
                <div class="meta-row">
                    <span id="modalYear"></span>
                    <span class="badge" id="modalCategoryBadge"></span>
                </div>
                <div class="overview" id="modalOverview"></div>
                <div class="similar-section">
                    <div class="similar-title">More Like This</div>
                    <div class="similar-grid" id="similarGrid"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const allMovies = {movies_json};
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
                        <span class="badge">${{m.category}}</span>
                        <span class="card-title" title="${{m.title}}">${{m.title}}</span>
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
            document.getElementById('modalBanner').style.backgroundImage = `url('${{movie.backdrop}}')`;
            document.getElementById('modalTitle').innerText = movie.title;
            document.getElementById('modalYear').innerText = movie.year;
            document.getElementById('modalCategoryBadge').innerText = movie.category;
            document.getElementById('modalOverview').innerText = movie.overview;

            // Set direct download links
            document.getElementById('dlLink1').href = movie.dl_url_1;
            document.getElementById('dlLink2').href = movie.dl_url_2;

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

        renderGrid();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Download-focused script generated successfully!")
