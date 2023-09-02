[CmdletBinding()]
param(
	[string]$start_id,
	[string]$end_id)
poetry shell

scrapy crawl rjid -s JOBDIR=.scrapy/jobdir/rjid1  -a start_id=$start_id  -a end_id=$end_id