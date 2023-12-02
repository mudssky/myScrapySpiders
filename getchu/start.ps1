[CmdletBinding()]
param(
	[string]$start_id,
	[string]$end_id,
	[switch]$switchEnv
)

if ($switchEnv) {
	poetry shell
	exit 0
}



# scrapy crawl getchuID  -s JOBDIR=.scrapy/jobdir/rjid15 -a start_id=1232471  -a end_id=1251084
scrapy crawl getchuID  -s JOBDIR=.scrapy/jobdir/rjid15 -a start_id=$start_id  -a end_id=$end_id