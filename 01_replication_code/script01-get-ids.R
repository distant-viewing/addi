library(tidyverse)
library(xml2)
library(stringi)

dir.create(file.path("inter", "web"), FALSE)
dir.create(file.path("inter", "web"), FALSE)
dir.create(file.path("inter", "web", "index"), FALSE)

##############################################################################
# DESCRIPTION OF THE COLLECTIONS TO DOWNLOAD
sets <- tibble(
  name = c("George Grantham Bain Collection",
           "Farm Security Administration/Office of War Information b/w",
           "Farm Security Administration/Office of War Information color",
           "Detroit Publishing Company",
           "National Photo Company Collection",
           "Harris & Ewing Collection"),
  code = c("ggbain", "fsa", "fsac", "det", "npco", "hec"),
  pages = c(417L, 1754L, 17L, 253L, 357L, 416L)
)

##############################################################################
# DOWNLOAD INDEX FILES (100 LINKS ON EACH)
base_url <- "https://www.loc.gov/pictures/search/?sp=%d&co=%s&st=grid"
for (j in seq_len(nrow(sets)))
{
  for (i in seq_len(sets$pages[j]))
  {
    url <- sprintf(base_url, i, sets$code[j])
    fout <- sprintf("%s_%04d.html", sets$code[j], i)
    fout <- file.path("inter", "web",  "index", fout)
    if (!file.exists(fout))
    {
      download.file(url, fout, quiet = TRUE)
      system("sleep 0.2")
    }
    cat(sprintf("Done with %s page %d of %d\n", sets$code[j], i, sets$pages[j]))
  }
}

##############################################################################
# PARSE INDEX HTML FILES
root <- file.path("inter", "web",  "index")
all_index <- dir(root, pattern = ".html$")
collection <- stri_extract(all_index, regex = "\\A[a-z]+")

df <- vector("list", length(all_index))
for (j in seq_along(all_index))
{
  x <- read_html(file.path(root, all_index[j]))
  thumbs <- xml_find_all(x, ".//table[@class='grid']/tr/td")

  df[[j]] <- tibble(
    collection = collection[j],
    href = xml_attr(xml_find_all(thumbs, "./a"), "href"),
    rel = xml_attr(xml_find_all(thumbs, "./a"), "rel"),
    title = xml_attr(xml_find_all(thumbs, "./a/img"), "title")
  )
}
df <- bind_rows(df)

##############################################################################
# SANITY CHECK THE PARSED DATA

# will be a few missing rels (not digitized); around 4500
table(is.na(df$rel))

# rel starts with  "//cdn.loc.gov/service/pnp/" or "https://tile.loc.gov/stora"
table(stri_sub(df$rel, 1, 26))

# rel ends with "_150px.jpg"
table(stri_sub(df$rel, -10, -1))

# there are a few item numbers that have spaces and letters; these seem real
# but there are just a few, so we will remove them for this project as they
# will likely break something
basename(df$href)[stri_detect(basename(df$href), regex = "[^0-9]")]

##############################################################################
# CLEANUP AND SAVE AS STRUCTURED DATA

df$item_number <- basename(df$href)
df$image_url <- df$rel

index <- which(stri_sub(df$image_url, 1, 13) == "//cdn.loc.gov")
df$image_url[index] <- sprintf("https:%s", df$image_url[index])
df$image_url <- sprintf("%sv.jpg", stri_sub(df$image_url, 1, -11))

# do not include records that do not have an image associated with them
df <- filter(df, !is.na(rel), !stri_detect(basename(href), regex = "[^0-9]"))
df <- filter(df, stri_sub(item_number, 1L, 1L) %in% c(2, 8, 9))
df <- select(df, collection, item_number, image_url)

write_csv(df, file.path("inter", "all_item_links.csv.bz2"))
