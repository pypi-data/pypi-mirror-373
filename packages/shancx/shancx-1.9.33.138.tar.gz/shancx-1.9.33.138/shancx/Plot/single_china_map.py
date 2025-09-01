import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import datetime
import os

def add_china_map(ax):
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)
    provinces = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')   ###自动下载 
    provinces_features = shpreader.Reader(provinces).geometries()
    """
    本地路径读取 #'/home/scx/.local/share/cartopy/shapefiles/natural_earth/cultural/ne_10m_admin_1_states_provinces.shp'   #ne_10m_admin_1_states_provinces.shx 
    # shapefile_path = '/home/scx/.local/share/cartopy/shapefiles/natural_earth/cultural/admin_1_states_provinces.shp'
    # provinces_features = shpreader.Reader(shapefile_path).geometries()
    """
    ax.add_geometries(provinces_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)

def mkDir(filepath):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def drawpic(data, num_images, output_name="temp"):
    # Validate input
    if not data.shape[0] >= num_images:
        raise ValueError("Data does not contain enough entries for the number of images specified.")

    # Setup figure dimensions based on the number of images
    fig, axs = plt.subplots(1, num_images, figsize=(10 * num_images, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    for i in range(num_images):
        axs[i].imshow(data[i, :, :], vmax=70, vmin=0, cmap=cmp_hjnwtx["radar_nmc"], transform=ccrs.PlateCarree(), extent=[73, 135, 18, 54])
        add_china_map(axs[i])
        axs[i].axis('off')
    
    # Save the figure
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    outpath = f"./aplot_image/{output_name}_{now_str}.png"
    mkDir(outpath)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
