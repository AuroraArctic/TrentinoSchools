# Libraries
library(tidyverse)
library(spdep)
library(rgdal)
library(sf)

# Change working directory
getwd()

# Import and try to change CRS
# Read municipality data
tn <- readOGR("../data/Limiti01012021_g/Com01012021_g")

# Filter the province of Trento
tn <- tn[tn$COD_PROV == 22, ]
plot(tn, axes = 1)
tn <- spTransform(tn, CRS("+init=epsg:4326"))
plot(tn, axes = T)


# Import shapefile as SpatialPointsDataFrame
schools <- readOGR("../data/Trentino/schools/schools.shp",
    verbose = FALSE
)
schools@data["long"] <- schools@coords[, 1]
schools@data["lat"] <- schools@coords[, 2]
schools <- spTransform(schools, CRS("+init=epsg:4326"))


# Plot schools over Trentino's map
plot(tn, border = "grey", axes = F)
points(schools@coords, col = "cornflowerblue", cex = 1, pch = 1)

# Gather municipalities information about students
munic <- readOGR("../data/aggregated_data_per_municipality/aggregated_data_per_municipality.shp")


######################################
coords = unique(coordinates(schools))
k6 <- knn2nb(knearneigh(coords, k = 6, longlat=T))

plot(tn, border = "grey80", axis = tn)
plot(k6, coords, lwd=.2, col=alpha("blue",alpha=0.5), cex = .3, add=TRUE, points=FALSE,)


jpeg(paste0("../viz/knn/knn_",1,".jpg"))
k <- knn2nb(knearneigh(coords, k = 1, longlat=T))
plot(tn, border = "grey80", axis = tn)
plot(k, coords, lwd=.2, col=alpha("blue",alpha=0.5), cex = .3, add=TRUE, points=FALSE)
title(paste0("KNN with k=",1))
dev.off()

# KNN
library(animation)
## make sure ImageMagick has been installed in your system
saveGIF({
    
    for(i in 1:20){
        #jpeg(paste0("../viz/knn/knn_",i,".jpg"))
        k <- knn2nb(knearneigh(coords, k = i, longlat=T))
        plot(tn, border = "grey80", axis = tn)
        plot(k, coords, lwd=.2, col=alpha("#F27059",alpha=0.5), cex = .3, add=TRUE, points=FALSE)
        title(paste0("KNN with k=",i))
        #dev.off()
    
}}, movie.name="knn.gif")

# Threshold (all schools have a neighbour at at least 9.18km)
knn1IT <- knn2nb(knearneigh(coords,k=1,longlat=T))
all.linkedT <- max(unlist(nbdists(knn1IT, coords, longlat=T))) 
all.linkedT

######################################
# Contiguity based approach
contnb_q <- poly2nb(munic, queen=T)
contnb_q
plot(munic, border="grey")
plot(contnb_q, munic, add=TRUE)

######################################
# Get students data
stud_schools = read.csv("../data/schools/students.csv")

# Regression about population, students, classes and position