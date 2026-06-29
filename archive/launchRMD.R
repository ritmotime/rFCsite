# 1) Turn post_row_analysis.html into a single-file HTML
setwd("~/ritmo_repositories/rFCsite")


rmarkdown::render("GetStarted.Rmd", output_file = "index.html", output_options = list(self_contained = FALSE))






rmarkdown::render("GS_pdf.Rmd", output_file = "index.html",  output_format = rmarkdown::html_document(self_contained = TRUE))
