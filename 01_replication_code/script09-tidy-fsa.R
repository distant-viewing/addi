library(readr)
library(dplyr)
library(xml2)
library(stringi)
library(tidyr)

source("funs.R")

###########################################################################################
# 1. load data and define small helper functions
marc <- read_csv(file.path("output", "fsa", "marc_records_fsa.csv.bz2"))
county <- read_csv(file.path("input", "county_lookup.csv"))
place <- read_csv(file.path("input", "place_lookup.csv"))
geonames <- read_csv(file.path("input", "geonames_lookup.csv"))
state <- read_csv(file.path("input", "state_lookup.csv"))
vanderbilt <- read_csv(file.path("input", "vanderbilt_lookup.csv"))

stopifnot(nrow(anti_join(place, county, by = c("state_name", "county"))) == 0)
stopifnot(nrow(anti_join(geonames, county, by = c("state_name", "county"))) == 0)

###########################################################################################
# 2. create output dataset
output_data <- tibble(id = unique(marc$id))
output_data$loc_code <- stri_sub(filter_first_na(filter(marc, tag == "035", code == "a")), 6, -1)
output_data$call_num <- filter_first_na(filter(marc, tag == "037", code == "a"))
output_data$photographer <- filter_first_na(filter(marc, tag == "100", i1 == 1, code == "a"))
output_data$caption <- filter_first_na(filter(marc, tag == "245", i1 == 1, code == "a"))
output_data$date <- filter_first_na(filter(marc, tag == "260", code == "c"), TRUE)
output_data$path <- filter_first_na(filter(marc, tag == "856", i1 == 4, i2 == 1, code == "f"))
output_data$path_start <- filter_first_na(filter(marc, tag == "985", code == "a"))
output_data$other_letter <- filter_first_na(filter(marc, tag == "084", code == "a"))
output_data$other_number <- filter_first_na(filter(marc, tag == "084", code == "b"))

output_data$geo_country <- filter_first_na(filter(marc, tag == "752", code == "a"), TRUE)
output_data$geo_state <- filter_first_na(filter(marc, tag == "752", code == "b"), TRUE)
output_data$geo_county <- filter_first_na(filter(marc, tag == "752", code == "c"), TRUE)
output_data$geo_city <- filter_first_na(filter(marc, tag == "752", code == "d"), TRUE)

###########################################################################################
# 3. clean photographer names
first_names <- stri_extract(output_data$photographer, regex = ",[\\w\\W]+")
first_names <- stri_trim(stri_replace_all(first_names, "", fixed = ","))
first_names[is.na(first_names)] <- ""
last_names <- stri_extract(output_data$photographer, regex = "[^,]+,")
last_names <- stri_trim(stri_replace_all(last_names, "", fixed = ","))
last_names[is.na(last_names)] <- ""

full_names <- sprintf("%s %s", first_names, last_names)
full_names[full_names == " "] <- NA_character_
full_names <- stri_trim(full_names)
output_data$photographer <- full_names

###########################################################################################
# 3. clean dates
num_years <- stri_count(output_data$date, regex = "[0-9][0-9][0-9][0-9]")
first_year <- stri_extract(output_data$date, regex = "[0-9][0-9][0-9][0-9]")
first_text <- stri_extract(output_data$date, regex = "[A-Z][a-z]+")
month <- rep(NA_character_, nrow(output_data))
month[first_text == "Jan"] <- "01"
month[first_text == "Feb"] <- "02"
month[first_text %in% c("Mar", "March")] <- "03"
month[first_text %in% c("Apr", "April")] <- "04"
month[first_text == "May"] <- "05"
month[first_text == "June"] <- "06"
month[first_text == "July"] <- "07"
month[first_text %in% c("Aug", "August")] <- "08"
month[first_text == "Sept"] <- "09"
month[first_text == "Oct"] <- "10"
month[first_text %in% c("Nov", "November")] <- "11"
month[first_text %in% c("Dec", "December")] <- "12"
month[first_text == "Spring"] <- "04"
month[first_text == "Summer"] <- "07"
month[first_text == "Fall"] <- "10"
month[first_text == "Winter" & first_year == 1942] <- "12"
month[first_text == "Winter" & first_year == 1943] <- "01"

year <- if_else(num_years == 1, first_year, NA_character_)
month <- if_else(num_years == 1, month, NA_character_)
month[year <= 1934] <- NA_character_
month[year > 1943] <- NA_character_
year[year < 1935] <- NA_character_
year[year > 1945] <- NA_character_

output_data$year <- year
output_data$month <- month

###########################################################################################
# 4. clean category codes
suppressWarnings({ output_data$other_number <- as.numeric(output_data$other_number) })
output_data <- left_join(output_data, vanderbilt, by = "other_number")

###########################################################################################
# 5. join with geographic data

# clean the data
output_data <- clean_non_48(output_data)
cset <- output_data$geo_county
sset <- output_data$geo_state
output_data$geo_county <- clean_county_names(cset, sset)

# join to county
output_data$county <- output_data$geo_county
output_data$county[output_data$geo_country != "United States"] <- NA
output_data$county[is.na(output_data$geo_state)] <- NA
output_data$county[is.na(output_data$geo_county)] <- NA
output_data$county <- stri_replace_all(output_data$county, "", fixed = " County")
output_data$county <- stri_replace_all(output_data$county, "", fixed = " Parish")
output_data$county <- stri_replace_all(output_data$county, "", fixed = " Municipio")
output_data$county <- stri_trim(output_data$county)
output_data$county <- stri_trans_totitle(output_data$county)
output_data <- left_join(
  output_data,
  mutate(county, county_flag = 1),
  by = c("geo_state" = "state_name", "county" = "county")
)

table(
  has_county_field = !is.na(output_data$county),
  in_county_table = !is.na(output_data$county_flag)
)

# join to place
output_data$city <- output_data$geo_city
output_data$city[output_data$geo_country != "United States"] <- NA
output_data$city[is.na(output_data$geo_state)] <- NA
output_data <- left_join(
  output_data, place,
  by = c("geo_state" = "state_name", "city" = "place"),
  suffix = c("", "_city")
)

table(
  has_city_field = !is.na(output_data$city),
  in_places_table = !is.na(output_data$lon)
)

# join to geoname
output_data$place <- NA_character_
output_data$place[is.na(output_data$county_flag)] <- output_data$county[is.na(output_data$county_flag)]
index <- which(is.na(output_data$lon) & !is.na(output_data$city))
output_data$place[index] <- output_data$city[index]
output_data <- left_join(
  output_data, geonames,
  by = c("geo_state" = "state_name", "city" = "place"),
  suffix = c("", "_geonames")
)

has_lat_long <- (!is.na(output_data$lat) | !is.na(output_data$lat_geonames))
has_county <- (!is.na(output_data$county_flag) | !is.na(output_data$county_city) | !is.na(output_data$county_geonames))
table(has_lat_long = has_lat_long, has_county = has_county)

# pick county, lat, and lon
output_data$lat[is.na(output_data$lat)] <- output_data$lat_geonames[is.na(output_data$lat)]
output_data$lon[is.na(output_data$lon)] <- output_data$lon_geonames[is.na(output_data$lon)]
output_data$county_use <- NA_character_
output_data$county_use[!is.na(output_data$county_flag)] <- output_data$county[!is.na(output_data$county_flag)]
output_data$county_use[is.na(output_data$county_use)] <- output_data$county_city[is.na(output_data$county_use)]
output_data$county_use[is.na(output_data$county_use)] <- output_data$county_geonames[is.na(output_data$county_use)]

# pick place name
output_data$place_use <- output_data$geo_city
index <- which(is.na(output_data$place_use) & is.na(output_data$county_flag))
output_data$place_use[index] <- output_data$geo_county[index]

# zero out non-US lat/lon
okay_geo <- (
  (output_data$geo_country == "United States") &
  (output_data$geo_state %in% state$state_name)
)
output_data$geo_state[!okay_geo] <- NA_character_
output_data$county_use[!okay_geo] <- NA_character_
output_data$lon[!okay_geo] <- NA_real_
output_data$lat[!okay_geo] <- NA_real_
output_data$place_use[!okay_geo] <- NA_real_

###########################################################################################
# 6. select variables to use
photo_data <- select(output_data, id, loc_code, call_num, photographer,
         country = geo_country, state = geo_state, county = county_use,
         place = place_use, lon, lat,
         v1, v2, v3,
         year, month,
         caption)
photo_data <- photo_data[!duplicated(photo_data$id),]

###########################################################################################
# 7. create output.
write_csv(photo_data, file.path("output", "fsa", "fsa_tidy_metadata.csv.bz2"))

