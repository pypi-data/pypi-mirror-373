import cC from './sign.js'

const [_, __, now, trace, payload] = process.argv
const e = {
  timestamp: now,
  traceId: trace,
  deviceId: "ccfb6d50-b63b-11ef-b31f-ef1f76f67c4e",
  platformId: "30",
  appVersion: "9.0.5",
  requestPayload: JSON.parse(payload)
};

const sgn = cC(e).sign;
console.log(sgn);