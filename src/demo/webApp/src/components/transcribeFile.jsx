import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { getTokenOrRefresh } from '../util';
import {
  AudioConfig,
  AudioInputStream,
  SpeechConfig,
  ResultReason,
} from 'microsoft-cognitiveservices-speech-sdk';
const sdk = require('microsoft-cognitiveservices-speech-sdk');

export class TranscribeFileComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      displayText: 'Will display transcription here.',
      customEndpoint: '',
    };
  }

  async componentDidMount() {
    // check for valid speech key/region
    const tokenRes = await getTokenOrRefresh();

    if (tokenRes.authToken === null) {
      this.setState({
        displayText: 'FATAL_ERROR: ' + tokenRes.error,
      });
    } else {
      const speechConfig = SpeechConfig.fromAuthorizationToken(
        tokenRes.authToken,
        tokenRes.region
      );
      speechConfig.speechRecognitionLanguage = 'en-US';
      this.setState({
        speechConfiguration: speechConfig,
      });
    }
  }

  openPushStream(audioFile) {
    console.log('openPushStream:', audioFile.name);

    // create the push stream we need for the speech sdk.
    let pushStream = AudioInputStream.createPushStream();
    const reader = new FileReader();

    reader.onload = function () {
      pushStream.write(reader.result);
    };

    reader.onloadend = function () {
      pushStream.close();
    };

    reader.readAsArrayBuffer(audioFile);
    return pushStream;
  }

  customEndpointChanged = async function (event) {
    await this.setState({
      customEndpoint: event.target.value,
    });
    // console.log("customEndpointChanged: ", this.state.customEndpoint);
  };

  async startSpeechRecognizerForStream(audioStream) {
    const speechConfig = this.state.speechConfiguration;
    const audioConfig = AudioConfig.fromStreamInput(audioStream);
    const endpoint = this.state.customEndpoint;
    if (endpoint.length !== 0) {
      speechConfig.endpointId = endpoint;
      console.log('setting speech setting endpointId: ', endpoint);
    }
    let resultText = '';

    const reco = new sdk.SpeechRecognizer(speechConfig, audioConfig);

    reco.canceled = (s, e) => {
      let str = '(cancel) Reason: ' + sdk.CancellationReason[e.reason];
      if (e.reason === sdk.CancellationReason.Error) {
        str += ': ' + e.errorDetails;
      }
      console.log(str);
    };

    // Signals that a new session has started with the speech service
    reco.sessionStarted = (s, e) => {
      this.setState({
        displayText: 'Starting transcription...',
      });
      let str = '(sessionStarted) SessionId: ' + e.sessionId;
      console.log(str);
    };

    // Signals the end of a session with the speech service.
    reco.sessionStopped = (s, e) => {
      let str = '(sessionStopped) SessionId: ' + e.sessionId;
      console.log(str);
    };

    // Signals that the speech service has started to detect speech.
    reco.speechStartDetected = (s, e) => {
      let str = '(speechStartDetected) SessionId: ' + e.sessionId;
      console.log(str);
    };

    // Signals that the speech service has detected that speech has stopped.
    reco.speechEndDetected = (s, e) => {
      let str = '(speechEndDetected) SessionId: ' + e.sessionId;
      console.log(str);
    };

    reco.recognized = (s, e) => {
      if (e.result.reason === ResultReason.RecognizedSpeech) {
        resultText += `\n${e.result.text}`;

        this.setState({
          displayText: resultText,
          lastRecognizedResult: e.result.text,
        });
      } else if (e.result.reason === ResultReason.NoMatch) {
        resultText += `\nNo Match`;
      }

      let str = '(speechRecognized) Text: ' + e.result.text;
      console.log(str);
    };

    reco.startContinuousRecognitionAsync();
  }

  static propTypes = {
    fileName: PropTypes.string,
    audioFile: PropTypes.object,
  };

  render() {
    return (
      <div>
        <div>
          Custom endpoint to be used for transcription:
          <input
            id="customEndpointText"
            type="text"
            onChange={(e) => this.customEndpointChanged(e)}
          />
        </div>
        <div>
          <i
            className="fas fa-sync mr-2"
            id="continuousRecoIcon"
            onClick={() =>
              this.startSpeechRecognizerForStream(
                this.openPushStream(this.props.audioFile)
              )
            }
          ></i>
          Start continuous recognition on file:{' '}
          <code>{this.props.fileName}</code>
        </div>
        <p></p>
        <div className="luis-output-display rounded">
          <code>{this.state.displayText}</code>
        </div>
      </div>
    );
  }
}
