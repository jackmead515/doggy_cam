import React from 'react';
import eio from 'engine.io-client';

import JSMpegWritableSource from '../Source';


export default class Stream extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            connected: false,
            streaming: false,
        };

        this.socket = undefined;
        this.player = undefined;
        this.streamingTimeout = undefined;
    }

    componentWillUnmount() {
        if (this.socket) {
            this.socket.close();
        }

        if (this.streamingTimeout) {
            clearTimeout(this.streamingTimeout);
        }
    }

    componentDidMount() {
        //const host = window.location.hostname;
        const host = '172.23.0.104';
    
        this.socket = new eio.Socket(`ws://${host}:30300`, {
            upgrade: true,
            //transports: ['websocket']
        });
        this.socket.binaryType = 'arraybuffer';

        const canvas = document.getElementById('video-canvas');
    
        // eslint-disable-next-line no-undef
        this.player = new JSMpeg.Player(this.socket, {
            source: JSMpegWritableSource,
            audio: false,
            canvas: canvas,
        });
    
        this.socket.on('open', () => {
            this.setState({ connected: true });
    
            this.socket.on('data', data => {
                if (!isNaN(data.byteLength)) {
                    if (!this.state.streaming) {
                        this.setState({ streaming: true });
                        if (this.streamingTimeout) clearTimeout(this.streamingTimeout);
                        this.streamingTimeout = setTimeout(() => this.setState({ streaming: false }), 1000);
                    } else {
                        if (this.streamingTimeout) clearTimeout(this.streamingTimeout);
                        this.streamingTimeout = setTimeout(() => this.setState({ streaming: false }), 1000);
                    }
        
                    try {
                        this.player.source.write(data);
                    } catch (e) {}
                }
            });
        });
        
        this.socket.on('close', (error) => {
            if (this.streamingTimeout) clearTimeout(this.streamingTimeout);
            this.setState({ connected: false, streaming: false });
        });
        
        this.socket.on('error', (error) => {
            console.log('error', error);
        });
    }

    playStream() {
        this.socket.send('play_stream');
    }
    
    pauseStream() {
        this.socket.send('stop_stream');
    }

    renderStreamStatus() {
        const { connected, streaming } = this.state;

        let streamingComponent = (
            <div class="connected">
                Not Streaming
                <div class='connected--false'></div>
            </div>
        );

        if (streaming) {
            streamingComponent = (
                <div class="connected">
                    Streaming
                    <div class='connected--true'></div>
                </div>
            );
        }

        let connectedComponent = (
            <div class="connected">
                Disconnected
                <div class='connected--false'></div>
            </div>
        );

        if (connected) {
            connectedComponent = (
                <div class="connected">
                    Connected
                    <div class='connected--true'></div>
                </div>
            );
        }

        return (
            <div className='stream__status'>
                {connectedComponent}
                {streamingComponent}
            </div>
        );
    }

    render() {
        return (
            <div className='stream'>
                <div className='stream__player'>
                    <div className='stream__video'> 
                        <canvas className='stream__canvas' id="video-canvas">
                        </canvas>
                    </div>
                    <div className='stream__controls'>
                        <button onClick={() => this.playStream()}>Play</button>
                        <button onClick={() => this.pauseStream()}>Pause</button>
                    </div>
                </div>

            </div>
        );
    }
}