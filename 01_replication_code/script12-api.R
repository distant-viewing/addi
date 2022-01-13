suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(stringi))
suppressPackageStartupMessages(library(jsonlite))
suppressPackageStartupMessages(library(cli))

dir.create("api", showWarnings = FALSE)
url_base <- "https://www.loc.gov/collections/%s?fo=json&c=150&sp=%d"

coll_set <- c("ggbain", "fsac", "det", "npco", "hec")
for (coll in coll_set)
{
  json <- read_json(sprintf(url_base, coll, 1L))
  npages <- json$pagination$total

  cli_alert(sprintf("Downloading %d pages for %s", npages, coll))

  for (j in seq_len(npages))
  try({
    fout <- file.path("api", sprintf("%s_%d.json", coll, j))
    if (!file.exists(fout))
    {
      json <- read_json(sprintf(url_base, coll, j))
      write_json(json, fout)
      cli_alert_success(
        sprintf("%s => received page %d of %d", coll, j, npages)
      )
      system("sleep 1")
    }
  })
}
