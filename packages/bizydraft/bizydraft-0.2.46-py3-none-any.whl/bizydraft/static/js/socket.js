export class WebSocketClient {
  constructor(url, protocols) {

    const host = 'api.bizyair.cn';

    if (url.startsWith('ws://') || url.startsWith('wss://')) {
      this.url = url;
    } else {
      this.url = `${location.protocol == 'http:' ? 'wss' : 'wss'}://${host}${url}`
    }
    this.protocols = protocols
    this.reconnectDelay = 1000
    this.maxReconnectDelay = 30000
    this.keepAliveInterval = 10000
    this.ws = null
    this.keepAliveTimer = null
    this.reconnectTimer = null

    this.connect()
  }

  connect() {
    this.ws = new WebSocket(this.url, this.protocols)
    this.ws.onopen = () => {
      this.onOpen()
    }

    this.ws.onmessage = (message) => {
      if (message.data !== 'pong') {
        this.onMessage(message)
      }
    }

    this.ws.onerror = (error) => {
      this.onError(error)
    }

    this.ws.onclose = () => {
      console.warn('The WebSocket connection has been closed and is ready to be reconnected')
      this.onClose()
      this.scheduleReconnect()
    }
  }

  startKeepAlive() {
    if (this.keepAliveTimer) return

    this.keepAliveTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, this.keepAliveInterval)
  }

  stopKeepAlive() {
    if (this.keepAliveTimer) {
      clearInterval(this.keepAliveTimer)
      this.keepAliveTimer = null
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer) return

    this.reconnectTimer = setTimeout(() => {
      console.log(`Attempt to reconnect...`)
      this.connect()
      this.reconnectTimer = null

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay)
    }, this.reconnectDelay)
  }

  onOpen() {
    this.reconnectDelay = 2000
    this.startKeepAlive()
  }


  onError(error) {
    console.error('WebSocket Error: ', error)
  }

  onClose() {
    this.stopKeepAlive()
  }

  close() {
    if (this.ws) {
      this.ws.close()
    }
    this.stopKeepAlive()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  on(event, callback) {
    if (event === 'message') {
      this.onMessage = callback;
    } else if (event === 'open') {
      this.onOpen = callback;
    } else if (event === 'error') {
      this.onError = callback;
    } else if (event === 'close') {
      this.onClose = callback;
    }
    return this;
  }
}
