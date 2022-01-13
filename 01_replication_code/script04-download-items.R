library(tidyverse)
library(xml2)
library(stringi)

##############################################################################
# LOAD DATA AND CREATE OUTPUT DIRECTORIES

df <- read_csv(file.path("inter", "all_item_links.csv.bz2"))
df <- filter(df, collection == "fsa")

dir.create(file.path("inter", "items"), FALSE)
for (col in unique(df$collection))
{
  dir.create(file.path("inter", "items", col), FALSE)
}

##############################################################################
# DOWNLOAD IMAGES

ofile <- file.path(
  "inter", "items", df$collection, sprintf("%d.html", df$item_number)
)
ifile <- sprintf("https://www.loc.gov/item/%d", df$item_number)

for (j in seq_len(nrow(df)))
try({
  if (!file.exists(ofile[j]))
  {
    download.file(ifile[j], ofile[j], quiet = TRUE)
    cat(sprintf("Done with %s page %d of %d\n", df$collection[j], j, nrow(df)))
    system("sleep 0.1")
  }
})
