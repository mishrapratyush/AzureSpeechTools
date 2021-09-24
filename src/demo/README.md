# Azure CustomSpeech Demo
This project has demo code to demonstrate various features of azure speech service

## Source Code
The source code is in the /src/demo folder. This is a browser based application that demonstrates various capabilities of Azure cognitive services (azure speech). The code has two parts:

1. A web api that the web app interacts with to get access tokens for Azure cognitive services. This is in the **/demo/service** folder. This is an express app.


2. The web app that you see in the browser and interact with various features. This is in the /**/demo/webApp** folder. The webApp is based on create-react-app template

### /src/demo/service folder
This is the web api used by the webApp to get cognitive Services token to connect to Azure cognitive services

### /src/demo/webApp folder
Code in this folder is setup as follows:
1. The default webpage or the home page is in the webApp/public/index.html folder
2. All the react components are in the webApp/src/components folder

## How to Run
The service and the webApp are separate nodejs projects each has its own npm dependencies and environment variables. Since the webApp needs to know where the service is running, you will need to make sure to change the values in the .env files of each project.

For the service to run, update .env file and populate these values to match your local environment

```
SPEECH_KEY=""
SPEECH_REGION=""
PORT="3001"
ENVIRONMENT=development
```

For the webApp to run copy the /src/demo/webApp/.env file and save it as /src/demo/webApp/.env.development and set these values. This is the URL where service app will be running. 

REACT_APP_SERVICE_URL = "http://localhost:3001"

To avoid CORS error when running locally, ensure ENVIRONMENT variable in /src/service/.env is set to "development". The webApp will run on port 3000 so the following code has been added in /src/demo/service/index.js

```
app.use(function (req, res, next) {
  const environment = process.env.NODE_ENV;
  if (environment === 'development') {
    res.header('Access-Control-Allow-Origin', 'http://localhost:3000'); // update to match the domain you will make the request from
    res.header(
      'Access-Control-Allow-Headers',
      'Origin, X-Requested-With, Content-Type, Accept'
    );
  }
  next();
});
```

### To run the apps:
1. For the service app: 

```
cd service
npm install
npm run dev
```

2. For the webApp app: 

```
cd webApp
npm install
npm run start
```
