# jawbone
Automatic data retrieval, descriptive stats, plotting and regression for the sleep data from the Jawbone UP3 fitness tracker

I own a [Jawbone UP3](https://jawbone.com/fitness-tracker/up3) fitness tracker, which I wear at night to track how long I sleep and how much [light, deep and REM sleep](https://en.wikipedia.org/wiki/Sleep_cycle) I get.  This repo contains some code I've written to automatically retrieve my data from the Jawbone website and to do some statistics and visualization.

The script `jawbone.py`, when run from the command line, will retrieve the data, print some statistical information to standard output, and create a PDF file with some plots.  As detailed below, it expects files called `cookies.txt` and `lifestyle_variables.csv` to be present in the same directory.

## Retrieval

Jawbone allows users to download their data for a specified calendar year after they have logged in to the Jawbone website.  My code sends a request using a cookie that the website gives me when I log in.  If you have an account on the Jawbone website and want to use the code, do the following:

1. Log in to the Jawbone website
2. Look up the value of the cookie named `jbsession` from jawbone.com
3. create a file called `cookies.txt`, containing this value, in the same directory as the code

## Lifestyle variables

The main reason I wrote this code was to explore how day-to-day lifestyle factors, like exercise or taking sleeping pills, affect my sleep.  I record these in a file called ``lifestyle_variables.csv.``

(To be continued)
