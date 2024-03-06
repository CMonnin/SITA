# SITA

## Purpose
This app was created to aid in stable isotope tracer analysis (SITA) experiments.  
It is used to determine the inverted correction matrix to correct for natural abudnace in analaytes of interest.

## Features
- Enter a chemical formula to obtain a an inverted correction matrix for the analyte

## How to use
A live version of this app is currently available at https://sita-app.up.railway.app/  
This repo also allows you to run a local version in your browser.  
It uses mostly numpy in the backend and provides a GUI in the browser using Plotly Dash.  

### To run a local version

##### Prerequsites
- Python => 3.10

#### Set up
- Clone this repo either by downloading or using  
`$ git clone https://github.com/CMonnin/SITA.git`  
- Once you've cloned the repo `cd` into the directory and create a virtual environment.  
- For example: `$ python -m venv venv`  
- Active your venv: `$ source venv/bin/activate`
- Install requirements `$ pip install -r requirements.txt`  
- You should now be able to run a server locally in your browser using:`$ python app.py`

## Tech Stack
- Python, numpy for backend matrix calculations
- Plotly Dash for frontend
- Railway for hosting

## Citations
- Natural abudnace of common elements: Coursey, J. S., et al. "Atomic weights and isotopic compositions with relative atomic masses." NIST Physical Measurement Laboratory (2015).
 https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl 
- Nanchen A, Nanchen, Annik, Tobias Fuhrer, and Uwe Sauer. "Determination of metabolic flux ratios from 13 C-experiments and gas chromatography-mass spectrometry data: protocol and principles." Metabolomics: Methods and protocols (2007): 177-197.

## Contributing
This is an open-source project. Contribution are welcome.  
Please for the repo, make changes, and perform a pull request.  
If you'd like a feature to be added please open an issue or reach me: ` cianmonnin at gmail dot com`  

## Release History
- 0.1.0 Initial Release



