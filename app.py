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

# Cloud run ke liye pages limit (GitHub Actions timeout se bachne ke liye per run 30-50 pages best hain)
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
        print(f"\n--- Fetching {category} from Page {start_page} to {end_page - 1} ---")
        
        for page in range(start_page, end_page):
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language={lang}&sort_by=popularity.desc&page={page}"
            
            try:
                response = requests.get(url)
                if response.status_code == 429:
                    print("Rate limit hit! Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                    
                if response.status_code == 200:
                    res = response.json()
                    results = res.get("results", [])
                    if not results:
                        print(f"No more pages for {category}.")
                        break
                        
                    for item in results:
                        title = item.get("title")
                        poster_path = item.get('poster_path')
                        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750"
                        tmdb_id = item.get("id")
                        
                        time.sleep(0.15)
                        ext_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
                        ext_res = requests.get(ext_url).json()
                        imdb_id = ext_res.get("imdb_id")
                        
                        if imdb_id and tmdb_id not in existing_ids:
                            stream_url = f"https://vidsrc.to/embed/movie/{imdb_id}"
                            alt_url = f"https://vidsrc.icu/embed/movie/{imdb_id}"
                            
                            newItem = {
                                "id": tmdb_id,
                                "title": title,
                                "poster": poster,
                                "stream_url": stream_url,
                                "alt_url": alt_url,
                                "category": category,
                                "type": "MOVIE"
                            }
                            brand_new_items.append(newItem)
                            existing_ids.add(tmdb_id)
                            
                print(f"Fetched {category} Page {page} successfully.")
                category_pages[category] = page + 1
                time.sleep(0.2)
            except Exception as e:
                print(f"Error fetching {category} page {page}: {e}")
                time.sleep(2)
                
    updated_data = brand_new_items + existing_data
    
    progress["category_pages"] = category_pages
    progress["data"] = updated_data
    save_progress(progress)
    
    print(f"\nAdded {len(brand_new_items)} new movies. Total library size: {len(updated_data)}")
    return updated_data

existing_data = fetch_all_deep_data()

# HTML & Frontend Generation
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Film360 - Streaming Portal</title>
    <style>
        body {{ background-color: #141414; color: white; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 15px; }}
        h1 {{ color: #E50914; margin: 0; font-size: 30px; }}
        .search-box {{ padding: 10px 15px; width: 280px; background: #222; border: 1px solid #444; color: white; border-radius: 4px; }}
        .categories {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
        .cat-btn {{ background: #222; color: white; border: 1px solid #444; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
        .cat-btn.active, .cat-btn:hover {{ background: #E50914; border-color: #E50914; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; }}
        .card {{ background: #222; border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform 0.2s; display: none; }}
        .card.visible {{ display: block; }}
        .card:hover {{ transform: scale(1.05); }}
        .card img {{ width: 100%; height: 230px; object-fit: cover; }}
        .card-info {{ padding: 10px; font-size: 13px; text-align: center; }}
        .badge {{ background: #E50914; font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; }}
        .load-more-container {{ text-align: center; margin: 30px 0; }}
        .load-btn {{ background: #E50914; color: white; border: none; padding: 12px 30px; font-size: 16px; font-weight: bold; border-radius: 4px; cursor: pointer; }}
        .load-btn:hover {{ background: #b20710; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); }}
        .modal-content {{ position: relative; margin: 3% auto; width: 90%; max-width: 900px; }}
        .close {{ position: absolute; right: -15px; top: -35px; color: white; font-size: 35px; cursor: pointer; }}
        .server-btns {{ margin-bottom: 10px; text-align: center; }}
        .server-btn {{ background: #333; color: white; border: none; padding: 8px 15px; margin: 0 5px; cursor: pointer; border-radius: 4px; font-weight: bold; }}
        .server-btn.active {{ background: #E50914; }}
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

    <div class="grid" id="movieGrid">
"""

for item in existing_data:
    html_content += f"""
        <div class="card" data-title="{item['title'].lower()}" data-category="{item['category']}" onclick="openPlayer('{item['stream_url']}', '{item['alt_url']}')">
            <img src="{item['poster']}" alt="{item['title']}">
            <div class="card-info">
                <span class="badge">{item['category']}</span><br>
                <strong style="margin-top:5px; display:block;">{item['title']}</strong>
            </div>
        </div>
    """

html_content += """
    </div>

    <div class="load-more-container" id="loadMoreContainer">
        <button class="load-btn" onclick="loadMore()">Load More</button>
    </div>

    <div id="playerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closePlayer()">&times;</span>
            <div class="server-btns">
                <button class="server-btn active" id="btn1" onclick="switchServer(currentUrl1, 'btn1')">Server 1</button>
                <button class="server-btn" id="btn2" onclick="switchServer(currentUrl2, 'btn2')">Server 2 (Dubbed/Multi-Audio)</button>
            </div>
            <div style="position:relative; padding-bottom:56.25%; height:0;">
                <iframe id="videoIframe" src="" style="position:absolute; top:0; left:0; width:100%; height:100%;" frameborder="0" allowfullscreen></iframe>
            </div>
        </div>
    </div>

    <script>
        let currentUrl1 = '';
        let currentUrl2 = '';
        let itemsToShow = 36;
        let currentCategory = 'All';

        function renderGrid() {
            let cards = document.getElementsByClassName('card');
            let searchInput = document.getElementById('searchInput').value.toLowerCase();
            let totalMatching = 0;

            for (let i = 0; i < cards.length; i++) {
                let card = cards[i];
                let title = card.getAttribute('data-title');
                let category = card.getAttribute('data-category');

                let matchesCategory = (currentCategory === 'All' || category === currentCategory);
                let matchesSearch = title.includes(searchInput);

                if (matchesCategory && matchesSearch) {
                    totalMatching++;
                    if (totalMatching <= itemsToShow) {
                        card.classList.add('visible');
                    } else {
                        card.classList.remove('visible');
                    }
                } else {
                    card.classList.remove('visible');
                }
            }

            let loadBtn = document.getElementById('loadMoreContainer');
            if (totalMatching > itemsToShow && searchInput === '') {
                loadBtn.style.display = 'block';
            } else {
                loadBtn.style.display = 'none';
            }
        }

        function loadMore() {
            itemsToShow += 36;
            renderGrid();
        }

        function setCategory(cat, btn) {
            currentCategory = cat;
            itemsToShow = 36;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderGrid();
        }

        function filterContent() {
            itemsToShow = 36;
            renderGrid();
        }

        function openPlayer(url1, url2) {
            currentUrl1 = url1;
            currentUrl2 = url2;
            switchServer(url1, 'btn1');
            document.getElementById('playerModal').style.display = 'block';
        }

        function switchServer(url, btnId) {
            document.getElementById('videoIframe').src = url;
            document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(btnId).classList.add('active');
        }

        function closePlayer() {
            document.getElementById('videoIframe').src = '';
            document.getElementById('playerModal').style.display = 'none';
        }

        renderGrid();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML and progress updated successfully for Cloud runner.")
