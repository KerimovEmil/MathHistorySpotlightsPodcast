
nlm login

# set variable of notebook id
$NB_ID = "692242fc-0aa1-4d2c-a276-ff9e0123e4ef"

# Example of adding a source

nlm source add $NB_ID --url "https://mathshistory.st-andrews.ac.uk/Biographies/Mobius/"

# Example of generating an audio podcast
nlm audio create $NB_ID --confirm

## check status
nlm studio status $NB_ID
### This shows the header (first 3 lines) and the very first entry (4th line)
nlm studio status $NB_ID | Select-Object -First 4
### This shows only in progress
nlm studio status $NB_ID | Select-String "in_progress"
### This loops
while($true) {
  Clear-Host
  date
  nlm studio status $NB_ID | Select-String "in_progress", "ID" # Keeps the header line for context
  Start-Sleep -Seconds 10
}

# Download Audio file

## 1. Force PowerShell to handle UTF-8 so "ö" doesn't become "├╢"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

## 2. Get the item with full metadata
$FirstItem = (nlm studio status $NB_ID --full --json | ConvertFrom-Json)[0]

## 3. Clean the title: Remove illegal chars AND fix encoding artifacts
$Title = [System.Text.Encoding]::UTF8.GetString([System.Text.Encoding]::Default.GetBytes($FirstItem.title))
$CleanTitle = $Title -replace '[\\\/\:\*\?\"\<\>\|]', ''

## 3. Download the file using that Title as the filename
nlm download audio --id $FirstItem.id --output "./$CleanTitle.m4a" $NB_ID


# 

nlm infographic create $NB_ID --confirm

$InfographicID = (nlm infographic create $NB_ID --confirm | Out-String | Select-String -Pattern '[a-f0-9-]{36}').Matches.Value

$FirstItem = (nlm studio status $NB_ID --full --json | ConvertFrom-Json)[0]

$InfographicID = "a3a7b3c7-51a8-467e-ac13-e46e6c935b4e"
# Download using the $InfographicID we just saved
nlm download infographic --id $FirstItem.id --output "./mobius.png" $NB_ID

# (Optional) If you have ImageMagick installed, convert to AVIF
magick convert "./August Ferdinand Möbius.png" "./August Ferdinand Möbius.avif"


# 3. Download the resulting image
nlm download infographic $NB_ID ./mobius_info.png

# delete sources
nlm source list $NB_ID
nlm source delete <source-id> -y


# 1. Ensure only the one source is in the notebook
# 2. Generate the infographic
nlm studio create $NB_ID --type infographic --style scientific --confirm

# 3. Download the resulting image
nlm download infographic $NB_ID ./mobius_info.png


# Bash

#!/bin/bash

# Array of your 3 biography links
SOURCES=(
  "https://mathshistory.st-andrews.ac.uk/Biographies/Mobius/"
  "https://mathshistory.st-andrews.ac.uk/Biographies/Cauchy/"
)

for URL in "${SOURCES[@]}"; do
  NAME=$(basename $URL)
  echo "Processing $NAME..."

  # 1. Create a clean notebook for THIS source only
  NB_ID=$(nlm notebook create "Project_$NAME" --raw)

  # 2. Add the URL
  nlm source add $NB_ID --url "$URL"

  # 3. Generate Audio Deep Dive
  nlm studio create $NB_ID --type audio --confirm
  nlm download audio $NB_ID "./${NAME}_podcast.mp3"

  # 4. Generate Infographic
  nlm studio create $NB_ID --type infographic --style professional --confirm
  nlm download infographic $NB_ID "./${NAME}_visual.png"

  echo "Completed $NAME. Files saved."
done