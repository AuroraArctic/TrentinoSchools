# Libraries
library(tidyverse)
library(spdep)
library(rgdal)
library(sf)
library(sp)

# Change working directory
setwd("G:/Il mio Drive/2nd Year/Geospatial/TrentinoSchools/src")

# Import 
# Read municipality data
tn <- readOGR("../data/aggregated_data_per_municipality")

# Plot the municipalities in Trentino
plot(tn, axes = 1)

# Import shapefile as SpatialPointsDataFrame
schools <- readOGR("../data/Trentino/schools/schools.shp",
    verbose = FALSE
)
# Setting coordinates
schools@data["long"] <- schools@coords[, 1]
schools@data["lat"] <- schools@coords[, 2]
# Changing CRS
schools <- spTransform(schools, CRS("+init=epsg:4326"))


# Plot schools over Trentino's map
plot(tn, border = "grey", axes = F)
points(schools@coords, col = "cornflowerblue", cex = 1, pch = 1)


######################################
# KNN
coords = unique(coordinates(schools))
for(i in 19:50){
    png(paste0("../viz/knn/",i,".png"),res=300, width=1000, height=1000)
    k <- knn2nb(knearneigh(coords, k = i, longlat=T))
    par(mar = c(0,0,0,0))
    plot(tn, border = "grey80", axis = tn, lwd=0.5)
    plot(k, coords, lwd=.6, col=alpha("#F27059",alpha=0.5), cex = .3, add=TRUE, points=FALSE)
    dev.off()
}


#####################################
# Critical cut-off neighbourhood
# Threshold (all schools have a neighbour at at least 9.18km)
knn1IT <- knn2nb(knearneigh(coords,k=1,longlat=T))
all.linkedT <- max(unlist(nbdists(knn1IT, coords, longlat=T))) 
all.linkedT

coords = coordinates(tn)

dnb10 <- dnearneigh(coords, 0, 2, longlat=TRUE); dnb10
dnb20 <- dnearneigh(coords, 0, 5, longlat=TRUE); dnb20
dnb50 <- dnearneigh(coords, 0, 10, longlat=TRUE); dnb50
dnb100 <- dnearneigh(coords, 0, 20, longlat=TRUE); dnb100

plot(tn, border="grey",xlab="",ylab="",xlim=NULL)
title(main="d nearest neighbours, d = 10-100") 
plot(dnb10, coords, add=TRUE, col="lightblue")
plot(dnb20, coords, add=TRUE, col="cornflowerblue")
plot(dnb50, coords, add=TRUE, col="blue")
plot(dnb100, coords, add=TRUE, col="black")

########################################
# Contiguity based approach based on municipalities
coords = coordinates(tn)

contnb_q <- poly2nb(tn, queen=T)
contnb_q
plot(tn, border="grey")
plot(contnb_q, coords, add=TRUE)
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

length(dnb100.listw)
tn$Scuole.tot[is.na(tn$Scuole.tot)] <- 0
tn$Scuole.tot[is.na(tn$Media.stud)] <- 0

col_names = names(tn)

na.zero <- function (x) {
    x[is.na(x)] <- 0
    return(x)
}

# MORAN TEST
# Number of schools + Municipalities
moran.test(na.zero(tn$Scuole.tot), dnb100.listw, randomisation=FALSE)
moran.mc(italy$gprb, dnb379.listw, nsim=999)


moran.test(na.zero(tn$Studenti), dnb100.listw, randomisation=TRUE)

# Mean number of students per school and class
moran.test(na.zero(tn$Media.stud), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(tn$Media.st_1), dnb100.listw, randomisation=FALSE)

# Population
moran.test(na.zero(as.numeric(tn$Pop.under)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Pop_mat)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Pop_ele)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Pop_med)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Pop_sup)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Popolazion)), dnb100.listw, randomisation=FALSE)

moran.test(na.zero(as.numeric(tn$Pop_stud.P)), dnb100.listw, randomisation=FALSE)
moran.test(na.zero(as.numeric(tn$Stud.Pop_s)), dnb100.listw, randomisation=FALSE)


# LINEAR MODEL
model = lm(Studenti ~ Pop.under + Scuole.tot, tn)
summary(model)

studres <- rstudent(model)
resdistr <- quantile(studres, na.rm=TRUE) 
colours <- grey((length(resdistr):2)/length(resdistr))
plot(tn, col=colours[findInterval(studres, resdistr, all.inside=TRUE)])

lm.morantest(model,dnb100.listw,resfun=rstudent)

# MORAN SCATTERPLOT

dnb321 <- dnearneigh(coordinates(tn), 0, 100, longlat=TRUE)
dnb321.listw <- nb2listw(dnb321,style="W",zero.policy=F)
mplot <- moran.plot(na.zero(tn$Studenti), listw=dnb321.listw, main="Moran scatterplot", 
                    return_df=F)
grid()

