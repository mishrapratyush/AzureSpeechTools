import React, { Component } from 'react';
import { Row, Col } from 'reactstrap';
import { getTokenOrRefresh } from '../util';

import '../custom.css';
import { ResultReason } from 'microsoft-cognitiveservices-speech-sdk';
const speechsdk = require('microsoft-cognitiveservices-speech-sdk');

export class SpeechComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      displayText: 'INITIALIZED: ready to test speech...',
      lastRecognizedResult:
        'Last recognized result from speech will be displayed here...',
      speechRecognizer: null,
      startRecognizer: true,
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
      const speechConfig = speechsdk.SpeechConfig.fromAuthorizationToken(
        tokenRes.authToken,
        tokenRes.region
      );
      speechConfig.speechRecognitionLanguage = 'en-US';

      const audioConfig = speechsdk.AudioConfig.fromDefaultMicrophoneInput();
      const recognizer = new speechsdk.SpeechRecognizer(
        speechConfig,
        audioConfig
      );
      this.setState({
        speechRecognizer: recognizer,
        startRecognizer: true,
      });
    }
  }

  async continuousRecoFromMic(startRecognizer) {
    console.log('startRecognizer:', startRecognizer);

    if (startRecognizer) {
      this.setState({
        displayText: 'speak into your microphone...',
      });

      const tokenObj = await getTokenOrRefresh();
      const speechConfig = speechsdk.SpeechConfig.fromAuthorizationToken(
        tokenObj.authToken,
        tokenObj.region
      );
      speechConfig.speechRecognitionLanguage = 'en-US';

      const audioConfig = speechsdk.AudioConfig.fromDefaultMicrophoneInput();
      const recognizer = new speechsdk.SpeechRecognizer(
        speechConfig,
        audioConfig
      );

      let resultText = '';

      recognizer.sessionStarted = (s, e) => {
        resultText = 'Session ID: ' + e.sessionId;

        this.setState({
          displayText: resultText,
        });
      };

      recognizer.sessionStopped = (s, e) => {
        resultText += 'Session ID: ' + e.sessionId + ' has ended.';
        this.setState({
          displayText: resultText,
        });
      };

      recognizer.recognized = (s, e) => {
        if (e.result.reason === ResultReason.RecognizedSpeech) {
          resultText += `\n${e.result.text}`;

          this.setState({
            displayText: resultText,
            lastRecognizedResult: e.result.text,
          });

          this.props.updateLastRecognizedResult(e.result.text);
        } else if (e.result.reason === ResultReason.NoMatch) {
          resultText += `\nNo Match`;
        }
      };

      recognizer.startContinuousRecognitionAsync();
      this.setState({
        speechRecognizer: recognizer,
        startRecognizer: false,
      });
    } else {
      const recognizer = this.state.speechRecognizer;
      recognizer.stopContinuousRecognitionAsync();
      this.setState({
        displayText:
          'Transcription stopped. Click microphone button to start again.',
        startRecognizer: true,
      });
    }
  }

  async recognizeOnceFromMic() {
    const tokenObj = await getTokenOrRefresh();
    const speechConfig = speechsdk.SpeechConfig.fromAuthorizationToken(
      tokenObj.authToken,
      tokenObj.region
    );
    speechConfig.speechRecognitionLanguage = 'en-US';

    const audioConfig = speechsdk.AudioConfig.fromDefaultMicrophoneInput();
    const recognizer = new speechsdk.SpeechRecognizer(
      speechConfig,
      audioConfig
    );

    this.setState({
      displayText: 'speak into your microphone...',
      lastRecognizedResult: 'waiting for recognition to finish ...',
      speechRecognizer: null,
      startRecognizer: true,
    });

    recognizer.recognizeOnceAsync((result) => {
      let displayText;
      if (result.reason === ResultReason.RecognizedSpeech) {
        displayText = `RECOGNIZED: Text=${result.text}`;
      } else {
        displayText =
          'ERROR: Speech was cancelled or could not be recognized. Ensure your microphone is working properly.';
      }

      this.setState({
        displayText: displayText,
        lastRecognizedResult: result.text,
        luisResult: '',
      });
      this.props.updateLastRecognizedResult(result.text);
    });
  }

  async fileChange(event) {
    const audioFile = event.target.files[0];
    console.log(audioFile);
    const fileInfo = audioFile.name + ` size=${audioFile.size} bytes `;

    this.setState({
      displayText: fileInfo,
      lastRecognizedResult: 'waiting for recognition to finish ...',
      speechRecognizer: null,
      startRecognizer: true,
      fileName: audioFile,
    });

    this.props.updateLastRecognizedResult('');

    const tokenObj = await getTokenOrRefresh();
    const speechConfig = speechsdk.SpeechConfig.fromAuthorizationToken(
      tokenObj.authToken,
      tokenObj.region
    );
    speechConfig.speechRecognitionLanguage = 'en-US';

    const audioConfig = speechsdk.AudioConfig.fromWavFileInput(audioFile);
    const recognizer = new speechsdk.SpeechRecognizer(
      speechConfig,
      audioConfig
    );

    recognizer.recognizeOnceAsync((result) => {
      let displayText;
      if (result.reason === ResultReason.RecognizedSpeech) {
        displayText = `RECOGNIZED: Text=${result.text}`;
        this.props.updateLastRecognizedResult(result.text);
      } else {
        displayText =
          'ERROR: Speech was cancelled or could not be recognized. Ensure your microphone is working properly.';
      }

      this.setState({
        displayText: fileInfo + displayText,
      });
    });
  }

  async handleContinuousRecoButtonOnClick() {
    let currState = this.state.startRecognizer;
    if (currState) {
      document.getElementById('continuousRecoIcon').classList.add('fa-spin');
    } else {
      document.getElementById('continuousRecoIcon').classList.remove('fa-spin');
    }
    await this.continuousRecoFromMic(this.state.startRecognizer);
  }

  render() {
    return (
      <Row xs="2">
        <Col className="speech-col1">
          <div className="row main-container">
            <div>
              <i
                className="fas fa-sync mr-2"
                id="continuousRecoIcon"
                onClick={() => this.handleContinuousRecoButtonOnClick()}
              ></i>
              Start continuous recognition using microphone
              <div className="mt-2">
                <label htmlFor="audio-file">
                  <i className="fas fa-file-audio fa-lg mr-2"></i>
                </label>
                <input
                  type="file"
                  id="audio-file"
                  onChange={(e) => this.fileChange(e)}
                  style={{ display: 'none' }}
                />
                Start recognition on an audio (.wav) file
              </div>
              <div>
                <i
                  className="fas fa-microphone fa-lg mr-2"
                  onClick={() => this.recognizeOnceFromMic()}
                ></i>
                Do single shot recognition using microphone
              </div>
            </div>
          </div>
        </Col>
        <Col>
          <div className="output-display rounded">
            <code>{this.state.displayText}</code>
          </div>
        </Col>
      </Row>
    );
  }
}
