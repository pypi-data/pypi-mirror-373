# Nightly scripts for LHCbPR2

## Files directly related to LHCbPR

* [scripts/lbpr-example](scripts/lbpr-example) - Run selected test, process it with LHCbPR handlers and produce zip file with results
* [scripts/lbpr-get-command](scripts/lbpr-get-command) - the main command  It writes and runs the script that:
    1. setup environment
    2. run the selected test
    3. get handlers (from git or selected folder)
    4. process result with handlers and saves it to the zip file.
* [scripts/lbpr-collect](scripts/lbpr-collect) - run handlers on job results. It's used in step 3. and 4. of lbpr-get-command command.
* [python/LbPR/LbPRJobManager.py](python/LbPR/LbPRJobManager.py) - get information from LHCbPR2BE API server. This information is used in steps 1. and 2. of lbpr-get-command.

## How to run example test

See documenation in [scripts/lbpr-example](scripts/lbpr-example) file.
What you can setup in this file:
1. Url of LHCbPR2BE API server.
2. Job description name from LHCbPR2BE server. By the job description name we get the information from the server on how we need to run the test (lb-run parameters). The job description should exists at the LHCbPR2BE service.
3. Nightly slot name and number.
4. Platform (CMTCONFIG value).
5. Project name (GEANT4, Brunel,...)
6. Handler name for job results.
