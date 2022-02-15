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

# Get students data
stud_schools = read.csv("../data/schools/students.csv")

#####################################
# Critical cut-off neighbourhood
# Threshold (all schools have a neighbour at at least 9.18km)
knn1IT <- knn2nb(knearneigh(coords,k=1,longlat=T))
all.linkedT <- max(unlist(nbdists(knn1IT, coords, longlat=T))) 
all.linkedT

dnb10 <- dnearneigh(coords, 0, 10, longlat=TRUE); dnb10
dnb20 <- dnearneigh(coords, 0, 20, longlat=TRUE); dnb20
dnb50 <- dnearneigh(coords, 0, 50, longlat=TRUE); dnb50
dnb100 <- dnearneigh(coords, 0, 100, longlat=TRUE); dnb100

plot(tn, border="grey",xlab="",ylab="",xlim=NULL)
title(main="d nearest neighbours, d = 10-100") 
plot(dnb10, coords, add=TRUE, col="blue")
plot(dnb20, coords, add=TRUE, col="red")
plot(dnb50, coords, add=TRUE, col="yellow")
plot(dnb100, coords, add=TRUE, col="green")

########################################
# Contiguity based approach based on municipalities
contnb_q <- poly2nb(munic, queen=T)
contnb_q
plot(munic, border="grey")
plot(contnb_q, munic, add=TRUE)
plot(knn2nb(knearneigh(coords, k = 5, longlat=T)), coords, add=TRUE, col="red")

######################################
dnb10.listw <- nb2listw(dnb10,style="W")
dnb20.listw <- nb2listw(dnb20,style="W")
dnb50.listw <- nb2listw(dnb50,style="W")
dnb100.listw <- nb2listw(dnb100,style="W")

distM <- as.matrix(dist(coords)) #distance matrix
# Three possible weight matrices
W1 <- 1/(1+(distM)); diag(W1) <- 0
W2 <- 1/(1+distM)^2; diag(W2) <- 0
W3 <- exp(-distM^2); diag(W3) <- 0

#Row-standardize them 
W1s <- W1/rowSums(W1) 
W2s <- W1/rowSums(W2) 
W3s <- W1/rowSums(W3) 

#We can convert the weight matrix into a "listw" object (just for computational reasons)
listW1s <- mat2listw(W1s)
listW2s <- mat2listw(W2s)
listW3s <- mat2listw(W3s)

length(dnb10.listw)

stat_or_par = ifelse(schools@data$Gestione == "Statale",0,1)
moran.test(stat_or_par, dnb10.listw, randomisation=FALSE)


#######################
# LG
lm_model <- lm(gprb ~ , stud_schools)
summary(LinearSolow) 
