import React from 'react';
import {
  useHistory
} from "react-router-dom";

import './imgbox.css';

function queryUrl(query, key, fallback = null) {
  let res = (new URLSearchParams(query)).get(key);
  return res === null ? fallback : res;
}

function ImgWithId(props) {
  let history = useHistory();
  function handleClick(data) {
    let res = new URLSearchParams(history.location.search);
    res.set("id", props.id);

    history.push({
        "pathname": "/",
        "search": "?" + res.toString()
    });
    history.go(0);
  }

  return (
      <img className='thumb' src={props.ilink} onClick={() => handleClick()} alt="nav"/>
  );
}

class ImgBox extends React.Component {

  constructor(props) {
     super(props);
     this.state = {
       data: null,
       dtype: "none",
       opacity: 80,
       conf: 50
     }
   }

   componentDidMount() {
     let atype = queryUrl(this.props.location.search, "id", "2017877547");

     // for local dev => /addi_project/06_interactive_viz/build/json/
     // for build ver => ./json/
     fetch("./json/" + atype + ".json").then(res => {
       return res.json()
     }).then(res => {
       this.setState({
         data: res
       });
     })
   }

   handleSelectDataType(dtype) {
     this.setState({
       dtype: dtype,
     });
   }

   handleOpacityChange(e) {
      this.setState({
        opacity: e.target.value
      });
    }

    handleConfChange(e) {
       this.setState({
         conf: e.target.value
       });
     }

    render() {
      if (!this.state.data) {
        return <span></span>
      }

      let ipath = this.state.data.image_url;

      var annotation = null;
      var annotation2 = null;

      if (this.state.dtype === "face")
      {
        annotation = this.state.data.face.filter(
          val => (100 * val.prob) > this.state.conf
        ).map( (val, i) => {
          return(
            <g key={i}>
              <rect
                x={val.x}
                y = {val.y}
                width = {val.width}
                height = {val.height}
                stroke="#d79921"
                strokeWidth="4"
                fill="none"
                />
            </g>
          )
        });
      } else if (this.state.dtype === "inst") {
        annotation = this.state.data.inst.filter(
          val => (100 * val.prob) > this.state.conf
        ).map( (val, i) => {
          return(
            <g key={i}>
              <rect
                x={val.x}
                y = {val.y}
                width = {val.width}
                height = {val.height}
                stroke="#d79921"
                strokeWidth="4"
                fill="none"
                />
              <text
                x={val.x}
                y={val.y - 5}
                style={{font: "18px sans-serif", fill: "#d79921"}}>
                {val.class}
              </text>
            </g>
          )
        });
    } else if (this.state.dtype === "lvic") {
      annotation = this.state.data.lvic.filter(
        val => (100 * val.prob) > this.state.conf
      ).map( (val, i) => {
        return(
          <g key={i}>
            <rect
              x={val.x}
              y = {val.y}
              width = {val.width}
              height = {val.height}
              stroke="#d79921"
              strokeWidth="4"
              fill="none"
              />
            <text
              x={val.x}
              y={val.y - 5}
              style={{font: "18px sans-serif", fill: "#d79921"}}>
              {val.class}
            </text>
          </g>
        )
      });
    } else if (this.state.dtype === "kpnt") {
      annotation = this.state.data.kpnt.filter(
        val => (100 * val.score) > this.state.conf
      ).map( (val, i) => {
        return(
          <g key={i}>
            <circle cx={val.x} cy={val.y} r="5" fill="#d79921"/>
          </g>
        )
      });
      annotation2 = this.state.data.kcnt.filter(
        val => ((100 * val.score0) > this.state.conf) & ((100 * val.score1) > this.state.conf)
      ).map( (val, i) => {
        return(
          <g key={i}>
            <line x1={val.x0} y1={val.y0} x2={val.x1} y2={val.y1} stroke="#d79921"/>
          </g>
        )
      });
    }

    let nn_recs = this.state.data.nn.map( (val, i) => {
      return(
        <div key ={i} className='thumbcon'><ImgWithId id={val} ilink={this.state.data.nn_thumb[i]}/></div>
      )
    });

    let rr_recs = this.state.data.rr.map( (val, i) => {
      return(
        <div key ={i} className='thumbcon'><ImgWithId id={val} ilink={this.state.data.rr_thumb[i]}/></div>
      )
    });

    let pano = this.state.data.pano.map( (val, i) => {
      return(
        <div
          key={i}
          className="pano-bar-size"
          ><div
            className="pano-bar-inner"
            style={{width: val.value / 1 + "%", backgroundColor: val.color}}>
            </div>
          <span className='pano-bar-text'>
            {val.class_name + " (" + Math.round(val.value) + "%)"}
          </span>
        </div>
      )
    });

    let c_name = this.state.data.collection === "fsac" ? "FSA-OWI Color Images" : "George Grantham Bain Collection";
    let c_link = this.state.data.collection === "fsac" ? "https://www.loc.gov/pictures/collection/fsac/" : "https://www.loc.gov/pictures/collection/ggbain/";

    return (
      <div className="wrapper">
      <div className="mbox">
        <div className="mboxdata">
          <p className="mboxtitle"><b>Access & Discovery of Documentary Images (ADDI) Visualization</b></p>
          <p className="mboxabout"><b>By Taylor Arnold and Lauren Tilton for the Library of Congress</b></p>
          <p className="mboxabout">This interactive vizaliation is part of the ADDI project, which was designed to
          adapt and apply computer vision algorithms to aid in the discovery and use of digital collections,
          specifically documentary photography collections held by the Library of Congress.</p>
          <p className="mboxabout">For more information, see the project's <a href="https://github.com/statsmaths/addi_project" target="_blank" rel="noopener noreferrer">main page</a>.</p>
        </div>
      </div>
      <div className="ibox">
        <div className="ibox-inner">
          <svg viewBox={"0 0 " + this.state.data.width + " " + this.state.data.height}>
            <image x="0" y="0" width="100%" height="100%" href={ipath}/>
            <rect x="0" y="0" width="100%" height="100%" fill="black" opacity={(100 - this.state.opacity) + "%"} stroke="#928374" strokeWidth="4"/>
            {annotation} {annotation2}
          </svg>
        </div>
      </div>
      <div className="tbox">
        <div className="tbox-inner">
            <div className="mdata">
              <span><b><u>ARCHIVAL DATA</u></b>
                <div className="tooltipbottom">
                  &nbsp;[?]
                  <span className="tooltiptextbottom">The fields in this section were directly taken from
                  the archival information produced by the Library of Congress.</span>
                </div>
              </span><br/>
              <p className="archinfo"><b>Title:</b> {this.state.data.title}</p>
              <p className="archinfo"><b>Date:</b> {this.state.data.sort_date}</p>
              <p className="archinfo"><b>Collection:</b> <a href={c_link} target="_blank" rel="noopener noreferrer">{c_name}</a></p>
              <p className="archinfo"><b>Library of Congress:</b> <a href={this.state.data.url} target="_blank" rel="noopener noreferrer">{this.state.data.filename}</a></p>
              <hr/>
              <span><b><u>COMPUTER VISION ANNOTATIONS</u></b>
                <div className="tooltip">
                  &nbsp;[?]
                  <span className="tooltiptext">The information below was created automatically
                  by the application of computer vision algorithms. See each element for more information
                  about each alogorithm.</span>
                </div>
              </span><br/>
              <div className="inputcont-outer">
                <div className="inputcont">
                  <input
                    type='range'
                    min="0"
                    max="100"
                    step="1"
                    value={this.state.opacity}
                    onChange={this.handleOpacityChange.bind(this)}/>
                  <b>&#8592; Opacity </b>
                  <div className="tooltipright">
                    &nbsp;[?]
                    <span className="tooltiptextright">Slider to fade the image to highlight the annotations.</span>
                  </div>
                </div>
                <div className="inputcont">
                <input
                  type='range'
                  min="0"
                  max="100"
                  step="1"
                  value={this.state.conf}
                  onChange={this.handleConfChange.bind(this)}/>
                  <b>&#8592; Confidence</b>
                  <div className="tooltipright">
                    &nbsp;[?]
                    <span className="tooltiptextright">Each annotation has a confidence score attached to it. Slide
                    to the left to include less confident annotations and to the right to include only those
                    annotations with a high confidence score.</span>
                  </div>
                </div>
              </div>
              <div className="anno-button-box">
                <b>Annotation &#8594;</b>
                <button
                  className={"anno-button tooltip " + (this.state.dtype === "none" ? " anno-button-active" : "")}
                  onClick={() => this.handleSelectDataType("none")}>None
                  <span className="tooltiptext">Clear annotations.</span>
                  </button>
                <button
                  className={"anno-button tooltip " + (this.state.dtype === "face" ? " anno-button-active" : "")}
                  onClick={() => this.handleSelectDataType("face")}>Faces
                  <span className="tooltiptext">Draw boxes around detected faces.</span>
                  </button>
                <button
                  className={"anno-button tooltip " + (this.state.dtype === "inst" ? " anno-button-active" : "")}
                  onClick={() => this.handleSelectDataType("inst")}> Objects
                  <span className="tooltiptext">Draw boxes around detected objects and people.</span>
                  </button>
                <button
                  className={"anno-button tooltip " + (this.state.dtype === "lvic" ? " anno-button-active" : "")}
                  onClick={() => this.handleSelectDataType("lvic")}>LVIS
                  <span className="tooltiptext">Draw boxes around detected objects; uses a larger set of
                  object types than the Objects annotations.</span>
                  </button>
                <button
                  className={"anno-button tooltipright " + (this.state.dtype === "kpnt" ? " anno-button-active" : "")}
                  onClick={() => this.handleSelectDataType("kpnt")}>Pose
                  <span className="tooltiptextright">Show the limbs and body of detected people.</span>
                  </button>
              </div>
              <div className="pano-bars-outer">
                <div className="pano-bars-title">
                  <b>Panoptic Segmentation</b>
                  <div className="tooltip">
                    &nbsp;[?]
                    <span className="tooltiptext">Detected regions in the image, by percentage of the entire image. Stuff is in yellow; objects are in green.</span>
                  </div>
                </div>
                <div className="pano-bars-inner">
                  {pano}
                </div>
              </div>
            </div>
            <div className="recs">
              <span>Similar Photographs
                <div className="tooltip">
                  &nbsp;[?]
                  <span className="tooltiptext">Ten images that have some visual similarity
                  to the starting image based on the image embedding method.</span>
                </div>
              </span>
              <div className="flex-container">
               {nn_recs}
              </div>
              <span>Other Recommendations
                <div className="tooltip">
                  &nbsp;[?]
                  <span className="tooltiptext">Five randomly selected images from the collection to show
                  other possibilities.</span>
                </div>
              </span>
              <div className="flex-container">
                {rr_recs}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export { ImgBox };
