/**
 * Slate IPC message types and helpers for frontend/backend communication.
 */

/**
 * @typedef {Object} IPCMessage
 * @property {string} type
 * @property {Object} payload
 * @property {string} sender
 */

export const SENDER_CORE = 'slate-core';
export const SENDER_UI = 'slate-ui';

/**
 * @param {string} type
 * @param {Object} payload
 * @param {string} sender
 * @returns {IPCMessage}
 */
export function createIPCMessage(type, payload, sender = SENDER_CORE) {
  return {
    type,
    payload,
    sender
  };
}

export const MSG_WEBVIEW_LOAD = 'BROWSER_WEBVIEW_LOAD';

/**
 * @param {string} tabId
 * @param {string} url
 * @param {boolean} adBlocked
 * @returns {IPCMessage}
 */
export function createWebviewIPC(tabId, url, adBlocked) {
  return createIPCMessage(MSG_WEBVIEW_LOAD, {
    tabId,
    url,
    config: {
      sandbox: true,
      adBlocked
    }
  });
}
