require('dotenv').config();
const express = require('express');
const axios = require('axios');
const helmet = require('helmet');
const pino = require('express-pino-logger')();

const app = express();
app.use(helmet());
app.use(express.json());
app.use(pino);

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

app.get('/api/get-speech-token', async (req, res, next) => {
  res.setHeader('Content-Type', 'application/json');
  const speechKey = process.env.SPEECH_KEY;
  const speechRegion = process.env.SPEECH_REGION;

  if (
    speechKey === 'paste-your-speech-key-here' ||
    speechRegion === 'paste-your-speech-region-here'
  ) {
    res
      .status(400)
      .send('You forgot to add your speech key or region to the .env file.');
  } else {
    const headers = {
      headers: {
        'Ocp-Apim-Subscription-Key': speechKey,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    };

    try {
      const tokenResponse = await axios.post(
        `https://${speechRegion}.api.cognitive.microsoft.com/sts/v1.0/issueToken`,
        null,
        headers
      );
      res.send({ token: tokenResponse.data, region: speechRegion });
    } catch (err) {
      res.status(401).send('There was an error authorizing your speech key.');
    }
  }
});

app.post('/api/get-luis-prediction', async (req, res, next) => {
  // console.dir(req.body.query);
  // res.json({request_query: req.body.query});
  res.setHeader('Content-Type', 'application/json');
  const luisKey = process.env.LUIS_KEY;
  const luisAppId = process.env.LUIS_APP_ID;
  const luisEndpoint = process.env.LUIS_ENDPOINT;
  if (
    luisKey === 'paste-your-luis-key-here' ||
    luisAppId === 'paste-your-luis-appId-here' ||
    luisEndpoint === 'paste-your-luis-endpoint-here'
  ) {
    res
      .status(400)
      .send(
        'You forgot to add your luis subscription key or luis appId or the endpoint to the .env file.'
      );
  } else {
    console.log('Request query: ', req.body, req.body.query);
    let luisPredictionUrl = `${luisEndpoint}/luis/prediction/v3.0/apps/${luisAppId}/slots/production/predict?subscription-key=${luisKey}&verbose=false&show-all-intents=false&log=false&query=${req.body.query}`;
    // console.log("LuisPredictionUrl: ", luisPredictionUrl);

    try {
      const luisResult = await axios.post(luisPredictionUrl);
      res.status(200).json(luisResult.data);
    } catch (err) {
      console.log(err);
      res.status(500).send('There was error calling luis');
    }
  }
});

const port = process.env.PORT || 3001;
console.log(`port: ${port}`);
process.env.NODE_ENV = process.env.ENVIRONMENT
console.log(`Environment: ${process.env.NODE_ENV}`);

app.listen(port, () =>
  console.log(`Express server is running on localhost:${port}`)
);
