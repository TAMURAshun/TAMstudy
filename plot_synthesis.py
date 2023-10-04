#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.image import imread
import matplotlib.cm as cm
import numpy as np
import math
import sys
import os
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader


if __name__ == "__main__":
    altitude = int(sys.argv[1]) #[m]

    #open suita 1
    f1=open('raderheight.txt')
    h1=f1.read()
    rader_height1=float(h1)
    f1.close()

    alt1=round((altitude-rader_height1*1000)/100)
    data1=np.load('lonlat_data.npy')
    # Lon1=np.load('Lon.npy')
    # Lat1=np.load('Lat.npy')
    # Lon1= Lon1.astype(np.float32)
    # Lat1= Lat1.astype(np.float32)
    # Lon1=Lon1/60 #min->deg
    # Lat1=Lat1/60
    z_arr1 = data1[:,:,alt1]
    print(z_arr1)

    #open kobe 2
    f=open('raderheight_k.txt')
    h=f.read()
    rader_height2=float(h)
    f.close()

    alt2=round((altitude-rader_height2*1000)/100)
    data2=np.load('lonlat_data_k.npy')
    # Lon2=np.load('Lon_k.npy')
    # Lat2=np.load('Lat_k.npy')
    # Lon2= Lon2.astype(np.float32)
    # Lat2= Lat2.astype(np.float32)
    # Lon2=Lon2/60 #min->deg
    # Lat2=Lat2/60
    z_arr2 = data2[:,:,alt2]

    #synthesize
    z_arr1_p=np.pad(z_arr1,[(137,0),(27,0)],"constant")
    z_arr2_p=np.pad(z_arr2,[(0,137),(0,27)],"constant")
    print(np.shape(z_arr1_p))
    print(np.shape(z_arr2_p))
    print(z_arr1_p)
    print(z_arr2_p)
    # sys.exit()

    z_m=z_arr1_p+z_arr2_p
    u=z_m.real
    v=z_m.imag
    u=np.nan_to_num(u,nan = 0)
    v=np.nan_to_num(v,nan = 0)

    Lon=np.linspace(8057.85,8170.60,num=452) #min
    Lat=np.linspace(2050.35,2121.60,num=286)
    lon=Lon/60 #deg
    lat=Lat/60
    x, y = np.meshgrid(lon, lat)
    x=x.transpose()
    y=y.transpose()
    print(np.shape(x))
    print(np.shape(y))

    fig = plt.figure()
    ax = fig.add_subplot(111,projection=ccrs.PlateCarree())
    # 都道府県境界
    shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces') # 日本の都道府県のみ取得 
    provinces = shapereader.Reader(shpfilename).records() 
    prefs = filter(lambda province: province.attributes['admin'] == 'Japan', provinces)
    for pref in prefs:     
        geometry = pref.geometry     
        ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='none', linestyle='--',lw=0.1)
    
    ax.coastlines(lw=0.2, resolution='10m')
    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True) # 経度線・緯度線ラベルを有効に
    gl.xlocator = mticker.FixedLocator(np.arange(134.5,136.2,0.2)) # 経度線の設定 
    gl.ylocator = mticker.FixedLocator(np.arange(34.3,35.5,0.2)) # 緯度線の設定
    ax.set_extent([134.3, 136.2, 34.1, 35.4], crs=ccrs.PlateCarree())

    # custom_color = cus_color()
    levels=np.arange(0,31,5)
    z=np.sqrt(u**2 + v**2)

    cf = ax.contourf(x, y, z, levels=levels, cmap='GnBu', extend = "both",alpha=0.5)
    plt.colorbar(cf, aspect=40, orientation="horizontal" )
    
    Q=ax.quiver(x, y, u, v, color='black',regrid_shape=50,scale=300.)
    ax.quiverkey(Q, 1.03, -0.08, 10, '10 m/s', color='k', labelpos='S', labelsep=0.03)
    ax.plot(134.951, 34.71, 'ro',markersize='6')
    ax.plot(135.523, 34.823, 'ro',markersize='6')

    rect = plt.Rectangle((134.868,34.285), 0.74, 0.95, facecolor='none', edgecolor='r', alpha=0.5) 
    ax.add_patch(rect)
    ax.set_aspect("equal")
    ax.set_title('multi 20211214 Altitude: %i[m]'%altitude)

    plt.show()