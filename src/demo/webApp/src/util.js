require('dotenv').config();
import axios from 'axios';
import Cookie from 'universal-cookie';

export async function getTokenOrRefresh() {
  const cookie = new Cookie();
  const speechToken = cookie.get('speech-token');

  if (speechToken === undefined) {
    try {
      const serviceUrl = process.env.REACT_APP_SERVICE_URL;
      console.log(`serviceURL: ${serviceUrl}`);
      const res = await axios.get(`${serviceUrl}/api/get-speech-token`);
      const token = res.data.token;
      const region = res.data.region;
      cookie.set('speech-token', region + ':' + token, {
        maxAge: 540,
        path: '/',
      });

    //   console.log('Token fetched from back-end: ' + token);
      return { authToken: token, region: region };
    } catch (err) {
      console.log(err.response.data);
      return { authToken: null, error: err.response.data };
    }
  } else {
    // console.log('Token fetched from cookie: ' + speechToken);
    const idx = speechToken.indexOf(':');
    return {
      authToken: speechToken.slice(idx + 1),
      region: speechToken.slice(0, idx),
    };
  }
}

export async function getLuisPrediction(queryText) {
  try {
    const serviceUrl = process.env.REACT_APP_SERVICE_URL;
    const queryJson = { query: queryText };
    const res = await axios.post(
      `${serviceUrl}/api/get-luis-prediction`,
      queryJson
    );
    return res;
  } catch (err) {
    console.log(err.response.data);
    return { error: err.response.data };
  }
}
