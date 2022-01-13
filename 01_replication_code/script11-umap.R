library(tidyverse)
library(stringi)
library(umap)

collection_set <- list.dirs(file.path("output"), recursive = FALSE)
collection_set <- basename(collection_set)

for (coll in collection_set)
{
  pca_embd <-  read_csv(
    file.path("output", coll, sprintf("pca_embd_%s.csv.bz2", coll)),
    col_types = cols(
      .default = col_double(),
      collection = col_character()
    )
  )
  X <- as.matrix(select(pca_embd, -filename, -collection))

  umap_embd <- umap(X, verbose = TRUE, n_neighbors = 5)

  df <- tibble(
    filename = pca_embd$filename,
    collection = pca_embd$collection,
    umap_01 = umap_embd$layout[,1],
    umap_02 = umap_embd$layout[,2]
  )

  write_csv(
    df, file.path("output", coll, sprintf("umap_embd_%s.csv.bz2", coll))
  )
  cat(sprintf("[UMAP] Done with %s\n", coll))
}

# ggplot(df, aes(umap_01, umap_02)) + geom_point()
