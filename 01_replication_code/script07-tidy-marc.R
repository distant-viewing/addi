library(tidyverse)
library(xml2)
library(stringi)

collection_set <- dir(file.path("inter", "marc"))

for (coll in collection_set)
{
  dir.create(file.path("output", coll), showWarnings = FALSE)

  ifile <- dir(file.path("inter", "marc", coll))
  ids <- stri_sub(ifile, 1, -5)

  # grab the marc records and create one large data set
  df_list <- vector("list", length(ifile))
  for (i in seq_along(ifile))
  {
    x <- read_html(file.path("inter", "marc", coll, ifile[i]))
    tr <- xml_text(xml_find_all(x, ".//table/tr/td"))
    if((length(tr) %% 5) != 0) { print(i) }
    mat <- matrix(tr, byrow=TRUE, ncol = 5)
    df <- tibble(
      id = ids[i],
      tag = mat[,1],
      i1 = mat[,2],
      i2 = mat[,3],
      code = mat[,4],
      text = mat[,5]
    )
    df$tag <- stri_trim(df$tag)
    df$i1 <- stri_trim(df$i1)
    df$i2 <- stri_trim(df$i2)
    df$code <- stri_trim(df$code)
    df$text <- stri_trim(df$text)

    df$tag[df$tag == ""] <- NA
    df$i1[df$i1 == ""] <- NA
    df$i2[df$i2 == ""] <- NA
    df_list[[i]] <- fill(df, tag)

    if ((i %% 100) == 0) print(sprintf("Done with %d of %d", i, length(ifile)))
  }

  df_list <- bind_rows(df_list)
  write_csv(
    df_list, file.path("output", coll, sprintf("marc_records_%s.csv.bz2", coll))
  )
}
