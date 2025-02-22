import folium

#Create map object
mapObj = folium.Map(location=(43.099613, -89.5078801),
                     zoom_start=9, width=800, height=500)

# save as HTML file
mapObj.save("output.html")