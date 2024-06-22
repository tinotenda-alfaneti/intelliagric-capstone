# IntelliAgric API

## How to test

Request the environment variable and crops dataset - `ml_models` and `api keys`

Place the folders inside the `models` directory

Run `pip install -r requirements.txt` while in the root of the project (best option create venv)

Then run `flask --app app run`

The web app will be open on http://127.0.0.1:5000


## Running test

`python -m unittest discover -s tests` 

## Generate test suites reports and coverage

`pytest --html=report.html --cov=src --cov-report=html`

## Example test for frontend of protected endpoints
```
// Example using fetch in JavaScript
const idToken = await firebase.auth().currentUser.getIdToken(true);
const response = await fetch('/get-soil-data', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${idToken}`
    }
});
const data = await response.json();
```


