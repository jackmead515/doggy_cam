export default class JSMpegWritableSource {
    constructor(url, options) {
      this.destination = null;
      this.completed = false;
      this.established = false;
      this.progress = 0;
      this.streaming = true;
    }
  
    connect(destination) {
      this.destination = destination;
    }
  
    start() {
      this.established = true;
      this.completed = true;
      this.progress = 1;
    }
  
    resume() {}
  
    destroy() {}
  
    write(data) {
      this.destination.write(data);
    }
  }