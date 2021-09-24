import React, { Component } from 'react';
import { getLuisPrediction } from '../util';

export class LuisComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      luisResult: '',
    };
  }

  async getEntitiesFromLuis(recognizedText) {
    console.log('LUIS: ', recognizedText);
    //call server api to call LUIS
    const result = await getLuisPrediction(recognizedText);
    console.log('luis result: ', result);

    let luisResult = '';

    if (result.status === 200) {
      luisResult = JSON.stringify(result.data);
    } else {
      luisResult = JSON.stringify(result);
    }

    this.setState({
      luisResult: luisResult,
    });
  }

  render() {
    return (
      <div>
        <div>
          <p>
            <code>{this.props.luisQuery}</code>
          </p>
        </div>

        <div>
          <i
            className="fas fa-stream mr-2"
            onClick={() => this.getEntitiesFromLuis(this.props.luisQuery)}
          ></i>
          Get entities for last recognized result
        </div>
        <p></p>
        <div className="luis-output-display rounded">
          <code>{this.state.luisResult}</code>
        </div>
      </div>
    );
  }
}
