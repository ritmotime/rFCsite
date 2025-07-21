setwd("~/ritmo_repositories/ritmortools")
rmarkdown::render("GetStarted.Rmd", output_file = "index.html", output_options = list(self_contained = TRUE))
