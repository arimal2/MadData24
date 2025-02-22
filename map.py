import folium

#Create map object
mapObj = follium.Map(location=(10, 79),
                     zoom_start=5, width=800, height=500)

# save as HTML file
mapObj.save("output.html")