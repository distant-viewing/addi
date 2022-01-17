suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(magrittr))
suppressPackageStartupMessages(library(stringi))
suppressPackageStartupMessages(library(ggrepel))
suppressPackageStartupMessages(library(jpeg))

theme_set(theme_minimal())
Sys.setlocale(locale = "en_US.UTF-8")
Sys.setenv(LANG = "en")
options(pillar.min_character_chars = 15)
options(dplyr.summarise.inform = FALSE)
options(readr.show_col_types = FALSE)
options(ggrepel.max.overlaps = Inf)
options(width = 76L)

read_data <- function(collection = "", name = "")
{
  fname <- sprintf("%s_%s.csv.bz2", name, collection)
  finput <- file.path("..", "02_computed_metadata", collection, fname)
  z <- read_csv(finput)
  z
}

api <- read_csv(
  file.path("..", "02_computed_metadata", "global", "api_metadata.csv.bz2")
)

get_img <- function(id)
{
  index <- which(api$filename == id)
  fname <- file.path("img", sprintf("%s.jpg", id))
  url <- api$image_url[index]
  if (!file.exists(fname)) { download.file(url, fname, quiet = TRUE) }
  img <- readJPEG(fname)
  img
}

show_images <- function(ids, nc = 5, nr = 4)
{
  par(mfrow = c(nr, nc))
  par(mar = rep(0, 4L))

  for (j in seq_along(ids))
  {
    plot(0, 0, xlim = c(0, 1), ylim = c(0, 1), type = "n", axes = FALSE)
    try({img <- get_img(ids[j])
    rasterImage(img, 0, 0, 1, 1)}, silent = TRUE)
  }
}

cnames <- tibble(
  collection = c("det", "fsa", "fsac", "ggbain", "hec", "npco"),
  title = c("Detroit Publishing Co.", "FSA-OWI (B&W)", "FSA-OWI (Color)",
  "Bain Collection", "Harris & Ewing", "National Photo Co.")
)
