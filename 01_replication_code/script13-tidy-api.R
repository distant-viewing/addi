suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(stringi))
suppressPackageStartupMessages(library(jsonlite))
suppressPackageStartupMessages(library(cli))

ifiles <- dir("api")
nfiles <- length(ifiles)
ifnull <- function(u, v) {ifelse(is.null(u), v, u)}
ifempty <- function(u, v) {ifelse(length(u) == 0, list(v), list(u))[[1]]}
last <- function(v) { v[[length(v)]] }

cli_alert(sprintf("Loading %d files", nfiles))
df_list <- vector("list", nfiles)
for (j in seq_along(ifiles))
{
  json <- read_json(file.path("api", ifiles[j]))
  df_list[[j]] <- tibble(
    filename = sapply(json$results, function(v) ifnull(v$item$id[[1]], "")),
    title = sapply(json$results, function(v) ifnull(v$title[[1]], "")),
    sort_date = sapply(json$results, function(v) ifnull(v$item$sort_date[[1]], "")),
    thumb_url = sapply(json$results, function(v) ifempty(v$image_url, "")[[1]][[1]]),
    image_url = sapply(json$results, function(v) last(ifempty(v$image_url, ""))[[1]]),
    url = sapply(json$results, function(v) ifnull(v$url[[1]], ""))
  )
  cli_alert_success(sprintf("loaded file %d of %d", j, nfiles))
}
df_list <- bind_rows(df_list)

write_csv(df_list, file.path("output", "api_metadata.csv.bz2"))
