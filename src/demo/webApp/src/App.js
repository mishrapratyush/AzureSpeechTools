import React, { Component } from 'react';
import { Container, Row, Col } from 'reactstrap';
import { TranscribeFileComponent } from './components/transcribeFile';

import './custom.css';

export default class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      fileToRecognize: null,
    };
  }

  fileChange(event) {
    const audioFile = event.target.files[0];
    console.log(audioFile);

    this.setState({
      fileToRecognize: audioFile,
      fileName: audioFile.name,
    });
  }

  render() {
    return (
      <Container className="app-container">
        <h1 className="display-4 mb-3">Azure cognitive services demo app</h1>
        <Row xs="1">
          <Col>
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
              Select an audio (.wav) file
            </div>
          </Col>
          <Col></Col>
        </Row>
        <Row xs="1">
          <Col>
            <hr></hr>
          </Col>
        </Row>

        <Row xs="1">
          <Col>
            <TranscribeFileComponent
              id="baseline"
              audioFile={this.state.fileToRecognize}
              fileName={this.state.fileName}
            />
          </Col>
        </Row>
        <Row xs="1">
          <Col>
            <hr></hr>
          </Col>
        </Row>
        <Row xs="1">
          <Col>
            <TranscribeFileComponent
              id="customEndPoint"
              audioFile={this.state.fileToRecognize}
              fileName={this.state.fileName}
            />
          </Col>
        </Row>
      </Container>
    );
  }
}
