import ee, os, requests, zipfile, io
from tqdm import tqdm

# ---- EDIT THESE TWO LINES ----
PROJECT_ID = 'blue-carbon-project-475409'  # your EE Cloud Project
ASSET_FOLDER = 'projects/blue-carbon-project-475409/assets'  # or subfolder path if you use one
NAME_PREFIX = 'CHIRPSv2_BantenBox_daily_2024_01_'  # filter (leave '' to get everything)
# --------------------------------

def main():
    ee.Authenticate()                       # first-run opens a browser for login
    ee.Initialize(project='blue-carbon-project-475409')       # use your EE Cloud Project

    # Create output folder
    out_dir = 'downloads'
    os.makedirs(out_dir, exist_ok=True)

    # List assets under the folder
    resp = ee.data.listAssets({'parent': ASSET_FOLDER})
    assets = resp.get('assets', [])
    targets = [a for a in assets
               if a.get('type') == 'IMAGE' and a['name'].split('/')[-1].startswith(NAME_PREFIX)]
    print(f'Found {len(assets)} assets; downloading {len(targets)} images matching prefix "{NAME_PREFIX}".')

    # Download each image
    for a in tqdm(sorted(targets, key=lambda x: x['name'])):
        asset_id = a['name']
        img_name = asset_id.split('/')[-1]
        out_path = os.path.join(out_dir, f'{img_name}.tif')

        img = ee.Image(asset_id)
        url = img.getDownloadURL({'crs': 'EPSG:4326', 'scale': 5000})
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)

    # Zip everything for convenience
    zip_path = 'CHIRPS_downloads.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fn in os.listdir(out_dir):
            zf.write(os.path.join(out_dir, fn), arcname=fn)
    print(f'✅ Done. Saved individual TIFFs in "{out_dir}/" and a zip at "{zip_path}".')

if __name__ == '__main__':
    main()

