import { gone } from '../_lib/gone.js';

export function onRequest(context) {
  return gone(context.request);
}
