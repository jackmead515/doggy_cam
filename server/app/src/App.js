import React from 'react';

import Stream from './views/Stream';

export default class App extends React.Component {

  constructor(props) {  
    super(props);

    this.state = {
      view: 'stream',
    };
  }

  onViewStream() {
    this.setState({ view: 'stream' });
  }

  renderMenu() {
    return (
      <div className="menu">
        <button onClick={() => this.setState({ view: 'stream'})}>Stream</button>
        <button onClick={() => this.setState({ view: 'record'})}>Recordings</button>
      </div>
    )
  }

  render() {
    const { view, drawerOpen } = this.state;

    let viewComponent;

    if (view === 'stream') {
      viewComponent = <Stream />;
    }

    return (
      <>
        {this.renderMenu()}
        {viewComponent}
      </>
    );
  }
}