# MaJOrCA - Multiple JObs CreAtor

## Configure
1. modify `./create_job.py -c your_conf.conf`
2. modify `your_conf.conf`
3. launch `./create_job.py -f your_conf.conf`

## Note:
- In `conf` file you can generate multiple jobs adding new sections
- For every varibale you can select multiples choice separating each entry with 
a semicolon

## makefile
- `clean` : remove unused file.
- `qsub` :  submit all `pbs` file. 
- `sh` :  submit all `sh` file. 