library(tidyverse)
library(stringi)

collection_set <- dir(file.path("inter", "nn"))

# emdb, face, inst, kpnt, lvic, pano, size

for (coll in collection_set)
{
  dir.create(file.path("output", coll), showWarnings = FALSE)

  fname <- dir(file.path("inter", "nn", coll))
  ftype <- stri_sub(fname, -8, -5)

  # Get Size Data
  these_fname <- fname[ftype == "size"]
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]),
      col_types = "dcdd"
    )
    print(j)
  }
  output <- bind_rows(res)
  write_csv(
    output, file.path("output", coll, sprintf("nn_size_%s.csv.bz2", coll))
  )

  # Get LVIC annotations
  these_fname <- fname[ftype == "lvic"]
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]),
      col_types = "dcdddcddddd"
    )
    print(j)
  }
  output <- bind_rows(res)
  write_csv(
    output, file.path("output", coll, sprintf("nn_lvic_%s.csv.bz2", coll))
  )

  # Get Instance Data
  these_fname <- fname[ftype == "inst"]
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]),
      col_types = "dcdddcddddd"
    )
    print(j)
  }
  output <- bind_rows(res)
  write_csv(
    output, file.path("output", coll, sprintf("nn_inst_%s.csv.bz2", coll))
  )

  # Get face data
  these_fname <- fname[ftype == "face"]
  these_id <- as.integer(stri_sub(these_fname, 1, -10))
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]), col_types = "dcdddddc"
    )
    print(j)
  }
  output <- bind_rows(res)
  output <- filter(output, !is.na(confidence))
  output <- select(
    output, filename, collection, top, right, bottom, left, confidence
  )
  write_csv(
    output, file.path("output", coll, sprintf("nn_face_%s.csv.bz2", coll))
  )

  # Get Panoptic Data
  these_fname <- fname[ftype == "pano"]
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]), col_types = "dcddddlcd"
    )
    print(j)
  }
  output <- bind_rows(res)
  write_csv(
    output, file.path("output", coll, sprintf("nn_pano_%s.csv.bz2", coll))
  )

  # Get Image Embeddings (the format here is quite different)
  these_fname <- fname[ftype == "embd"]
  res <- matrix(NA_real_, nrow = length(these_fname), ncol = 2048L)
  for (j in seq_along(these_fname))
  {
    res[j,] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]),
      col_types = "d",
      col_names = FALSE
    )$X1
    print(j)
  }
  colnames(res) <- sprintf("embed_%04d", seq_len(ncol(res)))
  output <- bind_cols(
    tibble(
      filename = as.numeric(stri_sub(these_fname, 1, -10)),
      collection = coll
    ),
    as_tibble(res)
  )
  # these files are huge; most need to be collapsed into several smaller files
  id <- ((seq_len(nrow(output)) - 1L) %/% 5000)
  for (j in unique(id))
  {
    index <- which(id == j)
    write_csv(
      output[index,],
      file.path("output", coll, sprintf("nn_embd_%s_%02d.csv.bz2", coll, j))
    )
  }

  # Get Keypoint Data
  these_fname <- fname[ftype == "kpnt"]
  res <- vector("list", length(these_fname))
  for (j in seq_along(res))
  {
    res[[j]] <- read_csv(
      file.path("inter", "nn", coll, these_fname[j]), col_types = "dcdcddd"
    )
    print(j)
  }
  output <- bind_rows(res)

  if (coll == "fsa")
  {
    # Too big for GitHub as one file => split it up into two files
    write_csv(
      output[seq(1L, 6e6),],
      file.path("output", coll, sprintf("nn_kpnt_%s_00.csv.bz2", coll))
    )
    write_csv(
      output[seq(6e6 + 1L, nrow(output)),],
      file.path("output", coll, sprintf("nn_kpnt_%s_01.csv.bz2", coll))
    )
  } else {
    # Other collections are okay as one file
    write_csv(
      output, file.path("output", coll, sprintf("nn_kpnt_%s.csv.bz2", coll))
    )
  }
}

