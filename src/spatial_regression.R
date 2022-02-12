# Libraries
library(tidyverse)
library(spdep)
library(rgdal)
library(sf)

# Change working directory
getwd()
setwd("G:/Il mio Drive/2nd Year/Geospatial/TrentinoSchools/src")

# Import and try to change CRS
# Read municipality data
tn <- readOGR("../data/Limiti01012021_g/Com01012021_g")
# Filter the province of Trento
tn <- tn[tn$COD_PROV == 22, ]
plot(tn, axes = 1)
tn <- spTransform(tn, CRS("+init=epsg:4326"))
plot(tn, axes = T)


# 01-Import shapefile as SpatialPointsDataFrame
df <- readOGR("../data/Trentino/schools/schools.shp",
    verbose = FALSE
)
df@data["long"] <- df@coords[, 1]
df@data["lat"] <- df@coords[, 2]
df <- spTransform(df, CRS("+init=epsg:4326"))


# Plot schools over Trentino's map
plot(tn, border = "grey", axes = F)
points(df@coords, col = "cornflowerblue", cex = 1, pch = 1)

######################################
# TODO: Animation of Trentino school network based on the number of neighbours
# KNN
knn = c()
for(i in 1:10){
    knn <- append(knn,
                  knn2nb(knearneigh(coordinates(df),
                                    k = i,
                                    longlat = T
                  )))
}

plot(knn2nb(knearneigh(coordinates(df),
                  k = i,
                  longlat = T
)), df@coords)

# define the neighbourhood relationships amongst the spatial units. 
plot(tn, border = "grey90", axis = tn)
plot(knn[2], df@coords, col = "cornflowerblue", lwd=0.2, cex=0.5, add=TRUE)

######################################
# Contiguity based approach
contnb_q <- poly2nb(tn, queen=T)
contnb_q
plot(tn, border="grey")
plot(contnb_q, df@coords, add=TRUE)

######################################
# Get students data
stud_df = read.csv("../data/schools/students.csv")

# Regression about population, students, classes and position