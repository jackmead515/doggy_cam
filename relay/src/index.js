const http = require('http');

const socket = require('./socket');
const config = require('./config');

async function main() {
    console.info('loaded configurations', JSON.stringify(config));

    try {
        const httpServer = http.createServer();

        console.info('initializing socket');

        await socket.initialize(httpServer);

        console.info('socket initialized');

        // healthz endpoint
        httpServer.on('request', (req, res) => {
            if (req.url === '/healthz') {
                res.writeHead(200);
                res.end('OK');
            }
        });

        httpServer.on('error', (error) => {
            console.error('http server error', error);
        });

        httpServer.listen(config.httpPort, () => {
            console.info('websocket relay started');
        });

    } catch (error) {
        console.error('error starting relay', error);
        throw error;
    }

    console.info('http server initialized');
}

main();