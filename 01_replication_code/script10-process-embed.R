library(tidyverse)
library(stringi)
library(irlba)
library(FNN)

# Read the individual embedding files into a single R object; this is slow so
# create a cached version in "inter" and read this if it already exists
if (!file.exists(cache_file <- file.path("inter", "embd_combinded.rds")))
{
  embed_files <- dir("output", recursive = TRUE, full.names = TRUE)
  embed_files <- embed_files[stri_sub(basename(embed_files), 4, 7) == "embd"]

  res <- vector("list", length(embed_files))
  for (j in seq_along(embed_files))
  {
    res[[j]] <- read_csv(
      embed_files[j],
      col_types = cols(collection = col_character(), .default = col_double())
    )
    cat(sprintf("[load] Done with %02d of %02d\n", j, length(embed_files)))
  }
  output <- bind_rows(res)
  write_rds(output, cache_file)
} else {
  output <- read_rds(cache_file)
}

# Split the data into metadata and a matrix of embeddings
meta <- select(output, filename, collection)
X <- as.matrix(select(output, -filename, -collection))

# Dimensionality reduction with PCA
set.seed(1L)
index <- sample(seq_len(nrow(X)), 25000L)
pca_rotation <- irlba::svdr(X[index,], 25L)
pca_embd <- (X %*% pca_rotation$v)

# Nearest neighbors across all collections
index <- (seq_len(nrow(pca_embd)) - 1L) %/% 5000
res <- vector("list", length(index))
index_set <- unique(index)

for (j in seq_along(index_set))
{
  z <- get.knnx(pca_embd, pca_embd[index == index_set[j],], k = 51L)

  meta_this <- meta[index == index_set[j],]

  out <- tibble(
    filename = meta_this$filename[as.integer(row(z$nn.index))],
    collection = meta_this$collection[as.integer(row(z$nn.index))],
    rank = as.integer(col(z$nn.index)) - 1L,
    filename_n = meta$filename[as.integer(z$nn.index)],
    collection_n = meta$collection[as.integer(z$nn.index)],
    distance = as.numeric(z$nn.dist)
  )
  out <- filter(out, rank > 0L)
  out <- arrange(out, filename, rank)
  res[[j]] <- out
  cat(sprintf("[Global NN] Done with %02d of %02d\n", j, length(index_set)))
}
output <- bind_rows(res)
output$distance <- round(output$distance, 3)
output <- filter(output, rank <= 40)
write_csv(output, file.path("output", "knn_global.csv.bz2"))

# Nearest neighbors within a collection
collections <- unique(meta$collection)

for (coll in collections)
{
  pca_embd_coll <- pca_embd[meta$collection == coll,]
  meta_coll <- meta[meta$collection == coll,]

  index <- (seq_len(nrow(pca_embd_coll)) - 1L) %/% 5000
  res <- vector("list", length(index))
  index_set <- unique(index)

  for (j in seq_along(index_set))
  {
    z <- get.knnx(pca_embd_coll, pca_embd_coll[index == index_set[j],], k = 51L)

    meta_this <- meta_coll[index == index_set[j],]

    out <- tibble(
      filename = meta_this$filename[as.integer(row(z$nn.index))],
      collection = meta_this$collection[as.integer(row(z$nn.index))],
      rank = as.integer(col(z$nn.index)) - 1L,
      filename_n = meta_coll$filename[as.integer(z$nn.index)],
      collection_n = meta_coll$collection[as.integer(z$nn.index)],
      distance = as.numeric(z$nn.dist)
    )
    out <- filter(out, rank > 0L)
    out <- arrange(out, filename, rank)
    res[[j]] <- out
    cat(sprintf(
      "[NN | %s] Done with %02d of %02d\n", coll, j, length(index_set))
    )
  }
  output <- bind_rows(res)
  output$distance <- round(output$distance, 3)
  write_csv(
    output, file.path("output", coll, sprintf("knn_local_%s.csv.bz2", coll))
  )
}

# Save PCA components
collections <- unique(meta$collection)

for (coll in collections)
{
  pca_embd_coll <- pca_embd[meta$collection == coll,]
  meta_coll <- meta[meta$collection == coll,]
  colnames(pca_embd_coll) <- sprintf("pca_%02d", seq_len(ncol(pca_embd_coll)))
  pca_embd_coll <- as_tibble(pca_embd_coll)
  output <- bind_cols(meta_coll, pca_embd_coll)
  write_csv(
    output, file.path("output", coll, sprintf("pca_embd_%s.csv.bz2", coll))
  )
  cat(sprintf(
    "[PCA] Done with %s\n", coll)
  )
}


