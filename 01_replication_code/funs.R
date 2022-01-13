library(stringi)

filter_first_na <- function(df, remove_dot = FALSE)
{
  df <- select(df, id, text)
  df <- df[!duplicated(df$id),]
  if (remove_dot) df$text <- stri_replace(stri_trim(df$text), "", regex = "\\.$")
  df_new <- left_join(tibble(id = unique(marc$id)), df, by = "id")
  df_new$text
}


clean_non_48 <- function(output_data)
{
  output_data$geo_state <- stri_replace_all(output_data$geo_state, "", fixed = " (State)")

  # puerto rico
  these_pr <- which(output_data$geo_country == "Puerto Rico")
  output_data$geo_county[these_pr] <- output_data$geo_state[these_pr]
  output_data$geo_state[these_pr] <- "Puerto Rico"
  output_data$geo_country[these_pr] <- "United States"
  output_data$geo_county[output_data$geo_county == "Bayamon Municipality"] <- "Bayamón Municipality"
  output_data$geo_county[output_data$geo_county == "Comerio Municipality"] <- "Comerío Municipality"
  output_data$geo_county[output_data$geo_county == "Guanica Municipality"] <- "Guánica Municipality"
  output_data$geo_county[output_data$geo_county == "Manati Municipality"] <- "Manatí Municipality"
  output_data$geo_county[output_data$geo_county == "Mayaguez Municipality"] <- "Mayagüez Municipality"
  output_data$geo_county[output_data$geo_county == "San German Municipality"] <- "San Germán Municipality"
  output_data$geo_county[these_pr] <- stri_replace_all(
    output_data$geo_county[these_pr], "Municipio", fixed = "Municipality"
  )

  # virgin islands
  these_vi <- which(output_data$geo_country == "Virgin Islands of the United States")
  output_data$geo_state[these_vi] <- "Virgin Islands of the U.S."
  output_data$geo_country[these_vi] <- "United States"
  output_data$geo_county[output_data$geo_county == "Saint Croix Island"] <- "St. Croix"
  output_data$geo_county[output_data$geo_county == "Saint John Island"] <- "St. John"
  output_data$geo_county[output_data$geo_county == "Saint Thomas"] <- "St. Thomas"
  output_data$geo_county[output_data$geo_county == "Saint Thomas Island"] <- "St. Thomas"

  # Washington D.C.
  these_dc <- which((output_data$geo_country == "Washington (D.C.)") |
                    (output_data$geo_country == "United States ÏbDistrict of Columbia ÏdWashington (D.C.)") |
                    (output_data$geo_state == "District of Columbia") |
                    (output_data$geo_city == "Washington (D.C)") |
                    (output_data$geo_city == "Washington (D.C.)"))

  output_data$geo_country[these_dc] <- "United States"
  output_data$geo_state[these_dc] <- "District of Columbia"
  output_data$geo_county[these_dc] <- NA_character_
  output_data$geo_city[these_dc] <- "Washington"

  # Southern States, Southwestern States, Northeastern States, Germany, Russia
  these_region <- which(
    output_data$geo_state %in% c("Southern States", "Southwestern States", "Northeastern States", "Germany", "Russia")
  )

  output_data$geo_country[these_region] <- NA_character_
  output_data$geo_state[these_region] <- NA_character_
  output_data$geo_county[these_region] <- NA_character_
  output_data$geo_city[these_region] <- NA_character_

  return(output_data)
}

clean_county_names <- function(cset, sset) {
  cset <- stri_replace_all(cset, "St", fixed = "Saint")
  cset <- stri_replace_all(cset, "", fixed = "'")
  cset[sset == "Alabama" & cset == "DeKalb County"] <- "De Kalb County" # 9
  cset[sset == "Arizona" & cset == "Maricpoa County"] <- "Maricopa County" # 1
  cset[sset == "Arkansas" & cset == "Johnston County"] <- "Johnson County" # 1
  cset[sset == "California" & cset == "King County"] <- "Kings County" # 12
  cset[sset == "California" & cset == "Sacremento County"] <- "Sacramento County" # 1
  cset[sset == "California" & cset == "San Bernadino County"] <- "San Bernardino County" # 1
  cset[sset == "California" & cset == "Tehana County"] <- "Tehama County" # 1
  cset[sset == "Colorado" & cset == "Anchuleta County"] <- "Archuleta County" # 1
  cset[sset == "Colorado" & cset == "Moffatt County"] <- "Moffat County" # 1
  cset[sset == "Florida" & cset == "Miami-Dade County"] <- "Dade County"
  cset[sset == "Florida" & cset == "St Lucia County"] <- "St Lucie County" # 2
  cset[sset == "Florida" & cset == "Suwanee County"] <- "Suwannee County" # 2
  cset[sset == "Georgia" & cset == "Hale County"] <- "Hall County" # 1
  cset[sset == "Illinois" & cset == "DeKalb County"] <- "De Kalb County" # 3
  cset[sset == "Illinois" & cset == "DuPage County"] <- "Du Page County" # 23
  cset[sset == "Illinois" & cset == "LaSalle County"] <- "La Salle County" # 3
  cset[sset == "Indiana" & cset == "Tipppecanoe County"] <- "Tippecanoe County" # 18
  cset[sset == "Louisiana" & cset == "Placquemines Parish"] <- "Plaquemines Parish" # 6
  cset[sset == "Louisiana" & cset == "Charlotte Parish"] <- "Plaquemines Parish" # 22
  cset[sset == "Maine" & cset == "Tork County"] <- "York County" # 1
  cset[sset == "Maryland" & cset == "Monrgomery County"] <- "Montgomery County" # 1
  cset[sset == "Maryland" & cset == "Queen Anne County"] <- "Queen Annes County" # 3
  cset[sset == "Massachusetts" & cset == "Berkshire Hills County"] <- "Berkshire County" # 63
  cset[sset == "Michigan" & cset == "Ontonagan County"] <- "Ontonagon County" # 1
  cset[sset == "Michigan" & cset == "Wastenaw County"] <- "Washtenaw County" # 6
  cset[sset == "Minnesota" & cset == "Lake Itasca County"] <- "Lake County" # 9
  cset[sset == "Mississippi" & cset == "Cross County"] <- "Cross County" # 1
  cset[sset == "Mississippi" & cset == "Forest County"] <- "Forrest County" # 24
  cset[sset == "Mississippi" & cset == "Waren County"] <- "Warren County" # 4
  cset[sset == "Montana" & cset == "Beaverheed County"] <- "Beaverhead County" # 1
  cset[sset == "New Hampshire" & cset == "Windsor County"] <- "Hillsborough County" # 1
  cset[sset == "New Jersey" & cset == "NMercer County"] <- "Mercer County" # 102
  cset[sset == "New Mexico" & cset == "Dona Ana County"] <- "Doã‘a Ana County" # 22
  cset[sset == "New York" & cset == "Jeferson County"] <- "Jefferson County" # 1
  cset[sset == "New York" & cset == "Long Island County"] <- "Suffolk County" # 5
  cset[sset == "New York" & cset == "Renesselaer County"] <- "Rensselaer County" # 8
  cset[sset == "New York" & cset == "Schulyler County"] <- "Schuyler County" # 2
  cset[sset == "New York" & cset == "Scoharie County"] <- "Schoharie County" # 2
  cset[sset == "North Carolina" & cset == "Johnson County"] <- "Johnston County" # 12
  cset[sset == "North Dakota" & cset == "Nckenzie County"] <- "Mckenzie County" # 1
  cset[sset == "North Dakota" & cset == "Rollette County"] <- "Rolette County" # 2
  cset[sset == "Ohio" & cset == "Galia County"] <- "Gallia County" # 4
  cset[sset == "Oregon" & cset == "Klamath Falls County"] <- "Klamath County" # 1
  cset[sset == "Oregon" & cset == "Lake Sutton County"] <- "Lake County" # 1
  cset[sset == "Tennessee" & cset == "Harding County"] <- "Hardin County" # 1
  cset[sset == "Tennessee" & cset == "Loudoun County"] <- "Loudon County"
  cset[sset == "Texas" & cset == "Nacogdoches. County"] <- "Nacogdoches. County" # 1
  cset[sset == "Texas" & cset == "San Patricia County"] <- "San Patricio County" # 3
  cset[sset == "Virginia" & cset == "Albermarle County"] <- "Albemarle County" # 5
  cset[sset == "Virginia" & cset == "Albermarle"] <- "Albemarle County" # 1
  cset[sset == "Virginia" & cset == "Loudon County"] <- "Loudoun County" # 3
  cset[sset == "Washington" & cset == "Klicktat County"] <- "Klickitat County" # 1
  cset[sset == "Wyoming" & cset == "Larimer County"] <- "Laramie County" # 3

  return(cset)
}
