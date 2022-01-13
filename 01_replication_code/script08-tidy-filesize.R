library(tidyverse)
library(stringi)
library(xml2)

d <- file.path("inter", "items", "fsa")
input_files <- dir(d)

df <- vector("list", length(input_files))
for (i in seq_along(df))
try({
  x <- read_html(file.path(d, input_files[i]))
  y <- xml_text(xml_find_all(x, ".//option[@data-file-download='TIFF']"))
  file_num <- as.numeric(stri_extract(y, regex = '[0-9\\.]+'))
  file_unit <- stri_sub(stri_extract(y, regex = '[A-Z]+\\)'), 1, -2)
  df[[i]] <- tibble(
    item = input_files[i],
    file_num = file_num,
    file_unit = file_unit
  )
  print(i)
})

df <- bind_rows(df)
df <- filter(df, !is.na(file_num), !is.na(file_unit))
df$size_mb <- df$file_num
df$size_mb[df$file_unit == "KB"] <- df$size_mb[df$file_unit == "KB"] / 1000
df$size_mb[df$file_unit == "GB"] <- df$size_mb[df$file_unit == "GB"] * 1000

write_csv(df, file.path("output", "fsa_file_size.csv.bz2"))
