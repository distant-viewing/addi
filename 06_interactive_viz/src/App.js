import React from 'react';
import {
  BrowserRouter as Router,
  Route
} from "react-router-dom";

import { ImgBox } from "./components/imgbox.js";

import './reset.css';
import './App.css';

class ImageViewer extends React.Component {

  render() {
    return (
      <ImgBox location={this.props.location}/>
    );
  }
}

// ***************************************************************************
// Wrap the App and return the rendered Viewer
function App() {
  return (
    <Router basename={process.env.PUBLIC_URL}>
      <Route component={ImageViewer} />
    </Router>
  );
}

export default App;
