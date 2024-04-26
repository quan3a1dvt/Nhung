import logo from './logo.svg';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import socketIOClient from 'socket.io-client';

import './App.css';
import './static/assets/css/adminlte.min.css'
import './static/assets/plugins/tempusdominus-bootstrap-4/css/tempusdominus-bootstrap-4.min.css'
import './static/assets/plugins/icheck-bootstrap/icheck-bootstrap.min.css'
import './static/assets/plugins/jqvmap/jqvmap.min.css'
import './static/assets/plugins/overlayScrollbars/css/OverlayScrollbars.min.css'
import './static/assets/plugins/summernote/summernote-bs4.min.css'
import './static/assets/plugins/fontawesome-free/css/all.min.css'
const ENDPOINT = 'http://127.0.0.1:5000';
const socket = socketIOClient(ENDPOINT);

function App() {
  const [file, setFile] = useState()
  const [frame, setFrame] = useState('');
  useEffect(() => {
    socket.on('connected', (data) => {
      console.log('Connected to server:', data);
    });
    socket.on('frame', (frameData) => {
      setFrame(frameData);
    });
  }, []);
  function handleChange(event) {
    setFile(event.target.files[0])
  }
  
  function handleSubmit(event) {
    event.preventDefault()
    const url = `${ENDPOINT}/upload`;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileName', file.name);
    const config = {
      headers: {
        'content-type': 'multipart/form-data',
      },
    };
    axios.post(url, formData, config).then((response) => {
      console.log(response.data);
    });

  }
  return (
    <div className="App">
      <div className="content-wrapper" style={{marginLeft: 0}}>
        <div className="content-header">
          <h1 className="m-0 text-dark">YOLOv9 Dashboard</h1>
        </div>
        <section className="content">
          <div className="container-fluid">
            <div className="row">
              <section className="col-lg-6 connectedSortable">
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">
                      <i className="fas fa-chart-pie mr-1" />
                      YOLOv9 Object Detection
                    </h3>
                  </div>
                  <div className="card-body">
                    <div className="tab-content p-0">
                      <div className="chart tab-pane active" id="revenue-chart" style={{position: 'relative', height: 700}}>
                        <form className="form-signin col-lg-3" onSubmit={handleSubmit} name="form1">
                          <h1 className="h3 mb-3 font-weight-normal">Upload any image or video</h1>
                          <input type="file" name="file" className="form-control-file" onChange={handleChange}/>
                          <br />
                          <button className="btn btn-block btn-default btn-sm " type="submit">Upload</button>
                        </form>
                      </div>
                    </div>
                  </div>
                </div></section>
              <section className="col-lg-6 connectedSortable">
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">
                      <i className="fas fa-chart-pie mr-1" />
                      YOLOv9 Object Detection Results
                    </h3>
                  </div>
                  <div className="card-body">
                    <div className="tab-content p-0">
                      <div className="chart tab-pane active" id="revenue-chart" style={{position: 'relative', height: 700}}>
                        {frame && <img src={`data:image/jpeg;base64,${frame}`} alt="Detected Frame" style={{height: 640, width: 640}}/>}
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
