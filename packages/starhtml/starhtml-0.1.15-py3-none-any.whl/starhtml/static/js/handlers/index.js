import persist_default from "./persist.js";
import scroll_default from "./scroll.js";
import resize_default from "./resize.js";
import drag_default from "./drag.js";
import canvas_default from "./canvas.js";
import position_default from "./position.js";
const persist = persist_default;
const scroll = scroll_default;
const resize = resize_default;
const drag = drag_default;
const canvas = canvas_default;
const position = position_default;
export {
  canvas,
  canvas_default as canvasPlugin,
  drag,
  drag_default as dragPlugin,
  persist,
  persist_default as persistPlugin,
  position,
  position_default as positionPlugin,
  resize,
  resize_default as resizePlugin,
  scroll,
  scroll_default as scrollPlugin
};
