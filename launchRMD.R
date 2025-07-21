setwd("~/ritmo_repositories/rFCsite")
rmarkdown::render("GetStarted.Rmd", output_file = "index.html", output_options = list(self_contained = TRUE))
