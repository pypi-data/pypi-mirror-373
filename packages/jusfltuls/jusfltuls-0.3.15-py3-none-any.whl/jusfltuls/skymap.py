
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.vizier import Vizier
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import LinearSegmentedColormap

# Target center coordinates
center = SkyCoord('05h36m13s', '-01d12m07s', frame='icrs')

# Vizier query setup: Hipparcos catalog (I/239/hip_main)
Vizier.ROW_LIMIT = 10000
catalog = "I/239/hip_main"

# Search radius
radius = 25 * u.deg

# Query stars around center within radius
result = Vizier.query_region(center, radius=radius, catalog=catalog)
maxmag=5
if result:
    print(result)
    stars = result[0]
    stars = stars[stars['Vmag'] <= maxmag]
    print(stars)
    # Filter stars with magnitude Hp <= 4
    print(stars.colnames)
    #bright_stars = stars[stars['Vmag'] <= 5]
    #mag = bright_stars['Vmag'] #####bright_stars = stars[stars['Hp'] <= 4]


    # Assuming bright_stars with 'B-V' column exists
    bv = stars['B-V']
    norm = plt.Normalize(vmin=np.min(bv), vmax=np.max(bv))
    #colors = plt.cm.rainbow(norm(bv))

    # Create a custom colormap from red to blue (excluding violet)
    #colors_list = [(0, 0, 1), (1, 0, 0)]  # red to blue
    #custom_cmap = LinearSegmentedColormap.from_list('red_blue', colors_list)
    #colors = custom_cmap(norm(bv))


    # Create a custom colormap from red to white to blue
    #colors_list = [(0, 1, 1), (1,1,1), (1, 1, 1), (1,1,1),(1,1,1),  (1,1,1),(1,1,1), (1, 0, 0)]  # red -> white -> blue
    #custom_cmap = LinearSegmentedColormap.from_list('red_white_blue', colors_list)
    # Custom colormap with slight blue at low end, white in middle, red at high end
    colors_list = [(0.5, 0.7, 1), (1, 1, 1), (1, 0, 0)]  # light blue -> white -> red
    custom_cmap = LinearSegmentedColormap.from_list('lightblue_white_red', colors_list)
    colors = custom_cmap(norm(bv))


    sizes = np.log10((maxmag - stars['Vmag']) * 5 + 1) * 20  # +1 to avoid log10(0), scaled for visibility
    sizes = 20 * np.exp(-0.5 * stars['Vmag'])  # smaller sizes for higher magnitudes (fainter stars)
    sizes = (maxmag - stars['Vmag']) ** 2  # Larger size for brighter stars
    # Plot
    plt.figure(figsize=(6,6))
    plt.scatter(stars['RAICRS'], stars['DEICRS'], s=sizes , c=colors)
    #plt.scatter(ra, dec, s=10, c='white')
    plt.gca().set_facecolor('black')
    plt.xlabel('RA (deg)')
    plt.ylabel('DEC (deg)')
    plt.title('Stars up to 4th magnitude near RA 5h36m13s Dec -1°12′7″')
    plt.gca().invert_xaxis()  # RA increases to the left in sky maps
    plt.gca().set_aspect('equal', adjustable='datalim')
    plt.show()
else:
    print("No stars found in the region.")
