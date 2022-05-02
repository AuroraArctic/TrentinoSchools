# :school: Schools in Trentino

## :dart: Aim of the project
This repository has been created for the [**Geospatial Analysis and Representation for Data Science**](https://napo.github.io/geospatial_course_unitn/) course of the University of Trento, teached by [Diego Giuliani](https://webapps.unitn.it/du/it/Persona/PER0020867/Didattica) and [Maurizio Napolitano](https://ict.fbk.eu/people/detail/maurizio-napolitano/) (a.y. 2021/2022).

The aim is to provide some insights about the scholastic system in the province of Trento, in Italy, considering all the schools inside [VivoScuola](https://www.vivoscuola.it/), the official website for schools in Trentino. 

## :computer: The website

The results of this project are presented through a website: https://auroraarctic.github.io/TrentinoSchools, showing: 

* All the schools in the province;
* The distribution of schools (private, public and per grade);
* The network of streets around a specific school;
* Some choropleths with population and students' data;
* Points of interest around a school;
* Evolution of Trentino's school network through the KNN algorithm varying the parameter $k$;
* The distribution of students, schools, classes and population among communities. 

## :file_folder: Repository structure

The repository is structured in three different folders:

* `data`: it contains all datasets used within the project (population, geographical boundaries, schools and Trentino's data);

* `env`, with the configuration files to create virtual environments or packages to install in order to execute the code;
  
* `src`: jupyter notebooks and Rmarkdown files are contained inside this folder. There is also the html version of the Rmarkdown analysis of schools;
  
* `viz`: it is a folder with subfolders containing all the visualizations generated through the code in src folder. There are barplots for points of interest, isochrones, knn images, Moran's I scatterplots, open street map points of interest, treemap and other maps;
  
* `website`, with some css and js files to build the website. Only the `index.html` file is left outside, for Github Pages hosting.

## :snake: How to execute the code

### Python part
#### Option :one:: Anaconda Specification File

This option is available for Windows users only with anaconda installed. Inside the env folder there is a file called `spec-file.txt`, which provides the exact version of packages from conda-forge:

```
conda create --name geospatial --file env/spec-file.txt
conda activate geospatial
```

An alternative for all users may be to create a virtual environment through the environment configuration file:

```
conda env create --file env/env.yaml
```

In either cases, `conda activate geospatial` should work. 

#### Option :two:: Pip install

Despite it is highly suggested to choose option 1 through anaconda, still a virtual environment can be created with python and then install the requirements contained inside `requirements.txt` through the following commands:

```
# Creation of the virtual environment
python -m venv geospatial

# Env activation on 
# LINUX/ MAC OS based
source geospatial/bin/activate
# WINDOWS based
geospatial\Scripts\activate.bat

# Install requirements
pip install -r env/requirements.txt
```

#### Option :three:: Look at Notebooks

Since notebooks are commented and executed with their outputs, you can just read them. This case applies in particular to the R part of the project, whose output is an html file (`src/07-SpatialRegression.html`). 

### R Part

For the R part, the installation is pretty easy. You just need to run on Rstudio console the following command:
```{r}
install.packages(c("geosphere", "tidyverse", "spdep", 
                   "rgdal", "sf", "sp", "rgeos", "terra", 
                   "DT", "knitr", "spatialreg"), 
                 dependencies = TRUE)
```

