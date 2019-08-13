library(maps)
library(ggplot2)
library(outliers)
library(dplyr)


stipend.dat <- read.csv('C:/Users/mattd/Desktop/Projects/Python Projects/Stipe And Locations.txt', sep='\t')


#FIND OUTLIERS
#let's see what a quick model looks like
stipend.dat <- stipend.dat[order(stipend.dat$LW.Ratio), ]
plot(stipend.dat$LW.Ratio, ylab = 'LW Ratio', main = 'LW Ratio per University')

#get a generalized linear model
lw.glm <- glm(1:length(stipend.dat$LW.Ratio)~stipend.dat$LW.Ratio)

#get outliers
lw.cooks <- cooks.distance(lw.glm)
lw.outlier <- c(which(lw.cooks >= mean(lw.cooks)*4))

stipend.dat[lw.outlier,c('Subject', 'LW.Ratio', 'Stipend')]

#remove outliers
stipend.dat.clean <- stipend.dat[-lw.outlier[6],]

#remove <0
stipend.dat.clean <- stipend.dat.clean[which(stipend.dat.clean$Stipend > 0),]

#GET BASIC STATS
lw.ratio.mean <- sort(tapply(stipend.dat.clean$LW.Ratio, stipend.dat.clean$State, mean), decreasing = T)

#remove weirdos
stipend.dat.clean <- subset(stipend.dat.clean, State != 'CAT' & State != 'LAZ' & State != '' & State != 'Auvergne-RhÃ´ne-Alpes')

#average by state
lw.ratio.mean <- sort(tapply(stipend.dat.clean$LW.Ratio, stipend.dat.clean$State, mean), decreasing = T)

colMeans(lw.ratio.mean)

mean(stipend.dat.clean$LW.Ratio)
  [1] 1.131833 ```R mean(stipend.dat.clean$Stipend) ``` 
  [1] 26375.38
  
  #remove data with one point
unrow <- table(stipend.dat.clean$Subject)
no.uni <- stipend.dat.clean[stipend.dat.clean$Subject %in% names(unrow)[unrow > 5],]

#average LW ratio per subject
sort(tapply(no.uni$LW.Ratio, tolower(no.uni$Subject), mean), decreasing = T)[c(1:5,104:109)] %>% 
  data.frame(.) 
  
  library(usmap)
library(ggiraph)
states <- us_map(region = 'states')

#merge the two data sets
lw.ratio.mean['State'] <- tolower(rownames(lw.ratio.mean))
states.lw = merge(x = states, y = lw.ratio.mean, by.x = 'full', by.y = 'State', all.x = T)
states.lw$lw.ratio.mean = round(states.lw$lw.ratio.mean,digits = 3)

oc <- "alert(this.getAttribute(\"data-id\"))"
g <- ggplot(data = states) + 
  geom_polygon_interactive(aes(x = long, y = lat, fill = states.lw$lw.ratio.mean, group = group,
                               tooltip=states.lw$lw.ratio.mean, 
                               data_id = states.lw$full, onclick = oc), color = "white") +
  coord_fixed(1) + labs(fill = 'Living-Wage \n Ratio') + ggtitle('Average Stipend per State')
  
ggiraph(code=print(g))
